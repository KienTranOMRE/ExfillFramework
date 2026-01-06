import sys
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from extraction_service import extract_field_info


def load_field_descriptions(file_path):
    """Load field descriptions from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_document(file_path):
    """Load document from JSON file (OCR output)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('markdown_text', '')


def extract_single_field(field_desc, document, index):
    """Extract a single field and return with index for ordering."""
    print(f"[{index + 1}] Extracting: {field_desc['name']}")
    result = extract_field_info(field_desc, document)
    print(f"[{index + 1}] ✓ Completed: {field_desc['name']}")
    return index, field_desc['name'], result


def main():
    # File paths
    field_descriptions_path = "data/input/partial_field_descriptions.json"
    document_path = "data/output/Input_test1.json"
    output_path = "data/output/extraction_results.json"

    print("=" * 80)
    print("EXTRACTION SERVICE TEST")
    print("=" * 80)

    # Load field descriptions
    print(f"\n1. Loading field descriptions from: {field_descriptions_path}")
    field_descriptions = load_field_descriptions(field_descriptions_path)
    print(f"   Found {len(field_descriptions)} fields to extract")

    # Load document
    print(f"\n2. Loading document from: {document_path}")
    document = load_document(document_path)
    print(f"   Document loaded ({len(document)} characters)")

    # Extract all fields concurrently for speed
    print(f"\n3. Extracting fields (concurrent processing)...")
    print("-" * 80)

    start_time = datetime.now()
    results = {}

    # Use ThreadPoolExecutor for concurrent API calls
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all extraction tasks
        futures = {
            executor.submit(extract_single_field, field_desc, document, i): i
            for i, field_desc in enumerate(field_descriptions)
        }

        # Collect results as they complete
        for future in as_completed(futures):
            try:
                index, field_name, result = future.result()
                results[field_name] = result
            except Exception as e:
                print(f"   ✗ Error extracting field: {e}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("-" * 80)
    print(f"\n4. Extraction completed in {duration:.2f} seconds")

    # Prepare output data
    output_data = {
        "extraction_timestamp": datetime.now().isoformat(),
        "source_document": document_path,
        "field_descriptions_source": field_descriptions_path,
        "total_fields": len(field_descriptions),
        "extraction_duration_seconds": duration,
        "results": results
    }

    # Save results
    print(f"\n5. Saving results to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"   ✓ Results saved successfully")

    # Print summary
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)

    for i, field_desc in enumerate(field_descriptions, 1):
        field_name = field_desc['name']
        result = results.get(field_name, {})

        print(f"\n{i}. {field_name}")
        print(f"   Extracted Value: {result.get('extracted_value', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 'N/A')}")
        if result.get('source_text'):
            source_preview = result['source_text'][:100] + "..." if len(result['source_text']) > 100 else result['source_text']
            print(f"   Source: {source_preview}")

    print("\n" + "=" * 80)
    print(f"Test completed! Results saved to: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
