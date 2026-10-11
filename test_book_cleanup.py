"""Tests for Gutenberg text cleanup and chapter headings in gutenberg_to_grafoni.py"""
from gutenberg_to_grafoni import GrafoniConverter

BOOK = (
    "The Project Gutenberg EBook of Example\r\n\r\nlicense words\r\n"
    "*** START OF THIS PROJECT GUTENBERG EBOOK EXAMPLE ***\r\n\r\n"
    "Produced by Someone\r\n\r\n\r\n"
    "  [Transcriber's note:\r\n\r\n    Errors fixed.]\r\n\r\n"
    "CHAPTER XIV\r\n\r\n  Pirates of Space\r\n\r\n"
    "“Go,” he said—quietly.\r\nThen he left.\r\n\r\n"
    "  [Illustration:\r\n\r\n    A ship.]\r\n\r\n"
    "Last line.\r\n\r\n"
    "End of the Project Gutenberg EBook of Example\r\n\r\n"
    "*** END OF THIS PROJECT GUTENBERG EBOOK EXAMPLE ***\r\nmore license\r\n"
)


def test_clean_text_keeps_only_the_book():
    text = GrafoniConverter()._clean_text(BOOK)
    paragraphs = text.split("\n\n")
    assert paragraphs == [
        "CHAPTER XIV",
        "Pirates of Space",
        '"Go," he said--quietly.\nThen he left.',
        "Last line.",
    ]


def test_chapter_heading_and_subtitle():
    c = GrafoniConverter()
    assert c._heading("CHAPTER XIV", False) == "Chapter 14"
    assert c._heading("Pirates of Space", True) == "Pirates of Space"
    assert c._heading("Pirates of Space", False) is None
    assert c._heading('"Go," he said.', True) is None


def test_headings_are_marked_and_enlarged():
    pages = GrafoniConverter().convert_text(BOOK)
    items = [item for page in pages for item in page]
    assert [item['heading'] for item in items] == [True, True, False, False]
    assert items[0]['size'] > 1
