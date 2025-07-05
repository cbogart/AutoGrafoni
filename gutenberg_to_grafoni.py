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
        search_url = f"{self.base_url}/ebooks/search/?query={title.replace(' ', '+')}"
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
    
    def extract_title(self, text):
        """Extract book title from the downloaded text"""
        # Look for common title patterns in Project Gutenberg books
        title_patterns = [
            r'Title:\s*([^\n\r]+)',
            r'The Project Gutenberg eBook of\s+([^\n\r,]+)',
            r'Title\s*:\s*([^\n\r]+)',
            r'Title\s*=\s*([^\n\r]+)',
            # Look for title after illustration and before "by Author"
            r'\[Illustration\]\s*\n+\s*([^\n\r]+?)\s*\n+\s*by\s+',
            # Look for standalone title lines (not followed by "by" immediately)
            r'\n\s*([A-Z][^\n\r]+?)\s*\n\s*(?=by\s+[A-Z])',
            # Look for title after START OF PROJECT GUTENBERG EBOOK
            r'\*\*\* START OF THE PROJECT GUTENBERG EBOOK \d+ \*\*\*\s*\n+\s*\[Illustration\]\s*\n+\s*([^\n\r]+?)\s*\n',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                title = match.group(1).strip()
                # Clean up the title - keep apostrophes and basic punctuation
                title = re.sub(r'[^\w\s\-.,!?\'"()]', '', title)
                title = re.sub(r'\s+', ' ', title).strip()
                if title and len(title) > 3:  # Ensure we have a reasonable title
                    return title
        
        return None


class GrafoniConverter:
    """Converts text to Grafoni script"""
    
    def __init__(self):
        self.page_height = 1800  # Height for each SVG page
        self.wrap_width = 260   # Wrap width for text
        self.paragraph_spacing = 2  # Space between paragraphs
    
    def convert_text(self, text, max_pages=1000):
        """Convert text to Grafoni pages with paragraph-based processing"""
        # Clean the text
        text = self._clean_text(text)
        
        # Split text into paragraphs
        
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        
        # Convert paragraphs to Grafoni pages
        grafoni_pages = []
        current_page = []
        current_page_height = 0
        page_count = 0
        
        try:
            for paragraph in paragraphs:
                if page_count >= max_pages:
                    break
                
                # Calculate remaining space on current page
                remaining_height = self.page_height - current_page_height
                
                # Convert paragraph to SVG(s)
                svg_list = grafoni_utils.to_svg_no_display(
                    paragraph, 
                    wrap=self.wrap_width, 
                    page_height=self.page_height,
                    remaining_page_height=remaining_height
                )
                
                # Add SVGs to current page or start new page
                for svg in svg_list:
                    # Check if this SVG fits on current page
                    print(f"Adding {paragraph[:50]} to current page")
                    if current_page_height + svg.height + self.paragraph_spacing <= self.page_height:
                        # Add to current page
                        current_page.append({
                            'text': paragraph[:50] + "..." if len(paragraph) > 50 else paragraph,
                            'svg': svg
                        })
                        current_page_height += svg.height + self.paragraph_spacing
                    else:
                        print(f"Starting new page with {paragraph[:50]}")
                        # Start new page
                        if current_page:
                            grafoni_pages.append(current_page)
                            page_count += 1
                            if page_count >= max_pages:
                                break
                        
                        # Start fresh page with this SVG
                        current_page = [{
                            'text': paragraph[:50] + "..." if len(paragraph) > 50 else paragraph,
                            'svg': svg
                        }]
                        current_page_height = svg.height + self.paragraph_spacing
                
        except Exception as e:
            print(f"Error converting text: {e}")
            return []
        
        # Add the last page if it has content
        if current_page and page_count < max_pages:
            grafoni_pages.append(current_page)
        
        return grafoni_pages
    
    def _clean_text(self, text):
        """Clean and prepare text for conversion"""
        # Remove Project Gutenberg header/footer more carefully
        text = re.sub(r'\*\*\* START OF THE PROJECT GUTENBERG EBOOK .*? \*\*\*', '', text, flags=re.DOTALL)
        text = re.sub(r'\*\*\* START OF THIS PROJECT GUTENBERG EBOOK .*? \*\*\*', '', text, flags=re.DOTALL)
        text = re.sub(r'\*\*\* END OF THE PROJECT GUTENBERG EBOOK .*? \*\*\*', '', text, flags=re.DOTALL)
        
        # Remove extra whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Keep only basic ASCII characters that Grafoni supports
        text = re.sub(r'[^a-zA-Z0-9\s.,!?;:\'\"()-]', ' ', text)
        
        # Clean up extra spaces
        text = re.sub(r'[ \t]+', ' ', text)
        
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
        self.between_paragraph_space = 2
        self.use_svg_embedding = True  # Try SVG embedding first, fall back to PNG if needed
        self.compression_level = 'high'  # Default compression level
    
    def set_compression(self, level):
        """Set the compression level for PDF generation"""
        self.compression_level = level
        if level == 'low':
            self.use_svg_embedding = False  # Skip SVG embedding for faster generation
    
    def generate_pdf(self, grafoni_pages, output_filename, book_title="Unknown Book"):
        """Generate PDF from Grafoni pages with compression"""
        # Ensure output directory exists
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create canvas with compression settings
        c = canvas.Canvas(str(output_path), pagesize=A4)
        
        for page_num, page in enumerate(grafoni_pages):
            print(f"Generating page {page_num + 1}/{len(grafoni_pages)}")
            
            # Add page number
            c.setFont("Helvetica", 10)
            c.drawString(self.page_width - 100, 30, f"Page {page_num + 1}")
            
            # Add title on first page
            if page_num == 0:
                c.setFont("Helvetica-Bold", 16)
                c.drawString(self.margin, self.page_height - 50, f"{book_title} - Grafoni Script")
                c.setFont("Helvetica", 12)
                c.drawString(self.margin, self.page_height - 70, "Converted from Project Gutenberg")
            
            # Each page can contain multiple SVGs (paragraphs)
            y_position = self.page_height - 100 if page_num == 0 else self.page_height - 50
            
            for item in page:
                try:
                    svg_data = item['svg'].as_svg()
                    
                    # Use SVG dimensions directly - no scaling
                    svg_width = item['svg'].width / 2.5
                    svg_height = item['svg'].height / 2.5
                    
                    # Check if we need a new page
                    if y_position - svg_height < 50:
                        c.showPage()
                        y_position = self.page_height - 50
                        
                        # Add page number
                        c.setFont("Helvetica", 10)
                        c.drawString(self.page_width - 100, 30, f"Page {page_num + 1}")
                    
                    # Position SVG on the page
                    x_position = self.margin
                    
                    # Use PNG embedding (more efficient for line drawings)
                    self._embed_png(c, svg_data, x_position, y_position - svg_height, 
                                  svg_width, svg_height)
                    
                    y_position -= svg_height + self.between_paragraph_space
                    
                except Exception as e:
                    print(f"Error processing SVG: {e}")
                    continue
            
            c.showPage()
        
        # Save with compression
        c.save()
        
        # Apply additional PDF compression if possible
        self._compress_pdf(output_path)
        
        print(f"PDF saved as: {output_path}")
    
    def _compress_pdf(self, pdf_path):
        """Apply additional compression to the PDF if possible"""
        if self.compression_level in ['low', 'no']:
            print(f"Skipping additional compression ({self.compression_level} compression mode)")
            return
            
        try:
            # Try to use Ghostscript for additional compression if available
            import subprocess
            compressed_path = pdf_path.with_suffix('.compressed.pdf')
            
            # Choose compression settings based on level
            if self.compression_level == 'high':
                pdf_settings = '/printer'  # Highest quality, good compression
            else:  # medium
                pdf_settings = '/ebook'    # Good balance of size and quality
            
            # Ghostscript command for compression
            gs_command = [
                'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                f'-dPDFSETTINGS={pdf_settings}',
                '-dNOPAUSE', '-dQUIET', '-dBATCH',
                f'-sOutputFile={compressed_path}',
                str(pdf_path)
            ]
            
            result = subprocess.run(gs_command, capture_output=True, text=True)
            
            if result.returncode == 0 and compressed_path.exists():
                # Replace original with compressed version
                pdf_path.unlink()
                compressed_path.rename(pdf_path)
                print(f"Applied additional compression to PDF ({self.compression_level} level)")
            else:
                print(f"Ghostscript compression not available, using standard PDF")
                
        except (ImportError, FileNotFoundError, subprocess.SubprocessError):
            # Ghostscript not available, use standard PDF
            print(f"Ghostscript not available, using standard PDF compression")
        except Exception as e:
            print(f"Compression failed: {e}, using standard PDF")
    
    def _embed_svg(self, canvas, svg_data, x, y, width, height):
        """Embed SVG directly into PDF for better compression"""
        try:
            # For now, fall back to PNG since direct SVG embedding in reportlab is complex
            # This is a placeholder for future implementation
            raise NotImplementedError("Direct SVG embedding not yet implemented")
        except NotImplementedError:
            # Fall back to PNG method
            self._embed_png(canvas, svg_data, x, y, width, height)
    
    def _embed_png(self, canvas, svg_data, x, y, width, height):
        """Convert SVG to PNG and embed with optimized compression"""
        # Choose DPI based on compression level
        if self.compression_level == 'no':
            dpi = 150  # High quality for no compression
        elif self.compression_level == 'high':
            dpi = 72  # Standard screen DPI
        elif self.compression_level == 'medium':
            dpi = 96  # Slightly higher quality
        elif self.compression_level == 'low':
            dpi = 120  # Higher quality for low compression mode
        else:
            raise ValueError(f"Invalid compression level: {self.compression_level}")
        
        # Convert SVG to PNG using cairosvg
        png_data = cairosvg.svg2png(
            bytestring=svg_data.encode('utf-8'),
            background_color='white',
            dpi=dpi
        )
        
        if not png_data:
            raise ValueError("Failed to convert SVG to PNG")
        
        # For "no compression" mode, use original high-quality approach
        if self.compression_level == 'no':
            # Create a temporary file for the high-quality PNG
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_file.write(png_data)
                tmp_file_path = tmp_file.name
            
            try:
                # Draw image without additional compression
                canvas.drawImage(tmp_file_path, x, y, width=width, height=height, mask='auto')
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
            return
        
        # For compression modes, optimize PNG using PIL
        from PIL import Image
        import io
        
        png_image = Image.open(io.BytesIO(png_data))
        
        # Convert to indexed color (1-bit) for maximum compression
        if png_image.mode != 'P':
            # Convert to grayscale first, then to indexed
            if png_image.mode in ('RGBA', 'LA'):
                # Create white background
                background = Image.new('RGB', png_image.size, (255, 255, 255))
                background.paste(png_image, mask=png_image.split()[-1] if png_image.mode == 'RGBA' else None)
                png_image = background
            
            # Convert to grayscale, then to 1-bit indexed
            png_image = png_image.convert('L').convert('P', palette=Image.Palette.ADAPTIVE, colors=8)
        
        # Save optimized PNG
        optimized_buffer = io.BytesIO()
        png_image.save(optimized_buffer, format='PNG', optimize=True, compress_level=9)
        optimized_png_data = optimized_buffer.getvalue()
        
        # Create a temporary file for the optimized PNG
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(optimized_png_data)
            tmp_file_path = tmp_file.name
        
        try:
            # Draw image with compression
            canvas.drawImage(tmp_file_path, x, y, width=width, height=height, mask='auto')
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
    



def main():
    parser = argparse.ArgumentParser(description='Convert Project Gutenberg books to Grafoni PDF')
    parser.add_argument('title', nargs='?', help='Book title to search for')
    parser.add_argument('--book-id', type=int, help='Specific Project Gutenberg book ID')
    parser.add_argument('--output', '-o', default='output/grafoni_book.pdf', help='Output PDF filename')
    parser.add_argument('--max-pages', type=int, default=50000, help='Maximum number of pages to generate')
    parser.add_argument('--compression', choices=['no', 'high', 'medium', 'low'], default='high', 
                       help='PDF compression level (no=high quality, high=smaller file, low=faster generation)')
    
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
    
    # Extract book title
    book_title = args.title
    if not book_title:
        extracted_title = downloader.extract_title(text)
        if extracted_title:
            book_title = extracted_title
            print(f"Extracted title: {book_title}")
        else:
            book_title = f"Book {book_id}"
            print(f"Could not extract title, using: {book_title}")
    
    # Convert to Grafoni
    print("Converting to Grafoni script...")
    grafoni_pages = converter.convert_text(text, max_pages=args.max_pages)
    
    print(f"Generated {len(grafoni_pages)} pages of Grafoni script.")
    
    # Generate PDF
    print("Generating PDF...")
    pdf_generator.set_compression(args.compression)
    pdf_generator.generate_pdf(grafoni_pages, args.output, book_title)
    
    print("Conversion complete!")


if __name__ == "__main__":
    main() 