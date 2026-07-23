#!/usr/bin/env python3
"""
Utility functions for Grafoni conversion without IPython dependencies
"""

import grafoni
from math import sqrt


def _visual_x(strokes, shear_val, v_scale):
    """Horizontal advance including shear, matching the historical wrap check."""
    return strokes[-1][-2] + shear_val * v_scale * strokes[-1][-1]


def _append_glyph(out, last_char, glyph):
    """Append one letter/ligature glyph to the stroke list."""
    if glyph in grafoni.letter_forms:
        forms = grafoni.letter_forms
    elif glyph in grafoni.ligatures:
        forms = grafoni.ligatures
    else:
        print("Unsupported Character: " + glyph)
        return out, last_char

    l_kern, r_kern = grafoni.kerning[(grafoni.last(last_char), grafoni.first(glyph))]
    n_val = grafoni.nudge_kern[(grafoni.last(last_char), grafoni.first(glyph))]
    new_out = grafoni.concat(
        grafoni.v_nudge(grafoni.r_extend(out, l_kern), n_val),
        grafoni.l_extend(forms[glyph], r_kern),
    )
    return new_out, glyph


def _append_glyphs(out, last_char, glyphs):
    for glyph in glyphs:
        out, last_char = _append_glyph(out, last_char, glyph)
    return out, last_char


def _newline_move(out, line_space, shear_val, v_scale):
    """Append a move to the start of the next line; return (out, new_y)."""
    new_y = out[-1][-1] + line_space
    out = out + [
        ('move', -shear_val * v_scale * (out[-1][-1] + line_space),
         out[-1][-1] + line_space)
    ]
    return out, new_y


def _emit_page(svg_list, strokes, v_scale, shear_val):
    if not strokes:
        return
    page_strokes = grafoni.shear(grafoni.scale(strokes, 1, v_scale), by=shear_val)
    svg_list.append(grafoni.svgStrokes(page_strokes, scale=4, padding=10, stroke_width=1.0 / 3))


def to_svg_no_display(in_string, wrap=800, page_height=1000, remaining_page_height=None,
                      shear_val=-1 / sqrt(3), line_space=20, v_scale=0.5):
    """
    Convert text to Grafoni SVG without displaying it.
    If remaining_page_height is provided, will break into multiple SVGs if needed.
    Returns a list of SVG objects for the given text.

    Wrapping is word-aware: an overflowing word is moved to the next line when
    possible; words wider than wrap are broken at glyph boundaries.
    """
    chars = in_string
    if isinstance(chars, str):
        chars = grafoni.to_list(in_string)

    out = [('move', 0, 0)]
    last_char = " "
    current_page_strokes = [('move', 0, 0)]
    current_y = 0
    svg_list = []

    if remaining_page_height is None:
        remaining_page_height = page_height

    # Glyphs of the word currently being placed, and stroke state before it.
    word_glyphs = []
    out_before_word = [('move', 0, 0)]
    last_char_before_word = " "
    line_has_content = False

    def copy_strokes(strokes):
        return [s for s in strokes]

    def begin_word():
        nonlocal word_glyphs, out_before_word, last_char_before_word
        word_glyphs = []
        out_before_word = copy_strokes(out)
        last_char_before_word = last_char

    def page_break_if_needed(new_y):
        """Emit current page when new_y exceeds remaining height. Returns True if paged."""
        nonlocal out, last_char, current_page_strokes, current_y
        nonlocal remaining_page_height, line_has_content
        nonlocal out_before_word, last_char_before_word

        if new_y <= remaining_page_height:
            current_y = new_y
            return False

        _emit_page(svg_list, current_page_strokes, v_scale, shear_val)
        out = [('move', 0, 0)]
        last_char = " "
        current_page_strokes = [('move', 0, 0)]
        current_y = 0
        remaining_page_height = page_height
        line_has_content = False
        out_before_word = [('move', 0, 0)]
        last_char_before_word = " "
        return True

    def break_line():
        """Move to next line, paging if needed. Leaves out at the new line start."""
        nonlocal out, line_has_content
        out, new_y = _newline_move(out, line_space, shear_val, v_scale)
        paged = page_break_if_needed(new_y)
        if not paged:
            # Keep prior-line content as the page snapshot; new line starts after the move.
            pass
        line_has_content = False
        return paged

    def place_word_on_current_line(glyphs):
        """Place glyphs starting from out_before_word / last_char_before_word."""
        nonlocal out, last_char
        out = copy_strokes(out_before_word)
        last_char = last_char_before_word
        out, last_char = _append_glyphs(out, last_char, glyphs)
        return _visual_x(out, shear_val, v_scale) <= wrap

    def place_with_midword_breaks(glyphs):
        """
        Place glyphs on an empty line, inserting mid-word line breaks whenever
        a glyph would exceed wrap. Assumes out is already at a line start
        (out_before_word / last_char_before_word describe that start).
        """
        nonlocal out, last_char, current_page_strokes, line_has_content
        nonlocal out_before_word, last_char_before_word, word_glyphs

        out = copy_strokes(out_before_word)
        last_char = last_char_before_word
        word_glyphs = []

        for glyph in glyphs:
            out_before_glyph = copy_strokes(out)
            last_before_glyph = last_char
            out, last_char = _append_glyph(out, last_char, glyph)

            if _visual_x(out, shear_val, v_scale) <= wrap:
                word_glyphs.append(glyph)
                line_has_content = True
                current_page_strokes = copy_strokes(out)
                continue

            # Glyph does not fit on this line — break before it.
            out = out_before_glyph
            last_char = last_before_glyph
            current_page_strokes = copy_strokes(out)
            break_line()
            out_before_word = copy_strokes(out)
            last_char_before_word = last_char
            word_glyphs = [glyph]
            out, last_char = _append_glyph(out, last_char, glyph)
            # A single glyph should always be placeable; if wrap is tiny it may
            # still overflow, but we accept that pathological case.
            line_has_content = True
            current_page_strokes = copy_strokes(out)

    begin_word()

    for l in chars:
        if l == " ":
            out, last_char = _append_glyph(out, last_char, l)
            current_page_strokes = copy_strokes(out)
            line_has_content = True
            begin_word()
            continue

        if not word_glyphs:
            out_before_word = copy_strokes(out)
            last_char_before_word = last_char

        word_had_prior_content = line_has_content
        word_glyphs.append(l)
        out, last_char = _append_glyph(out, last_char, l)

        if _visual_x(out, shear_val, v_scale) <= wrap:
            line_has_content = True
            current_page_strokes = copy_strokes(out)
            continue

        # Overflow while placing this word.
        if word_had_prior_content:
            # Move the whole word to the next line.
            current_page_strokes = copy_strokes(out_before_word)
            out = copy_strokes(out_before_word)
            last_char = last_char_before_word
            break_line()
            out_before_word = copy_strokes(out)
            last_char_before_word = last_char

            if place_word_on_current_line(word_glyphs):
                line_has_content = True
                current_page_strokes = copy_strokes(out)
                continue

            # Word alone is wider than wrap — break it at glyph boundaries.
            place_with_midword_breaks(word_glyphs)
        else:
            # Already at line start and still overflowing — mid-word break.
            # Rewind the overflowing glyph, then mid-word place the word so far.
            place_with_midword_breaks(word_glyphs)

    if current_page_strokes:
        _emit_page(svg_list, current_page_strokes, v_scale, shear_val)

    return svg_list


def test_conversion():
    """Test the conversion function"""
    test_text = (
        "Hello world. This is a test paragraph.\n\n"
        "This is a second paragraph that should be separate.\n\n"
        "This is a third paragraph with more text to test page breaking functionality."
    )

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
