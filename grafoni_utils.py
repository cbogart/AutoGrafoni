#!/usr/bin/env python3
"""
Utility functions for Grafoni conversion without IPython dependencies
"""

import grafoni
from math import sqrt

def to_svg_no_display(in_string, wrap=800, page_height=1000, shear_val=-1/sqrt(3), line_space=20, v_scale=0.5):
    """
    Convert text to Grafoni SVG without displaying it.
    Yields SVG objects as pages fill up, taking a page_height parameter.
    No dynamic scaling - content appears at natural size.
    """
    chars = in_string
    if isinstance(chars, str):
        chars = grafoni.to_list(in_string)
    
    out = [('move',0,0)]
    last_char = " "
    current_page_strokes = []
    current_y = 0
    
    for l in chars:
        if l in grafoni.letter_forms:
            l_kern, r_kern = grafoni.kerning[(grafoni.last(last_char), grafoni.first(l))]
            n_val = grafoni.nudge_kern[(grafoni.last(last_char), grafoni.first(l))]
            last_char = l
            out = grafoni.concat(grafoni.v_nudge(grafoni.r_extend(out, l_kern), n_val), 
                                grafoni.l_extend(grafoni.letter_forms[l], r_kern))
        elif l in grafoni.ligatures:
            l_kern, r_kern = grafoni.kerning[(grafoni.last(last_char), grafoni.first(l))]
            n_val = grafoni.nudge_kern[(grafoni.last(last_char), grafoni.first(l))]
            last_char = l
            out = grafoni.concat(grafoni.v_nudge(grafoni.r_extend(out, l_kern), n_val), 
                                grafoni.l_extend(grafoni.ligatures[l], r_kern))
        else:
            print("Unsupported Character: " + l)
        
        # Check for line wrapping
        if last_char == " " and out[-1][-2] + shear_val*v_scale*out[-1][-1] > wrap:
            # Move to start of next line - use the same logic as the original to_svg function
            new_y = out[-1][-1] + line_space
            #out.append(('move', int(-shear_val*v_scale*new_y), int(new_y)))
            out.append(('move',int(-shear_val*v_scale*new_y),out[-1][-1]+line_space))
            #out.append(('move', 0, int(new_y)))
            current_y = new_y
            
            # Check if we need to start a new page
            if current_y > page_height:
                # Apply vertical scaling and shear to current page strokes
                page_strokes = grafoni.shear(grafoni.scale(current_page_strokes, 1, v_scale), by=shear_val)
                
                # Create SVG for this page
                svg = grafoni.svgStrokes(page_strokes, scale=4, padding=10, stroke_width=1.0/3)
                yield svg
                
                # Start new page
                current_page_strokes = out[-1:]  # Keep the last move command
                current_y = line_space
                out = [('move', 0, 0)]  # Reset for new page
                last_char = " "
                continue
        
        current_page_strokes = out.copy()
    
    # Apply vertical scaling and shear to final page strokes
    if current_page_strokes:
        page_strokes = grafoni.shear(grafoni.scale(current_page_strokes, 1, v_scale), by=shear_val)
        
        # Create SVG for final page
        svg = grafoni.svgStrokes(page_strokes, scale=4, padding=10, stroke_width=1.0/3)
        yield svg


def test_conversion():
    """Test the conversion function"""
    test_text = "Hello world. This is a test. The quick brown fox jumps over the lazy dog. Project Gutenberg is amazing. This is a longer text to test page breaking functionality. We need more text to ensure we get multiple lines and can see if the line wrapping is working correctly without the horizontal drift bug."
    
    print("Testing Grafoni conversion with page breaking...")
    print("=" * 50)
    
    print(f"Converting: '{test_text}'")
    try:
        svg_count = 0
        for svg in to_svg_no_display(test_text, wrap=100, page_height=200):  # Smaller wrap to force line breaks
            svg_count += 1
            print(f"   ✓ Generated page {svg_count}")
            print(f"   SVG dimensions: {svg.width} x {svg.height}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    test_conversion() 