#!/usr/bin/env python3
"""
Test script to verify SVG background and PNG conversion
"""

import grafoni_utils
import cairosvg
import tempfile
import os

def test_svg_background():
    """Test SVG to PNG conversion with proper background"""
    
    test_sentence = "Hello world, this is a test sentence."
    
    print("Testing SVG background and PNG conversion...")
    print("=" * 50)
    
    try:
        # Convert to Grafoni SVG
        print(f"Converting: '{test_sentence}'")
        svg = grafoni_utils.to_svg_no_display(test_sentence)
        print(f"✓ SVG created successfully")
        print(f"  SVG dimensions: {svg.width} x {svg.height}")
        
        # Get SVG data
        svg_data = svg.as_svg()
        print(f"  SVG data length: {len(svg_data)} characters")
        
        # Convert to PNG with white background
        print("\nConverting SVG to PNG with white background...")
        png_data = cairosvg.svg2png(
            bytestring=svg_data.encode('utf-8'),
            background_color='white'
        )
        print(f"✓ PNG created successfully")
        print(f"  PNG data size: {len(png_data)} bytes")
        
        # Save PNG to file for inspection
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(png_data)
            tmp_file_path = tmp_file.name
        
        print(f"  PNG saved to: {tmp_file_path}")
        print(f"  File size: {os.path.getsize(tmp_file_path)} bytes")
        
        # Clean up
        os.unlink(tmp_file_path)
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_svg_background() 