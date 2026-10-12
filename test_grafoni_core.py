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


def test_no_context_dependent_forms():
    # A word is always written the same way, whatever surrounds it.
    assert grafoni.cleaner_ipa("the man the apple") == "ðə mæn ðə ˈæpəl"
    assert grafoni.cleaner_ipa("we close the door, a close call") == "wi kloʊs ðə dɔr, ə kloʊs kɔl"


@pytest.mark.parametrize("word, expected", [
    ("Costigan's", "kɑstɪgænz"),  # 's on a known word
    ("lugged", "ləgd"),           # doubled consonant + ed
    ("dyne", "daɪn"),             # letter rules: y, silent e
    ("sux", "səks"),              # x -> ks, never the velar-fricative glyph
    ("quaq", "kwæk"),             # q -> k
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
    # a kerning entry may name a whole ligature; otherwise its outer letters are used
    grafoni.kerning[("s_uv1", "zz")] = (3, 3)
    try:
        assert grafoni.pair_kerning("s_uv1", "zz")[:2] == (3, 3)
    finally:
        del grafoni.kerning[("s_uv1", "zz")]
    assert grafoni.pair_kerning("s_uv1", "ng") == grafoni.pair_kerning("uv1", "ng")


def test_th_vowel_ng_is_a_plain_arch():
    # "thing": no extra room between the i arch and the ng loop
    assert grafoni.pair_kerning("th_uv1", "ng") == grafoni.pair_kerning("uv1", "ng")


def test_t_sh_flows_together():
    # ch (t+sh) and j (d+zh) are common and must join without extra room
    for a, b in [("t", "sh"), ("d", "zh"), ("d", "zh_l"), ("t", "sh_l")]:
        assert grafoni.pair_kerning(a, b) == grafoni.pair_kerning("x", "y")


def test_ng_n_separated():
    assert grafoni.pair_kerning("ng", "n")[1] > 0


@pytest.mark.parametrize("text, expected", [
    ("DNA", ["L-D", "L-N", "L-A"]),      # said letter by letter: Latin letters
    ("FBI", ["L-F", "L-B", "L-I"]),
    ("XYZ", ["L-X", "L-Y", "L-Z"]),      # unknown short acronym
    ("Br", ["L-B", "L-R"]),              # no vowels
])
def test_acronyms_as_latin_letters(text, expected):
    assert grafoni.to_list(text) == expected


def test_spoken_acronym_uses_pronunciation():
    assert not any(g.startswith("L-") for g in grafoni.to_list("NASA"))


def test_all_caps_words_stay_grafoni():
    # AM's dictionary primary is the word, not the letters
    assert not any(g.startswith("L-") for g in grafoni.to_list("I AM HERE"))


@pytest.mark.parametrize("word, expected", [
    ("XIV", "14"), ("VIII", "8"),          # Roman numerals -> Grafoni digits
    ("complacence", "kɑmplæsɛns"),          # soft c before silent e
    ("declination", "dɛklɪnæʃən"),
    ("dirigible", "dərɪgɪbəl"),
])
def test_more_unknown_words(word, expected):
    assert grafoni.lookup_word(word) == expected


def test_roman_numeral_renders_as_digits():
    assert grafoni.to_list("XIV") == ["1", "4"]

