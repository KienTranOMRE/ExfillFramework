import sys
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from reasoning_service import process_field_complete


def load_field_descriptions(file_path):
    """Load field descriptions from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_document(file_path):
    """Load document from JSON file (OCR output)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('markdown_text', '')


def process_single_field(field_desc, document, index):
    """Process a single field through extraction and reasoning."""
    print(f"[{index + 1}] Processing: {field_desc['name']}")
    result = process_field_complete(field_desc, document)
    print(f"[{index + 1}] ✓ Completed: {field_desc['name']}")
    return index, field_desc['name'], result


def main():
    # File paths
    field_descriptions_path = "data/input/partial_field_descriptions.json"
    document_path = "data/output/Input_test1.json"
    output_path = "data/output/complete_pipeline_results.json"

    print("=" * 80)
    print("COMPLETE PIPELINE TEST: EXTRACTION + REASONING")
    print("=" * 80)

    # Load field descriptions
    print(f"\n1. Loading field descriptions from: {field_descriptions_path}")
    field_descriptions = load_field_descriptions(field_descriptions_path)
    print(f"   Found {len(field_descriptions)} fields to process")

    # Load document
    print(f"\n2. Loading document from: {document_path}")
    document = load_document(document_path)
    print(f"   Document loaded ({len(document)} characters)")

    # Process all fields concurrently
    print(f"\n3. Processing fields (extraction + reasoning, concurrent)...")
    print("-" * 80)

    start_time = datetime.now()
    results = {}

    # Use ThreadPoolExecutor for concurrent API calls
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all processing tasks (reduced workers to avoid rate limits)
        futures = {
            executor.submit(process_single_field, field_desc, document, i): i
            for i, field_desc in enumerate(field_descriptions)
        }

        # Collect results as they complete
        for future in as_completed(futures):
            try:
                index, field_name, result = future.result()
                results[field_name] = result
            except Exception as e:
                print(f"   ✗ Error processing field: {e}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("-" * 80)
    print(f"\n4. Processing completed in {duration:.2f} seconds")

    # Prepare output data
    output_data = {
        "processing_timestamp": datetime.now().isoformat(),
        "source_document": document_path,
        "field_descriptions_source": field_descriptions_path,
        "total_fields": len(field_descriptions),
        "processing_duration_seconds": duration,
        "results": results
    }

    # Save results
    print(f"\n5. Saving results to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"   ✓ Results saved successfully")

    # Print summary
    print("\n" + "=" * 80)
    print("FINAL ANSWERS SUMMARY")
    print("=" * 80)

    for i, field_desc in enumerate(field_descriptions, 1):
        field_name = field_desc['name']
        result = results.get(field_name, {})
        final_answer_data = result.get('final_answer', {})

        print(f"\n{i}. {field_name}")
        print(f"   Format: {field_desc.get('format', 'N/A')}")
        print(f"   Expected Example: {field_desc.get('example', 'N/A')}")
        print(f"   -" * 38)
        print(f"   FINAL ANSWER: {final_answer_data.get('final_answer', 'N/A')}")
        print(f"   Confidence: {final_answer_data.get('confidence', 'N/A')}")

        # Show reasoning
        reasoning = final_answer_data.get('reasoning', '')
        if reasoning:
            reasoning_preview = reasoning[:150] + "..." if len(reasoning) > 150 else reasoning
            print(f"   Reasoning: {reasoning_preview}")

        # Show extraction summary
        extraction = result.get('extraction', {})
        paragraphs_found = extraction.get('total_paragraphs_found', 0)
        print(f"   Paragraphs Found: {paragraphs_found}")

    print("\n" + "=" * 80)
    print(f"Pipeline test completed! Full results saved to: {output_path}")
    print("=" * 80)

    # Print final answers in clean format
    print("\n" + "=" * 80)
    print("CLEAN FIELD VALUES (for LC document)")
    print("=" * 80)

    for i, field_desc in enumerate(field_descriptions, 1):
        field_name = field_desc['name']
        result = results.get(field_name, {})
        final_answer_data = result.get('final_answer', {})
        final_value = final_answer_data.get('final_answer', '')

        print(f"{field_name}: {final_value}")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
