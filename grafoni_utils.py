#!/usr/bin/env python3
"""
Utility functions for Grafoni conversion without IPython dependencies
"""

import grafoni
from math import sqrt

def to_svg_no_display(in_string, wrap=800, page_height=1000, remaining_page_height=None, shear_val=-1/sqrt(3), line_space=20, v_scale=0.5):
    """
    Convert text to Grafoni SVG without displaying it.
    If remaining_page_height is provided, will break into multiple SVGs if needed.
    Returns a list of SVG objects for the given text.
    """
    chars = in_string
    if isinstance(chars, str):
        chars = grafoni.to_list(in_string)
    
    out = [('move',0,0)]
    last_char = " "
    current_page_strokes = []
    current_y = 0
    svg_list = []
    
    # If no remaining_page_height specified, use full page_height
    if remaining_page_height is None:
        remaining_page_height = page_height
    
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
            # Move to start of next line - reset to left margin
            new_y = out[-1][-1] + line_space
            #out.append(('move', 0, new_y))
            out.append(('move',-shear_val*v_scale*(out[-1][-1]+line_space),out[-1][-1]+line_space))
            current_y = new_y
            
            # Check if we need to start a new page
            if current_y > remaining_page_height:
                # Apply vertical scaling and shear to current page strokes
                page_strokes = grafoni.shear(grafoni.scale(current_page_strokes, 1, v_scale), by=shear_val)
                
                # Create SVG for this page
                svg = grafoni.svgStrokes(page_strokes, scale=4, padding=10, stroke_width=1.0/3)
                svg_list.append(svg)
                
                # Start new page with remaining content
                current_page_strokes = out[-1:]  # Keep the last move command
                current_y = line_space
                remaining_page_height = page_height  # Reset to full page height for subsequent pages
                out = [('move', 0, 0)]  # Reset for new page
                last_char = " "
                continue
        
        current_page_strokes = out.copy()
    
    # Apply vertical scaling and shear to final page strokes
    if current_page_strokes:
        page_strokes = grafoni.shear(grafoni.scale(current_page_strokes, 1, v_scale), by=shear_val)
        
        # Create SVG for final page
        svg = grafoni.svgStrokes(page_strokes, scale=4, padding=10, stroke_width=1.0/3)
        svg_list.append(svg)
    
    return svg_list


def test_conversion():
    """Test the conversion function"""
    test_text = "Hello world. This is a test paragraph.\n\nThis is a second paragraph that should be separate.\n\nThis is a third paragraph with more text to test page breaking functionality."
    
    print("Testing Grafoni conversion with paragraph-based approach...")
    print("=" * 50)
    
    print(f"Converting: '{test_text}'")
    try:
        paragraphs = test_text.split('\n\n')
        for i, paragraph in enumerate(paragraphs):
            print(f"\nParagraph {i+1}: '{paragraph.strip()}'")
            svg_list = to_svg_no_display(paragraph.strip(), wrap=100, page_height=200)
            print(f"   Generated {len(svg_list)} SVG(s) for this paragraph")
            for j, svg in enumerate(svg_list):
                print(f"   SVG {j+1} dimensions: {svg.width} x {svg.height}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    test_conversion() 