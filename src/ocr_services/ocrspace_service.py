import os
import requests
from .base import OCRServiceBase


class OCRSpaceService(OCRServiceBase):
    """
    OCR service implementation using OCR.space API.
    Free tier available at https://ocr.space/ocrapi
    """

    def __init__(self, api_key: str = None):
        """
        Initialize OCR.space service.

        Args:
            api_key: OCR.space API key. If not provided, will use OCRSPACE_API_KEY from environment.
                    Free API key available at https://ocr.space/ocrapi
        """
        self.api_key = api_key or os.getenv("OCRSPACE_API_KEY")
        self.api_url = "https://api.ocr.space/parse/image"

    @property
    def service_name(self) -> str:
        return "OCR.space"

    def validate_config(self) -> bool:
        """
        Validate that OCR.space API key is configured.

        Returns:
            True if API key is set, False otherwise
        """
        return self.api_key is not None and len(self.api_key) > 0

    def ocr(self, pdf_file_path: str) -> str:
        """
        Perform OCR on a PDF file using OCR.space API.

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
            raise ValueError(f"{self.service_name} API key is not configured. Set OCRSPACE_API_KEY in environment.")

        # Validate file exists
        if not os.path.exists(pdf_file_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_file_path}")

        # Prepare the request
        with open(pdf_file_path, 'rb') as f:
            payload = {
                'apikey': self.api_key,
                'language': 'eng',
                'isOverlayRequired': False,
                'detectOrientation': True,
                'scale': True,
                'OCREngine': 2,  # Engine 2 supports more languages and better accuracy
                'filetype': 'PDF',
            }

            files = {
                'file': f
            }

            # Make API request
            response = requests.post(
                self.api_url,
                files=files,
                data=payload
            )

        # Check response
        if response.status_code != 200:
            raise Exception(f"OCR.space API request failed with status {response.status_code}: {response.text}")

        result = response.json()

        # Check for errors
        if result.get('IsErroredOnProcessing'):
            error_message = result.get('ErrorMessage', ['Unknown error'])
            raise Exception(f"OCR processing failed: {', '.join(error_message)}")

        # Extract text from all pages
        all_text = []
        parsed_results = result.get('ParsedResults', [])

        for i, page_result in enumerate(parsed_results):
            page_text = page_result.get('ParsedText', '').strip()

            # Add page separator if multiple pages
            if len(parsed_results) > 1:
                all_text.append(f"# Page {i + 1}\n\n{page_text}")
            else:
                all_text.append(page_text)

        # Join all pages
        full_text = "\n\n---\n\n".join(all_text)

        return full_text
