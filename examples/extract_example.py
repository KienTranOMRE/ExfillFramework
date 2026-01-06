import sys
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from extraction_service import extract_field_info, extract_multiple_fields, extract_from_file


def example_1_simple_extraction():
    """Example 1: Simple extraction with a single field"""
    print("=" * 60)
    print("EXAMPLE 1: Simple Field Extraction")
    print("=" * 60)

    field_description = "The date when the contract was signed"

    document = """
    SALES CONTRACT

    This contract is made on December 25, 2024 between:
    - Seller: ABC Company
    - Buyer: XYZ Corporation

    Total Amount: USD 100,000.00
    Payment Terms: Letter of Credit
    Delivery: 30 days from contract date
    """

    result = extract_field_info(field_description, document)
    print("\nField Description:", field_description)
    print("\nExtraction Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def example_2_structured_field():
    """Example 2: Extraction with structured field description"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Structured Field Description")
    print("=" * 60)

    field_description = {
        "name": "32B: Currency and Amount",
        "description": "The total value of the letter of credit including currency code and amount",
        "format": "3-letter currency code + decimal number",
        "example": "USD 449,220.00"
    }

    document = """
    LETTER OF CREDIT

    LC Number: LC2024-0001
    Date: December 26, 2024
    Beneficiary: XYZ Corporation

    Amount: USD 449,220.00
    Expiry Date: 15/12/2025
    """

    result = extract_field_info(field_description, document)
    print("\nField Name:", field_description['name'])
    print("\nExtraction Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def example_3_multiple_fields():
    """Example 3: Extract multiple fields at once"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Multiple Field Extraction")
    print("=" * 60)

    field_descriptions = [
        {
            "name": "LC Amount",
            "description": "The total value of the letter of credit",
            "format": "Currency code + amount"
        },
        {
            "name": "Expiry Date",
            "description": "The date when the letter of credit expires",
            "format": "DD/MM/YYYY"
        },
        {
            "name": "Partial Shipments",
            "description": "Whether partial shipments are allowed or not",
            "format": "Allowed/Not Allowed"
        }
    ]

    document = """
    LETTER OF CREDIT

    LC Number: LC2024-0001
    Issue Date: December 26, 2024

    Amount: USD 449,220.00
    Expiry Date: 15/12/2025 in SINGAPORE

    Partial Shipments: Allowed
    Transhipments: Not Allowed
    """

    results = extract_multiple_fields(field_descriptions, document)
    print("\nExtraction Results:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Field {i} ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))


def example_4_from_json_file():
    """Example 4: Extract from a JSON file (OCR output)"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Extract from JSON File")
    print("=" * 60)

    # This assumes you have an OCR output JSON file
    # You can run ocr.py first to generate this file

    field_description = {
        "name": "Ngày hết hạn thư tín dụngclear",
        "description": "Ngày hết hạn của thư tín dụng - đây là ngày cuối cùng mà người hưởng lợi có thể xuất trình chứng từ để được thanh toán theo thư tín dụng. Trong hợp đồng, thông tin này có thể được đề cập trong các điều khoản về thanh toán, thời hạn hiệu lực của thư tín dụng, hoặc điều khoản về chứng từ. Tìm kiếm các cụm từ như: 'ngày hết hạn', 'expiry date', 'thời hạn hiệu lực', 'valid until', 'expires on', 'ngày cuối cùng xuất trình', 'last presentation date', 'thời hạn xuất trình chứng từ', hoặc các điều khoản liên quan đến thời hạn thanh toán. Ngày có thể được viết theo các format: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY, hoặc dạng chữ như 'ngày 15 tháng 12 năm 2025'. CHỈ TRÍCH XUẤT PHẦN NGÀY, bỏ qua phần địa điểm nếu có. Đảm bảo trích xuất đúng ngày tháng năm, không bao gồm thời gian trong ngày.",

    }

    # Check if sample OCR output exists
    sample_file = Path(__file__).parent.parent / "data" / "output" / "Input_test1.json"

    if sample_file.exists():
        print(f"\nExtracting from: {sample_file}")
        result = extract_from_file(field_description, str(sample_file))
        print("\nExtraction Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\nSample file not found: {sample_file}")
        print("Run ocr.py first to generate the OCR output.")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "EXTRACTION SERVICE EXAMPLES" + " " * 21 + "║")
    print("╚" + "=" * 58 + "╝")

    # Run all examples
    # example_1_simple_extraction()
    # example_2_structured_field()
    # example_3_multiple_fields()
    example_4_from_json_file()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60 + "\n")
