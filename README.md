# Adobe India Hackathon 2025 - Challenge 1a: PDF Processing Solution

## Overview
This solution implements a high-performance PDF processing system that extracts structured data from PDF documents and outputs JSON files according to the challenge specifications. The solution is optimized for speed, memory efficiency, and meets all Docker containerization requirements.

## Challenge Requirements ✅
- **Execution Time**: ≤ 10 seconds for a 50-page PDF
- **Model Size**: ≤ 200MB (if using ML models)
- **Network**: No internet access during runtime
- **Runtime**: CPU-only (AMD64) with 8 CPUs and 16 GB RAM
- **Architecture**: AMD64 compatible
- **Processing**: Automatic processing of all PDFs from `/app/input`
- **Output**: Generate `filename.json` for each `filename.pdf`
- **Libraries**: Open source only

## Solution Architecture

### Core Components
1. **PDF Text Extraction**: Uses PyMuPDF (fitz) for fast, reliable text extraction
2. **Document Structure Analysis**: Identifies headings, paragraphs, tables, and lists
3. **Content Classification**: Categorizes content using rule-based and pattern matching
4. **JSON Generation**: Creates structured output conforming to the required schema
5. **Performance Optimization**: Multi-threading and memory-efficient processing

### Key Features
- **Fast Processing**: Optimized for sub-10-second execution on 50-page PDFs
- **Memory Efficient**: Streaming processing to stay within 16GB RAM limit
- **Robust Text Extraction**: Handles complex layouts, multi-column text, and tables
- **Schema Compliance**: Outputs conform to the required JSON schema
- **Error Handling**: Graceful handling of corrupted or problematic PDFs

## Project Structure
```
Challenge_1a/
├── src/
│   ├── pdf_processor.py      # Main PDF processing logic
│   ├── text_extractor.py     # Text extraction utilities
│   ├── structure_analyzer.py # Document structure analysis
│   ├── content_classifier.py # Content categorization
│   └── json_generator.py     # JSON output generation
├── sample_dataset/
│   ├── pdfs/                 # Sample input PDFs
│   ├── outputs/              # Expected JSON outputs
│   └── schema/
│       └── output_schema.json # Output schema definition
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker container configuration
├── process_pdfs.py          # Main entry point
└── README.md               # This file
```

## Installation & Setup

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python process_pdfs.py
```

### Docker Build & Run
```bash
# Build the Docker image
docker build --platform linux/amd64 -t pdf-processor-1a .

# Run with sample data
docker run --rm \
  -v $(pwd)/sample_dataset/pdfs:/app/input:ro \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-processor-1a
```

## Technical Implementation

### PDF Processing Pipeline
1. **Document Loading**: Load PDF using PyMuPDF for optimal performance
2. **Text Extraction**: Extract text with position and formatting information
3. **Structure Analysis**: Identify document hierarchy (headings, sections, paragraphs)
4. **Content Classification**: Categorize content (title, author, abstract, body, etc.)
5. **Table Detection**: Identify and extract tabular data
6. **List Processing**: Extract bullet points and numbered lists
7. **JSON Generation**: Create structured output matching the schema

### Performance Optimizations
- **Parallel Processing**: Utilize multiple CPU cores for batch processing
- **Memory Management**: Stream processing to handle large documents efficiently
- **Caching**: Cache frequently used patterns and configurations
- **Fast Libraries**: Use optimized libraries (PyMuPDF, NumPy) for core operations

### Schema Compliance
The output JSON structure includes:
- Document metadata (title, author, creation date)
- Content hierarchy (sections, subsections)
- Text elements (paragraphs, headings)
- Structured data (tables, lists)
- Formatting information (fonts, styles)

## Dependencies (Open Source)
- **PyMuPDF (fitz)**: Fast PDF processing and text extraction
- **NumPy**: Numerical operations and array processing
- **Python Standard Library**: JSON, multiprocessing, pathlib, re
- **Total Size**: < 200MB including all dependencies

## Testing & Validation

### Performance Testing
```bash
# Test with 50-page PDF
time docker run --rm \
  -v $(pwd)/test_pdfs:/app/input:ro \
  -v $(pwd)/test_output:/app/output \
  --network none \
  pdf-processor-1a
```

### Validation Checklist
- [x] Processes all PDFs in input directory
- [x] Generates JSON for each PDF
- [x] Output conforms to required schema
- [x] Execution time < 10 seconds for 50-page PDFs
- [x] Memory usage < 16GB
- [x] Works without internet access
- [x] AMD64 architecture compatibility
- [x] Open source libraries only

## Sample Output
```json
{
  "document_info": {
    "filename": "sample.pdf",
    "title": "Document Title",
    "author": "Author Name",
    "pages": 10,
    "creation_date": "2025-01-XX"
  },
  "content": {
    "sections": [
      {
        "heading": "Introduction",
        "level": 1,
        "content": "Section content...",
        "subsections": []
      }
    ],
    "tables": [],
    "figures": []
  },
  "metadata": {
    "processing_time": 2.34,
    "extraction_method": "PyMuPDF",
    "schema_version": "1.0"
  }
}
```

## Troubleshooting

### Common Issues
1. **Memory Issues**: Ensure sufficient RAM for large PDFs
2. **Font Issues**: Some PDFs may have embedded fonts that affect extraction
3. **Layout Issues**: Complex layouts may require additional processing time

### Performance Tips
- Use SSD storage for faster I/O operations
- Ensure adequate CPU cores for parallel processing
- Monitor memory usage with large batch operations

## License
This solution uses only open-source libraries and is compatible with the challenge requirements.

## Contact
For questions or issues, please refer to the challenge documentation or create an issue in this repository.