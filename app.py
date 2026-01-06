import streamlit as st
import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from io import BytesIO

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from reasoning_service import process_field_complete
from ocr import ocr_and_save

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="LC Form Auto-Fill System",
    page_icon="📄",
    layout="wide"
)

# Modern CSS styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1400px;
    }

    /* Modern gradient header */
    .lc-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        color: white;
    }

    .lc-title {
        font-size: 26px;
        font-weight: 700;
        margin: 10px 0;
    }

    .lc-subtitle {
        font-size: 14px;
        opacity: 0.95;
        margin-top: 5px;
    }

    /* Field value styling */
    .field-value-box {
        border: 2px solid #e0e0e0;
        background-color: #fafafa;
        padding: 14px;
        min-height: 65px;
        border-radius: 8px;
        font-size: 13px;
        color: #333;
        margin-top: 10px;
        transition: all 0.3s ease;
    }

    .field-value-box.filled {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8f4 100%);
        border-color: #4caf50;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.15);
    }

    .field-value-box.empty {
        color: #999;
        font-style: italic;
    }

    /* Confidence badges with modern styling */
    .confidence-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 600;
        margin-top: 8px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .confidence-high { background-color: #4caf50; color: white; }
    .confidence-medium { background-color: #ff9800; color: white; }
    .confidence-low { background-color: #f44336; color: white; }

    /* Control section with gradient */
    .control-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    /* Enhanced checkbox */
    input[type="checkbox"] {
        width: 18px;
        height: 18px;
        cursor: pointer;
        accent-color: #667eea;
    }

    /* Checkbox label styling */
    .stCheckbox {
        margin-bottom: 8px !important;
    }

    .stCheckbox label {
        font-weight: 600 !important;
        color: #333 !important;
        font-size: 14px !important;
    }

    /* Column spacing */
    div[data-testid="column"] {
        padding: 12px !important;
        background: white;
        border-radius: 8px;
        border: 2px solid #e8e8e8;
        margin-bottom: 12px;
    }

    div[data-testid="column"]:hover {
        border-color: #667eea;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
        transition: all 0.2s ease;
    }

    /* Remove extra spacing */
    .element-container {
        margin-bottom: 0.3rem !important;
    }
</style>
""", unsafe_allow_html=True)


def load_field_descriptions():
    """Load field descriptions from JSON file."""
    file_path = Path(__file__).parent / "data" / "input" / "partial_field_descriptions.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_document():
    """Load document from JSON file (OCR output)."""
    file_path = Path(__file__).parent / "data" / "output" / "Input_test1.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('markdown_text', '')


def check_ocr_output_exists(pdf_filename, output_dir):
    """Check if OCR output JSON file exists for the given PDF."""
    json_filename = Path(pdf_filename).stem + ".json"
    json_path = Path(output_dir) / json_filename
    return json_path.exists(), json_path


def process_uploaded_pdf(uploaded_file):
    """Process uploaded PDF: check for existing OCR output or run new OCR."""
    temp_dir = Path(__file__).parent / "data" / "temp"
    output_dir = Path(__file__).parent / "data" / "output"

    temp_dir.mkdir(exist_ok=True, parents=True)
    output_dir.mkdir(exist_ok=True, parents=True)

    pdf_filename = uploaded_file.name
    temp_pdf_path = temp_dir / pdf_filename

    with open(temp_pdf_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    exists, json_path = check_ocr_output_exists(pdf_filename, output_dir)

    if exists:
        st.info(f"Found existing OCR output for '{pdf_filename}'")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('markdown_text', '')
    else:
        st.info(f"Processing '{pdf_filename}' through OCR...")
        with st.spinner("Running OCR..."):
            json_output_path = ocr_and_save(str(temp_pdf_path), str(output_dir))
            st.success(f"OCR completed! Output: {Path(json_output_path).name}")

            with open(json_output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('markdown_text', '')


def process_field_async(field_desc, document):
    """Process a single field asynchronously."""
    try:
        result = process_field_complete(field_desc, document)
        return {
            'success': True,
            'field_name': field_desc['name'],
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'field_name': field_desc['name'],
            'error': str(e)
        }


def generate_pdf(field_descriptions):
    """Generate PDF of the form with Vietnamese support."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    story = []

    # Register Vietnamese-compatible fonts
    font_registered = False
    try:
        # Try to register Arial fonts with Vietnamese support
        font_paths = {
            'regular': [
                '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',  # macOS - best for Vietnamese
                '/System/Library/Fonts/Supplemental/Arial.ttf',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                'C:\\Windows\\Fonts\\arial.ttf',  # Windows
            ],
            'bold': [
                '/System/Library/Fonts/Supplemental/Arial Bold.ttf',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
                'C:\\Windows\\Fonts\\arialbd.ttf',  # Windows
            ],
            'italic': [
                '/System/Library/Fonts/Supplemental/Arial Italic.ttf',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf',  # Linux
                'C:\\Windows\\Fonts\\ariali.ttf',  # Windows
            ]
        }

        # Try to register each font variant
        for font_type, paths in font_paths.items():
            for font_path in paths:
                try:
                    if Path(font_path).exists():
                        if font_type == 'regular':
                            pdfmetrics.registerFont(TTFont('VietnameseFont', font_path))
                        elif font_type == 'bold':
                            pdfmetrics.registerFont(TTFont('VietnameseFont-Bold', font_path))
                        elif font_type == 'italic':
                            pdfmetrics.registerFont(TTFont('VietnameseFont-Italic', font_path))
                        break
                except Exception as e:
                    continue

        # Check if fonts were registered successfully
        font_registered = 'VietnameseFont' in pdfmetrics.getRegisteredFontNames()
    except Exception as e:
        pass

    # Font names to use
    regular_font = 'VietnameseFont' if font_registered else 'Times-Roman'
    bold_font = 'VietnameseFont-Bold' if 'VietnameseFont-Bold' in pdfmetrics.getRegisteredFontNames() else 'Times-Bold'
    italic_font = 'VietnameseFont-Italic' if 'VietnameseFont-Italic' in pdfmetrics.getRegisteredFontNames() else 'Times-Italic'

    # Custom styles with Vietnamese-supporting fonts
    title_style = ParagraphStyle(
        'CustomTitle',
        fontName=bold_font,
        fontSize=20,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=10,
        alignment=1,  # Center
        leading=24
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        fontName=regular_font,
        fontSize=12,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=8,
        alignment=1,
        leading=16
    )

    section_style = ParagraphStyle(
        'SectionTitle',
        fontName=bold_font,
        fontSize=12,
        textColor=colors.black,
        spaceAfter=15,
        spaceBefore=10
    )

    field_name_style = ParagraphStyle(
        'FieldName',
        fontName=bold_font,
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        spaceAfter=3,
        leftIndent=10
    )

    field_value_style = ParagraphStyle(
        'FieldValue',
        fontName=regular_font,
        fontSize=9,
        textColor=colors.HexColor('#555555'),
        spaceAfter=12,
        leftIndent=20,
        borderPadding=5
    )

    empty_field_style = ParagraphStyle(
        'EmptyField',
        fontName=italic_font,
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=12,
        leftIndent=20
    )

    # Helper function to encode text for PDF
    def safe_text(text):
        """Ensure text is properly encoded for PDF with Vietnamese support."""
        if isinstance(text, str):
            return text
        return str(text)

    # Add header
    story.append(Paragraph(safe_text("TECHCOMBANK"), title_style))
    story.append(Paragraph(safe_text("YÊU CẦU PHÁT HÀNH THƯ TÍN DỤNG"), subtitle_style))
    story.append(Paragraph(safe_text("APPLICATION FOR ISSUANCE OF LETTER OF CREDIT"), subtitle_style))
    story.append(Paragraph(safe_text("Ngân hàng Thương mại Cổ phần Kỹ Thương Việt Nam - TECHCOMBANK"),
                          ParagraphStyle('BankInfo', parent=subtitle_style, fontSize=9)))
    story.append(Spacer(1, 0.3*inch))

    # Add section title
    story.append(Paragraph(safe_text("I. DOCUMENTARY CREDIT DETAILS"), section_style))
    story.append(Spacer(1, 0.1*inch))

    # Add ALL fields (both filled and unfilled)
    for field_desc in field_descriptions:
        field_name = safe_text(field_desc['name'])
        field_value_data = st.session_state.field_values.get(field_desc['name'], {})

        # Field name
        story.append(Paragraph(f"<b>{field_name}</b>", field_name_style))

        # Field value
        if field_value_data:
            final_answer_data = field_value_data.get('final_answer', {})
            final_answer = safe_text(final_answer_data.get('final_answer', ''))
            confidence = final_answer_data.get('confidence', '')

            value_text = final_answer if final_answer else '<i>Not filled</i>'
            if confidence and final_answer:
                value_text += f" <font color='#666666' size='8'>[{confidence}]</font>"

            story.append(Paragraph(value_text, field_value_style))
        else:
            # Show unfilled field
            story.append(Paragraph("<i>Not filled</i>", empty_field_style))

    # Add footer
    story.append(Spacer(1, 0.4*inch))
    footer_style = ParagraphStyle(
        'Footer',
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )

    story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
    story.append(Paragraph("LC Form Auto-Fill System · Powered by AI", footer_style))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def render_field_cell(field_desc, col_index):
    """Render a single field cell."""
    field_name = field_desc['name']
    field_value_data = st.session_state.field_values.get(field_name, {})
    has_value = bool(field_value_data)

    final_answer_data = field_value_data.get('final_answer', {}) if has_value else {}
    final_answer = final_answer_data.get('final_answer', '')
    confidence = final_answer_data.get('confidence', '')
    reasoning = final_answer_data.get('reasoning', '')

    with col_index:
        # Checkbox with proper state tracking
        checkbox_key = f"select_{field_name}"

        # Render checkbox - key parameter automatically manages state
        is_selected = st.checkbox(
            f"**{field_name}**",
            key=checkbox_key
        )

        # Track selection in our custom dict for easy access
        st.session_state.field_selections[checkbox_key] = is_selected

        # Value display
        value_class = "filled" if (has_value and final_answer) else "empty"
        value_text = final_answer if (has_value and final_answer) else "Select and click Fill to auto-complete"

        confidence_badge = ""
        if has_value and confidence:
            confidence_badge = f'<span class="confidence-badge confidence-{confidence.lower()}">{confidence}</span>'

        st.markdown(f"""
            <div class="field-value-box {value_class}">
                {value_text}
                {confidence_badge}
            </div>
        """, unsafe_allow_html=True)

        # Details section
        if has_value:
            with st.expander("View Details", expanded=False):
                extraction = field_value_data.get('extraction', {})
                paragraphs_found = extraction.get('total_paragraphs_found', 0)
                relevant_paragraphs = extraction.get('relevant_paragraphs', [])

                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"**Format:** {field_desc.get('format', 'N/A')}")
                    st.caption(f"**Example:** {field_desc.get('example', 'N/A')}")
                with col2:
                    st.caption(f"**Paragraphs Found:** {paragraphs_found}")
                    st.caption(f"**Confidence:** {confidence}")

                if relevant_paragraphs:
                    st.markdown("---")
                    st.caption("**Source Paragraphs:**")
                    for i, para in enumerate(relevant_paragraphs, 1):
                        para_text = para.get('paragraph_text', '')
                        location = para.get('location', 'Unknown')
                        relevance = para.get('relevance_note', '')

                        if len(para_text) > 300:
                            para_text = para_text[:300] + "..."

                        st.markdown(f"**Paragraph {i}** ({location})")
                        st.text(para_text)
                        if relevance:
                            st.caption(f"*{relevance}*")

                if reasoning:
                    st.markdown("---")
                    st.caption("**Reasoning:**")
                    st.text(reasoning)


def main():
    # Initialize session state
    if 'field_values' not in st.session_state:
        st.session_state.field_values = {}
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'document' not in st.session_state:
        st.session_state.document = load_document()
    if 'field_selections' not in st.session_state:
        st.session_state.field_selections = {}
    if 'uploaded_pdf_name' not in st.session_state:
        st.session_state.uploaded_pdf_name = None

    field_descriptions = load_field_descriptions()

    # Document Upload Section
    st.markdown('<div class="control-section">', unsafe_allow_html=True)
    st.markdown("### Document Upload")

    uploaded_file = st.file_uploader(
        "Upload PDF document for processing:",
        type=['pdf'],
        help="Upload a PDF file. System will check for existing OCR output or process new file."
    )

    if uploaded_file is not None:
        if st.session_state.uploaded_pdf_name != uploaded_file.name:
            try:
                markdown_text = process_uploaded_pdf(uploaded_file)
                st.session_state.document = markdown_text
                st.session_state.uploaded_pdf_name = uploaded_file.name
                st.session_state.field_values = {}
                st.session_state.field_selections = {}
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")

    if st.session_state.uploaded_pdf_name:
        st.success(f"Current document: **{st.session_state.uploaded_pdf_name}**")
    else:
        st.info("Using default document: **Input_test1.json**")

    st.markdown('</div>', unsafe_allow_html=True)

    # Controls Section
    st.markdown('<div class="control-section">', unsafe_allow_html=True)
    st.markdown("### Field Controls")

    # Count selected fields by checking checkbox states directly from session_state
    selected_count = sum(
        1 for field_desc in field_descriptions
        if st.session_state.get(f"select_{field_desc['name']}", False)
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        fill_button = st.button(
            "Fill Selected Fields",
            disabled=selected_count == 0 or st.session_state.processing,
            use_container_width=True,
            type="primary"
        )

    with col2:
        if st.button("Clear All", use_container_width=True):
            st.session_state.field_values = {}
            # Clear all checkbox states
            for field_desc in field_descriptions:
                checkbox_key = f"select_{field_desc['name']}"
                if checkbox_key in st.session_state:
                    st.session_state[checkbox_key] = False
            st.session_state.field_selections = {}
            st.rerun()

    with col3:
        if st.session_state.field_values:
            if st.button("Export JSON", use_container_width=True):
                output_data = {
                    "timestamp": datetime.now().isoformat(),
                    "fields": st.session_state.field_values
                }
                output_path = Path(__file__).parent / "data" / "output" / "lc_form_filled.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                st.success("Exported successfully!")

    st.markdown('</div>', unsafe_allow_html=True)

    # Process fields
    if fill_button:
        # Get selected fields by checking checkbox states directly
        selected_fields = [
            field_desc for field_desc in field_descriptions
            if st.session_state.get(f"select_{field_desc['name']}", False)
        ]

        if selected_fields:
            st.session_state.processing = True
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Processing fields in parallel...")

            results = {}
            completed = 0
            total = len(selected_fields)

            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_field = {
                    executor.submit(process_field_async, field_desc, st.session_state.document): field_desc
                    for field_desc in selected_fields
                }

                for future in as_completed(future_to_field):
                    field_desc = future_to_field[future]
                    try:
                        result_data = future.result()
                        if result_data['success']:
                            results[result_data['field_name']] = result_data['result']
                        else:
                            st.error(f"{result_data['field_name']}: {result_data['error']}")

                        completed += 1
                        progress_bar.progress(completed / total)
                        status_text.text(f"Processing... {completed}/{total} completed")

                    except Exception as e:
                        st.error(f"{field_desc['name']}: {str(e)}")

            st.session_state.field_values.update(results)
            st.session_state.processing = False

            progress_bar.progress(1.0)
            status_text.text(f"Completed! Processed {total} field(s)")

            st.rerun()

    # Header - positioned near the fields
    st.markdown("""
    <div class="lc-header">
        <div style="font-size: 32px; font-weight: bold;">TECHCOMBANK</div>
        <div class="lc-title">YÊU CẦU PHÁT HÀNH THƯ TÍN DỤNG</div>
        <div class="lc-subtitle">APPLICATION FOR ISSUANCE OF LETTER OF CREDIT</div>
        <div style="margin-top: 12px; font-size: 13px; opacity: 0.9;">
            Ngân hàng Thương mại Cổ phần Kỹ Thương Việt Nam - TECHCOMBANK
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Form Section
    st.markdown("### I. DOCUMENTARY CREDIT DETAILS")

    # Render fields in 2-column grid
    for i in range(0, len(field_descriptions), 2):
        col1, col2 = st.columns(2)

        render_field_cell(field_descriptions[i], col1)

        if i + 1 < len(field_descriptions):
            render_field_cell(field_descriptions[i + 1], col2)

    # PDF Download Section
    st.markdown("---")
    st.markdown('<div class="control-section" style="text-align: center;">', unsafe_allow_html=True)
    st.markdown("### Export Form")

    if PDF_AVAILABLE:
        try:
            pdf_buffer = generate_pdf(field_descriptions)
            st.download_button(
                label="Download Form as PDF",
                data=pdf_buffer,
                file_name=f"LC_Form_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=False,
                type="primary"
            )
            st.caption("PDF includes all fields (both filled and unfilled)")
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
    else:
        st.warning("PDF generation is not available. Please install reportlab: pip install reportlab")

    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 12px; padding: 20px;">
        <b>LC Form Auto-Fill System</b> · Powered by AI
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
