"""
Text extraction utilities using PyMuPDF for high-performance PDF processing.
Optimized for the Adobe India Hackathon 2025 Challenge 1a requirements.
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class TextExtractor:
    """High-performance text extraction from PDF documents."""
    
    def __init__(self):
        self.doc = None
        self.metadata = {}
        
    def load_document(self, pdf_path: str) -> bool:
        """Load PDF document and extract basic metadata."""
        try:
            self.doc = fitz.open(pdf_path)
            self.metadata = self.doc.metadata
            return True
        except Exception as e:
            print(f"Error loading PDF {pdf_path}: {e}")
            return False
    
    def get_document_info(self, filename: str) -> Dict:
        """Extract document metadata and information."""
        if not self.doc:
            return {}
            
        # Convert dates to ISO format
        creation_date = None
        modification_date = None
        
        if self.metadata.get('creationDate'):
            try:
                # Handle PyMuPDF date format
                date_str = self.metadata['creationDate']
                if date_str.startswith('D:'):
                    date_str = date_str[2:16]  # Extract YYYYMMDDHHMMSS
                    creation_date = datetime.strptime(date_str, '%Y%m%d%H%M%S').isoformat()
            except:
                pass
                
        if self.metadata.get('modDate'):
            try:
                date_str = self.metadata['modDate']
                if date_str.startswith('D:'):
                    date_str = date_str[2:16]
                    modification_date = datetime.strptime(date_str, '%Y%m%d%H%M%S').isoformat()
            except:
                pass
        
        return {
            'filename': filename,
            'title': self.metadata.get('title') or None,
            'author': self.metadata.get('author') or None,
            'subject': self.metadata.get('subject') or None,
            'pages': self.doc.page_count,
            'creation_date': creation_date,
            'modification_date': modification_date
        }
    
    def extract_text_blocks(self, page_num: int) -> List[Dict]:
        """Extract text blocks from a specific page with formatting info."""
        if not self.doc or page_num >= self.doc.page_count:
            return []
            
        page = self.doc[page_num]
        blocks = []
        
        # Get text blocks with detailed information
        text_dict = page.get_text("dict")
        
        for block in text_dict.get("blocks", []):
            if "lines" not in block:  # Skip image blocks
                continue
                
            block_text = ""
            font_info = {}
            
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span.get("text", "").strip()
                    if text:
                        block_text += text + " "
                        # Collect font information
                        font_info = {
                            'font_name': span.get('font', ''),
                            'font_size': span.get('size', 0),
                            'flags': span.get('flags', 0)  # Bold, italic flags
                        }
            
            if block_text.strip():
                blocks.append({
                    'text': block_text.strip(),
                    'bbox': block.get('bbox', [0, 0, 0, 0]),
                    'page_number': page_num + 1,
                    'font_name': font_info.get('font_name'),
                    'font_size': font_info.get('font_size'),
                    'is_bold': bool(font_info.get('flags', 0) & 2**4),
                    'is_italic': bool(font_info.get('flags', 0) & 2**1)
                })
        
        return blocks
    
    def extract_all_text(self) -> List[Dict]:
        """Extract all text blocks from all pages."""
        if not self.doc:
            return []
            
        all_blocks = []
        for page_num in range(self.doc.page_count):
            page_blocks = self.extract_text_blocks(page_num)
            all_blocks.extend(page_blocks)
            
        return all_blocks
    
    def extract_tables(self, page_num: int) -> List[Dict]:
        """Extract table data from a specific page."""
        if not self.doc or page_num >= self.doc.page_count:
            return []
            
        page = self.doc[page_num]
        tables = []
        
        try:
            # Try to find tables using PyMuPDF's table detection
            tabs = page.find_tables()
            
            for tab in tabs:
                table_data = tab.extract()
                if table_data and len(table_data) > 1:  # At least 2 rows
                    # Clean empty cells and rows
                    cleaned_data = []
                    for row in table_data:
                        cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                        if any(cleaned_row):  # Skip completely empty rows
                            cleaned_data.append(cleaned_row)
                    
                    if cleaned_data:
                        # Try to identify headers (first row with content)
                        headers = None
                        if len(cleaned_data) > 1:
                            first_row = cleaned_data[0]
                            if all(cell for cell in first_row):  # All cells have content
                                headers = first_row
                                rows = cleaned_data[1:]
                            else:
                                rows = cleaned_data
                        else:
                            rows = cleaned_data
                        
                        tables.append({
                            'page_number': page_num + 1,
                            'caption': None,  # Caption detection would need additional logic
                            'headers': headers,
                            'rows': rows
                        })
        except Exception as e:
            # Fallback: try to detect tables from text layout
            pass
            
        return tables
    
    def detect_lists(self, text_blocks: List[Dict]) -> List[Dict]:
        """Detect and extract lists from text blocks."""
        lists = []
        current_list = None
        
        # Patterns for list detection
        bullet_pattern = re.compile(r'^[\s]*[•·▪▫◦‣⁃]\s+(.+)$')
        number_pattern = re.compile(r'^[\s]*(\d+[\.\)]|\([a-z]\)|\([0-9]+\))\s+(.+)$')
        letter_pattern = re.compile(r'^[\s]*([a-zA-Z][\.\)])\s+(.+)$')
        
        for block in text_blocks:
            text = block['text']
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for bullet points
                bullet_match = bullet_pattern.match(line)
                if bullet_match:
                    if current_list and current_list['type'] != 'bulleted':
                        lists.append(current_list)
                        current_list = None
                    
                    if not current_list:
                        current_list = {
                            'type': 'bulleted',
                            'items': [],
                            'page_number': block['page_number']
                        }
                    
                    current_list['items'].append(bullet_match.group(1))
                    continue
                
                # Check for numbered lists
                number_match = number_pattern.match(line)
                if number_match:
                    if current_list and current_list['type'] != 'numbered':
                        lists.append(current_list)
                        current_list = None
                    
                    if not current_list:
                        current_list = {
                            'type': 'numbered',
                            'items': [],
                            'page_number': block['page_number']
                        }
                    
                    current_list['items'].append(number_match.group(2))
                    continue
                
                # If we had a list and this line doesn't match, end the list
                if current_list:
                    lists.append(current_list)
                    current_list = None
        
        # Add the last list if exists
        if current_list:
            lists.append(current_list)
            
        return lists
    
    def close(self):
        """Close the document and free memory."""
        if self.doc:
            self.doc.close()
            self.doc = None