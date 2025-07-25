"""
Main PDF processor that orchestrates text extraction, structure analysis, and JSON generation.
Optimized for the Adobe India Hackathon 2025 Challenge 1a requirements.
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

try:
    from .text_extractor import TextExtractor
    from .structure_analyzer import StructureAnalyzer
except ImportError:
    from text_extractor import TextExtractor
    from structure_analyzer import StructureAnalyzer


class PDFProcessor:
    """High-performance PDF processor with multi-threading support."""
    
    def __init__(self, max_workers: Optional[int] = None):
        """Initialize processor with optional worker count."""
        self.max_workers = max_workers or min(8, multiprocessing.cpu_count())
        self.schema_version = "1.0"
        
    def process_single_pdf(self, pdf_path: Path, output_dir: Path) -> Dict:
        """Process a single PDF file and generate JSON output."""
        start_time = time.time()
        
        # Initialize components
        extractor = TextExtractor()
        analyzer = StructureAnalyzer()
        
        try:
            # Load document
            if not extractor.load_document(str(pdf_path)):
                return {
                    'status': 'error',
                    'message': f'Failed to load PDF: {pdf_path.name}',
                    'processing_time': time.time() - start_time
                }
            
            # Extract document information
            doc_info = extractor.get_document_info(pdf_path.name)
            
            # Extract all text blocks
            text_blocks = extractor.extract_all_text()
            
            if not text_blocks:
                return {
                    'status': 'error',
                    'message': f'No text extracted from PDF: {pdf_path.name}',
                    'processing_time': time.time() - start_time
                }
            
            # Analyze document structure
            sections = analyzer.extract_sections(text_blocks)
            paragraphs = analyzer.extract_paragraphs(text_blocks)
            figures = analyzer.detect_figures(text_blocks)
            
            # Extract tables from all pages
            all_tables = []
            for page_num in range(doc_info['pages']):
                page_tables = extractor.extract_tables(page_num)
                all_tables.extend(page_tables)
            
            # Detect lists
            lists = extractor.detect_lists(text_blocks)
            
            # Calculate statistics
            stats = analyzer.calculate_reading_statistics(text_blocks)
            
            # Build final JSON structure
            result = {
                'document_info': doc_info,
                'content': {
                    'sections': sections,
                    'paragraphs': paragraphs,
                    'tables': all_tables,
                    'lists': lists,
                    'figures': figures
                },
                'metadata': {
                    'processing_time': time.time() - start_time,
                    'extraction_method': 'PyMuPDF',
                    'schema_version': self.schema_version,
                    'total_characters': stats['total_characters'],
                    'total_words': stats['total_words'],
                    'language': stats['language']
                }
            }
            
            # Save JSON output
            output_file = output_dir / f"{pdf_path.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            return {
                'status': 'success',
                'filename': pdf_path.name,
                'output_file': str(output_file),
                'processing_time': time.time() - start_time,
                'pages': doc_info['pages'],
                'sections': len(sections),
                'paragraphs': len(paragraphs),
                'tables': len(all_tables),
                'lists': len(lists),
                'figures': len(figures)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'filename': pdf_path.name,
                'message': str(e),
                'processing_time': time.time() - start_time
            }
        finally:
            # Clean up
            extractor.close()
    
    def process_batch(self, input_dir: Path, output_dir: Path) -> Dict:
        """Process all PDFs in the input directory."""
        start_time = time.time()
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all PDF files
        pdf_files = list(input_dir.glob("*.pdf"))
        
        if not pdf_files:
            return {
                'status': 'error',
                'message': 'No PDF files found in input directory',
                'processing_time': time.time() - start_time
            }
        
        results = []
        successful = 0
        failed = 0
        
        print(f"Processing {len(pdf_files)} PDF files using {self.max_workers} workers...")
        
        # Process PDFs in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_pdf = {
                executor.submit(self.process_single_pdf, pdf_file, output_dir): pdf_file
                for pdf_file in pdf_files
            }
            
            # Collect results
            for future in as_completed(future_to_pdf):
                pdf_file = future_to_pdf[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['status'] == 'success':
                        successful += 1
                        print(f"✓ {result['filename']} ({result['processing_time']:.2f}s, "
                              f"{result['pages']} pages, {result['sections']} sections)")
                    else:
                        failed += 1
                        print(f"✗ {result.get('filename', pdf_file.name)}: {result.get('message', 'Unknown error')}")
                        
                except Exception as e:
                    failed += 1
                    error_result = {
                        'status': 'error',
                        'filename': pdf_file.name,
                        'message': str(e),
                        'processing_time': 0
                    }
                    results.append(error_result)
                    print(f"✗ {pdf_file.name}: {str(e)}")
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        total_pages = sum(r.get('pages', 0) for r in results if r['status'] == 'success')
        total_sections = sum(r.get('sections', 0) for r in results if r['status'] == 'success')
        total_paragraphs = sum(r.get('paragraphs', 0) for r in results if r['status'] == 'success')
        total_tables = sum(r.get('tables', 0) for r in results if r['status'] == 'success')
        
        summary = {
            'status': 'completed',
            'total_files': len(pdf_files),
            'successful': successful,
            'failed': failed,
            'total_processing_time': total_time,
            'average_time_per_file': total_time / len(pdf_files) if pdf_files else 0,
            'statistics': {
                'total_pages': total_pages,
                'total_sections': total_sections,
                'total_paragraphs': total_paragraphs,
                'total_tables': total_tables,
                'pages_per_second': total_pages / total_time if total_time > 0 else 0
            },
            'results': results
        }
        
        print(f"\nProcessing completed:")
        print(f"  Total files: {len(pdf_files)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average time per file: {summary['average_time_per_file']:.2f}s")
        print(f"  Pages per second: {summary['statistics']['pages_per_second']:.2f}")
        
        return summary
    
    def validate_performance(self, results: Dict) -> bool:
        """Validate that processing meets performance requirements."""
        # Check if any 50-page document took more than 10 seconds
        for result in results.get('results', []):
            if result['status'] == 'success':
                pages = result.get('pages', 0)
                time_taken = result.get('processing_time', 0)
                
                # Estimate time for 50 pages
                if pages > 0:
                    time_per_page = time_taken / pages
                    estimated_time_50_pages = time_per_page * 50
                    
                    if estimated_time_50_pages > 10:
                        print(f"⚠️  Performance warning: {result['filename']} would take "
                              f"{estimated_time_50_pages:.2f}s for 50 pages")
                        return False
        
        return True