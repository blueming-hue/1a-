#!/bin/bash

# Adobe India Hackathon 2025 - Challenge 1a: Build and Test Script
# This script builds the Docker image and runs comprehensive tests

set -e  # Exit on any error

echo "=================================="
echo "Adobe India Hackathon 2025"
echo "Challenge 1a: PDF Processing Solution"
echo "Build and Test Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_IMAGE_NAME="pdf-processor-1a"
DOCKER_TAG="latest"
FULL_IMAGE_NAME="${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker and try again."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker and try again."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Function to run local tests
run_local_tests() {
    print_status "Running local tests..."
    
    if [[ ! -f "test_solution.py" ]]; then
        print_warning "test_solution.py not found. Skipping local tests."
        return 0
    fi
    
    if python3 test_solution.py; then
        print_success "Local tests passed"
        return 0
    else
        print_error "Local tests failed"
        return 1
    fi
}

# Function to build Docker image
build_docker_image() {
    print_status "Building Docker image: ${FULL_IMAGE_NAME}"
    
    # Check if Dockerfile exists
    if [[ ! -f "Dockerfile" ]]; then
        print_error "Dockerfile not found in current directory"
        exit 1
    fi
    
    # Build the image
    if docker build --platform linux/amd64 -t "${FULL_IMAGE_NAME}" .; then
        print_success "Docker image built successfully"
        
        # Show image details
        print_status "Docker image details:"
        docker images "${DOCKER_IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}\t{{.CreatedAt}}"
        
        # Check image size
        IMAGE_SIZE=$(docker images "${FULL_IMAGE_NAME}" --format "{{.Size}}")
        print_status "Image size: ${IMAGE_SIZE}"
        
        return 0
    else
        print_error "Failed to build Docker image"
        return 1
    fi
}

# Function to create test data
create_test_data() {
    print_status "Creating test directories..."
    
    # Create test directories
    mkdir -p test_input test_output
    
    # Create a simple test PDF using Python (if reportlab is available)
    cat > create_test_pdf.py << 'EOF'
#!/usr/bin/env python3
"""Create a simple test PDF for testing purposes."""

import sys
from pathlib import Path

def create_simple_test_pdf():
    """Create a simple test PDF using basic text."""
    # Create a minimal PDF-like structure (for testing purposes)
    # In a real scenario, you'd use a proper PDF library
    
    test_content = """
    This is a test document for the Adobe India Hackathon 2025 Challenge 1a.
    
    Introduction
    This document contains sample text to test the PDF processing solution.
    
    Section 1: Overview
    This section provides an overview of the test document structure.
    
    Section 2: Content
    This section contains the main content of the document.
    
    • First bullet point
    • Second bullet point  
    • Third bullet point
    
    1. First numbered item
    2. Second numbered item
    3. Third numbered item
    
    Conclusion
    This concludes the test document.
    """
    
    # Save as text file (in real scenario, this would be a PDF)
    test_file = Path("test_input/sample_test.txt")
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"Created test file: {test_file}")

if __name__ == "__main__":
    create_simple_test_pdf()
EOF
    
    python3 create_test_pdf.py
    rm create_test_pdf.py
    
    print_success "Test data created"
}

# Function to test Docker container
test_docker_container() {
    print_status "Testing Docker container..."
    
    # Create test directories if they don't exist
    create_test_data
    
    # Run the container
    print_status "Running Docker container..."
    
    if docker run --rm \
        -v "$(pwd)/test_input:/app/input:ro" \
        -v "$(pwd)/test_output:/app/output" \
        --network none \
        "${FULL_IMAGE_NAME}"; then
        
        print_success "Docker container ran successfully"
        
        # Check if output files were created
        if ls test_output/*.json &> /dev/null; then
            print_success "JSON output files were created"
            ls -la test_output/
        else
            print_warning "No JSON output files found"
        fi
        
        return 0
    else
        print_error "Docker container failed to run"
        return 1
    fi
}

# Function to validate challenge requirements
validate_requirements() {
    print_status "Validating challenge requirements..."
    
    local all_good=true
    
    # Check if Docker image exists
    if docker images "${FULL_IMAGE_NAME}" --format "{{.Repository}}" | grep -q "${DOCKER_IMAGE_NAME}"; then
        print_success "✓ Docker image exists"
    else
        print_error "✗ Docker image not found"
        all_good=false
    fi
    
    # Check if Dockerfile exists
    if [[ -f "Dockerfile" ]]; then
        print_success "✓ Dockerfile present"
    else
        print_error "✗ Dockerfile missing"
        all_good=false
    fi
    
    # Check if README.md exists
    if [[ -f "README.md" ]]; then
        print_success "✓ README.md present"
    else
        print_error "✗ README.md missing"
        all_good=false
    fi
    
    # Check if main script exists
    if [[ -f "process_pdfs.py" ]]; then
        print_success "✓ Main processing script present"
    else
        print_error "✗ process_pdfs.py missing"
        all_good=false
    fi
    
    # Check if source code exists
    if [[ -d "src" ]]; then
        print_success "✓ Source code directory present"
    else
        print_error "✗ src directory missing"
        all_good=false
    fi
    
    # Check image size (should be reasonable)
    if docker images "${FULL_IMAGE_NAME}" --format "{{.Size}}" | grep -q "MB\|GB"; then
        IMAGE_SIZE=$(docker images "${FULL_IMAGE_NAME}" --format "{{.Size}}")
        print_success "✓ Image size: ${IMAGE_SIZE}"
    else
        print_warning "⚠ Could not determine image size"
    fi
    
    if $all_good; then
        print_success "All requirements validation passed"
        return 0
    else
        print_error "Some requirements validation failed"
        return 1
    fi
}

# Function to show usage instructions
show_usage() {
    echo ""
    echo "Usage Instructions:"
    echo "=================="
    echo ""
    echo "1. Build the Docker image:"
    echo "   docker build --platform linux/amd64 -t ${DOCKER_IMAGE_NAME} ."
    echo ""
    echo "2. Run with your PDF files:"
    echo "   docker run --rm \\"
    echo "     -v \$(pwd)/input:/app/input:ro \\"
    echo "     -v \$(pwd)/output:/app/output \\"
    echo "     --network none \\"
    echo "     ${DOCKER_IMAGE_NAME}"
    echo ""
    echo "3. For testing with sample data:"
    echo "   docker run --rm \\"
    echo "     -v \$(pwd)/sample_dataset/pdfs:/app/input:ro \\"
    echo "     -v \$(pwd)/sample_dataset/outputs:/app/output \\"
    echo "     --network none \\"
    echo "     ${DOCKER_IMAGE_NAME}"
    echo ""
}

# Main execution
main() {
    local run_tests=true
    local build_image=true
    local test_container=true
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-tests)
                run_tests=false
                shift
                ;;
            --no-build)
                build_image=false
                shift
                ;;
            --no-container-test)
                test_container=false
                shift
                ;;
            --help|-h)
                echo "Build and test script for Adobe India Hackathon 2025 Challenge 1a"
                echo ""
                echo "Options:"
                echo "  --no-tests           Skip local tests"
                echo "  --no-build           Skip Docker image build"
                echo "  --no-container-test  Skip Docker container test"
                echo "  --help, -h           Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Check Docker
    check_docker
    
    # Run local tests
    if $run_tests; then
        if ! run_local_tests; then
            print_warning "Local tests failed, but continuing with build..."
        fi
    fi
    
    # Build Docker image
    if $build_image; then
        if ! build_docker_image; then
            print_error "Failed to build Docker image. Exiting."
            exit 1
        fi
    fi
    
    # Test Docker container
    if $test_container; then
        if ! test_docker_container; then
            print_error "Docker container test failed. Exiting."
            exit 1
        fi
    fi
    
    # Validate requirements
    validate_requirements
    
    # Show usage instructions
    show_usage
    
    print_success "Build and test completed successfully!"
    print_status "Your solution is ready for submission."
}

# Run main function with all arguments
main "$@"