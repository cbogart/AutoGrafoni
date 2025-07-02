# Project Knowledge: Gutenberg to Grafoni PDF Converter

This document captures the implicit knowledge, decisions, and technical specifications developed during the creation of the Gutenberg to Grafoni PDF converter.

## Project Overview

**Goal**: Create a script that downloads books from Project Gutenberg, converts them to Grafoni phonetic script, and generates readable PDFs for practice reading.

**Original Project**: Based on Brent Werness's AutoGrafoni (https://github.com/Koloth/AutoGrafoni)

**Current Status**: ✅ **FULLY FUNCTIONAL** - Successfully downloads books, converts to Grafoni, and generates multi-page PDFs

## Key Technical Decisions

### 1. Testing Framework: pytest
- **Decision**: Chose pytest over unittest
- **Reasoning**: 
  - More popular and modern
  - Less boilerplate code
  - Better auto-discovery
  - Rich assertion library
- **Implementation**: Converted all test scripts to pytest format with proper assertions

### 2. Text Wrapping Implementation
- **Problem**: Long sentences were being stretched horizontally instead of wrapping naturally
- **Solution**: Implemented proper text wrapping with proportional heights
- **Key Specifications**:
  - Wrap width: 260 (optimized for PDF layout)
  - Natural word boundaries for wrapping
  - Proportional heights (longer sentences = taller images)
  - No horizontal scaling - preserve aspect ratios
  - Line spacing: 20 units
- **Status**: ✅ **WORKING** - Text wraps naturally with proper proportions

### 3. File Organization
- **Decision**: Created organized output directory structure
- **Implementation**:
  - `output/` directory for all generated files
  - `gutenberg_cache/` for downloaded books
  - Proper `.gitignore` to exclude cache and generated files
  - Clean separation of source code vs. generated content
- **Status**: ✅ **IMPLEMENTED** - Clean, organized file structure

### 4. SVG Generation Architecture
- **Problem**: Original code had IPython dependencies
- **Solution**: Created `grafoni_utils.py` with standalone SVG generation
- **Key Functions**:
  - `to_svg_no_display()` - generates SVG without display dependencies
  - Proper scaling and shear transformations
  - White background for PNG conversion
- **Status**: ✅ **WORKING** - Standalone SVG generation without IPython dependencies

### 5. PDF Generation
- **Requirements**: Multi-page PDFs with proper formatting
- **Implementation**:
  - Uses ReportLab for PDF generation
  - CairoSVG for SVG-to-PNG conversion
  - White background to avoid black blocks
  - Consistent image width in PDF (maintains aspect ratios)
  - Page numbers and titles
  - Left-aligned text (margin-based positioning)
- **Status**: ✅ **WORKING** - Generates clean, readable PDFs

## Problems Solved

### 1. Text Cleaning Issues
- **Problem**: Aggressive regex was removing all content from Project Gutenberg books
- **Solution**: Improved regex patterns that specifically target Gutenberg headers/footers
- **Implementation**: More precise patterns that preserve actual book content
- **Status**: ✅ **FIXED** - Successfully extracts book content while removing headers

### 2. SVG Scaling and Wrapping
- **Problem**: SVGs were being stretched horizontally, making text unreadable
- **Root Cause**: Dynamic horizontal scaling was overriding natural text wrapping
- **Solution**: Removed horizontal scaling, let text wrap naturally with proportional heights
- **Result**: Long sentences now have taller images, maintaining readability
- **Status**: ✅ **FIXED** - Natural text wrapping with proper proportions

### 3. PDF Layout Issues
- **Problem**: Black blocks appearing in PDF due to transparent backgrounds
- **Solution**: Set white background in SVG-to-PNG conversion
- **Status**: ✅ **FIXED** - Clean white backgrounds in PDF

### 4. Text Positioning in PDF
- **Problem**: SVGs were being centered, causing layout issues
- **Solution**: Left-aligned positioning using margin-based layout
- **Status**: ✅ **FIXED** - Consistent left-aligned text layout

### 5. Book Title Extraction
- **Problem**: PDFs showed "Book {ID}" instead of actual book titles
- **Solution**: Added automatic title extraction from downloaded text
- **Implementation**: Multiple regex patterns to find titles in Project Gutenberg format
- **Result**: PDFs now show actual book titles (e.g., "Alices Adventures in Wonderland")
- **Status**: ✅ **FIXED** - Automatic title extraction working for standard formats

### 6. Git Workflow Setup
- **Problem**: Need to contribute to upstream repo without write access
- **Solution**: Proper fork workflow setup
- **Implementation**:
  - Forked original repo to personal GitHub
  - Set up remotes: `origin` (fork), `upstream` (original)
  - Feature branch workflow for development
  - Clean commit history and proper `.gitignore`
- **Status**: ✅ **IMPLEMENTED** - Proper development workflow

### 7. Dependencies and Environment
- **Problem**: Need to manage Python dependencies properly
- **Solution**: Created `requirements.txt` with all necessary packages
- **Dependencies**:
  - `drawsvg`: SVG generation
  - `eng_to_ipa`: Phonetic conversion
  - `requests`: Book downloading
  - `reportlab`: PDF generation
  - `cairosvg`: SVG to PNG conversion
  - `pytest`: Testing framework
- **Status**: ✅ **IMPLEMENTED** - All dependencies properly managed

## Technical Specifications

### Text Processing
- **Paragraph Splitting**: Split on `\n\n` (double newlines) for natural paragraph boundaries
- **Text Cleaning**: Remove Gutenberg headers/footers, normalize whitespace
- **Character Filtering**: Keep alphanumeric, punctuation, and basic symbols
- **Minimum Content**: Filters out empty paragraphs and very short content
- **Title Extraction**: Multiple regex patterns to find book titles in Project Gutenberg format

### SVG Generation
- **Wrap Width**: 260 units (optimized for PDF layout)
- **Line Spacing**: 20 units
- **Vertical Scale**: 0.5
- **Shear Value**: -1/√3 (maintains proper character angles)
- **Stroke Width**: 1.0/3 (thin, readable lines)
- **Page Height**: 2000 units (allows for tall content)

### PDF Layout
- **Page Size**: A4
- **Margins**: 50 units
- **Image Scaling**: 1/2.5 (maintains aspect ratio)
- **Left Alignment**: Consistent margin-based positioning
- **Page Numbers**: Bottom right, 10pt Helvetica
- **Title**: Book title + "Grafoni Script" on first page
- **Paragraph Spacing**: 10 units between paragraphs

### Performance Optimizations
- **Book Caching**: Downloaded books stored in `gutenberg_cache/`
- **Page Limiting**: Early termination based on max_pages parameter (default: 1000)
- **Efficient Processing**: Process paragraphs in batches
- **Memory Management**: Clean up temporary files after PNG conversion

## Current Capabilities

### ✅ Working Features
1. **Book Download**: Successfully downloads books from Project Gutenberg by ID or title search
2. **Text Processing**: Cleans and prepares text for Grafoni conversion
3. **Grafoni Conversion**: Converts text to phonetic Grafoni script
4. **PDF Generation**: Creates multi-page PDFs with proper formatting
5. **Text Wrapping**: Natural text wrapping with proportional heights
6. **Caching**: Caches downloaded books to avoid re-downloading
7. **Error Handling**: Robust error handling for network issues and malformed content
8. **Title Extraction**: Automatically extracts book titles from downloaded text for PDF headers

### 📊 Performance Metrics
- **Test Results**: Successfully converted "Alice's Adventures in Wonderland" (Book ID 11)
- **Output**: 28 pages of Grafoni script in 10.6 MB PDF
- **Processing Time**: Efficient processing with proper memory management
- **Text Quality**: Clean conversion with proper character filtering
- **Title Extraction**: Successfully extracts "Alices Adventures in Wonderland" from book content

## Known Issues and Future Work

### Current Limitations
1. **Search Functionality**: Project Gutenberg search URLs may change, requiring updates
2. **Character Support**: Limited to ASCII characters (Grafoni limitation)
3. **Large Books**: Very large books may require significant processing time
4. **Punctuation Handling**: Some punctuation may not convert perfectly to Grafoni

### Future Improvements
1. **Output Directory**: Create dedicated output folder for PDFs (as requested)
2. **Alternative Formats**: Consider formats other than PDF (e.g., for Kindle)
3. **Punctuation Optimization**: Improve punctuation handling in Grafoni conversion
4. **Performance**: Optimize for very large books
5. **Error Handling**: More robust error handling for malformed books
6. **UI Improvements**: Better user interface for book selection
7. **Title Extraction Enhancement**: Improve title extraction for edge cases and different book formats

## Development Workflow

### Branch Strategy
- `main`: Stable, working code
- `feature/*`: New features and improvements
- Clean merge workflow with proper PR process

### Testing Strategy
- Unit tests for all major components
- Integration tests for end-to-end workflow
- Skip tests that require cached data (with proper decorators)
- Focus on assertions rather than print statements

### Code Organization
- `gutenberg_to_grafoni.py`: Main application logic
- `grafoni_utils.py`: Utility functions for SVG generation
- `test_*.py`: Comprehensive test suite
- `requirements.txt`: Dependency management
- `README.md`: User documentation
- `PROJECT_KNOWLEDGE.md`: This file - technical documentation

## Usage Examples

### Basic Usage
```bash
# Download by book ID (automatically extracts title)
python gutenberg_to_grafoni.py --book-id 11

# Search by title
python gutenberg_to_grafoni.py "Alice in Wonderland"

# Custom output file
python gutenberg_to_grafoni.py --book-id 11 --output my_book.pdf

# Limit pages
python gutenberg_to_grafoni.py --book-id 11 --max-pages 10
```

### Successful Test Results
- **Book**: Alice's Adventures in Wonderland (ID: 11)
- **Input**: 144,696 characters of text
- **Output**: 28 pages of Grafoni script
- **File Size**: 10.6 MB PDF
- **Quality**: Clean, readable Grafoni script with proper text wrapping
- **Title Extraction**: Successfully extracts "Alices Adventures in Wonderland" from book content
- **PDF Header**: Shows actual book title instead of "Book 11"

## Lessons Learned

### AI-Assisted Development
- **Strength**: AI can generate significant amounts of working code quickly
- **Success**: Successfully implemented complex text processing and PDF generation
- **Challenge**: Requires careful testing and iteration for optimal results
- **Recommendation**: Use AI for initial implementation, then test and refine

### Open Source Contribution
- Proper fork workflow is essential for contributing to projects without write access
- Clean commit history and proper file organization make PRs more likely to be accepted
- Comprehensive testing and documentation increase project value

### Technical Architecture
- Separation of concerns (utilities vs. main logic) improves maintainability
- Proper file organization and `.gitignore` prevent repository bloat
- Testing framework choice affects development velocity and code quality

## References

- **Original Project**: https://github.com/Koloth/AutoGrafoni
- **Grafoni Reference**: Hitlofi, Iven (1913). "Complete Elementary Instructor in Grafoni: A New Phonography; A World-Shorthand"
- **Testing Framework**: pytest (https://docs.pytest.org/)
- **PDF Generation**: ReportLab (https://www.reportlab.com/)
- **SVG Processing**: CairoSVG (https://cairosvg.org/)
- **Project Gutenberg**: https://www.gutenberg.org/ 