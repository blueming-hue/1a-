"""
Adobe India Hackathon 2025 - Challenge 1a: PDF Processing Solution
Source package for high-performance PDF text extraction and structure analysis.
"""

__version__ = "1.0.0"
__author__ = "Adobe India Hackathon 2025 - Challenge 1a Team"

from .pdf_processor import PDFProcessor
from .text_extractor import TextExtractor
from .structure_analyzer import StructureAnalyzer

__all__ = [
    'PDFProcessor',
    'TextExtractor', 
    'StructureAnalyzer'
]