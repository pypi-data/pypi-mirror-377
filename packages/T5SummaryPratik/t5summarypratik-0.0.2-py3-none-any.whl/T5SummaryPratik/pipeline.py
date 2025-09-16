from transformers import (
    pipeline, T5ForConditionalGeneration, T5Tokenizer,
    BartForConditionalGeneration, BartTokenizer,
    AutoModelForCausalLM, AutoTokenizer
)
import textwrap
import warnings
import torch
import math
from evaluate import load
import textstat
import nltk
import json # Moved import json back to the top

# Suppress warnings
warnings.filterwarnings("ignore")

# Download necessary NLTK data if not already present
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("Downloading wordnet...")
    nltk.download('wordnet', quiet=True)
    try:
        nltk.data.find('corpora/wordnet')
        print("wordnet downloaded successfully.")
    except LookupError:
        print("Error: wordnet download failed.")

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading punkt...")
    nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('tokenizers/punkt')
        print("punkt downloaded successfully.")
    except LookupError:
        print("Error: punkt download failed.")

try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    print("Downloading omw-1.4...")
    nltk.download('omw-1.4', quiet=True)
    try:
        nltk.data.find('corpora/omw-1.4')
        print("omw-1.4 downloaded successfully.")
    except LookupError:
        print("Error: omw-1.4 download failed.")


class CompleteSummarizationPipeline:
    def __init__(self):
        """Initialize the complete pipeline with all models and metrics"""
        print("Initializing Complete Summarization Pipeline...")

        # Initialize summarization model
        self.model_name = "google/flan-t5-large"
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)

        # Set device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        # Initialize perplexity model
        self.ppl_model_name = "gpt2"
        self.ppl_model = AutoModelForCausalLM.from_pretrained(self.ppl_model_name)
        self.ppl_tokenizer = AutoTokenizer.from_pretrained(self.ppl_model_name)

        # Initialize evaluation metrics
        self.rouge = load("rouge")
        self.bleu = load("bleu")
        self.meteor = load("meteor")
        self.bertscore = load("bertscore")

        print("Pipeline initialization complete!")

    def preprocess_text(self, text):
        """Clean and prepare text for summarization"""
        # Remove excessive whitespace and newlines
        text = ' '.join(text.split())

        # Ensure text ends with proper punctuation
        if not text.endswith(('.', '!', '?')):
            text += '.'

        return text

    def create_prompt(self, text, summary_type="general"):
        """Create better prompts for more human-like output"""
        prompts = {
            "general": f"Summarize this text in a clear way without losing important information: {text}",
            "conversational": f"Explain the main points of this text in simple terms: {text}",
            "narrative": f"Tell me what this text is about in your own words: {text}",
            "bullet": f"List the key points from this text: {text}",
            "abstract": f"Write an abstract summarizing this research: {text}"
        }
        return prompts.get(summary_type, prompts["general"])

    def generate_summary(self, text, max_length=150, min_length=30,
                        summary_type="general", temperature=0.7):
        """Generate human-like summary with better parameters"""

        # Preprocess the input
        clean_text = self.preprocess_text(text)

        # Create appropriate prompt
        prompt = self.create_prompt(clean_text, summary_type)

        # Tokenize input
        inputs = self.tokenizer.encode(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).to(self.device)

        # Generate with parameters that encourage human-like output
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                min_length=min_length,
                num_beams=4,  # Good balance for quality
                do_sample=True,  # Add some randomness
                temperature=temperature,  # Control creativity
                top_p=0.9,  # Nucleus sampling
                top_k=50,  # Limit vocabulary
                repetition_penalty=1.2,  # Reduce repetition
                length_penalty=1.0,  # Don't penalize length
                early_stopping=True,
                no_repeat_ngram_size=3,  # Avoid repeating phrases
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode and clean output
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self.postprocess_summary(summary)

    def postprocess_summary(self, summary):
        """Clean up the generated summary"""
        # Remove common artifacts
        artifacts = [
            "summarize this text in a clear way without losing important information:",
            "explain the main points of this text in simple terms:",
            "tell me what this text is about in your own words:",
            "list the key points from this text:",
            "write an abstract summarizing this research:"
        ]

        summary_lower = summary.lower()
        for artifact in artifacts:
            if summary_lower.startswith(artifact):
                summary = summary[len(artifact):].strip()
                break

        # Capitalize first letter
        if summary:
            summary = summary[0].upper() + summary[1:]

        # Ensure proper ending punctuation
        if summary and not summary.endswith(('.', '!', '?')):
            summary += '.'

        return summary

    def chunk_and_summarize(self, text, chunk_size=400, overlap=50):
        """Handle long texts by chunking"""
        words = text.split()

        if len(words) <= chunk_size:
            return self.generate_summary(text)

        chunks = []
        start = 0

        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)

            if end >= len(words):
                break
            start += chunk_size - overlap

        # Summarize each chunk
        chunk_summaries = []
        for chunk in chunks:
            summary = self.generate_summary(
                chunk,
                max_length=80,
                min_length=20,
                temperature=0.6
            )
            chunk_summaries.append(summary)

        # Combine and create final summary
        combined = " ".join(chunk_summaries)

        if len(combined.split()) > 200:
            final_summary = self.generate_summary(
                combined,
                max_length=150,
                min_length=50,
                summary_type="general",
                temperature=0.7
            )
        else:
            final_summary = combined

        return final_summary

    def calculate_perplexity(self, text):
        """Compute perplexity for a given text"""
        inputs = self.ppl_tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.ppl_model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
        ppl = math.exp(loss.item())
        return ppl

    def evaluate_summary(self, generated_summary, reference_summary, original_text=None):
        """Evaluate summary quality using multiple metrics"""
        results = {}

        # ROUGE
        rouge_result = self.rouge.compute(
            predictions=[generated_summary],
            references=[reference_summary]
        )
        results['rouge'] = rouge_result

        # BLEU
        bleu_result = self.bleu.compute(
            predictions=[generated_summary],
            references=[[reference_summary]]
        )
        results['bleu'] = bleu_result

        # METEOR
        meteor_result = self.meteor.compute(
            predictions=[generated_summary],
            references=[reference_summary]
        )
        results['meteor'] = meteor_result

        # BERTScore
        bertscore_result = self.bertscore.compute(
            predictions=[generated_summary],
            references=[reference_summary],
            lang="en"
        )
        results['bertscore'] = bertscore_result

        # Perplexity
        ppl = self.calculate_perplexity(generated_summary)
        results['perplexity'] = ppl

        # Flesch Reading Ease
        results['flesch_reading_ease'] = textstat.flesch_reading_ease(generated_summary)


        # Compression Ratio
        # Ensure original_text is a string before splitting
        if original_text and isinstance(original_text, str):
            results['compression_ratio'] = len(generated_summary.split()) / len(original_text.split())
        else:
            # Fallback to reference summary if original text is not provided
            if isinstance(reference_summary, str): # Ensure reference is string before splitting
                 results['compression_ratio'] = len(generated_summary.split()) / len(reference_summary.split())
            else:
                results['compression_ratio'] = None


        # Coverage (% of reference words present in generated summary)
        # Ensure both generated_summary and reference_summary are strings before splitting
        if isinstance(reference_summary, str) and isinstance(generated_summary, str):
            ref_words = set(reference_summary.lower().split())
            gen_words = set(generated_summary.lower().split())
            coverage = len(ref_words & gen_words) / len(ref_words) * 100 if ref_words else 0
            results['coverage'] = coverage
        else:
            results['coverage'] = None


        return results


    def format_summary(self, summary, width=80):
        """Format summary for better readability"""
        return "\n".join(textwrap.wrap(summary, width=width))

    def summarize_and_evaluate(self, text, reference_summary=None, style="general", length="medium"):
        """Complete pipeline: summarize text and evaluate if reference is provided"""

        # Set length parameters
        length_configs = {
            "short": {"max_length": 80, "min_length": 20},
            "medium": {"max_length": 150, "min_length": 40},
            "long": {"max_length": 250, "min_length": 80},
            "large": {"max_length": 350, "min_length": 100}
        }

        config = length_configs.get(length, length_configs["medium"])

        print(f"\n{'='*60}")
        print(f"PROCESSING TEXT ({style.upper()} STYLE, {length.upper()} LENGTH)")
        print(f"{'='*60}")

        # Display original text
        print("\nORIGINAL TEXT:")
        print(self.format_summary(text, width=80))
        print(f"\n{'-'*50}\n")

        # Generate summary
        if len(text.split()) > 500:
            summary = self.chunk_and_summarize(text)
        else:
            summary = self.generate_summary(
                text,
                summary_type=style,
                **config
            )

        # Display generated summary
        print(f"{style.upper()} SUMMARY:")
        print(self.format_summary(summary))

        # Calculate perplexity for fluency
        ppl = self.calculate_perplexity(summary)
        print(f"\nFluency Score (Perplexity): {ppl:.2f} (lower is better)")

        # Evaluate against reference if provided
        if reference_summary:
            print(f"\n{'-'*30}")
            print("EVALUATION METRICS")
            print(f"{'-'*30}")

            evaluation = self.evaluate_summary(summary, reference_summary, text)

            print(f"\nROUGE Scores:")
            for key, value in evaluation['rouge'].items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")

            print(f"\nBLEU Score: {evaluation['bleu']['bleu']:.4f}")
            print(f"METEOR Score: {evaluation['meteor']['meteor']:.4f}")

            print(f"\nBERTScore:")
            print(f"  Precision: {evaluation['bertscore']['precision'][0]:.4f}")
            print(f"  Recall:    {evaluation['bertscore']['recall'][0]:.4f}")
            print(f"  F1:        {evaluation['bertscore']['f1'][0]:.4f}")

            # Display additional metrics if available
            if 'flesch_reading_ease' in evaluation:
                print(f"\nAdditional Metrics:")
                flesch_score = evaluation['flesch_reading_ease']
                print(f"  Flesch Reading Ease: {flesch_score:.2f}", end="")
                if flesch_score >= 90:
                    print(" (Very Easy)")
                elif flesch_score >= 80:
                    print(" (Easy)")
                elif flesch_score >= 70:
                    print(" (Fairly Easy)")
                elif flesch_score >= 60:
                    print(" (Standard)")
                elif flesch_score >= 50:
                    print(" (Fairly Difficult)")
                elif flesch_score >= 30:
                    print(" (Difficult)")
                else:
                    print(" (Very Difficult)")

                print(f"  Compression Ratio: {evaluation['compression_ratio']:.2f}")
                print(f"  Coverage: {evaluation['coverage']:.2f}%")


        return {
            'original_text': text,
            'summary': summary,
            'perplexity': ppl,
            'evaluation': evaluation if reference_summary else None
        }


    def compare_summaries(self, summaries_dict, metrics_list=None, output_json="best_summaries.json"):
        """
        Compare multiple summaries based on combined weighted score.
        metrics_list should be aligned with summaries_dict (same order).
        Appends the best summary + metrics to a JSON file.
        """
        from datetime import datetime


        print(f"\n{'='*40}")
        print("SUMMARY COMPARISON (Weighted Score)")
        print(f"{'='*40}")

        results = []
        for idx, (name, summary) in enumerate(summaries_dict.items()):
            ppl = self.calculate_perplexity(summary)

            # Get evaluation metrics if available
            evaluation = {} # Initialize evaluation dictionary
            if metrics_list and idx < len(metrics_list) and metrics_list[idx] is not None:
                evaluation = metrics_list[idx]

                bert_f1 = evaluation.get('bertscore', {}).get('f1', [0])[0]
                meteor = evaluation.get('meteor', {}).get('meteor', 0)
                coverage_score = evaluation.get('coverage', 0) / 100  # normalize 0–1
                flesch_score = evaluation.get('flesch_reading_ease', 0) / 100  # normalize 0–1
                compression_ratio = evaluation.get('compression_ratio', 0)

                # Weighted final score
                final_score = (
                    0.5 * bert_f1 +
                    0.15 * meteor +
                    0.15 * coverage_score +
                    0.1 * flesch_score +
                    0.1 * compression_ratio
                )
            else:
                final_score = None

            results.append((name, summary, ppl, final_score, evaluation))

            print(f"\n{name}:")
            print(f"Perplexity: {ppl:.2f}")
            if final_score is not None:
                print(f"Final Weighted Score: {final_score:.4f}")
            print(f"Summary: {self.format_summary(summary)}")

        # Find best summary
        if metrics_list and any(r[3] is not None for r in results):
            best = max(results, key=lambda x: x[3] if x[3] is not None else -float('inf'))  # highest final score
            print(f"\n🏆 BEST SUMMARY (Weighted Score): {best[0]} (Score: {best[3]:.4f})")
        else:
            best = min(results, key=lambda x: x[2])  # fallback to lowest perplexity
            print(f"\n🏆 MOST FLUENT SUMMARY: {best[0]} (Perplexity: {best[2]:.2f})")

        # ---- Append best summary + metrics to JSON ----
        best_summary_data = {
            "name": best[0],
            "summary": best[1],
            "perplexity": best[2],
            "final_score": best[3],
            "metrics": best[4]
        }

        # try:
        #     with open("hotels.json", "r") as f:
        #         data = json.load(f)
        # except (FileNotFoundError, json.JSONDecodeError):
        #     data = {} # Initialize as dictionary if file is empty or corrupt

        # # Ensure 'history' key exists and is a list
        # if "history" not in data or not isinstance(data["history"], list):
        #     data["history"] = []

        # data["history"].append(best_summary_data)

        # with open("hotels.json", "w") as f:
        #     json.dump(data, f, indent=4)

        # return results
        from datetime import datetime

        try:
          with open(output_json, "r") as f:
            data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
          data = {}  # keep root as dict

        timestamp = datetime.now().isoformat()
        data[timestamp] = best_summary_data  # store under unique key

        with open(output_json, "w") as f:
          json.dump(data, f, indent=4)