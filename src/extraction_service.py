import os
import json
import re
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def parse_json_response(response_text: str) -> dict:
    """
    Robust JSON parser that handles various LLM output formats.

    Args:
        response_text: The raw text response from the LLM

    Returns:
        Parsed JSON as a dictionary

    Raises:
        ValueError: If JSON cannot be parsed after all attempts
    """
    # Remove leading/trailing whitespace
    text = response_text.strip()

    # Try 1: Direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try 2: Remove markdown code blocks
    # Pattern: ```json ... ``` or ``` ... ```
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    matches = re.findall(code_block_pattern, text)
    if matches:
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

    # Try 3: Find JSON object between first { and last }
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        json_candidate = text[first_brace:last_brace + 1]
        try:
            return json.loads(json_candidate)
        except json.JSONDecodeError:
            pass

    # Try 4: Find JSON array between first [ and last ]
    first_bracket = text.find('[')
    last_bracket = text.rfind(']')
    if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
        json_candidate = text[first_bracket:last_bracket + 1]
        try:
            return json.loads(json_candidate)
        except json.JSONDecodeError:
            pass

    # Try 5: Clean up common issues
    # Remove potential extra commas before closing braces/brackets
    cleaned = re.sub(r',\s*([}\]])', r'\1', text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # If all attempts fail, raise an error with the original text
    raise ValueError(f"Failed to parse JSON from response. First 500 chars: {text[:500]}")


def load_prompt_template() -> str:
    """
    Load the extraction prompt template from the prompts folder.

    Returns:
        The prompt template as a string
    """
    prompt_path = Path(__file__).parent / "prompts" / "extraction_prompt.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_field_info(field_description: str, document: str) -> dict:
    """
    Extract specific information from a document based on a field description.

    Args:
        field_description: Description of the field to extract (can be string or dict)
        document: The document text to search in

    Returns:
        A dictionary containing the extracted information in JSON format
    """
    # Load prompt template
    prompt_template = load_prompt_template()

    # If field_description is a dict, convert it to a formatted string
    if isinstance(field_description, dict):
        field_desc_str = f"""
Field Name: {field_description.get('name', 'N/A')}
Description: {field_description.get('description', 'N/A')}
Format: {field_description.get('format', 'N/A')}
Example: {field_description.get('example', 'N/A')}
"""
    else:
        field_desc_str = field_description

    # Format the prompt with the field description and document
    prompt = prompt_template.format(
        field_description=field_desc_str,
        document=document
    )

    # Initialize the Gemini model (using Gemini 3 Flash)
    # Configure with JSON response format
    model = genai.GenerativeModel(
        "gemini-3-flash-preview",
        generation_config={
            "response_mime_type": "application/json"
        }
    )

    # Generate content
    response = model.generate_content(prompt)

    # Parse the JSON response using robust parser
    try:
        result = parse_json_response(response.text)
        return result
    except (json.JSONDecodeError, ValueError) as e:
        # If parsing fails, return error with raw response
        return {
            "error": f"Failed to parse JSON response: {str(e)}",
            "raw_response": response.text,
            "field_name": field_description.get('name', 'unknown') if isinstance(field_description, dict) else 'unknown'
        }


def extract_multiple_fields(field_descriptions: list, document: str) -> list:
    """
    Extract multiple fields from a document.

    Args:
        field_descriptions: List of field descriptions (can be strings or dicts)
        document: The document text to search in

    Returns:
        A list of dictionaries containing the extracted information for each field
    """
    results = []

    for field_desc in field_descriptions:
        result = extract_field_info(field_desc, document)
        results.append(result)

    return results


def extract_from_file(field_description: str, file_path: str) -> dict:
    """
    Extract field information from a document file.

    Args:
        field_description: Description of the field to extract
        file_path: Path to the document file (text, markdown, or JSON)

    Returns:
        A dictionary containing the extracted information
    """
    # Read the document file
    with open(file_path, 'r', encoding='utf-8') as f:
        if file_path.endswith('.json'):
            data = json.load(f)
            # If it's a JSON file with markdown_text field (from OCR)
            document = data.get('markdown_text', json.dumps(data))
        else:
            document = f.read()

    return extract_field_info(field_description, document)


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
    """

    print("Extracting field information...")
    result = extract_field_info(example_field_desc, example_document)
    print("\nResult:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
