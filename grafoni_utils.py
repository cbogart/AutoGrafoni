#!/usr/bin/env python3
"""
Utility functions for Grafoni conversion without IPython dependencies
"""

import grafoni
from math import sqrt

def to_svg_no_display(in_string, wrap=800, shear_val=-1/sqrt(3), line_space=20, v_scale=0.5):
    """
    Convert text to Grafoni SVG without displaying it.
    Returns the SVG object instead of calling display().
    No dynamic scaling - content appears at natural size.
    """
    chars = in_string
    if isinstance(chars, str):
        chars = grafoni.to_list(in_string)
    
    out = [('move',0,0)]
    last_char = " "
    
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
            out.append(('move', -shear_val*v_scale*(out[-1][-1]+line_space), out[-1][-1]+line_space))
    
    # Apply vertical scaling and shear only
    strokes = grafoni.shear(grafoni.scale(out, 1, v_scale), by=shear_val)
    
    # Let the SVG be its natural size based on content
    svg = grafoni.svgStrokes(strokes, scale=4, padding=10, stroke_width=1.0/3)
    
    return svg


def test_conversion():
    """Test the conversion function"""
    test_sentences = [
        "Hello world",
        "This is a test",
        "The quick brown fox jumps over the lazy dog",
        "Project Gutenberg is amazing"
    ]
    
    print("Testing Grafoni conversion...")
    print("=" * 50)
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n{i}. Converting: '{sentence}'")
        try:
            svg = to_svg_no_display(sentence)
            print(f"   ✓ Successfully converted to Grafoni")
            print(f"   SVG dimensions: {svg.width} x {svg.height}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    test_conversion() 