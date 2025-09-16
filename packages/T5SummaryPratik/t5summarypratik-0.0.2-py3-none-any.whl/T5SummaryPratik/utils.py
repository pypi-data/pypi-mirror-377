import json
from T5SummaryPratik.pipeline import CompleteSummarizationPipeline

def setx(file_path):
    """
    Extract content details from the last model_output in a JSON structure.

    Args:
        json_data (dict): The parsed JSON data

    Returns:
        str: Formatted string with extracted details or error message

    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            # return extract_content_details(json_data)
    except FileNotFoundError:
        return f'Error: File "{file_path}" not found.'
    except json.JSONDecodeError as e:
        return f'Error: Invalid JSON format - {str(e)}'
    except Exception as e:
        return f'Error reading file: {str(e)}'
    try:
        # Check if history exists
        if 'history' not in json_data or not isinstance(json_data['history'], list):
            return 'Error: No "history" array found in the JSON file.'

        # Get the last history entry
        if not json_data['history']:
            return 'Error: History array is empty.'

        last_entry = json_data['history'][-1]

        if 'model_output' not in last_entry:
            return 'Error: No "model_output" found in the last history entry.'

        model_output = last_entry['model_output']

        # Check if action exists
        if 'action' not in model_output or not isinstance(model_output['action'], list):
            return 'Error: No "action" array found in model_output.'

        # Find extract_content action
        extract_content_action = None
        for action in model_output['action']:
            if 'extract_content' in action:
                extract_content_action = action['extract_content']
                break

        if extract_content_action is None:
            return 'Error: No "extract_content" action found in the last model_output.'

        # Build the result string
        result_parts = []

        # Add memory, evaluation, and thinking if available
        if 'memory' in model_output and model_output['memory']:
            result_parts.append(model_output['memory'])

        if 'evaluation_previous_goal' in model_output and model_output['evaluation_previous_goal']:
            if model_output['evaluation_previous_goal'] != "No previous action to evaluate - this is the first step":
                result_parts.append(model_output['evaluation_previous_goal'])

        if 'next_goal' in model_output and model_output['next_goal']:
            result_parts.append(model_output['next_goal'])

        if 'thinking' in model_output and model_output['thinking']:
            result_parts.append(model_output['thinking'])

        result_message = '.. '.join(result_parts) + '.. Actions: ' if result_parts else 'Actions: '

        # Process extract_content details
        if 'details' in extract_content_action and isinstance(extract_content_action['details'], list):
            details_array = []

            for detail in extract_content_action['details']:
                detail_parts = []

                # Process each key-value pair in the detail object
                for key, value in detail.items():
                    if isinstance(value, list):
                        detail_parts.append(f"{key.capitalize()}: {', '.join(map(str, value))}")
                    else:
                        detail_parts.append(f"{key.capitalize()}: {value}")

                details_array.append('; '.join(detail_parts))

            result_message += ' | '.join(details_array)
        else:
            # Handle other formats of extract_content
            result_message += json.dumps(extract_content_action, indent=2)

        return result_message

    except Exception as e:
        return f'Error processing JSON: {str(e)}'

    # Example usage with file
    # result = extract_from_file('hotels.json')
    # print(result)
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
