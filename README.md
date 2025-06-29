# Gutenberg to Grafoni Converter

This script downloads books from Project Gutenberg, converts them to Grafoni script, and generates PDFs of the converted text.

## Features

- Downloads books from Project Gutenberg by title or book ID
- Converts English text to Grafoni phonetic script
- Generates multi-page PDFs with proper formatting
- Caches downloaded books for faster subsequent runs
- Supports various Project Gutenberg text formats
- Natural text wrapping with proportional heights
- Organized output directory structure

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have the existing `grafoni.py` file in the same directory.

## Usage

### Basic Usage

Search for a book by title:
```bash
python gutenberg_to_grafoni.py "Pride and Prejudice"
```

Use a specific Project Gutenberg book ID:
```bash
python gutenberg_to_grafoni.py --book-id 1342
```

### Advanced Options

```bash
python gutenberg_to_grafoni.py "Alice in Wonderland" --output output/alice_grafoni.pdf --max-pages 20
```

### Command Line Arguments

- `title`: Book title to search for (optional if using --book-id)
- `--book-id`: Specific Project Gutenberg book ID
- `--output, -o`: Output PDF filename (default: output/grafoni_book.pdf)
- `--max-pages`: Maximum number of pages to generate (default: 50)

## Examples

### Convert "The Great Gatsby"
```bash
python gutenberg_to_grafoni.py "The Great Gatsby"
```

### Convert "1984" with custom output
```bash
python gutenberg_to_grafoni.py "1984" --output output/1984_grafoni.pdf --max-pages 30
```

### Convert a specific book by ID
```bash
python gutenberg_to_grafoni.py --book-id 64317 --output output/moby_dick_grafoni.pdf
```

## How It Works

1. **Book Search**: The script searches Project Gutenberg for books matching the title
2. **Book Download**: Downloads the book text in UTF-8 format
3. **Text Processing**: Cleans the text and splits it into sentences
4. **Grafoni Conversion**: Converts each sentence to Grafoni phonetic script with natural wrapping
5. **PDF Generation**: Creates a PDF with the Grafoni text, properly formatted

## File Structure

- `gutenberg_to_grafoni.py`: Main conversion script
- `grafoni.py`: Existing Grafoni conversion library
- `grafoni_utils.py`: Utility functions for Grafoni conversion
- `requirements.txt`: Python dependencies
- `gutenberg_cache/`: Directory for caching downloaded books
- `output/`: Directory containing all generated PDFs and test files

## Text Wrapping

The script uses intelligent text wrapping that:
- Wraps text at natural word boundaries
- Maintains proportional heights (longer sentences = taller images)
- Preserves aspect ratios without horizontal scaling
- Uses consistent line spacing for readability

## Troubleshooting

### Common Issues

1. **Book not found**: Try using a more specific title or use the book ID directly
2. **Conversion errors**: Some books may have formatting issues that cause conversion problems
3. **PDF generation fails**: Make sure all dependencies are installed correctly

### Dependencies

The script requires:
- `drawsvg`: For SVG generation
- `eng_to_ipa`: For phonetic conversion
- `requests`: For downloading books
- `reportlab`: For PDF generation
- `cairosvg`: For SVG to PNG conversion

## Notes

- The script caches downloaded books in the `gutenberg_cache/` directory
- All generated PDFs are saved to the `output/` directory
- Large books may take a while to process
- The quality of conversion depends on the text quality from Project Gutenberg
- Some books may have formatting issues that affect the conversion
- Text wrapping is optimized for readability with natural line breaks

## License

This script is provided as-is for educational and personal use. 