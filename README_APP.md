# LC Form Auto-Fill System - Demo Interface

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Make sure you have a `.env` file with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

### 3. Run the Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## How to Use

1. **View the LC Form**: The interface displays all available fields in a two-column grid layout matching the official LC form format.

2. **Select Fields**: Click the checkbox in the **top-right corner** of each field cell that you want to auto-fill.
   - The "Selected Fields" counter shows how many fields are selected
   - You can select multiple fields at once

3. **Click "Fill Selected Fields"**: The system will:
   - Process all selected fields in parallel for speed
   - Extract relevant information from the document
   - Determine the final answer for each field
   - Fill the values into the form cells

4. **View Results**: Each filled field shows:
   - The final answer in a green highlighted box
   - Confidence badge (HIGH/MEDIUM/LOW) with color coding
   - Click "Details" to expand and see:
     - Format and example
     - Number of paragraphs found
     - Full reasoning
     - Source paragraphs

5. **Export**: Click "Export to JSON" to save the filled form data.

6. **Clear All**: Reset all field values and selections to start over.

## Features

- ✅ **Form-style Layout**: Two-column grid matching official LC form design
- ✅ **Checkbox Selection**: Top-right corner checkboxes for each field cell
- ✅ **Parallel Processing**: Process multiple fields concurrently for speed
- ✅ **Confidence Scoring**: Color-coded badges (green/orange/red)
- ✅ **Detailed Reasoning**: View extraction sources and AI reasoning
- ✅ **Real-time Progress**: Live progress bar and status updates
- ✅ **Export Functionality**: Save results to JSON format
- ✅ **Clean UI**: Professional design matching TECHCOMBANK LC form style

## System Architecture

```
User Interface (Streamlit)
    ↓
Field Selection
    ↓
Parallel Processing (ThreadPoolExecutor)
    ↓
For each field:
    1. Extract relevant paragraphs (extraction_service.py)
    2. Determine final answer (reasoning_service.py)
    ↓
Display Results
```

## Notes

- The system uses Gemini 3 Flash for both extraction and reasoning
- Processing is done in parallel with max 3 workers to avoid rate limits
- Document is loaded from `data/output/Input_test1.json`
- Field descriptions are loaded from `data/input/partial_field_descriptions.json`
