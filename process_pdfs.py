#!/usr/bin/env python3
"""
Adobe India Hackathon 2025 - Challenge 1a: PDF Processing Solution
Main entry point for processing PDFs from /app/input to /app/output

Requirements:
- Process all PDFs from /app/input directory
- Generate filename.json for each filename.pdf
- Execution time ≤ 10 seconds for 50-page PDFs
- Memory usage ≤ 16GB
- No internet access during runtime
- AMD64 architecture compatibility
"""

import sys
import os
from pathlib import Path
import time

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdf_processor import PDFProcessor


def main():
    """Main function to process PDFs according to challenge requirements."""
    print("Adobe India Hackathon 2025 - Challenge 1a: PDF Processing Solution")
    print("=" * 60)
    
    # Define input and output directories as per challenge requirements
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Validate input directory exists
    if not input_dir.exists():
        print(f"❌ Error: Input directory {input_dir} does not exist")
        sys.exit(1)
    
    # Check if input directory is accessible
    if not os.access(input_dir, os.R_OK):
        print(f"❌ Error: No read access to input directory {input_dir}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"❌ Error creating output directory {output_dir}: {e}")
        sys.exit(1)
    
    # Check if output directory is writable
    if not os.access(output_dir, os.W_OK):
        print(f"❌ Error: No write access to output directory {output_dir}")
        sys.exit(1)
    
    print(f"📁 Input directory: {input_dir}")
    print(f"📁 Output directory: {output_dir}")
    
    # Count PDF files in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    print(f"📄 Found {len(pdf_files)} PDF files to process")
    
    if not pdf_files:
        print("⚠️  No PDF files found in input directory")
        return
    
    # Initialize processor with optimal worker count for Docker environment
    # Use all available CPUs but limit to 8 as per challenge constraints
    processor = PDFProcessor(max_workers=8)
    
    # Process all PDFs
    start_time = time.time()
    try:
        results = processor.process_batch(input_dir, output_dir)
        
        # Validate performance requirements
        performance_ok = processor.validate_performance(results)
        
        # Print final summary
        print("\n" + "=" * 60)
        print("PROCESSING SUMMARY")
        print("=" * 60)
        
        if results['status'] == 'completed':
            print(f"✅ Status: {results['successful']}/{results['total_files']} files processed successfully")
            print(f"⏱️  Total time: {results['total_processing_time']:.2f} seconds")
            print(f"📊 Statistics:")
            print(f"   - Pages processed: {results['statistics']['total_pages']}")
            print(f"   - Sections extracted: {results['statistics']['total_sections']}")
            print(f"   - Paragraphs extracted: {results['statistics']['total_paragraphs']}")
            print(f"   - Tables extracted: {results['statistics']['total_tables']}")
            print(f"   - Processing speed: {results['statistics']['pages_per_second']:.2f} pages/second")
            
            if performance_ok:
                print("🚀 Performance: MEETS CHALLENGE REQUIREMENTS (≤10s for 50 pages)")
            else:
                print("⚠️  Performance: MAY NOT MEET CHALLENGE REQUIREMENTS")
            
            if results['failed'] > 0:
                print(f"⚠️  {results['failed']} files failed to process")
                print("\nFailed files:")
                for result in results['results']:
                    if result['status'] == 'error':
                        print(f"   - {result['filename']}: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ Processing failed: {results.get('message', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n🎉 PDF processing completed successfully!")
    print("📋 Check the output directory for generated JSON files")


if __name__ == "__main__":
    main()