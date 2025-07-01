# Project Knowledge: Gutenberg to Grafoni PDF Converter

This document captures the implicit knowledge, decisions, and technical specifications developed during the creation of the Gutenberg to Grafoni PDF converter.

## Project Overview

**Goal**: Create a script that downloads books from Project Gutenberg, converts them to Grafoni phonetic script, and generates readable PDFs for practice reading.

**Original Project**: Based on Brent Werness's AutoGrafoni (https://github.com/Koloth/AutoGrafoni)

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
  - Wrap width: 300 (down from 800 default)
  - Natural word boundaries for wrapping
  - Proportional heights (longer sentences = taller images)
  - No horizontal scaling - preserve aspect ratios
  - Line spacing: 20 units

### 3. File Organization
- **Decision**: Created organized output directory structure
- **Implementation**:
  - `output/` directory for all generated files
  - `gutenberg_cache/` for downloaded books
  - Proper `.gitignore` to exclude cache and generated files
  - Clean separation of source code vs. generated content

### 4. SVG Generation Architecture
- **Problem**: Original code had IPython dependencies
- **Solution**: Created `grafoni_utils.py` with standalone SVG generation
- **Key Functions**:
  - `to_svg_no_display()` - generates SVG without display dependencies
  - Proper scaling and shear transformations
  - White background for PNG conversion

### 5. PDF Generation
- **Requirements**: Multi-page PDFs with proper formatting
- **Implementation**:
  - Uses ReportLab for PDF generation
  - CairoSVG for SVG-to-PNG conversion
  - White background to avoid black blocks
  - Consistent image width in PDF (700px max)
  - Maintains aspect ratios
  - Page numbers and titles

## Problems Solved

### 1. Text Cleaning Issues
- **Problem**: Aggressive regex was removing all content from Project Gutenberg books
- **Solution**: Improved regex patterns that specifically target Gutenberg headers/footers
- **Implementation**: More precise patterns that preserve actual book content

### 2. SVG Scaling and Wrapping
- **Problem**: SVGs were being stretched horizontally, making text unreadable
- **Root Cause**: Dynamic horizontal scaling was overriding natural text wrapping
- **Solution**: Removed horizontal scaling, let text wrap naturally with proportional heights
- **Result**: Long sentences now have taller images, maintaining readability

### 3. Git Workflow Setup
- **Problem**: Need to contribute to upstream repo without write access
- **Solution**: Proper fork workflow setup
- **Implementation**:
  - Forked original repo to personal GitHub
  - Set up remotes: `origin` (fork), `upstream` (original)
  - Feature branch workflow for development
  - Clean commit history and proper `.gitignore`

### 4. Dependencies and Environment
- **Problem**: Need to manage Python dependencies properly
- **Solution**: Created `requirements.txt` with all necessary packages
- **Dependencies**:
  - `drawsvg`: SVG generation
  - `eng_to_ipa`: Phonetic conversion
  - `requests`: Book downloading
  - `reportlab`: PDF generation
  - `cairosvg`: SVG to PNG conversion
  - `pytest`: Testing framework

## Technical Specifications

### Text Processing
- **Sentence Splitting**: Simple regex-based splitting on `[.!?]+`
- **Text Cleaning**: Remove Gutenberg headers/footers, normalize whitespace
- **Character Filtering**: Keep alphanumeric, punctuation, and basic symbols
- **Minimum Sentence Length**: 10 characters (filters out very short fragments)

### SVG Generation
- **Wrap Width**: 300 units (optimized for readability)
- **Line Spacing**: 20 units
- **Vertical Scale**: 0.5
- **Shear Value**: -1/√3 (maintains proper character angles)
- **Stroke Width**: 1.0/3 (thin, readable lines)

### PDF Layout
- **Page Size**: A4
- **Margins**: 50 units
- **Image Width**: 700px max (maintains aspect ratio)
- **Minimum Image Height**: 30px (ensures readability)
- **Page Numbers**: Bottom right, 10pt Helvetica
- **Title**: "Grafoni Script" on first page

### Performance Optimizations
- **Book Caching**: Downloaded books stored in `gutenberg_cache/`
- **Sentence Limiting**: Early termination based on max_pages parameter
- **Efficient Processing**: Skip very short sentences (< 10 chars)
- **Memory Management**: Process sentences in batches

## Known Issues and Future Work

### Current Limitations
1. **Text Wrapping in PDF**: Wrapping doesn't play well with PDF placement, scale gets "wonky"
2. **Punctuation Handling**: Need to review how punctuation is handled in Grafoni
3. **Font Sizing**: AI struggled with size/scaling reasoning - needs manual intervention
4. **Mental Ramp-up**: AI-generated code requires significant understanding to modify manually

### Future Improvements
1. **Better PDF Layout**: Fix text wrapping integration with PDF generation
2. **Alternative Formats**: Consider formats other than PDF (e.g., for Kindle)
3. **Punctuation Optimization**: Improve punctuation handling in Grafoni conversion
4. **Performance**: Optimize for very large books
5. **Error Handling**: More robust error handling for malformed books

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

## Lessons Learned

### AI-Assisted Development
- **Strength**: AI can generate significant amounts of working code quickly
- **Limitation**: Struggles with complex spatial reasoning (sizing, scaling, layout)
- **Challenge**: AI-generated code requires significant mental ramp-up to understand and modify
- **Recommendation**: Use AI for initial implementation, but be prepared for manual intervention on complex problems

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