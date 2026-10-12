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
    
    # Wrap width in stroke units at scale=1.0; divided by scale so enlarged
    # text still fits the page width.
    BASE_WRAP_WIDTH = 260
    # Extra stroke-unit margin so sheared glyph curves stay inside the page
    # (bounding box extends past the wrap-cursor visual_x).
    WRAP_BBOX_SLACK = 12
    # Must match PDFGenerator / grafoni_utils SVG emission.
    BASE_SVG_DIVISOR = 2.5
    SVG_RENDER_SCALE = 4
    SVG_PADDING = grafoni_utils.PADDING
    SVG_FRAME = grafoni_utils.FRAME_ABOVE + grafoni_utils.FRAME_BELOW
    V_SCALE = 0.5
    LINE_SPACE = 20
    # PDF margins matching PDFGenerator (non-title top chrome).
    PDF_TOP_MARGIN = 50
    PDF_BOTTOM_MARGIN = 50
    PDF_SIDE_MARGIN = 50
    # SVG-unit slack below a full page. Blocks are framed to a fixed height
    # (grafoni_utils.FRAME_*), so this only absorbs rounding.
    PAGE_BBOX_SLACK_SVG = 8
    # Chapter headings: drawn this much larger, with a heavier pen.
    HEADING_SIZE = 1.6
    HEADING_STROKE = 0.55
    # First-line paragraph indent, stroke units.
    PARAGRAPH_INDENT = 12
    
    def __init__(self, scale=1.0):
        if scale <= 0:
            raise ValueError("scale must be positive")
        self.scale = scale
        self.paragraph_spacing = 2  # Space between paragraphs (SVG units)
        
        page_w, page_h = A4
        top = self.PDF_TOP_MARGIN * scale
        content_height_pt = page_h - top - self.PDF_BOTTOM_MARGIN
        self.page_height = (
            content_height_pt / scale * self.BASE_SVG_DIVISOR - self.PAGE_BBOX_SLACK_SVG
        )
        
        # Wrap so that SVG width after render fits the PDF content width.
        # Cap at the historical BASE_WRAP_WIDTH/scale so scale=1 stays familiar.
        content_width_pt = page_w - 2 * self.PDF_SIDE_MARGIN
        max_svg_width = content_width_pt / scale * self.BASE_SVG_DIVISOR
        max_stroke_wrap = (
            (max_svg_width - 2 * self.SVG_RENDER_SCALE * self.SVG_PADDING)
            / self.SVG_RENDER_SCALE
        ) - self.WRAP_BBOX_SLACK
        self.wrap_width = min(self.BASE_WRAP_WIDTH / scale, max_stroke_wrap)
        
        # Minimum remaining SVG height worth filling (~one Grafoni line).
        self.min_remaining_height = self._stroke_y_to_svg(0) + self.paragraph_spacing
    
    @classmethod
    def _stroke_y_to_svg(cls, stroke_y):
        """Convert pre-v_scale stroke Y to SVG pixel height (see svgStrokes)."""
        return (cls.SVG_RENDER_SCALE * cls.V_SCALE * (stroke_y + cls.SVG_FRAME)
                + 2 * cls.SVG_RENDER_SCALE * cls.SVG_PADDING)
    
    @classmethod
    def _svg_to_stroke_y(cls, svg_height):
        """Convert SVG pixel budget to stroke-Y budget for to_svg_no_display."""
        usable = svg_height - 2 * cls.SVG_RENDER_SCALE * cls.SVG_PADDING
        return max(0, usable / (cls.SVG_RENDER_SCALE * cls.V_SCALE) - cls.SVG_FRAME)
    
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
        previous_was_chapter = False
        
        try:
            for paragraph in paragraphs:
                if page_count >= max_pages:
                    break
                
                # Calculate remaining space on current page (SVG units)
                remaining_height = self.page_height - current_page_height
                
                # Skip unusable stubs: start a fresh page rather than leaving
                # a blank gap when the next paragraph cannot fit one line.
                if remaining_height < self.min_remaining_height and current_page:
                    grafoni_pages.append(current_page)
                    page_count += 1
                    if page_count >= max_pages:
                        break
                    current_page = []
                    current_page_height = 0
                    remaining_height = self.page_height
                
                heading = self._heading(paragraph, previous_was_chapter)
                previous_was_chapter = heading is not None and heading.split()[0] in ('Chapter', 'Part', 'Book')
                size = self.HEADING_SIZE if heading else 1.0
                # Headings start on a fresh page unless they follow another heading.
                if heading and current_page and not current_page[-1].get('heading'):
                    grafoni_pages.append(current_page)
                    page_count += 1
                    if page_count >= max_pages:
                        break
                    current_page = []
                    current_page_height = 0
                    remaining_height = self.page_height

                # to_svg_no_display measures Y in stroke units; convert budget.
                # Headings are drawn `size` times larger, so give them proportionally less room.
                svg_list = grafoni_utils.to_svg_no_display(
                    heading or paragraph,
                    wrap=self.wrap_width / size,
                    page_height=self._svg_to_stroke_y(self.page_height / size),
                    remaining_page_height=self._svg_to_stroke_y(
                        (remaining_height - self.paragraph_spacing) / size),
                    line_space=self.LINE_SPACE,
                    v_scale=self.V_SCALE,
                    indent=0 if heading else self.PARAGRAPH_INDENT,
                    stroke_width=self.HEADING_STROKE if heading else 1.0 / 3,
                )
                
                # Add SVGs to current page or start new page
                for svg in svg_list:
                    item = {
                        'text': paragraph[:50] + "..." if len(paragraph) > 50 else paragraph,
                        'svg': svg,
                        'size': size,
                        'heading': bool(heading),
                    }
                    height = svg.height * size + self.paragraph_spacing
                    if current_page_height + height <= self.page_height:
                        current_page.append(item)
                        current_page_height += height
                    else:
                        # Start new page
                        if current_page:
                            grafoni_pages.append(current_page)
                            page_count += 1
                            if page_count >= max_pages:
                                break
                        current_page = [item]
                        current_page_height = height
                
        except Exception as e:
            print(f"Error converting text: {e}")
            return []
        
        # Add the last page if it has content
        if current_page and page_count < max_pages:
            grafoni_pages.append(current_page)
        
        return grafoni_pages
    
    def _clean_text(self, text):
        """Clean and prepare text for conversion"""
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Keep only the book: drop the Project Gutenberg header and the license after it.
        start = re.search(r'^\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG.*$', text, flags=re.MULTILINE)
        if start:
            text = text[start.end():]
        end = re.search(r'^(\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG|End of (the )?Project Gutenberg)',
                        text, flags=re.MULTILINE | re.IGNORECASE)
        if end:
            text = text[:end.start()]
        text = re.sub(r'\A\s*Produced by.*?\n\s*\n', '', text, flags=re.DOTALL)

        # Bracketed editorial blocks: [Illustration: ...], [Transcriber's note: ...]
        text = re.sub(r'\[(Illustration|Transcriber)[^\]]*\]', '', text, flags=re.IGNORECASE)

        # Typographic punctuation to the plain forms Grafoni draws
        text = (text.replace('\u2018', "'").replace('\u2019', "'")
                    .replace('\u201c', '"').replace('\u201d', '"')
                    .replace('\u2014', '--').replace('\u2013', '-'))

        # Keep only basic ASCII characters that Grafoni supports
        text = re.sub(r'[^a-zA-Z0-9\s.,!?;:\'\"()-]', ' ', text)

        # Collapse spaces; normalise paragraph breaks to exactly one blank line
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' *\n *', '\n', text)
        text = re.sub(r'\n{2,}', '\n\n', text)

        return text.strip()

    @staticmethod
    def _roman_to_int(numeral):
        values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        total = 0
        for i, ch in enumerate(numeral):
            v = values[ch]
            total += -v if i + 1 < len(numeral) and values[numeral[i + 1]] > v else v
        return total

    def _heading(self, paragraph, previous_was_chapter):
        """Return heading text if this paragraph is a chapter heading (or its subtitle), else None."""
        m = re.fullmatch(r'(CHAPTER|Chapter|PART|Part|BOOK|Book)\s+([IVXLCDM]+|\d+)\.?', paragraph)
        if m:
            number = m.group(2)
            if not number.isdigit():
                number = str(self._roman_to_int(number))
            return f"{m.group(1).capitalize()} {number}"
        if previous_was_chapter and len(paragraph) < 60 and '\n' not in paragraph \
                and not paragraph.rstrip().endswith(('.', '"', '?', '!')):
            return paragraph
        return None

    def _split_into_sentences(self, text):
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]


class PDFGenerator:
    """Generates PDF from Grafoni SVG pages"""
    
    # Display scale applied on top of the historical /2.5 placement factor.
    BASE_SVG_DIVISOR = 2.5
    
    def __init__(self, scale=1.0):
        if scale <= 0:
            raise ValueError("scale must be positive")
        self.page_width, self.page_height = A4
        self.margin = 50
        self.scale = scale
        self.between_paragraph_space = 2 * scale
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
        s = self.scale
        page_font = 10 * s
        title_font = 16 * s
        subtitle_font = 12 * s
        top_offset = 50 * s
        subtitle_offset = 70 * s
        first_content_offset = 100 * s
        page_num_x = self.page_width - max(100, 40 + 60 * s)
        
        for page_num, page in enumerate(grafoni_pages):
            print(f"Generating page {page_num + 1}/{len(grafoni_pages)}")
            
            # Add page number
            c.setFont("Helvetica", page_font)
            c.drawString(page_num_x, 30, f"Page {page_num + 1}")
            
            # Add title on first page
            if page_num == 0:
                title = f"{book_title} - Grafoni Script"
                # Shrink a long title to fit between the margins.
                fit = (self.page_width - 2 * self.margin) / pdfmetrics.stringWidth(title, "Helvetica-Bold", 1)
                c.setFont("Helvetica-Bold", min(title_font, fit))
                c.drawString(self.margin, self.page_height - top_offset, title)
                c.setFont("Helvetica", subtitle_font)
                c.drawString(self.margin, self.page_height - subtitle_offset, "Converted from Project Gutenberg")
            
            # Each page can contain multiple SVGs (paragraphs)
            y_position = self.page_height - first_content_offset if page_num == 0 else self.page_height - top_offset
            
            for item in page:
                try:
                    svg_data = item['svg'].as_svg()
                    
                    # Scale display size; wrap width was adjusted inversely so
                    # full lines still fit the page width.
                    size = item.get('size', 1.0)
                    svg_width = item['svg'].width / self.BASE_SVG_DIVISOR * s * size
                    svg_height = item['svg'].height / self.BASE_SVG_DIVISOR * s * size
                    
                    # Check if we need a new page
                    if y_position - svg_height < 50:
                        c.showPage()
                        y_position = self.page_height - top_offset
                        
                        # Add page number
                        c.setFont("Helvetica", page_font)
                        c.drawString(page_num_x, 30, f"Page {page_num + 1}")
                    
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
    parser.add_argument('--scale', type=float, default=1.0,
                       help='Text size scale factor (default: 1.0). Values >1 enlarge Grafoni and '
                            'English labels; wrap and pagination adjust to keep content on the page.')
    
    args = parser.parse_args()
    
    if not args.title and not args.book_id:
        print("Please provide either a book title or a book ID.")
        print("Example: python gutenberg_to_grafoni.py 'Pride and Prejudice'")
        print("Example: python gutenberg_to_grafoni.py --book-id 1342")
        sys.exit(1)
    
    if args.scale <= 0:
        print("Error: --scale must be a positive number.")
        sys.exit(1)
    
    # Initialize components
    downloader = GutenbergDownloader()
    converter = GrafoniConverter(scale=args.scale)
    pdf_generator = PDFGenerator(scale=args.scale)
    
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