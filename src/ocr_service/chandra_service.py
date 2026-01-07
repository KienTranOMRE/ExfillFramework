import os
import requests
from pathlib import Path
from .base import OCRServiceBase


class ChandraOCRService(OCRServiceBase):
    """
    OCR service implementation using Chandra API.
    """

    def __init__(self, api_url: str = None):
        """
        Initialize Chandra OCR service.

        Args:
            api_url: Chandra API URL. If not provided, will use CHANDRA_API_URL from environment.
                    Defaults to http://localhost:8000
        """
        self.api_url = api_url or os.getenv("CHANDRA_API_URL", "http://localhost:8000")
        self.ocr_endpoint = f"{self.api_url.rstrip('/')}/ocr"

    @property
    def service_name(self) -> str:
        return "Chandra"

    def validate_config(self) -> bool:
        """
        Validate that Chandra API is accessible.

        Returns:
            True if API URL is configured, False otherwise
        """
        return self.api_url is not None and len(self.api_url) > 0

    def ocr(self, pdf_file_path: str) -> str:
        """
        Perform OCR on a PDF file using Chandra API.

        Args:
            pdf_file_path: Path to the PDF file

        Returns:
            Extracted text in markdown format

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If API URL is not configured
            requests.exceptions.RequestException: If API request fails
            Exception: If OCR processing fails
        """
        # Validate configuration
        if not self.validate_config():
            raise ValueError(f"{self.service_name} API URL is not configured. Set CHANDRA_API_URL in environment.")

        # Validate file exists
        pdf_path = Path(pdf_file_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_file_path}")

        # Prepare the multipart form data
        with open(pdf_file_path, 'rb') as pdf_file:
            files = {
                'file': (pdf_path.name, pdf_file, 'application/pdf')
            }
            data = {
                'output_format': 'both'  # Request both text and markdown
            }

            try:
                # Make POST request to Chandra API
                response = requests.post(
                    self.ocr_endpoint,
                    files=files,
                    data=data,
                    timeout=300  # 5 minute timeout for large PDFs
                )

                # Check if request was successful
                response.raise_for_status()

                # Parse response
                result = response.json()

                # Extract markdown text from response
                # Adjust based on actual Chandra API response format
                if 'markdown' in result:
                    return result['markdown']
                elif 'text' in result:
                    return result['text']
                elif 'content' in result:
                    return result['content']
                else:
                    # If response format is different, return the whole response as string
                    return str(result)

            except requests.exceptions.ConnectionError as e:
                raise ConnectionError(
                    f"Failed to connect to Chandra API at {self.ocr_endpoint}. "
                    f"Please ensure the Chandra service is running. Error: {str(e)}"
                )
            except requests.exceptions.Timeout as e:
                raise TimeoutError(
                    f"Request to Chandra API timed out. The PDF might be too large. Error: {str(e)}"
                )
            except requests.exceptions.HTTPError as e:
                raise Exception(
                    f"Chandra API returned an error: {response.status_code} - {response.text}"
                )
            except requests.exceptions.RequestException as e:
                raise Exception(
                    f"Failed to process OCR with Chandra API: {str(e)}"
                )
