"""The specimen sheet builds, and every case uses only glyphs Grafoni can draw."""
import specimen


def test_specimen_builds_with_supported_glyphs(tmp_path):
    out = tmp_path / "specimen.pdf"
    assert specimen.build(out) == []
    assert out.stat().st_size > 0
