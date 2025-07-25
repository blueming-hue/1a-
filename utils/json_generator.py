"""
JSON generation utilities for PDF processing output.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

class JSONGenerator:
    """Generates structured JSON output from processed PDF data."""
    
    def __init__(self):
        """Initialize the JSON generator."""
        self.schema_version = "1.0"
    
    def generate_document_metadata(self, raw_data: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Generate document metadata section."""
        metadata = raw_data.get('metadata', {})
        
        return {
            'filename': filename,
            'processing_timestamp': datetime.utcnow().isoformat() + 'Z',
            'schema_version': self.schema_version,
            'document_info': {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creation_date', ''),
                'modification_date': metadata.get('modification_date', ''),
                'page_count': metadata.get('page_count', 0)
            },
            'file_hash': self._generate_content_hash(raw_data.get('text_content', ''))
        }
    
    def generate_content_analysis(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content analysis section."""
        if not processed_data:
            return {}
        
        statistics = processed_data.get('statistics', {})
        keywords = processed_data.get('keywords', [])
        entities = processed_data.get('entities', {})
        sentiment = processed_data.get('sentiment', {})
        topics = processed_data.get('topics', [])
        
        return {
            'text_statistics': {
                'character_count': statistics.get('character_count', 0),
                'word_count': statistics.get('word_count', 0),
                'sentence_count': statistics.get('sentence_count', 0),
                'paragraph_count': statistics.get('paragraph_count', 0),
                'average_words_per_sentence': statistics.get('avg_words_per_sentence', 0),
                'average_characters_per_word': statistics.get('avg_chars_per_word', 0)
            },
            'keywords': [
                {
                    'term': keyword[0],
                    'score': float(keyword[1]) if len(keyword) > 1 else 1.0,
                    'rank': idx + 1
                }
                for idx, keyword in enumerate(keywords[:20])
            ],
            'named_entities': {
                'persons': entities.get('persons', []),
                'organizations': entities.get('organizations', []),
                'locations': entities.get('locations', []),
                'dates': entities.get('dates', []),
                'contact_info': {
                    'emails': entities.get('emails', []),
                    'phone_numbers': entities.get('phones', []),
                    'urls': entities.get('urls', [])
                }
            },
            'sentiment_analysis': {
                'polarity': sentiment.get('polarity', 0.0),
                'subjectivity': sentiment.get('subjectivity', 0.0),
                'sentiment_label': self._classify_sentiment(sentiment.get('polarity', 0.0))
            },
            'topics': [
                {
                    'topic_id': topic.get('topic_id', idx),
                    'terms': topic.get('terms', []),
                    'weight': topic.get('weight', 0.0),
                    'sample_sentences': topic.get('sentences', [])[:2]  # Limit to 2 sentences
                }
                for idx, topic in enumerate(topics[:10])  # Limit to top 10 topics
            ]
        }
    
    def generate_structure_analysis(self, structure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate document structure analysis section."""
        if not structure_data:
            return {}
        
        headings = structure_data.get('headings', [])
        lists = structure_data.get('lists', [])
        tables = structure_data.get('tables', [])
        layout = structure_data.get('layout', {})
        hierarchy = structure_data.get('hierarchy', {})
        structural_elements = structure_data.get('structural_elements', {})
        
        return {
            'document_structure': {
                'headings': [
                    {
                        'text': heading.get('text', ''),
                        'level': heading.get('level', 1),
                        'page': heading.get('page', 1),
                        'type': heading.get('type', 'unknown')
                    }
                    for heading in headings
                ],
                'lists': [
                    {
                        'type': lst.get('type', 'unknown'),
                        'page': lst.get('page', 1),
                        'item_count': len(lst.get('items', [])),
                        'items': [
                            {
                                'text': item.get('text', ''),
                                'marker': item.get('marker', '')
                            }
                            for item in lst.get('items', [])[:10]  # Limit items
                        ]
                    }
                    for lst in lists
                ],
                'tables': [
                    {
                        'page': table.get('page', 1),
                        'dimensions': table.get('dimensions', {}),
                        'has_header': table.get('has_header', False),
                        'column_types': table.get('column_types', []),
                        'summary': table.get('summary', {}),
                        'sample_data': table.get('data', [])[:3] if table.get('data') else []  # First 3 rows
                    }
                    for table in tables
                ]
            },
            'layout_analysis': {
                'page_count': layout.get('page_count', 0),
                'layout_type': layout.get('layout_type', 'unknown'),
                'page_statistics': layout.get('page_statistics', []),
                'text_distribution': layout.get('text_distribution', [])
            },
            'document_hierarchy': {
                'sections': hierarchy.get('sections', []),
                'outline': hierarchy.get('outline', []),
                'depth': hierarchy.get('depth', 0)
            },
            'structural_summary': {
                'heading_count': structural_elements.get('heading_count', 0),
                'list_count': structural_elements.get('list_count', 0),
                'table_count': structural_elements.get('table_count', 0),
                'has_table_of_contents': structural_elements.get('has_toc', False),
                'has_index': structural_elements.get('has_index', False),
                'document_type': structural_elements.get('document_type', 'general')
            }
        }
    
    def generate_page_analysis(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate per-page analysis."""
        pages = raw_data.get('pages', [])
        page_analysis = []
        
        for page in pages:
            page_info = {
                'page_number': page.get('page_number', 1),
                'text_length': page.get('text_length', 0),
                'content_summary': {
                    'has_text': bool(page.get('text', '').strip()),
                    'has_images': len(page.get('images', [])) > 0,
                    'has_tables': len(page.get('tables', [])) > 0,
                    'block_count': len(page.get('blocks', []))
                },
                'images': [
                    {
                        'index': img.get('index', 0),
                        'size': img.get('size', 0)
                    }
                    for img in page.get('images', [])
                ],
                'tables': [
                    {
                        'table_index': table.get('table_index', 0),
                        'rows': table.get('rows', 0),
                        'columns': table.get('columns', 0)
                    }
                    for table in page.get('tables', [])
                ]
            }
            
            # Add text preview (first 200 characters)
            page_text = page.get('text', '')
            if page_text:
                page_info['text_preview'] = page_text[:200].strip() + ('...' if len(page_text) > 200 else '')
            
            page_analysis.append(page_info)
        
        return page_analysis
    
    def generate_extraction_quality(self, raw_data: Dict[str, Any], processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate extraction quality metrics."""
        text_content = raw_data.get('text_content', '')
        pages = raw_data.get('pages', [])
        
        # Calculate basic quality metrics
        total_chars = len(text_content)
        total_pages = len(pages)
        
        # Estimate extraction success rate
        non_empty_pages = sum(1 for page in pages if page.get('text', '').strip())
        extraction_success_rate = (non_empty_pages / total_pages) if total_pages > 0 else 0
        
        # Calculate text density
        avg_chars_per_page = total_chars / total_pages if total_pages > 0 else 0
        
        # Detect potential issues
        issues = []
        if extraction_success_rate < 0.8:
            issues.append("Low text extraction success rate")
        if avg_chars_per_page < 100:
            issues.append("Low text density - possible image-heavy document")
        if total_chars < 50:
            issues.append("Very little text extracted")
        
        return {
            'extraction_metrics': {
                'total_characters_extracted': total_chars,
                'pages_with_text': non_empty_pages,
                'extraction_success_rate': round(extraction_success_rate, 3),
                'average_characters_per_page': round(avg_chars_per_page, 2)
            },
            'quality_indicators': {
                'has_structured_content': bool(processed_data.get('keywords')),
                'has_identifiable_entities': bool(any(processed_data.get('entities', {}).values())),
                'has_coherent_text': len(processed_data.get('sentences', [])) > 5,
                'extraction_issues': issues
            },
            'confidence_score': self._calculate_confidence_score(raw_data, processed_data)
        }
    
    def _classify_sentiment(self, polarity: float) -> str:
        """Classify sentiment based on polarity score."""
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash of the content for integrity checking."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _calculate_confidence_score(self, raw_data: Dict[str, Any], processed_data: Dict[str, Any]) -> float:
        """Calculate a confidence score for the extraction quality."""
        score = 0.0
        max_score = 10.0
        
        # Text extraction quality (0-3 points)
        text_content = raw_data.get('text_content', '')
        if len(text_content) > 1000:
            score += 3.0
        elif len(text_content) > 100:
            score += 2.0
        elif len(text_content) > 10:
            score += 1.0
        
        # Structure detection (0-2 points)
        if processed_data.get('keywords'):
            score += 1.0
        if any(processed_data.get('entities', {}).values()):
            score += 1.0
        
        # Content analysis (0-2 points)
        if processed_data.get('topics'):
            score += 1.0
        if len(processed_data.get('sentences', [])) > 10:
            score += 1.0
        
        # Metadata presence (0-1 point)
        metadata = raw_data.get('metadata', {})
        if any(metadata.values()):
            score += 1.0
        
        # Page consistency (0-2 points)
        pages = raw_data.get('pages', [])
        if pages:
            pages_with_text = sum(1 for page in pages if page.get('text', '').strip())
            consistency = pages_with_text / len(pages)
            score += 2.0 * consistency
        
        return min(round(score / max_score, 3), 1.0)
    
    def generate_json(self, raw_data: Dict[str, Any], processed_data: Dict[str, Any], 
                     structure_data: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Generate the complete JSON output structure."""
        
        # Generate all sections
        metadata = self.generate_document_metadata(raw_data, filename)
        content_analysis = self.generate_content_analysis(processed_data)
        structure_analysis = self.generate_structure_analysis(structure_data)
        page_analysis = self.generate_page_analysis(raw_data)
        quality_metrics = self.generate_extraction_quality(raw_data, processed_data)
        
        # Compile final JSON structure
        json_output = {
            'document_metadata': metadata,
            'content_analysis': content_analysis,
            'structure_analysis': structure_analysis,
            'page_analysis': page_analysis,
            'extraction_quality': quality_metrics,
            'raw_content': {
                'full_text': raw_data.get('text_content', ''),
                'page_count': len(raw_data.get('pages', [])),
                'has_images': len(raw_data.get('images', [])) > 0,
                'has_tables': len(raw_data.get('tables', [])) > 0
            }
        }
        
        return json_output
    
    def validate_json_output(self, json_output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the generated JSON output against basic requirements."""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required top-level keys
        required_keys = ['document_metadata', 'content_analysis', 'structure_analysis', 
                        'page_analysis', 'extraction_quality']
        
        for key in required_keys:
            if key not in json_output:
                validation_results['errors'].append(f"Missing required key: {key}")
                validation_results['is_valid'] = False
        
        # Check metadata completeness
        metadata = json_output.get('document_metadata', {})
        if not metadata.get('filename'):
            validation_results['warnings'].append("Missing filename in metadata")
        
        # Check content analysis
        content = json_output.get('content_analysis', {})
        if not content.get('text_statistics', {}).get('word_count', 0):
            validation_results['warnings'].append("No word count in text statistics")
        
        # Check page analysis
        pages = json_output.get('page_analysis', [])
        if not pages:
            validation_results['warnings'].append("No page analysis data")
        
        return validation_results