"""Tests for spelling, punctuation and fallback pronunciation in grafoni.py"""
import pytest
import grafoni


@pytest.mark.parametrize("word, expected", [
    # CMU primary pronunciations, not eng_to_ipa's alphabetically-last variant
    ("hundred", "həndrəd"), ("asked", "æskt"), ("question", "kwɛsʧən"), ("already", "ɔlrɛdi"),
    ("center", "sɛntər"), ("enter", "ɛntər"), ("just", "ʤəst"), ("I'm", "aɪm"), ("does", "dəz"),
    ("nice", "naɪs"), ("to", "tu"), ("him", "hɪm"), ("has", "hæz"), ("huge", "hjuʤ"),
    ("writhing", "raɪðɪŋ"), ("us", "əs"), ("that", "ðæt"), ("have", "hæv"),
])
def test_primary_pronunciation(word, expected):
    assert grafoni.cleaner_ipa(word).replace("ˈ", "").replace("ˌ", "") == expected


def test_the_before_vowel():
    assert grafoni.cleaner_ipa("the man the apple") == "ðə mæn ði ˈæpəl"


def test_close_as_verb():
    assert grafoni.cleaner_ipa("we close the door, a close call") == "wi kloʊz ðə dɔr, ə kloʊs kɔl"


@pytest.mark.parametrize("word, expected", [
    ("Costigan's", "kɑstɪgænz"),  # 's on a known word
    ("lugged", "ləgd"),           # doubled consonant + ed
    ("dyne", "daɪn"),             # letter rules: y, silent e
    ("sux", "səks"),              # x -> ks, never the velar-fricative glyph
    ("quaq", "kwæk"),             # q -> k
    ("XYZ", "ɛkswaɪzi"),          # unknown acronym spelled out
])
def test_unknown_words(word, expected):
    assert grafoni.cleaner_ipa(word).replace("ˈ", "").replace("ˌ", "") == expected


def test_fallback_uses_only_writable_sounds():
    glyphs = grafoni.grafoni_spell("cyclic quixotic jazzy")
    assert all(g in grafoni.letter_forms for g in glyphs if g != " "), glyphs


@pytest.mark.parametrize("text", ['"Go', 'Go"', "'Go", "Go?", "Go!", "(Go)"])
def test_punctuation_is_a_word_boundary(text):
    glyphs = grafoni.to_list(text)
    assert "g-beg" in glyphs


@pytest.mark.parametrize("mark", ["?", "!", '"', "'"])
def test_punctuation_has_a_glyph(mark):
    assert mark in grafoni.letter_forms
    assert mark in grafoni.to_list("yes" + mark)


def test_th_flows_into_d():
    assert "th_d" in grafoni.to_list("withdrew")


def test_ligature_aware_kerning():
    assert grafoni.pair_kerning("th_uv1", "ng")[0] > 0
    assert grafoni.pair_kerning("s_uv1", "ng") == grafoni.pair_kerning("uv1", "ng")
