"""
SnipText - Screenshot OCR Tool

A desktop application that captures screenshots and extracts text using OCR,
automatically copying the extracted text to clipboard.
"""

__version__ = "1.0.0"
__author__ = "Aaditya Kanjolia"
__email__ = "a21kanjolia@gmail.com"

from .app import SnipTextApp
from .ocr import extract_text_from_image

__all__ = ['SnipTextApp', 'extract_text_from_image']


