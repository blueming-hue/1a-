"""
Document structure analysis for identifying headings, sections, and content hierarchy.
Optimized for the Adobe India Hackathon 2025 Challenge 1a requirements.
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class StructureAnalyzer:
    """Analyzes document structure to identify headings, sections, and hierarchy."""
    
    def __init__(self):
        self.font_size_threshold = 2.0  # Minimum difference for heading detection
        self.common_heading_patterns = [
            r'^(\d+\.?\s+)',  # "1. " or "1 "
            r'^([A-Z][A-Z\s]+)$',  # ALL CAPS
            r'^(Chapter\s+\d+)',  # Chapter X
            r'^(Section\s+\d+)',  # Section X
            r'^([IVX]+\.?\s+)',  # Roman numerals
            r'^([A-Z]\.?\s+)',  # Single letter
        ]
    
    def analyze_font_hierarchy(self, text_blocks: List[Dict]) -> Dict:
        """Analyze font sizes to determine heading hierarchy."""
        font_stats = defaultdict(list)
        
        # Collect font size statistics
        for block in text_blocks:
            font_size = block.get('font_size', 0)
            if font_size > 0:
                font_stats[font_size].append(block)
        
        # Sort font sizes in descending order
        sorted_sizes = sorted(font_stats.keys(), reverse=True)
        
        # Determine heading levels based on font size
        heading_levels = {}
        level = 1
        
        for size in sorted_sizes:
            if level <= 6:  # Maximum 6 heading levels
                heading_levels[size] = level
                level += 1
            else:
                heading_levels[size] = 6  # All remaining sizes are level 6
        
        return {
            'font_stats': dict(font_stats),
            'heading_levels': heading_levels,
            'sorted_sizes': sorted_sizes
        }
    
    def is_likely_heading(self, block: Dict, font_hierarchy: Dict) -> Tuple[bool, int]:
        """Determine if a text block is likely a heading and its level."""
        text = block['text'].strip()
        font_size = block.get('font_size', 0)
        is_bold = block.get('is_bold', False)
        
        # Check if font size indicates heading
        heading_levels = font_hierarchy.get('heading_levels', {})
        if font_size in heading_levels:
            return True, heading_levels[font_size]
        
        # Check for pattern-based headings
        for pattern in self.common_heading_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                # Estimate level based on pattern and formatting
                if is_bold or font_size > 12:
                    return True, min(2, len([s for s in heading_levels.keys() if s > font_size]) + 1)
                else:
                    return True, 3
        
        # Check for short, bold text (likely headings)
        if is_bold and len(text) < 100 and not text.endswith('.'):
            return True, 4
        
        # Check for all caps short text
        if text.isupper() and len(text) < 50 and len(text.split()) <= 8:
            return True, 5
        
        return False, 0
    
    def extract_sections(self, text_blocks: List[Dict]) -> List[Dict]:
        """Extract sections with hierarchical structure."""
        font_hierarchy = self.analyze_font_hierarchy(text_blocks)
        sections = []
        current_section = None
        content_buffer = []
        
        for block in text_blocks:
            is_heading, level = self.is_likely_heading(block, font_hierarchy)
            
            if is_heading:
                # Save previous section if exists
                if current_section:
                    current_section['content'] = '\n'.join(content_buffer).strip()
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'heading': block['text'].strip(),
                    'level': level,
                    'content': '',
                    'page_number': block['page_number'],
                    'subsections': []
                }
                content_buffer = []
            else:
                # Add to content buffer
                if block['text'].strip():
                    content_buffer.append(block['text'].strip())
        
        # Add the last section
        if current_section:
            current_section['content'] = '\n'.join(content_buffer).strip()
            sections.append(current_section)
        
        # Build hierarchical structure
        return self.build_hierarchy(sections)
    
    def build_hierarchy(self, sections: List[Dict]) -> List[Dict]:
        """Build hierarchical structure from flat sections list."""
        if not sections:
            return []
        
        # Stack to keep track of parent sections at each level
        stack = []
        result = []
        
        for section in sections:
            level = section['level']
            
            # Pop sections from stack that are at same or deeper level
            while stack and stack[-1]['level'] >= level:
                stack.pop()
            
            # If stack is empty, this is a top-level section
            if not stack:
                result.append(section)
            else:
                # Add as subsection to the parent
                parent = stack[-1]
                parent['subsections'].append(section)
            
            # Add current section to stack
            stack.append(section)
        
        return result
    
    def extract_paragraphs(self, text_blocks: List[Dict]) -> List[Dict]:
        """Extract paragraphs from text blocks, excluding headings."""
        font_hierarchy = self.analyze_font_hierarchy(text_blocks)
        paragraphs = []
        
        for block in text_blocks:
            is_heading, _ = self.is_likely_heading(block, font_hierarchy)
            
            if not is_heading and block['text'].strip():
                # Split long blocks into paragraphs
                text = block['text'].strip()
                
                # Simple paragraph splitting based on double newlines or length
                if '\n\n' in text:
                    parts = text.split('\n\n')
                elif len(text) > 500:  # Long text, try to split at sentence boundaries
                    sentences = re.split(r'(?<=[.!?])\s+', text)
                    parts = []
                    current_part = ""
                    
                    for sentence in sentences:
                        if len(current_part + sentence) > 300:
                            if current_part:
                                parts.append(current_part.strip())
                            current_part = sentence
                        else:
                            current_part += " " + sentence if current_part else sentence
                    
                    if current_part:
                        parts.append(current_part.strip())
                else:
                    parts = [text]
                
                for part in parts:
                    if part.strip():
                        paragraphs.append({
                            'text': part.strip(),
                            'page_number': block['page_number'],
                            'font_size': block.get('font_size'),
                            'font_name': block.get('font_name')
                        })
        
        return paragraphs
    
    def detect_figures(self, text_blocks: List[Dict]) -> List[Dict]:
        """Detect figure references and captions."""
        figures = []
        figure_patterns = [
            r'(Figure\s+\d+[:\.]?\s*(.*))',
            r'(Fig\.\s*\d+[:\.]?\s*(.*))',
            r'(Image\s+\d+[:\.]?\s*(.*))',
            r'(Diagram\s+\d+[:\.]?\s*(.*))',
        ]
        
        for block in text_blocks:
            text = block['text'].strip()
            
            for pattern in figure_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    caption = match.group(1).strip()
                    description = match.group(2).strip() if len(match.groups()) > 1 else None
                    
                    figures.append({
                        'page_number': block['page_number'],
                        'caption': caption,
                        'description': description,
                        'bbox': block.get('bbox')
                    })
                    break
        
        return figures
    
    def calculate_reading_statistics(self, text_blocks: List[Dict]) -> Dict:
        """Calculate reading statistics for the document."""
        total_text = ""
        for block in text_blocks:
            total_text += block['text'] + " "
        
        total_chars = len(total_text)
        total_words = len(total_text.split())
        
        # Simple language detection based on common words
        language = self.detect_language(total_text)
        
        return {
            'total_characters': total_chars,
            'total_words': total_words,
            'language': language
        }
    
    def detect_language(self, text: str) -> Optional[str]:
        """Simple language detection based on common words."""
        text_lower = text.lower()
        
        # Common English words
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        english_count = sum(1 for word in english_words if word in text_lower)
        
        if english_count >= 3:  # If at least 3 common English words found
            return 'en'
        
        return None  # Unknown language