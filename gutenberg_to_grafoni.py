#!/usr/bin/env python3
"""
Gutenberg to Grafoni Converter

This script downloads a Project Gutenberg book, converts it to Grafoni script,
and generates a PDF of the converted text.

Usage:
    python gutenberg_to_grafoni.py "Book Title"
    python gutenberg_to_grafoni.py --book-id 12345
"""

import argparse
import requests
import re
import os
import sys
from pathlib import Path
import time
from urllib.parse import urljoin
import drawsvg as draw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import cairosvg
import io

# Import the existing grafoni module and our utility
import grafoni
import grafoni_utils


class GutenbergDownloader:
    """Downloads books from Project Gutenberg"""
    
    def __init__(self):
        self.base_url = "https://www.gutenberg.org"
        self.cache_dir = Path("gutenberg_cache")
        self.cache_dir.mkdir(exist_ok=True)
    
    def search_book(self, title):
        """Search for a book by title"""
        search_url = f"{self.base_url}/search/?query={title.replace(' ', '+')}"
        print(f"Searching for: {title}")
        print(f"Search URL: {search_url}")
        
        try:
            response = requests.get(search_url, timeout=30)
            response.raise_for_status()
            
            # Look for book links in the search results
            book_pattern = r'href="/ebooks/(\d+)"'
            book_ids = re.findall(book_pattern, response.text)
            
            if not book_ids:
                print("No books found matching the title.")
                return None
            
            print(f"Found {len(book_ids)} potential matches:")
            for i, book_id in enumerate(book_ids[:10]):  # Show first 10
                print(f"  {i+1}. Book ID: {book_id}")
            
            if len(book_ids) == 1:
                return book_ids[0]
            else:
                choice = input(f"Enter the number of the book you want (1-{min(len(book_ids), 10)}): ")
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(book_ids):
                        return book_ids[index]
                except ValueError:
                    pass
                print("Invalid choice. Using first book.")
                return book_ids[0]
                
        except requests.RequestException as e:
            print(f"Error searching for book: {e}")
            return None
    
    def download_book(self, book_id):
        """Download a book by its ID"""
        cache_file = self.cache_dir / f"{book_id}.txt"
        
        if cache_file.exists():
            print(f"Loading cached book {book_id}...")
            return cache_file.read_text(encoding='utf-8')
        
        # Try different download methods
        download_methods = [
            self._download_utf8,
            self._download_plain_text,
            self._download_html
        ]
        
        for method in download_methods:
            try:
                text = method(book_id)
                if text and len(text) > 1000:  # Ensure we got substantial content
                    print(f"Successfully downloaded book {book_id} using {method.__name__}")
                    cache_file.write_text(text, encoding='utf-8')
                    return text
            except Exception as e:
                print(f"Method {method.__name__} failed: {e}")
                continue
        
        print(f"Failed to download book {book_id}")
        return None
    
    def _download_utf8(self, book_id):
        """Download UTF-8 version"""
        url = f"{self.base_url}/files/{book_id}/{book_id}-0.txt"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    
    def _download_plain_text(self, book_id):
        """Download plain text version"""
        url = f"{self.base_url}/files/{book_id}/{book_id}.txt"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    
    def _download_html(self, book_id):
        """Download HTML version and extract text"""
        url = f"{self.base_url}/files/{book_id}/{book_id}-h/{book_id}-h.htm"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Simple HTML to text conversion
        text = response.text
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class GrafoniConverter:
    """Converts text to Grafoni script"""
    
    def __init__(self):
        self.max_chars_per_line = 80
        self.max_lines_per_page = 40
        self.line_height = 30
        self.page_width = 800
        self.page_height = 1200
        self.wrap_width = 300  # Smaller wrap width for more natural wrapping
    
    def convert_text(self, text, max_pages=50):
        """Convert text to Grafoni and split into pages"""
        # Clean the text
        text = self._clean_text(text)
        
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        # Estimate how many sentences we need based on max_pages
        sentences_per_page = self.max_lines_per_page // 2  # Rough estimate
        max_sentences_needed = max_pages * sentences_per_page
        
        # Limit sentences early to avoid unnecessary conversion
        if len(sentences) > max_sentences_needed:
            print(f"Limiting to {max_sentences_needed} sentences (out of {len(sentences)} total) for efficiency")
            sentences = sentences[:max_sentences_needed]
        
        # Convert sentences to Grafoni
        grafoni_pages = []
        current_page = []
        current_line_count = 0
        
        for sentence in sentences:
            if len(sentence.strip()) < 10:  # Skip very short sentences
                continue
                
            try:
                # Convert to Grafoni using our utility function with consistent wrap width
                grafoni_svg = grafoni_utils.to_svg_no_display(sentence, wrap=self.wrap_width, line_space=self.line_height)
                
                # Check if adding this would exceed page limit
                estimated_lines = len(sentence) // self.max_chars_per_line + 1
                if current_line_count + estimated_lines > self.max_lines_per_page:
                    if current_page:
                        grafoni_pages.append(current_page)
                        current_page = []
                        current_line_count = 0
                        
                        # Stop if we've reached max pages
                        if len(grafoni_pages) >= max_pages:
                            break
                
                current_page.append({
                    'text': sentence,
                    'svg': grafoni_svg
                })
                current_line_count += estimated_lines
                
            except Exception as e:
                print(f"Error converting sentence: {e}")
                print(f"Sentence: {sentence[:100]}...")
                continue
        
        # Add the last page if it has content and we haven't reached max pages
        if current_page and len(grafoni_pages) < max_pages:
            grafoni_pages.append(current_page)
        
        return grafoni_pages
    
    def _clean_text(self, text):
        """Clean and prepare text for conversion"""
        # Remove Project Gutenberg header/footer more carefully
        text = re.sub(r'\*\*\* START OF THE PROJECT GUTENBERG EBOOK .*? \*\*\*', '', text, flags=re.DOTALL)
        text = re.sub(r'\*\*\* START OF THIS PROJECT GUTENBERG EBOOK .*? \*\*\*', '', text, flags=re.DOTALL)
        text = re.sub(r'\*\*\* END OF THE PROJECT GUTENBERG EBOOK .*? \*\*\*', '', text, flags=re.DOTALL)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove some special characters but keep more content
        text = re.sub(r'[^\w\s.,!?;:\'\"()-]', ' ', text)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _split_into_sentences(self, text):
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]


class PDFGenerator:
    """Generates PDF from Grafoni SVG pages"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 50
    
    def generate_pdf(self, grafoni_pages, output_filename):
        """Generate PDF from Grafoni pages"""
        # Ensure output directory exists
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        c = canvas.Canvas(str(output_path), pagesize=A4)
        
        for page_num, page in enumerate(grafoni_pages):
            print(f"Generating page {page_num + 1}/{len(grafoni_pages)}")
            
            # Add page number
            c.setFont("Helvetica", 10)
            c.drawString(self.page_width - 100, 30, f"Page {page_num + 1}")
            
            # Add title on first page
            if page_num == 0:
                c.setFont("Helvetica-Bold", 16)
                c.drawString(self.margin, self.page_height - 50, "Grafoni Script")
                c.setFont("Helvetica", 12)
                c.drawString(self.margin, self.page_height - 70, "Converted from Project Gutenberg")
            
            # Convert SVG to PDF
            y_position = self.page_height - 100 if page_num == 0 else self.page_height - 50
            
            for item in page:
                try:
                    svg_data = item['svg'].as_svg()
                    
                    # Convert SVG to PNG using cairosvg with white background
                    png_data = cairosvg.svg2png(
                        bytestring=svg_data.encode('utf-8'),
                        background_color='white'
                    )
                    
                    # Create a temporary file for the PNG
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        tmp_file.write(png_data)
                        tmp_file_path = tmp_file.name
                    
                    # Calculate image dimensions based on SVG aspect ratio
                    svg_width = item['svg'].width
                    svg_height = item['svg'].height
                    
                    # Use consistent width for all SVGs in the PDF, maintain aspect ratio
                    img_width = min(700, self.page_width - 2 * self.margin)
                    img_height = (svg_height / svg_width) * img_width
                    
                    # Ensure minimum height for readability
                    img_height = max(img_height, 30)
                    
                    if y_position - img_height < 50:  # Check if we need a new page
                        c.showPage()
                        y_position = self.page_height - 50
                        
                        # Add page number
                        c.setFont("Helvetica", 10)
                        c.drawString(self.page_width - 100, 30, f"Page {page_num + 1}")
                    
                    c.drawImage(tmp_file_path, self.margin, y_position - img_height, 
                              width=img_width, height=img_height)
                    
                    y_position -= img_height + 20
                    
                    # Clean up temporary file
                    os.unlink(tmp_file_path)
                    
                except Exception as e:
                    print(f"Error processing SVG: {e}")
                    continue
            
            c.showPage()
        
        c.save()
        print(f"PDF saved as: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Convert Project Gutenberg books to Grafoni PDF')
    parser.add_argument('title', nargs='?', help='Book title to search for')
    parser.add_argument('--book-id', type=int, help='Specific Project Gutenberg book ID')
    parser.add_argument('--output', '-o', default='output/grafoni_book.pdf', help='Output PDF filename')
    parser.add_argument('--max-pages', type=int, default=50, help='Maximum number of pages to generate')
    
    args = parser.parse_args()
    
    if not args.title and not args.book_id:
        print("Please provide either a book title or a book ID.")
        print("Example: python gutenberg_to_grafoni.py 'Pride and Prejudice'")
        print("Example: python gutenberg_to_grafoni.py --book-id 1342")
        sys.exit(1)
    
    # Initialize components
    downloader = GutenbergDownloader()
    converter = GrafoniConverter()
    pdf_generator = PDFGenerator()
    
    # Get book ID
    book_id = args.book_id
    if not book_id and args.title:
        book_id = downloader.search_book(args.title)
        if not book_id:
            print("Could not find the book.")
            sys.exit(1)
    
    # Download book
    print(f"Downloading book {book_id}...")
    text = downloader.download_book(book_id)
    if not text:
        print("Failed to download the book.")
        sys.exit(1)
    
    print(f"Downloaded {len(text)} characters of text.")
    
    # Convert to Grafoni
    print("Converting to Grafoni script...")
    grafoni_pages = converter.convert_text(text, max_pages=args.max_pages)
    
    print(f"Generated {len(grafoni_pages)} pages of Grafoni script.")
    
    # Generate PDF
    print("Generating PDF...")
    pdf_generator.generate_pdf(grafoni_pages, args.output)
    
    print("Conversion complete!")


if __name__ == "__main__":
    main() 