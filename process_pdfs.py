#!/usr/bin/env python3
"""
Adobe India Hackathon 2025 - Challenge 1a: PDF Processing Solution
Extracts structured data from PDF documents and outputs JSON files.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

# PDF processing libraries
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import cv2
import numpy as np

# NLP and ML libraries
import spacy
import nltk
from textblob import TextBlob
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import re

# Import utility functions
from utils.text_processor import TextProcessor
from utils.structure_analyzer import StructureAnalyzer
from utils.json_generator import JSONGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Main PDF processing class that extracts structured data from PDFs."""
    
    def __init__(self):
        """Initialize the PDF processor with required models and tools."""
        self.text_processor = TextProcessor()
        self.structure_analyzer = StructureAnalyzer()
        self.json_generator = JSONGenerator()
        
        # Load NLP model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found, using basic processing")
            self.nlp = None
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract text and metadata from PDF using multiple methods."""
        extracted_data = {
            'text_content': '',
            'pages': [],
            'metadata': {},
            'images': [],
            'tables': [],
            'structure': {}
        }
        
        try:
            # Method 1: PyMuPDF for comprehensive extraction
            doc = fitz.open(str(pdf_path))
            
            # Extract metadata
            extracted_data['metadata'] = {
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'modification_date': doc.metadata.get('modDate', ''),
                'page_count': doc.page_count
            }
            
            full_text = []
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Extract text
                page_text = page.get_text()
                full_text.append(page_text)
                
                # Extract page structure information
                page_info = {
                    'page_number': page_num + 1,
                    'text': page_text,
                    'text_length': len(page_text),
                    'blocks': [],
                    'images': [],
                    'tables': []
                }
                
                # Get text blocks with positioning
                blocks = page.get_text("dict")
                for block in blocks.get("blocks", []):
                    if "lines" in block:
                        block_info = {
                            'bbox': block.get('bbox'),
                            'text': '',
                            'font_info': []
                        }
                        
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                block_info['text'] += span.get('text', '')
                                block_info['font_info'].append({
                                    'font': span.get('font', ''),
                                    'size': span.get('size', 0),
                                    'flags': span.get('flags', 0)
                                })
                        
                        page_info['blocks'].append(block_info)
                
                # Extract images
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            page_info['images'].append({
                                'index': img_index,
                                'xref': xref,
                                'size': len(img_data)
                            })
                        pix = None
                    except Exception as e:
                        logger.warning(f"Error extracting image {img_index} from page {page_num + 1}: {str(e)}")
                
                extracted_data['pages'].append(page_info)
            
            extracted_data['text_content'] = '\n'.join(full_text)
            doc.close()
            
            # Method 2: pdfplumber for table extraction
            self._extract_tables_with_pdfplumber(pdf_path, extracted_data)
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            # Fallback to PyPDF2
            self._fallback_extraction(pdf_path, extracted_data)
        
        return extracted_data
    
    def _extract_tables_with_pdfplumber(self, pdf_path: Path, extracted_data: Dict[str, Any]):
        """Extract tables using pdfplumber."""
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if table:
                            table_data = {
                                'page': page_num + 1,
                                'table_index': table_idx,
                                'rows': len(table),
                                'columns': len(table[0]) if table else 0,
                                'data': table
                            }
                            extracted_data['tables'].append(table_data)
                            
                            # Add table data to corresponding page
                            if page_num < len(extracted_data['pages']):
                                extracted_data['pages'][page_num]['tables'].append(table_data)
        
        except Exception as e:
            logger.warning(f"Error extracting tables with pdfplumber: {str(e)}")
    
    def _fallback_extraction(self, pdf_path: Path, extracted_data: Dict[str, Any]):
        """Fallback text extraction using PyPDF2."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                extracted_data['metadata']['page_count'] = len(pdf_reader.pages)
                
                full_text = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        full_text.append(page_text)
                        
                        page_info = {
                            'page_number': page_num + 1,
                            'text': page_text,
                            'text_length': len(page_text),
                            'blocks': [],
                            'images': [],
                            'tables': []
                        }
                        extracted_data['pages'].append(page_info)
                        
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                
                extracted_data['text_content'] = '\n'.join(full_text)
                
        except Exception as e:
            logger.error(f"Fallback extraction failed for {pdf_path}: {str(e)}")
    
    def process_single_pdf(self, pdf_path: Path, output_dir: Path) -> bool:
        """Process a single PDF file and generate JSON output."""
        start_time = time.time()
        
        try:
            logger.info(f"Processing {pdf_path.name}...")
            
            # Extract raw data from PDF
            raw_data = self.extract_text_from_pdf(pdf_path)
            
            # Process and analyze the extracted data
            processed_data = self.text_processor.process_text(raw_data['text_content'])
            structure_data = self.structure_analyzer.analyze_structure(raw_data)
            
            # Generate structured JSON output
            json_output = self.json_generator.generate_json(
                raw_data, processed_data, structure_data, pdf_path.name
            )
            
            # Save JSON output
            output_file = output_dir / f"{pdf_path.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, indent=2, ensure_ascii=False)
            
            processing_time = time.time() - start_time
            logger.info(f"Successfully processed {pdf_path.name} in {processing_time:.2f} seconds")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {str(e)}")
            return False
    
    def process_all_pdfs(self, input_dir: Path, output_dir: Path) -> Dict[str, Any]:
        """Process all PDF files in the input directory."""
        start_time = time.time()
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all PDF files
        pdf_files = list(input_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning("No PDF files found in input directory")
            return {'processed': 0, 'failed': 0, 'total_time': 0}
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Process PDFs in parallel for better performance
        max_workers = min(mp.cpu_count(), 4)  # Limit to 4 workers to manage memory
        processed_count = 0
        failed_count = 0
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_pdf = {
                executor.submit(self.process_single_pdf, pdf_file, output_dir): pdf_file
                for pdf_file in pdf_files
            }
            
            # Collect results
            for future in as_completed(future_to_pdf):
                pdf_file = future_to_pdf[future]
                try:
                    success = future.result(timeout=30)  # 30 second timeout per file
                    if success:
                        processed_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Error processing {pdf_file.name}: {str(e)}")
                    failed_count += 1
        
        total_time = time.time() - start_time
        
        results = {
            'processed': processed_count,
            'failed': failed_count,
            'total_files': len(pdf_files),
            'total_time': total_time
        }
        
        logger.info(f"Processing complete: {processed_count} successful, {failed_count} failed, {total_time:.2f} seconds total")
        
        return results

def main():
    """Main function to run the PDF processing solution."""
    # Define input and output directories
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Validate input directory
    if not input_dir.exists():
        logger.error(f"Input directory {input_dir} does not exist")
        return 1
    
    # Initialize processor
    processor = PDFProcessor()
    
    # Process all PDFs
    results = processor.process_all_pdfs(input_dir, output_dir)
    
    # Check if processing was successful
    if results['failed'] > 0:
        logger.warning(f"Some files failed to process: {results['failed']} out of {results['total_files']}")
    
    # Ensure processing completed within time constraints
    if results['total_time'] > 10 and results['total_files'] == 1:
        logger.warning(f"Processing took {results['total_time']:.2f} seconds, which exceeds the 10-second limit for single PDFs")
    
    return 0 if results['failed'] == 0 else 1

if __name__ == "__main__":
    exit(main())