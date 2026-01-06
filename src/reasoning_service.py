import os
import json
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Import the JSON parser from extraction_service
from extraction_service import parse_json_response

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def load_reasoning_prompt_template() -> str:
    """
    Load the reasoning prompt template from the prompts folder.

    Returns:
        The prompt template as a string
    """
    prompt_path = Path(__file__).parent / "prompts" / "reasoning_prompt.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def determine_final_answer(extraction_result: dict, field_description: dict) -> dict:
    """
    Determine the final answer for a field based on extraction results.

    Args:
        extraction_result: The result from extraction_service containing relevant_paragraphs
        field_description: Dict with field name, description, format, example

    Returns:
        A dictionary containing the final answer and reasoning
    """
    # Load prompt template
    prompt_template = load_reasoning_prompt_template()

    # Format the extracted paragraphs for the prompt
    paragraphs_text = ""
    if "relevant_paragraphs" in extraction_result and extraction_result["relevant_paragraphs"]:
        for i, para in enumerate(extraction_result["relevant_paragraphs"], 1):
            paragraphs_text += f"\n--- Paragraph {i} (Location: {para.get('location', 'Unknown')}) ---\n"
            paragraphs_text += para.get('paragraph_text', '')
            paragraphs_text += f"\nRelevance: {para.get('relevance_note', 'N/A')}\n"
    else:
        paragraphs_text = "No relevant paragraphs found."

    # Format the prompt
    prompt = prompt_template.format(
        field_name=field_description.get('name', 'N/A'),
        field_description=field_description.get('description', 'N/A'),
        field_format=field_description.get('format', 'N/A'),
        field_example=field_description.get('example', 'N/A'),
        extracted_paragraphs=paragraphs_text
    )

    # Initialize the Gemini model with JSON output
    model = genai.GenerativeModel(
        "gemini-3-flash-preview",
        generation_config={
            "response_mime_type": "application/json"
        }
    )

    # Generate content
    response = model.generate_content(prompt)

    # Parse the JSON response
    try:
        result = parse_json_response(response.text)
        return result
    except (json.JSONDecodeError, ValueError) as e:
        # If parsing fails, return error with raw response
        return {
            "error": f"Failed to parse JSON response: {str(e)}",
            "raw_response": response.text,
            "field_name": field_description.get('name', 'unknown')
        }


def process_field_complete(field_description: dict, document: str) -> dict:
    """
    Complete pipeline: extract paragraphs and determine final answer.

    Args:
        field_description: Dict with field name, description, format, example
        document: The document text to analyze

    Returns:
        A dictionary containing both extraction and reasoning results
    """
    from extraction_service import extract_field_info

    # Step 1: Extract relevant paragraphs
    extraction_result = extract_field_info(field_description, document)

    # Step 2: Determine final answer
    final_result = determine_final_answer(extraction_result, field_description)

    # Combine results
    return {
        "field_name": field_description.get('name', 'N/A'),
        "extraction": extraction_result,
        "final_answer": final_result
    }


def process_multiple_fields_complete(field_descriptions: list, document: str) -> list:
    """
    Process multiple fields through the complete pipeline.

    Args:
        field_descriptions: List of field description dicts
        document: The document text to analyze

    Returns:
        A list of results for each field
    """
    results = []

    for field_desc in field_descriptions:
        result = process_field_complete(field_desc, document)
        results.append(result)

    return results


if __name__ == "__main__":
    # Example usage
    example_field_desc = {
        "name": "Contract Date",
        "description": "The date when the contract was signed or became effective",
        "format": "DD/MM/YYYY",
        "example": "25/12/2024"
    }

    example_document = """
    SALES CONTRACT

    This contract is made on December 25, 2024 between:
    - Seller: ABC Company
    - Buyer: XYZ Corporation

    Total Amount: USD 100,000.00
    Payment Terms: Letter of Credit
    Delivery: 30 days from contract date

    The effective date of this agreement is 25/12/2024.
    """

    print("Processing field through complete pipeline...")
    result = process_field_complete(example_field_desc, example_document)

    print("\n" + "=" * 80)
    print("COMPLETE RESULT")
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
