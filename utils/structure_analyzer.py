"""
Document structure analysis utilities for PDF processing.
"""

import re
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from collections import Counter, defaultdict

class StructureAnalyzer:
    """Analyzes document structure and layout from extracted PDF data."""
    
    def __init__(self):
        """Initialize the structure analyzer."""
        self.heading_patterns = [
            r'^[A-Z][A-Z\s]{2,}$',  # ALL CAPS headings
            r'^\d+\.?\s+[A-Z]',      # Numbered headings
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:?$',  # Title case headings
            r'^\s*(?:Chapter|Section|Part)\s+\d+',   # Chapter/Section headings
        ]
        
        self.list_patterns = [
            r'^\s*[-•*]\s+',         # Bullet points
            r'^\s*\d+[\.\)]\s+',     # Numbered lists
            r'^\s*[a-zA-Z][\.\)]\s+', # Lettered lists
        ]
    
    def detect_headings(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect headings in the document based on various criteria."""
        headings = []
        
        for page_num, page in enumerate(pages):
            text = page.get('text', '')
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines):
                line = line.strip()
                if not line or len(line) < 3:
                    continue
                
                # Check against heading patterns
                heading_score = 0
                heading_type = None
                
                for pattern in self.heading_patterns:
                    if re.match(pattern, line):
                        heading_score += 1
                        heading_type = pattern
                
                # Additional heuristics
                if line.isupper() and len(line) > 5:
                    heading_score += 1
                    heading_type = "uppercase"
                
                if line.endswith(':') and len(line.split()) <= 5:
                    heading_score += 0.5
                    heading_type = "colon_ending"
                
                # Check font information if available
                if 'blocks' in page:
                    for block in page['blocks']:
                        if line in block.get('text', ''):
                            font_info = block.get('font_info', [])
                            if font_info:
                                avg_size = np.mean([f.get('size', 12) for f in font_info])
                                if avg_size > 14:  # Larger font size
                                    heading_score += 1
                                
                                # Check for bold text
                                bold_count = sum(1 for f in font_info if f.get('flags', 0) & 16)
                                if bold_count > len(font_info) * 0.5:
                                    heading_score += 1
                
                if heading_score >= 1:
                    headings.append({
                        'text': line,
                        'page': page_num + 1,
                        'line': line_num,
                        'score': heading_score,
                        'type': heading_type,
                        'level': self._determine_heading_level(line, heading_score)
                    })
        
        return sorted(headings, key=lambda x: (x['page'], x['line']))
    
    def _determine_heading_level(self, text: str, score: float) -> int:
        """Determine the hierarchical level of a heading."""
        # Level 1: Major headings (chapters, main sections)
        if re.match(r'^\s*(?:Chapter|CHAPTER)\s+\d+', text) or score >= 3:
            return 1
        
        # Level 2: Section headings
        if re.match(r'^\d+\.?\s+[A-Z]', text) or text.isupper():
            return 2
        
        # Level 3: Subsection headings
        if re.match(r'^\d+\.\d+\.?\s+', text):
            return 3
        
        # Default to level 2
        return 2
    
    def detect_lists(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect lists in the document."""
        lists = []
        current_list = None
        
        for page_num, page in enumerate(pages):
            text = page.get('text', '')
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines):
                original_line = line
                line = line.strip()
                
                if not line:
                    if current_list:
                        lists.append(current_list)
                        current_list = None
                    continue
                
                # Check if line is a list item
                list_match = None
                list_type = None
                
                for pattern in self.list_patterns:
                    match = re.match(pattern, original_line)
                    if match:
                        list_match = match
                        if '•' in pattern or '*' in pattern or '-' in pattern:
                            list_type = 'bullet'
                        elif r'\d+' in pattern:
                            list_type = 'numbered'
                        elif r'[a-zA-Z]' in pattern:
                            list_type = 'lettered'
                        break
                
                if list_match:
                    item_text = line[len(list_match.group(0)):].strip()
                    
                    if current_list and current_list['type'] == list_type:
                        # Continue existing list
                        current_list['items'].append({
                            'text': item_text,
                            'marker': list_match.group(0).strip(),
                            'line': line_num
                        })
                        current_list['end_line'] = line_num
                    else:
                        # Start new list
                        if current_list:
                            lists.append(current_list)
                        
                        current_list = {
                            'type': list_type,
                            'page': page_num + 1,
                            'start_line': line_num,
                            'end_line': line_num,
                            'items': [{
                                'text': item_text,
                                'marker': list_match.group(0).strip(),
                                'line': line_num
                            }]
                        }
                else:
                    if current_list:
                        lists.append(current_list)
                        current_list = None
            
            # End any ongoing list at page end
            if current_list:
                lists.append(current_list)
                current_list = None
        
        return lists
    
    def detect_tables(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and enhance table detection."""
        tables = raw_data.get('tables', [])
        enhanced_tables = []
        
        for table in tables:
            if not table.get('data'):
                continue
            
            table_data = table['data']
            
            # Analyze table structure
            analysis = {
                'page': table.get('page', 1),
                'table_index': table.get('table_index', 0),
                'dimensions': {
                    'rows': len(table_data),
                    'columns': len(table_data[0]) if table_data else 0
                },
                'has_header': self._detect_table_header(table_data),
                'column_types': self._analyze_column_types(table_data),
                'data': table_data,
                'summary': self._summarize_table(table_data)
            }
            
            enhanced_tables.append(analysis)
        
        return enhanced_tables
    
    def _detect_table_header(self, table_data: List[List[str]]) -> bool:
        """Detect if table has a header row."""
        if not table_data or len(table_data) < 2:
            return False
        
        first_row = table_data[0]
        second_row = table_data[1]
        
        # Check if first row contains header-like content
        header_indicators = 0
        
        for cell in first_row:
            if cell and isinstance(cell, str):
                # Check for title case
                if cell.istitle():
                    header_indicators += 1
                # Check for short descriptive text
                if len(cell.split()) <= 3 and not cell.isdigit():
                    header_indicators += 1
        
        return header_indicators >= len(first_row) * 0.5
    
    def _analyze_column_types(self, table_data: List[List[str]]) -> List[str]:
        """Analyze the data types of each column."""
        if not table_data:
            return []
        
        num_cols = len(table_data[0]) if table_data else 0
        column_types = []
        
        for col_idx in range(num_cols):
            column_values = []
            for row in table_data[1:]:  # Skip header
                if col_idx < len(row) and row[col_idx]:
                    column_values.append(row[col_idx])
            
            col_type = self._determine_column_type(column_values)
            column_types.append(col_type)
        
        return column_types
    
    def _determine_column_type(self, values: List[str]) -> str:
        """Determine the data type of a column based on its values."""
        if not values:
            return 'empty'
        
        numeric_count = 0
        date_count = 0
        text_count = 0
        
        for value in values:
            value = str(value).strip()
            
            # Check for numeric
            try:
                float(value.replace(',', '').replace('$', ''))
                numeric_count += 1
                continue
            except ValueError:
                pass
            
            # Check for date patterns
            date_patterns = [
                r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
                r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
            ]
            
            if any(re.search(pattern, value, re.IGNORECASE) for pattern in date_patterns):
                date_count += 1
                continue
            
            text_count += 1
        
        total = len(values)
        if numeric_count / total > 0.7:
            return 'numeric'
        elif date_count / total > 0.7:
            return 'date'
        else:
            return 'text'
    
    def _summarize_table(self, table_data: List[List[str]]) -> Dict[str, Any]:
        """Create a summary of the table content."""
        if not table_data:
            return {}
        
        return {
            'row_count': len(table_data),
            'column_count': len(table_data[0]) if table_data else 0,
            'non_empty_cells': sum(1 for row in table_data for cell in row if cell and str(cell).strip()),
            'first_row': table_data[0] if table_data else [],
            'sample_data': table_data[:3] if len(table_data) > 1 else table_data
        }
    
    def analyze_document_layout(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the overall document layout and structure."""
        layout_analysis = {
            'page_count': len(pages),
            'text_distribution': [],
            'layout_type': 'unknown',
            'column_detection': [],
            'page_statistics': []
        }
        
        for page_num, page in enumerate(pages):
            page_stats = {
                'page_number': page_num + 1,
                'text_length': len(page.get('text', '')),
                'block_count': len(page.get('blocks', [])),
                'image_count': len(page.get('images', [])),
                'table_count': len(page.get('tables', []))
            }
            
            layout_analysis['page_statistics'].append(page_stats)
            layout_analysis['text_distribution'].append(page_stats['text_length'])
        
        # Determine layout type
        avg_text_per_page = np.mean(layout_analysis['text_distribution']) if layout_analysis['text_distribution'] else 0
        
        if avg_text_per_page > 2000:
            layout_analysis['layout_type'] = 'text_heavy'
        elif any(page['table_count'] > 2 for page in layout_analysis['page_statistics']):
            layout_analysis['layout_type'] = 'table_heavy'
        elif any(page['image_count'] > 3 for page in layout_analysis['page_statistics']):
            layout_analysis['layout_type'] = 'image_heavy'
        else:
            layout_analysis['layout_type'] = 'mixed'
        
        return layout_analysis
    
    def extract_document_hierarchy(self, headings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract document hierarchy from detected headings."""
        hierarchy = {
            'sections': [],
            'outline': [],
            'depth': 0
        }
        
        current_section = None
        section_stack = []
        
        for heading in headings:
            level = heading['level']
            text = heading['text']
            page = heading['page']
            
            # Create section object
            section = {
                'title': text,
                'level': level,
                'page': page,
                'subsections': []
            }
            
            # Handle hierarchy
            while section_stack and section_stack[-1]['level'] >= level:
                section_stack.pop()
            
            if section_stack:
                section_stack[-1]['subsections'].append(section)
            else:
                hierarchy['sections'].append(section)
            
            section_stack.append(section)
            
            # Add to outline
            indent = '  ' * (level - 1)
            hierarchy['outline'].append(f"{indent}{text} (Page {page})")
        
        hierarchy['depth'] = max([h['level'] for h in headings]) if headings else 0
        
        return hierarchy
    
    def analyze_structure(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive structure analysis of the document."""
        pages = raw_data.get('pages', [])
        
        # Detect various structural elements
        headings = self.detect_headings(pages)
        lists = self.detect_lists(pages)
        tables = self.detect_tables(raw_data)
        layout = self.analyze_document_layout(pages)
        hierarchy = self.extract_document_hierarchy(headings)
        
        return {
            'headings': headings,
            'lists': lists,
            'tables': tables,
            'layout': layout,
            'hierarchy': hierarchy,
            'structural_elements': {
                'heading_count': len(headings),
                'list_count': len(lists),
                'table_count': len(tables),
                'has_toc': self._detect_table_of_contents(pages),
                'has_index': self._detect_index(pages),
                'document_type': self._classify_document_type(raw_data, headings, tables)
            }
        }
    
    def _detect_table_of_contents(self, pages: List[Dict[str, Any]]) -> bool:
        """Detect if document has a table of contents."""
        toc_indicators = [
            'table of contents', 'contents', 'index', 'toc'
        ]
        
        # Check first few pages for TOC indicators
        for page in pages[:5]:
            text = page.get('text', '').lower()
            if any(indicator in text for indicator in toc_indicators):
                # Look for page number patterns
                if re.search(r'\.\s*\d+\s*$', text, re.MULTILINE):
                    return True
        
        return False
    
    def _detect_index(self, pages: List[Dict[str, Any]]) -> bool:
        """Detect if document has an index."""
        # Check last few pages for index
        for page in pages[-3:]:
            text = page.get('text', '').lower()
            if 'index' in text and re.search(r'\w+,\s*\d+', text):
                return True
        
        return False
    
    def _classify_document_type(self, raw_data: Dict[str, Any], headings: List[Dict[str, Any]], tables: List[Dict[str, Any]]) -> str:
        """Classify the type of document based on structural elements."""
        text = raw_data.get('text_content', '').lower()
        
        # Academic paper
        if any(term in text for term in ['abstract', 'introduction', 'methodology', 'conclusion', 'references']):
            return 'academic_paper'
        
        # Report
        if any(term in text for term in ['executive summary', 'findings', 'recommendations']):
            return 'report'
        
        # Manual/Guide
        if any(term in text for term in ['step', 'procedure', 'instructions', 'how to']):
            return 'manual'
        
        # Financial document
        if len(tables) > 3 and any(term in text for term in ['financial', 'revenue', 'profit', 'balance']):
            return 'financial'
        
        # Legal document
        if any(term in text for term in ['whereas', 'hereby', 'party', 'agreement', 'contract']):
            return 'legal'
        
        # Technical specification
        if any(term in text for term in ['specification', 'requirements', 'technical', 'system']):
            return 'technical'
        
        return 'general'