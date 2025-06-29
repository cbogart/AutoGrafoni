#!/usr/bin/env python3
"""
Test script for Grafoni conversion
"""

import grafoni_utils
from pathlib import Path
import os

def test_grafoni_conversion():
    """Test converting text to Grafoni SVG"""
    
    test_sentences = [
        "Hello world",
        "This is a test sentence.",
        "The quick brown fox jumps over the lazy dog.",
        "This is a very long sentence that should wrap to multiple lines when converted to Grafoni script.",
        "Project Gutenberg is an amazing resource for free books."
    ]
    
    print("Testing Grafoni conversion...")
    print("=" * 50)
    
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n{i}. Converting: '{sentence}'")
        try:
            svg = grafoni_utils.to_svg_no_display(sentence)
            print(f"   ✓ Successfully converted to Grafoni")
            print(f"   SVG dimensions: {svg.width} x {svg.height}")
            
            # Save SVG to output directory
            svg_filename = output_dir / f"test_sentence_{i}.svg"
            with open(svg_filename, 'w') as f:
                f.write(svg.as_svg())
            print(f"   SVG saved as: {svg_filename}")
            
            assert svg.width > 0 and svg.height > 0, f"SVG dimensions should be positive for sentence {i}"
            assert os.path.exists(svg_filename), f"SVG file was not created: {svg_filename}"
            # Optionally, check that the SVG file is not empty
            assert os.path.getsize(svg_filename) > 100, f"SVG file is unexpectedly small: {svg_filename}"
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    test_grafoni_conversion() 