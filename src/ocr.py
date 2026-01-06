import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from ocr_services import OCRServiceFactory

# Load environment variables
load_dotenv()


def ocr(pdf_file_path: str, service: Optional[str] = None) -> str:
    """
    Perform OCR on a PDF file using the configured OCR service.

    Args:
        pdf_file_path: Path to the PDF file
        service: OCR service to use ('gemini', 'openai', 'ocrspace').
                If not provided, uses OCR_SERVICE from environment (default: 'gemini')

    Returns:
        Extracted text in markdown format

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        ValueError: If the service is not supported or not configured
        Exception: If OCR processing fails
    """
    # Create OCR service instance
    ocr_service = OCRServiceFactory.create(service)

    # Perform OCR
    return ocr_service.ocr(pdf_file_path)


def ocr_and_save(pdf_file_path: str, output_dir: str = None, service: Optional[str] = None) -> str:
    """
    Perform OCR on a PDF file and save the result to a JSON file.

    Args:
        pdf_file_path: Path to the PDF file
        output_dir: Directory to save the output JSON file (default: same directory as PDF)
        service: OCR service to use ('gemini', 'openai', 'ocrspace').
                If not provided, uses OCR_SERVICE from environment (default: 'gemini')

    Returns:
        Path to the saved JSON file
    """
    # Perform OCR
    markdown_text = ocr(pdf_file_path, service)

    # Get the PDF file name without extension
    pdf_path = Path(pdf_file_path)
    json_filename = pdf_path.stem + ".json"

    # Determine output directory
    if output_dir is None:
        output_path = pdf_path.parent / json_filename
    else:
        output_path = Path(output_dir) / json_filename

    # Get the service name used
    service_name = service or os.getenv('OCR_SERVICE', 'gemini')

    # Create the JSON data
    result_data = {
        "pdf_path": str(pdf_path.absolute()),
        "ocr_service": service_name,
        "markdown_text": markdown_text
    }

    # Save to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    return str(output_path)


def list_available_services():
    """
    Print information about available OCR services.
    """
    services = OCRServiceFactory.get_service_info()

    print("Available OCR Services:")
    print("=" * 60)

    for service_key, info in services.items():
        print(f"\n{service_key.upper()}: {info['name']}")
        print(f"  Environment Variable: {info['env_var']}")
        print(f"  Dependencies: {', '.join(info['dependencies'])}")
        print(f"  Description: {info['description']}")

    print("\n" + "=" * 60)
    print("\nTo use a service, set OCR_SERVICE environment variable")
    print("Example: OCR_SERVICE=openai")


if __name__ == "__main__":
    import sys

    # Check if user wants to list services
    if len(sys.argv) > 1 and sys.argv[1] == '--list-services':
        list_available_services()
        sys.exit(0)

    # Example usage
    output_dir = "/Users/kientran8/Codes/ExfillFramework/data/output"
    pdf_path = "/Users/kientran8/Codes/ExfillFramework/data/input/Input_test1.pdf"

    # You can specify which service to use:
    # - Pass service parameter: ocr_and_save(pdf_path, output_dir, service='openai')
    # - Or set OCR_SERVICE environment variable in .env file
    # - Defaults to 'gemini' if not specified

    try:
        # Perform OCR and save to JSON
        json_path = ocr_and_save(pdf_path, output_dir)
        print(f"OCR completed successfully!")
        print(f"Result saved to: {json_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
