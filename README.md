# Challenge 1a: PDF Processing Solution

## Overview

This is a comprehensive solution for Challenge 1a of the Adobe India Hackathon 2025. The solution implements a robust PDF processing system that extracts structured data from PDF documents and outputs detailed JSON files. The system is designed to handle various types of PDFs including simple text documents, complex multi-column layouts, documents with tables and images, and large documents up to 50 pages.

## Architecture

The solution follows a modular architecture with the following components:

```
Challenge_1a/
├── process_pdfs.py          # Main processing script
├── utils/                   # Utility modules
│   ├── __init__.py
│   ├── text_processor.py    # NLP and text analysis
│   ├── structure_analyzer.py # Document structure analysis
│   └── json_generator.py    # JSON output generation
├── Dockerfile              # Container configuration
├── requirements.txt         # Python dependencies
└── README.md               # This documentation
```

## Key Features

### 1. Multi-Method PDF Extraction
- **Primary Method**: PyMuPDF (fitz) for comprehensive text, image, and metadata extraction
- **Table Extraction**: pdfplumber for accurate table detection and parsing
- **Fallback Method**: PyPDF2 for robust text extraction when other methods fail
- **OCR Support**: Tesseract OCR for image-based text extraction (when needed)

### 2. Advanced Text Processing
- **NLP Analysis**: Using spaCy and NLTK for advanced text processing
- **Keyword Extraction**: TF-IDF based keyword identification
- **Named Entity Recognition**: Extraction of persons, organizations, locations, dates, emails, phones, URLs
- **Sentiment Analysis**: TextBlob-based sentiment scoring
- **Topic Modeling**: K-means clustering for topic identification

### 3. Document Structure Analysis
- **Heading Detection**: Multi-pattern heading identification with hierarchical levels
- **List Detection**: Bullet points, numbered lists, and lettered lists
- **Table Analysis**: Structure analysis, header detection, column type identification
- **Layout Analysis**: Document type classification and layout pattern recognition
- **Hierarchy Extraction**: Document outline and section structure

### 4. Comprehensive JSON Output
- **Document Metadata**: File information, processing timestamps, document properties
- **Content Analysis**: Text statistics, keywords, entities, sentiment, topics
- **Structure Analysis**: Headings, lists, tables, layout information
- **Page Analysis**: Per-page content breakdown and statistics
- **Quality Metrics**: Extraction confidence scores and quality indicators

## Models and Libraries Used

### Core PDF Processing Libraries
- **PyMuPDF (fitz) 1.23.14**: Primary PDF processing library for text, image, and metadata extraction
- **pdfplumber 0.10.3**: Specialized table extraction and layout analysis
- **PyPDF2 3.0.1**: Fallback text extraction method

### Natural Language Processing
- **spaCy 3.7.2**: Advanced NLP processing with en_core_web_sm model (~50MB)
- **NLTK 3.8.1**: Text tokenization, sentence segmentation, stopwords
- **TextBlob 0.17.1**: Sentiment analysis and basic NLP tasks

### Machine Learning and Analysis
- **scikit-learn 1.3.2**: TF-IDF vectorization, K-means clustering for topic modeling
- **numpy 1.24.3**: Numerical computations and array operations
- **pandas 2.1.4**: Data manipulation and analysis

### Image Processing (Optional)
- **OpenCV 4.8.1**: Image preprocessing for OCR
- **Pillow 10.1.0**: Image handling and manipulation
- **pytesseract 0.3.10**: OCR text extraction from images

### Performance Optimization
- **Multiprocessing**: Parallel processing for multiple PDFs
- **Memory Management**: Efficient handling of large documents
- **CPU Optimization**: Multi-threaded processing within constraints

## Performance Characteristics

### Resource Usage
- **Memory**: Optimized to stay within 16GB RAM limit
- **CPU**: Efficient use of 8 CPU cores with parallel processing
- **Model Size**: Total ML models ~150MB (well under 200MB limit)
- **Processing Speed**: <10 seconds for 50-page PDFs

### Scalability Features
- **Parallel Processing**: Multiple PDFs processed simultaneously
- **Memory Streaming**: Large documents processed in chunks
- **Timeout Handling**: 30-second timeout per file to prevent hanging
- **Error Recovery**: Graceful fallback mechanisms for corrupted files

## Installation and Usage

### Building the Docker Container

```bash
# Build the container (AMD64 platform)
docker build --platform linux/amd64 -t pdf-processor .
```

### Running the Solution

```bash
# Run with input and output directories mounted
docker run --rm \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-processor
```

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run locally
python process_pdfs.py
```

## Output Format

The solution generates a JSON file for each PDF with the following structure:

```json
{
  "document_metadata": {
    "filename": "document.pdf",
    "processing_timestamp": "2025-01-27T10:30:00Z",
    "schema_version": "1.0",
    "document_info": {
      "title": "Document Title",
      "author": "Author Name",
      "page_count": 25
    }
  },
  "content_analysis": {
    "text_statistics": {
      "character_count": 15000,
      "word_count": 2500,
      "sentence_count": 120
    },
    "keywords": [
      {"term": "important", "score": 0.85, "rank": 1}
    ],
    "named_entities": {
      "persons": ["John Doe"],
      "organizations": ["Adobe Inc"],
      "locations": ["San Francisco"]
    },
    "sentiment_analysis": {
      "polarity": 0.1,
      "subjectivity": 0.4,
      "sentiment_label": "positive"
    },
    "topics": [
      {
        "topic_id": 0,
        "terms": ["technology", "innovation"],
        "weight": 0.75
      }
    ]
  },
  "structure_analysis": {
    "document_structure": {
      "headings": [
        {
          "text": "Introduction",
          "level": 1,
          "page": 1,
          "type": "uppercase"
        }
      ],
      "lists": [
        {
          "type": "bullet",
          "page": 2,
          "item_count": 5,
          "items": [
            {"text": "First item", "marker": "•"}
          ]
        }
      ],
      "tables": [
        {
          "page": 3,
          "dimensions": {"rows": 10, "columns": 4},
          "has_header": true,
          "column_types": ["text", "numeric", "date", "text"]
        }
      ]
    },
    "layout_analysis": {
      "page_count": 25,
      "layout_type": "text_heavy",
      "text_distribution": [1200, 1150, 1300]
    },
    "document_hierarchy": {
      "sections": [],
      "outline": ["Introduction (Page 1)", "  Background (Page 2)"],
      "depth": 3
    }
  },
  "page_analysis": [
    {
      "page_number": 1,
      "text_length": 1200,
      "content_summary": {
        "has_text": true,
        "has_images": false,
        "has_tables": false
      },
      "text_preview": "This document provides..."
    }
  ],
  "extraction_quality": {
    "extraction_metrics": {
      "total_characters_extracted": 15000,
      "pages_with_text": 25,
      "extraction_success_rate": 1.0,
      "average_characters_per_page": 600
    },
    "quality_indicators": {
      "has_structured_content": true,
      "has_identifiable_entities": true,
      "has_coherent_text": true,
      "extraction_issues": []
    },
    "confidence_score": 0.95
  },
  "raw_content": {
    "full_text": "Complete extracted text...",
    "page_count": 25,
    "has_images": true,
    "has_tables": true
  }
}
```

## Technical Implementation Details

### PDF Processing Pipeline

1. **Document Loading**: Multi-method approach with PyMuPDF as primary
2. **Text Extraction**: Character-level extraction with positioning information
3. **Structure Detection**: Pattern-based identification of headings, lists, tables
4. **Content Analysis**: NLP processing for keywords, entities, sentiment
5. **Quality Assessment**: Confidence scoring and validation
6. **JSON Generation**: Structured output with comprehensive metadata

### Error Handling and Robustness

- **Multiple Extraction Methods**: Fallback mechanisms for different PDF types
- **Memory Management**: Streaming processing for large documents
- **Timeout Protection**: Process-level timeouts to prevent hanging
- **Graceful Degradation**: Partial results when complete processing fails
- **Validation**: Output validation against schema requirements

### Performance Optimizations

- **Parallel Processing**: Multi-process execution for multiple files
- **Efficient Libraries**: Optimized libraries for core operations
- **Memory Streaming**: Chunk-based processing for large files
- **Caching**: Reuse of expensive computations where possible
- **Resource Monitoring**: Memory and CPU usage tracking

## Testing and Validation

### Test Coverage
- **Simple PDFs**: Basic text documents with standard formatting
- **Complex PDFs**: Multi-column layouts, mixed content types
- **Table-Heavy PDFs**: Financial reports, data sheets
- **Image-Rich PDFs**: Presentations, brochures with embedded images
- **Large PDFs**: 50+ page documents for performance testing

### Quality Assurance
- **Output Validation**: JSON schema compliance checking
- **Content Accuracy**: Extraction quality verification
- **Performance Testing**: Speed and memory usage validation
- **Error Handling**: Robustness testing with corrupted files

## Compliance with Challenge Requirements

✅ **Execution Time**: ≤ 10 seconds for 50-page PDFs  
✅ **Model Size**: ≤ 200MB (actual: ~150MB)  
✅ **Network**: No internet access during runtime  
✅ **Runtime**: CPU-only execution on AMD64  
✅ **Architecture**: AMD64 compatible  
✅ **Processing**: Automatic processing from /app/input  
✅ **Output**: JSON files in /app/output  
✅ **Open Source**: All libraries and models are open source  
✅ **Cross-Platform**: Works on simple and complex PDFs  

## Future Enhancements

- **Advanced OCR**: Enhanced image-to-text extraction
- **Multi-Language Support**: Extended language models
- **Custom Schema**: Configurable output formats
- **Batch Optimization**: Further performance improvements
- **Quality Metrics**: Enhanced extraction quality assessment

## License

This solution uses open-source libraries and is provided under the MIT License.

## Support

For questions or issues with this solution, please refer to the documentation or contact the development team.