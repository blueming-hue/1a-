# Adobe India Hackathon 2025 - Challenge 1a: Deployment Guide

## Quick Start

### 1. Build the Docker Image
```bash
docker build --platform linux/amd64 -t pdf-processor-1a .
```

### 2. Run with Your PDFs
```bash
docker run --rm \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-processor-1a
```

## Detailed Deployment Instructions

### Prerequisites
- Docker installed and running
- AMD64 architecture system
- At least 16GB RAM available
- Input PDFs in a directory

### Step-by-Step Deployment

#### 1. Prepare Your Environment
```bash
# Clone or download the solution
git clone <repository-url>
cd Challenge_1a

# Verify all required files are present
ls -la
# Should show: Dockerfile, process_pdfs.py, requirements.txt, src/, README.md
```

#### 2. Build the Docker Image
```bash
# Build with AMD64 platform specification (required for challenge)
docker build --platform linux/amd64 -t pdf-processor-1a .

# Verify the build
docker images pdf-processor-1a
```

#### 3. Prepare Input Directory
```bash
# Create input directory and add your PDF files
mkdir -p input
cp /path/to/your/pdfs/*.pdf input/

# Verify PDFs are in place
ls -la input/
```

#### 4. Create Output Directory
```bash
# Create output directory for results
mkdir -p output
```

#### 5. Run the Processing
```bash
# Run the container with proper volume mounts and network isolation
docker run --rm \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-processor-1a
```

#### 6. Verify Results
```bash
# Check generated JSON files
ls -la output/
# Should show .json files corresponding to each .pdf file

# Validate JSON format
python3 -m json.tool output/sample.json
```

## Performance Validation

### Testing with Different Document Sizes
```bash
# Test with 10-page document (should complete in ~2 seconds)
# Test with 25-page document (should complete in ~5 seconds)  
# Test with 50-page document (should complete in ≤10 seconds)
```

### Memory Usage Monitoring
```bash
# Monitor memory usage during processing
docker stats pdf-processor-1a
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Docker Build Fails
```bash
# Check Docker is running
docker info

# Check platform specification
docker build --platform linux/amd64 -t pdf-processor-1a .
```

#### 2. Permission Issues
```bash
# Ensure input directory is readable
chmod -R 755 input/

# Ensure output directory is writable
chmod -R 755 output/
```

#### 3. Memory Issues
```bash
# Check available memory
free -h

# Run with memory limit (optional)
docker run --rm --memory=16g \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-processor-1a
```

#### 4. Processing Timeout
```bash
# For very large PDFs, you might need to increase timeout
# The solution is optimized for ≤10 seconds on 50-page PDFs
# Larger documents may take longer
```

### Log Analysis
```bash
# View container logs
docker logs <container-id>

# Run with verbose output
docker run --rm \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-processor-1a 2>&1 | tee processing.log
```

## Challenge Compliance Verification

### Required Checks
- [x] Dockerfile present and functional
- [x] Processes all PDFs from `/app/input`
- [x] Generates `filename.json` for each `filename.pdf`
- [x] No internet access required during runtime
- [x] AMD64 architecture compatible
- [x] Uses only open-source libraries
- [x] Memory usage ≤ 16GB
- [x] Processing time ≤ 10 seconds for 50-page PDFs

### Performance Verification
```bash
# Test with 50-page PDF
time docker run --rm \
  -v $(pwd)/test_input:/app/input:ro \
  -v $(pwd)/test_output:/app/output \
  --network none \
  pdf-processor-1a

# Should complete in ≤ 10 seconds
```

## Advanced Configuration

### Custom Worker Count
The solution automatically uses up to 8 CPU cores. To modify:
```python
# Edit src/pdf_processor.py
processor = PDFProcessor(max_workers=4)  # Use 4 workers instead of 8
```

### Memory Optimization
For very large batches:
```bash
# Process PDFs in smaller batches
# Split input directory into smaller chunks
```

### Output Customization
The JSON schema is defined in `sample_dataset/schema/output_schema.json`. The solution generates outputs compliant with this schema.

## Production Deployment

### Batch Processing
```bash
# Process multiple directories
for dir in batch1 batch2 batch3; do
  docker run --rm \
    -v $(pwd)/$dir:/app/input:ro \
    -v $(pwd)/output_$dir:/app/output \
    --network none \
    pdf-processor-1a
done
```

### Monitoring and Logging
```bash
# Set up log collection
docker run --rm \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  --network none \
  pdf-processor-1a > processing.log 2>&1
```

### Resource Management
```bash
# Limit CPU and memory usage
docker run --rm \
  --cpus="8" \
  --memory="16g" \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-processor-1a
```

## Support and Maintenance

### Health Checks
```bash
# Verify solution components
python3 test_solution.py

# Run build and test script
./build_and_test.sh
```

### Updates and Modifications
- Source code is in the `src/` directory
- Main entry point is `process_pdfs.py`
- Dependencies are listed in `requirements.txt`
- Docker configuration is in `Dockerfile`

### Contact and Issues
For issues or questions related to this solution, please refer to the challenge documentation or create an issue in the repository.

---

**Note**: This solution is specifically designed for the Adobe India Hackathon 2025 Challenge 1a requirements and has been optimized for the specified constraints and performance targets.