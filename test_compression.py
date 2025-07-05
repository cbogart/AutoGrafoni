#!/usr/bin/env python3
"""
Test script to demonstrate PDF compression improvements
"""

import grafoni
from gutenberg_to_grafoni import PDFGenerator
import os
from pathlib import Path

def test_compression():
    """Test different compression levels"""
    
    # Create a simple test text
    test_text = "This is a test of the compression system. Hello world! How are you today?"
    
    # Convert to Grafoni
    grafoni_pages = []
    current_page = []
    
    # Create a simple page with the test text
    from grafoni_utils import to_svg_no_display
    svg_list = to_svg_no_display(test_text, wrap=200)
    if svg_list:
        current_page.append({
            'text': test_text,
            'svg': svg_list[0]  # Use first SVG
        })
    grafoni_pages.append(current_page)
    
    # Test different compression levels
    compression_levels = ['high', 'medium', 'low']
    
    for level in compression_levels:
        print(f"\nTesting {level} compression...")
        
        # Create PDF generator
        pdf_gen = PDFGenerator()
        pdf_gen.set_compression(level)
        
        # Generate PDF
        output_file = f"test_compression_{level}.pdf"
        pdf_gen.generate_pdf(grafoni_pages, output_file, "Compression Test")
        
        # Check file size
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            size_kb = size / 1024
            print(f"  File size: {size_kb:.1f} KB")
        else:
            print(f"  Failed to create {output_file}")

if __name__ == "__main__":
    test_compression() 