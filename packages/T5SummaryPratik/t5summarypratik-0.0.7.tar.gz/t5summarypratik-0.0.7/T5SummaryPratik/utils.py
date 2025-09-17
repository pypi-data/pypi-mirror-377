import json
from T5SummaryPratik.pipeline import CompleteSummarizationPipeline

def setx(json_data):
    """
    Dynamically extract the last 'thinking' (inside model_output)
    and the last 'extracted_content' from any JSON structure.
    """
    with open(json_data, "r", encoding="utf-8") as f:
        data = json.load(f)
    def recursive_find(obj, key, results):
        """Recursively search for all values of a key in nested JSON."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    results.append(v)
                recursive_find(v, key, results)
        elif isinstance(obj, list):
            for item in obj:
                recursive_find(item, key, results)

    # Collect all "thinking" and "extracted_content"
    thinking_list, content_list = [], []
    # recursive_find(json_data, "thinking", thinking_list)
    recursive_find(data, "extracted_content", content_list)

    # Pick last occurrence if available
    # last_thinking = thinking_list[-1] if thinking_list else ""
    last_content = content_list[-1] if content_list else ""

    # Join them into one output
    return f"{last_content}"
# Usage Functions
def create_pipeline():
    """Factory function to create pipeline instance"""
    return CompleteSummarizationPipeline()

def quick_summarize(text, style="general", length="medium"):
    """Quick summarization without evaluation"""
    pipeline = create_pipeline()
    result = pipeline.summarize_and_evaluate(text, style=style, length=length)
    return result['summary']

def get(file_path):
    pipeline = create_pipeline()

    sample_text = setx(file_path)
    reference=sample_text
    # print("\nREFERENCE SUMMARY (Gemini):")
    # print(reference)
    print("\n" + "="*60 + "\n")

    # ---- Run pipeline with reference summary ----
    styles = ["general", "abstract", "conversational", "narrative"]
    ls=[]
    metrices=[]
    for style in styles:
        result = pipeline.summarize_and_evaluate(
            sample_text,
            reference_summary=reference, # Ensure reference_summary is a string
            style=style,
            length="medium"

        )
        ls.append(result["summary"])
        metrices.append(result['evaluation'])

    # Compare multiple summaries
    summaries_to_compare = {
        "Summary A": ls[0],
        "Summary B": ls[1],
        "Summary C": ls[2],
        "Summary D": ls[3]
    }

    pipeline.compare_summaries(summaries_to_compare,metrices)
