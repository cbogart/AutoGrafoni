#!/usr/bin/env python3
"""
Test script to verify text wrapping in Grafoni SVG
"""

import grafoni_utils

def test_text_wrapping():
    """Test text wrapping with different sentence lengths"""
    
    test_sentences = [
        "Short sentence.",
        "This is a medium length sentence that should wrap to multiple lines.",
        "This is a very long sentence that contains many words and should definitely wrap to multiple lines when converted to Grafoni script, demonstrating the text wrapping functionality.",
        "Another short one.",
        "The quick brown fox jumps over the lazy dog. This is a classic pangram that contains every letter of the alphabet at least once."
    ]
    
    print("Testing text wrapping in Grafoni SVG...")
    print("=" * 60)
    
    heights = []
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n{i}. Testing: '{sentence[:50]}{'...' if len(sentence) > 50 else ''}'")
        
        try:
            # Convert with consistent wrap width
            svg = grafoni_utils.to_svg_no_display(sentence, wrap=700, line_space=20)
            
            print(f"   ✓ SVG created successfully")
            print(f"   Original text length: {len(sentence)} characters")
            print(f"   SVG dimensions: {svg.width} x {svg.height}")
            print(f"   Aspect ratio: {svg.width/svg.height:.2f}")
            
            # Check if text wrapped (height should be greater for longer sentences)
            if svg.height > 50:
                print(f"   ✓ Text appears to have wrapped (height: {svg.height})")
            else:
                print(f"   ⚠ Single line (height: {svg.height})")
                
            heights.append(svg.height)
            assert svg.width > 0 and svg.height > 0, "SVG dimensions should be positive"
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    # Check that longer sentences have greater or equal height than shorter ones
    assert heights[2] > heights[0], "Long sentence should have greater height than short sentence"
    assert heights[4] >= heights[1], "Pangram+extra should have at least as much height as medium sentence"

if __name__ == "__main__":
    test_text_wrapping() 