import os
import base64
from pathlib import Path
from typing import Optional
from .base import OCRServiceBase

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIOCRService(OCRServiceBase):
    """
    OCR service implementation using OpenAI Vision API.
    Requires: pip install openai
    """

    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """
        Initialize OpenAI OCR service.

        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY from environment.
            model: Model to use (default: gpt-4o which supports vision)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    @property
    def service_name(self) -> str:
        return "OpenAI Vision"

    def validate_config(self) -> bool:
        """
        Validate that OpenAI API key is configured.

        Returns:
            True if API key is set, False otherwise
        """
        return self.api_key is not None and len(self.api_key) > 0

    def _pdf_to_images_base64(self, pdf_file_path: str) -> list:
        """
        Convert PDF to base64 encoded images.

        Args:
            pdf_file_path: Path to PDF file

        Returns:
            List of base64 encoded images
        """
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise ImportError("pdf2image library not installed. Install with: pip install pdf2image")

        import io
        from PIL import Image

        # Convert PDF to images
        images = convert_from_path(pdf_file_path)

        base64_images = []
        for img in images:
            # Convert image to base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            base64_images.append(img_base64)

        return base64_images

    def ocr(self, pdf_file_path: str) -> str:
        """
        Perform OCR on a PDF file using OpenAI Vision API.

        Args:
            pdf_file_path: Path to the PDF file

        Returns:
            Extracted text in markdown format

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If API key is not configured
            Exception: If OCR processing fails
        """
        # Validate configuration
        if not self.validate_config():
            raise ValueError(f"{self.service_name} API key is not configured. Set OPENAI_API_KEY in environment.")

        # Validate file exists
        if not os.path.exists(pdf_file_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_file_path}")

        # Convert PDF to images
        base64_images = self._pdf_to_images_base64(pdf_file_path)

        # Process each page
        all_text = []

        for i, img_base64 in enumerate(base64_images):
            # Create the message content
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Extract all text from this image and format it in markdown.
Preserve the structure, headings, lists, tables, and formatting as much as possible.
Return only the extracted text in clean markdown format."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ]

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=4096
            )

            page_text = response.choices[0].message.content

            # Add page separator if multiple pages
            if len(base64_images) > 1:
                all_text.append(f"# Page {i + 1}\n\n{page_text}")
            else:
                all_text.append(page_text)

        return "\n\n---\n\n".join(all_text)
