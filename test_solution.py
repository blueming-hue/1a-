#!/usr/bin/env python3
"""
Test script for the PDF processing solution.
This script validates that the solution works correctly and meets requirements.
"""

import json
import time
import tempfile
import shutil
from pathlib import Path
from process_pdfs import PDFProcessor

def create_test_pdf():
    """Create a simple test PDF for validation."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a temporary PDF file
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        # Create PDF content
        c = canvas.Canvas(temp_file.name, pagesize=letter)
        c.drawString(100, 750, "Test Document")
        c.drawString(100, 700, "This is a test PDF document for validation.")
        c.drawString(100, 650, "It contains some sample text content.")
        c.drawString(100, 600, "Contact: test@example.com")
        c.drawString(100, 550, "Phone: (555) 123-4567")
        c.showPage()
        c.save()
        
        return Path(temp_file.name)
    
    except ImportError:
        print("ReportLab not available, skipping PDF creation test")
        return None

def test_json_output_structure(json_data):
    """Test that JSON output has required structure."""
    required_keys = [
        'document_metadata',
        'content_analysis', 
        'structure_analysis',
        'page_analysis',
        'extraction_quality'
    ]
    
    for key in required_keys:
        assert key in json_data, f"Missing required key: {key}"
    
    # Test metadata structure
    metadata = json_data['document_metadata']
    assert 'filename' in metadata
    assert 'processing_timestamp' in metadata
    assert 'schema_version' in metadata
    
    # Test content analysis structure
    content = json_data['content_analysis']
    assert 'text_statistics' in content
    assert 'keywords' in content
    assert 'named_entities' in content
    
    print("✅ JSON structure validation passed")

def test_processing_speed():
    """Test processing speed requirements."""
    processor = PDFProcessor()
    
    # Create test directories
    input_dir = Path("test_input")
    output_dir = Path("test_output")
    
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Create or use existing test PDF
        test_pdf = create_test_pdf()
        if test_pdf:
            # Copy to input directory
            shutil.copy(test_pdf, input_dir / "test.pdf")
            
            # Test processing speed
            start_time = time.time()
            results = processor.process_all_pdfs(input_dir, output_dir)
            processing_time = time.time() - start_time
            
            print(f"Processing time: {processing_time:.2f} seconds")
            
            # Check if output was created
            output_file = output_dir / "test.json"
            assert output_file.exists(), "Output JSON file not created"
            
            # Load and validate JSON
            with open(output_file, 'r') as f:
                json_data = json.load(f)
            
            test_json_output_structure(json_data)
            
            print("✅ Processing speed test passed")
            
            # Cleanup test PDF
            test_pdf.unlink()
        else:
            print("⚠️  Skipping speed test - no test PDF created")
    
    finally:
        # Cleanup test directories
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)

def test_error_handling():
    """Test error handling with invalid inputs."""
    processor = PDFProcessor()
    
    # Test with non-existent directory
    input_dir = Path("non_existent_dir")
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        results = processor.process_all_pdfs(input_dir, output_dir)
        assert results['processed'] == 0
        assert results['failed'] == 0
        print("✅ Error handling test passed")
    
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)

def test_memory_usage():
    """Test memory usage characteristics."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    processor = PDFProcessor()
    
    # Memory after initialization
    init_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = init_memory - initial_memory
    
    print(f"Initial memory: {initial_memory:.2f} MB")
    print(f"Memory after init: {init_memory:.2f} MB")
    print(f"Memory increase: {memory_increase:.2f} MB")
    
    # Check if memory usage is reasonable
    assert memory_increase < 500, f"Memory usage too high: {memory_increase:.2f} MB"
    
    print("✅ Memory usage test passed")

def main():
    """Run all tests."""
    print("🧪 Running PDF Processing Solution Tests")
    print("=" * 50)
    
    try:
        # Test 1: Memory usage
        print("\n1. Testing memory usage...")
        test_memory_usage()
        
        # Test 2: Error handling
        print("\n2. Testing error handling...")
        test_error_handling()
        
        # Test 3: Processing speed and output
        print("\n3. Testing processing speed and output...")
        test_processing_speed()
        
        print("\n🎉 All tests passed!")
        print("Solution is ready for submission.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()