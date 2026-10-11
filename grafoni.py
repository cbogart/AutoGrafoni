import eng_to_ipa as ipa
import drawsvg as draw
from math import sqrt
from collections import defaultdict

convert_dict = {
    'i': ["uv1","uv1"], # sometimes can be duplicated like "see"
    'ɪ': ["uv1"],
    'ɛ': ["uv2"],
    'e': ["uv2"],
    'æ': ["uv3"],
    'ʊ': ["mv1"],
    'ə': ["mv2"],
    'ɑ': ["mv3"],
    'a': ["mv3"],
    'u': ["lv1"],
    'o': ["lv2"],
    'ɔ': ["lv3"],

    'j': ["uv1"],
    'w': ["lv1"],

    'θ': ["th"],
    'ð': ["dh"],
    'ʃ': ["sh"],
    'ʒ': ["zh"],

    'ʤ': ["d","zh"],
    'ʧ': ["t","sh"],

    'ŋ': ["ng"],

    'ˈ': [],
    'ˌ': [],
    '*': [],
    
    ' ': [" "]
}

vowel_scale = 1.5

letter_forms = {
    " ": [('move',4,0)],

    "uv1": [('quadratic',1*vowel_scale,-1*vowel_scale,2*vowel_scale,0)],
    "uv2": [('quadratic',2*vowel_scale,-2*vowel_scale,4*vowel_scale,0)],
    "uv3": [('quadratic',4*vowel_scale,-4*vowel_scale,8*vowel_scale,0)],
    "mv1": [('line',2*vowel_scale,0)],
    "mv2": [('line',4*vowel_scale,0)],
    "mv3": [('line',8*vowel_scale,0)],
    "lv1": [('quadratic',1*vowel_scale,1*vowel_scale,2*vowel_scale,0)],
    "lv2": [('quadratic',2*vowel_scale,2*vowel_scale,4*vowel_scale,0)],
    "lv3": [('quadratic',4*vowel_scale,4*vowel_scale,8*vowel_scale,0)],

    "r": [('cubic',1,-2,1,-4,0,-4),('cubic',-1,-4,-1,-2,0,0)],
    "l": [('cubic',1,-2,1,-8,0,-8),('cubic',-1,-8,-1,-2,0,0)],
    # "m": [('cubic',1,0,1,2,0,2),('cubic',-1,2,-1,0,0,0)],
    # "m": [('cubic',2,2,-2,2,0,0)],
    # "m": [('cubic',3,0,0,3,0,0)],
    # "m": [('cubic',3,3,0,3,0,0)],
    # "m": [('cubic',0,3,-3,3,0,0)],
    "m": [('cubic',0.5,1,0.5,2,0,2),('cubic',-0.5,2,-0.5,1,0,0)],
    "n": [('cubic',1,2,1,4,0,4),('cubic',-1,4,-1,2,0,0)],
    "ng":[('cubic',1,2,1,8,0,8),('cubic',-1,8,-1,2,0,0)],

    "k": [('cubic',2,-2,0,-2,2,-4),('quadratic',0,-2,2,0)],
    "g": [('cubic',2,-2,0,-4,2,-8),('quadratic',0,-4,2,0)],
    "h": [('cubic',2,2,0,2,2,4),('quadratic',0,2,2,0)],
    "x": [('cubic',2,2,0,4,2,8),('quadratic',0,4,2,0)],

    "t": [('quadratic',2,0,2,-2),('line',2,-4),('line',2,0)],
    "d": [('quadratic',2,0,2,-2),('line',2,-8),('line',2,0)],
    "th": [('line',0,4),('line',0,2),('quadratic',0,0,2,0)],
    "dh": [('line',0,8),('line',0,2),('quadratic',0,0,2,0)],

    "p": [('quadratic',2,-2,0,-4),('cubic',2,-2,0,-2,2,0)],
    "b": [('quadratic',2,-4,0,-8),('cubic',2,-4,0,-2,2,0)],
    "f": [('quadratic',2,2,0,4),('cubic',2,2,0,2,2,0)],
    "v": [('quadratic',2,4,0,8),('cubic',2,4,0,2,2,0)],

    "s": [('quadratic',0,-4,1,-4),('quadratic',2,-4,2,0)],
    "z": [('quadratic',0,-8,1,-8),('quadratic',2,-8,2,0)],
    "sh": [('quadratic',0,4,1,4),('quadratic',2,4,2,0)],
    "zh": [('quadratic',0,8,1,8),('quadratic',2,8,2,0)],

    "Y": [('cubic',1,1,-1,1,0,0)],
    "W": [('cubic',1,-1,-1,-1,0,0)],

    "k-beg": [('move',0,-4),('quadratic',-2,-2,0,0)],
    "g-beg": [('move',0,-8),('quadratic',-2,-4,0,0)],
    "h-beg": [('move',0,4),('quadratic',-2,2,0,0)],
    "x-beg": [('move',0,8),('quadratic',-2,4,0,0)],

    "t-beg": [('move',0,-4),('line',0,0)],
    "d-beg": [('move',0,-8),('line',0,0)],
    "th-beg": [('move',0,4),('line',0,0)],
    "dh-beg": [('move',0,8),('line',0,0)],

    "p-beg": [('move',0,-4),('quadratic',2,-2,0,0)],
    "b-beg": [('move',0,-8),('quadratic',2,-4,0,0)],
    "f-beg": [('move',0,4),('quadratic',2,2,0,0)],
    "v-beg": [('move',0,8),('quadratic',2,4,0,0)],

    "k-end": [('quadratic',-2,-2,0,-4),('move',0,0)],
    "g-end": [('quadratic',-2,-4,0,-8),('move',0,0)],
    "h-end": [('quadratic',-2,2,0,4),('move',0,0)],
    "x-end": [('quadratic',-2,4,0,8),('move',0,0)],

    "t-end": [('line',0,-4),('move',0,0)],
    "d-end": [('line',0,-8),('move',0,0)],
    "th-end": [('line',0,4),('move',0,0)],
    "dh-end": [('line',0,8),('move',0,0)],

    "p-end": [('quadratic',2,-2,0,-4),('move',0,0)],
    "b-end": [('quadratic',2,-4,0,-8),('move',0,0)],
    "f-end": [('quadratic',2,2,0,4),('move',0,0)],
    "v-end": [('quadratic',2,4,0,8),('move',0,0)],

    ".": [('move',2,0),('quadratic',2,0.25,2.125,0.25),('quadratic',2.25,0.25,2.25,0),('quadratic',2.25,-0.25,2.125,-0.25),('quadratic',2,-0.25,2,0),('move',4,0)],
    ",": [('move',2,0),('quadratic',3,1,2,2),('move',4,0)],
    ":": [('move',2,2),('quadratic',2,2.25,2.125,2.25),('quadratic',2.25,2.25,2.25,2),('quadratic',2.25,1.75,2.125,1.75),('quadratic',2,1.75,2,2),('move',2,-2),('quadratic',2,-2.25,2.125,-2.25),('quadratic',2.25,-2.25,2.25,-2),('quadratic',2.25,-1.75,2.125,-1.75),('quadratic',2,-1.75,2,-2),('move',4,0)], 
    ";": [('move',2,2),('quadratic',3,3,2,4),('move',2,-2),('quadratic',2,-2.25,2.125,-2.25),('quadratic',2.25,-2.25,2.25,-2),('quadratic',2.25,-1.75,2.125,-1.75),('quadratic',2,-1.75,2,-2),('move',4,0)],   
    #"-": [('move',2,-1),('line',3,1),('move',5,0)], #from the 1910 edition
    "-": [('move',2,-1),('line',4,-1),('move',2,1),('line',4,1),('move',6,0)], #from the 1913 edition
    # Hitlofi uses ordinary English punctuation (except the doubled hyphen above).
    "?": [('move',1,-6),('cubic',1,-9,4.5,-9,4.5,-6.5),('quadratic',4.5,-4.5,2.5,-4),('line',2.5,-2),('move',2.5,0),('quadratic',2.5,0.25,2.625,0.25),('quadratic',2.75,0.25,2.75,0),('quadratic',2.75,-0.25,2.625,-0.25),('quadratic',2.5,-0.25,2.5,0),('move',5,0)],
    "!": [('move',2.5,-8),('line',2.5,-2),('move',2.5,0),('quadratic',2.5,0.25,2.625,0.25),('quadratic',2.75,0.25,2.75,0),('quadratic',2.75,-0.25,2.625,-0.25),('quadratic',2.5,-0.25,2.5,0),('move',4.5,0)],
    '"': [('move',1.5,-9),('line',1.5,-6.5),('move',3,-9),('line',3,-6.5),('move',4.5,0)],
    "'": [('move',1.5,-9),('line',1.5,-6.5),('move',3,0)],
    "(": [('move',3,6),('quadratic',0,0,3,-6),('move',5,0)],
    ")": [('move',2,6),('quadratic',5,0,2,-6),('move',5,0)],

    #from the 1917 book on just the numerals, not from the 1913 text
    "1": [('move',0,-8),('line',0,0),('move',3,0)],
    "2": [('move',0,-8),('quadratic',2,-8,0,-4),('quadratic',-1,-2,0,0),('move',3,0)],
    "3": [('move',0,-8),('quadratic',2,-6,0,-4),('quadratic',2,-2,0,0),('move',3,0)],
    "4": [('move',0,-8),('quadratic',2,-4,0,0),('line',2,-2),('move',3,0)],
    "5": [('move',0,-8),('quadratic',-2,-6,0,-4),('quadratic',2,-2,0,0),('move',3,0)],
    "6": [('move',1,-8),('quadratic',-1,0,1,0),('quadratic',2,0,3,-1),('move',4,0)],
    "7": [('move',-1,-6),('quadratic',0,-7,0,-8),('line',0,0),('move',3,0)],
    "8": [('move',0,-8),('line',0,-4),('quadratic',0,0,-1,0),('quadratic',-2,0,0,-4),('move',3,0)],
    "9": [('move',0,-8),('quadratic',2,-4,0,0),('move',3,0)],
    "0": [('move',0,-4),('quadratic',1,-5,2,-4),('move',3,0)],
}

# this dictionary will hold kerning instructions for pairs of letters, it says how much to kern the left letter on the right and the right letter on the left
kerning = defaultdict(lambda: (-1,-1))
kerning[("t-beg","r")] = (-1,2)
kerning[("t-beg","l")] = (-1,2)
kerning[("d-beg","r")] = (-1,2)
kerning[("d-beg","l")] = (-1,2)
kerning[("t","r")] = (-1,2)
kerning[("t","l")] = (-1,2)
kerning[("d","r")] = (-1,2)
kerning[("d","l")] = (-1,2)
kerning[("t","s")] = (-1,2)
kerning[("t","z")] = (-1,2)
kerning[("d","s")] = (-1,2)
kerning[("d","z")] = (-1,2)
kerning[("g-beg","r")] = (1,1)
kerning[("g-beg","l")] = (1,1)
kerning[("k-beg","r")] = (1,1)
kerning[("k-beg","l")] = (1,1)
kerning[("g","r")] = (1,1)
kerning[("g","l")] = (1,1)
kerning[("k","r")] = (1,1)
kerning[("k","l")] = (1,1)
kerning[("r","p")] = (1,0.5)
kerning[("r","b")] = (1,0.5)
kerning[("l","p")] = (1,0.5)
kerning[("l","b")] = (1,0.5)
kerning[("p-beg","r")] = (-1,2.5)
kerning[("p-beg","l")] = (-1,2.5)
kerning[("b-beg","r")] = (-1,2.5)
kerning[("b-beg","l")] = (-1,2.5)
kerning[("p","r")] = (0.5,1)
kerning[("p","l")] = (0.5,1)
kerning[("b","r")] = (0.5,0.5)
kerning[("b","l")] = (0.5,0.5)
kerning[("r","l")] = (1,1)
kerning[("r","k")] = (0.5,0.5)
kerning[("r","g")] = (0.5,0.5)
kerning[("r","s")] = (1.5,0.5)
kerning[("r","z")] = (1.5,0.5)
kerning[("l","r")] = (1,1)
kerning[("l","k")] = (0.5,0.5)
kerning[("l","g")] = (0.5,0.5)
kerning[("l","s")] = (1.5,0.5)
kerning[("l","z")] = (1.5,0.5)
kerning[("s","t-end")] = (-1,1)
kerning[("s","d-end")] = (-1,1)
kerning[("z","t-end")] = (-1,1)
kerning[("z","d-end")] = (-1,1)
kerning[("r","t-end")] = (2,-1)
kerning[("r","d-end")] = (2,-1)
kerning[("l","t-end")] = (2,-1)
kerning[("l","d-end")] = (2,-1)
kerning[("k","t-end")] = (2,-1)
kerning[("k","d-end")] = (2,-1)
kerning[("g","t-end")] = (2,-1)
kerning[("g","d-end")] = (2,-1)
kerning[("s","p")] = (-1,1)
kerning[("s","b")] = (-1,1)
kerning[("z","p")] = (-1,1)
kerning[("z","b")] = (-1,1)
kerning[("s","k")] = (-1,0.5)
kerning[("s","g")] = (-1,0.5)
kerning[("z","k")] = (-1,0.5)
kerning[("z","g")] = (-1,0.5)
kerning[("s","r")] = (-1,2)
kerning[("s","l")] = (-1,2)
kerning[("z","r")] = (-1,2)
kerning[("z","l")] = (-1,2)
kerning[("k","s")] = (1,-1)
kerning[("k","z")] = (1,-1)
kerning[("g","s")] = (1,-1)
kerning[("g","z")] = (1,-1)
kerning[("s","k-end")] = (2,-1)
kerning[("s","g-end")] = (2,-1)
kerning[("z","k-end")] = (2,-1)
kerning[("z","g-end")] = (2,-1)
kerning[("k-beg","s")] = (1,-1)
kerning[("k-beg","z")] = (1,-1)
kerning[("g-beg","s")] = (1,-1)
kerning[("g-beg","z")] = (1,-1)
kerning[("t","r")] = (-1,2)
kerning[("t","l")] = (-1,2)
kerning[("d","r")] = (-1,2)
kerning[("d","l")] = (-1,2)
kerning[("t","k")] = (-1,2)
kerning[("t","g")] = (-1,2)
kerning[("d","k")] = (-1,2)
kerning[("d","g")] = (-1,2)
kerning[("t","p")] = (-1,2)
kerning[("t","b")] = (-1,2)
kerning[("d","p")] = (-1,2)
kerning[("d","b")] = (-1,2)
kerning[("r","mv1")] = (1,-1)
kerning[("r","mv2")] = (1,-1)
kerning[("r","mv3")] = (1,-1)
kerning[("l","mv1")] = (1,-1)
kerning[("l","mv2")] = (1,-1)
kerning[("l","mv3")] = (1,-1)
kerning[("mv1","r")] = (-1,1)
kerning[("mv2","r")] = (-1,1)
kerning[("mv3","r")] = (-1,1)
kerning[("mv1","l")] = (-1,1)
kerning[("mv2","l")] = (-1,1)
kerning[("mv3","l")] = (-1,1)
kerning[("n","mv1")] = (1,-1)
kerning[("n","mv2")] = (1,-1)
kerning[("n","mv3")] = (1,-1)
kerning[("ng","mv1")] = (1,-1)
kerning[("ng","mv2")] = (1,-1)
kerning[("ng","mv3")] = (1,-1)
kerning[("mv1","n")] = (-1,1)
kerning[("mv2","n")] = (-1,1)
kerning[("mv3","n")] = (-1,1)
kerning[("mv1","ng")] = (-1,1)
kerning[("mv2","ng")] = (-1,1)
kerning[("mv3","ng")] = (-1,1)
kerning[("n","sh")] = (2,-1)
kerning[("n","zh")] = (2,-1)
kerning[("ng","sh")] = (2,-1)
kerning[("ng","zh")] = (2,-1)
kerning[("m","r")] = (-1,1)
kerning[("m","l")] = (-1,1)
kerning[("n","r")] = (0.5,0.5)
kerning[("n","l")] = (0.5,0.5)
kerning[("ng","r")] = (0.5,0.5)
kerning[("ng","l")] = (0.5,0.5)
kerning[("r","m")] = (1,-1)
kerning[("r","n")] = (0.5,0.5)
kerning[("r","ng")] = (0.5,0.5)
kerning[("l","m")] = (1,-1)
kerning[("l","n")] = (0.5,0.5)
kerning[("l","ng")] = (0.5,0.5)
kerning[("n","h")] = (0.5,0.5)
kerning[("n","x")] = (0.5,0.5)
kerning[("ng","h")] = (0.5,0.5)
kerning[("ng","x")] = (0.5,0.5)
kerning[("r","k")] = (0.5,0.5)
kerning[("l","k")] = (0.5,0.5)
kerning[("r","g")] = (0.5,0.5)
kerning[("l","g")] = (0.5,0.5)
kerning[("r","k-end")] = (2.5,-1)
kerning[("l","k-end")] = (2.5,-1)
kerning[("r","g-end")] = (2.5,-1)
kerning[("l","g-end")] = (2.5,-1)
kerning[("p","t-end")] = (1,-1)
kerning[("p","d-end")] = (1,-1)
kerning[("b","t-end")] = (1,-1)
kerning[("b","d-end")] = (1,-1)
kerning[("n","f")] = (1,1)
kerning[("n","v")] = (1,1)
kerning[("m","n")] = (-1,1.5)
kerning[("m","ng")] = (-1,1.5)
kerning[("n","m")] = (1.5,-1)
kerning[("ng","m")] = (1.5,-1)
kerning[("r","p-end")] = (2,-1)
kerning[("l","p-end")] = (2,-1)
kerning[("r","b-end")] = (2,-1)
kerning[("l","b-end")] = (2,-1)
kerning[("m","th")] = (2,-1)
kerning[("m","dh")] = (2,-1)
kerning[("n","th")] = (2,-1)
kerning[("n","dh")] = (2,-1)
kerning[("ng","th")] = (2,-1)
kerning[("ng","dh")] = (2,-1)
kerning[("r","r")] = (1,1)
kerning[("l","l")] = (1,1)
kerning[("m","m")] = (0.5,0.5)
kerning[("n","n")] = (1,1)
kerning[("ng","ng")] = (1,1)
kerning[("m","th-end")] = (2,-1)
kerning[("m","dh-end")] = (2,-1)
kerning[("n","th-end")] = (2,-1)
kerning[("n","dh-end")] = (2,-1)
kerning[("ng","th-end")] = (2,-1)
kerning[("ng","dh-end")] = (2,-1)
kerning[("sh","m")] = (-1,1)
kerning[("zh","m")] = (-1,1)
kerning[("m","sh")] = (1,-1)
kerning[("m","zh")] = (1,-1)

# a little room before a downward loop that would otherwise sit on the t/d stem ("savagely", "strangely")
for _a in ["t","d"]:
    for _b in ["sh","zh"]:
        kerning[(_a,_b)] = (1,-1)
# s/z followed by m without the s_m ligature (e.g. after n_s in "transmitter")
kerning[("s","m")] = (1,-1)
kerning[("z","m")] = (1,-1)
# keys may also name a whole ligature on the left; these keep the th/dh descender clear of a following loop ("nothingness")
for _a in ["th_uv1","dh_uv1"]:
    for _b in ["n","ng","sh","zh","f","v"]:
        kerning[(_a,_b)] = (2.5,-1)

def pair_kerning(last_char, glyph):
    """(left kern, right kern, nudge) between the previous glyph and the next one."""
    key = (last_char, first(glyph))
    if key not in kerning:
        key = (last(last_char), first(glyph))
    return kerning[key] + (nudge_kern[(last(last_char), first(glyph))],)

ligatures = {
    "n_t": [('cubic',1,2,1,4,0,4),('cubic',-1,4,-1,2,0,0),('quadratic',1,-2,1,-4),('line',1,0)],
    "n_d": [('cubic',1,2,1,4,0,4),('cubic',-1,4,-1,2,0,0),('quadratic',1,-2,1,-4),('line',1,-8),('line',1,0)],
    "ng_t": [('cubic', 1, 2, 1, 8, 0, 8), ('cubic', -1, 8, -1, 2, 0, 0), ('quadratic',1,-2,1,-4),('line',1,0)],
    "ng_d": [('cubic', 1, 2, 1, 8, 0, 8), ('cubic', -1, 8, -1, 2, 0, 0), ('quadratic',1,-2,1,-4),('line',1,-8),('line',1,0)],
    
    "r_th": [('cubic',1,-2,1,-4,0,-4),('cubic',-1,-4,-1,-2,0,0),('quadratic',1,2,1,4),('line',1,0)],
    "r_dh": [('cubic',1,-2,1,-4,0,-4),('cubic',-1,-4,-1,-2,0,0),('quadratic',1,2,1,4),('line',1,8),('line',1,0)],
    "l_th": [('cubic', 1, -2, 1, -8, 0, -8), ('cubic', -1, -8, -1, -2, 0, 0), ('quadratic',1,2,1,4),('line',1,0)],
    "l_dh": [('cubic', 1, -2, 1, -8, 0, -8), ('cubic', -1, -8, -1, -2, 0, 0), ('quadratic',1,2,1,4),('line',1,8),('line',1,0)],

    "m_t-end": [('cubic',1,1,1,2,0.5,2),('cubic',0,2,0,1,0,0),('line',0,-4),('move',0,0)],
    "m_d-end": [('cubic',1,1,1,2,0.5,2),('cubic',0,2,0,1,0,0),('line',0,-8),('move',0,0)],
    "n_t-end": [('cubic',2,2,2,4,1,4),('cubic',0,4,0,2,0,0),('line',0,-4),('move',0,0)],
    "n_d-end": [('cubic',2,2,2,4,1,4),('cubic',0,4,0,2,0,0),('line',0,-8),('move',0,0)],
    "ng_t-end": [('cubic',2,2,2,8,1,8),('cubic',0,8,0,2,0,0),('line',0,-4),('move',0,0)],
    "ng_d-end": [('cubic',2,2,2,8,1,8),('cubic',0,8,0,2,0,0),('line',0,-8),('move',0,0)],
    "th-beg_r": [('move',0,4),('line',0,0),('cubic',0,-2,0,-4,-1,-4),('cubic',-2,-4,-2,-2,0,0)],
    "th-beg_l": [('move',0,4),('line',0,0),('cubic',0,-2,0,-8,-1,-8),('cubic',-2,-8,-2,-2,0,0)],
    "dh-beg_r": [('move',0,8),('line',0,0),('cubic',0,-2,0,-4,-1,-4),('cubic',-2,-4,-2,-2,0,0)],
    "dh-beg_l": [('move',0,8),('line',0,0),('cubic',0,-2,0,-8,-1,-8),('cubic',-2,-8,-2,-2,0,0)],

    "r_th-end": [('cubic',2,-2,2,-4,1,-4),('cubic',0,-4,0,-2,0,0),('line',0,4),('move',0,0)],
    "r_dh-end": [('cubic',2,-2,2,-4,1,-4),('cubic',0,-4,0,-2,0,0),('line',0,8),('move',0,0)],
    "l_th-end": [('cubic',2,-2,2,-8,1,-8),('cubic',0,-8,0,-2,0,0),('line',0,4),('move',0,0)],
    "l_dh-end": [('cubic',2,-2,2,-8,1,-8),('cubic',0,-8,0,-2,0,0),('line',0,8),('move',0,0)],
    
    "n_s": [('cubic',2,2,2,4,1,4),('cubic',0,4,0,2,0,0), ('quadratic', 0, -4, 1, -4), ('quadratic', 2, -4, 2, 0)],
    "n_z": [('cubic',2,2,2,4,1,4),('cubic',0,4,0,2,0,0), ('quadratic', 0, -8, 1, -8), ('quadratic', 2, -8, 2, 0)],
    "ng_s": [('cubic',2,2,2,8,1,8),('cubic',0,8,0,2,0,0), ('quadratic', 0, -4, 1, -4), ('quadratic', 2, -4, 2, 0)],
    "ng_z": [('cubic',2,2,2,8,1,8),('cubic',0,8,0,2,0,0), ('quadratic', 0, -8, 1, -8), ('quadratic', 2, -8, 2, 0)],
    "r_sh": [('cubic',2,-2,2,-4,1,-4),('cubic',0,-4,0,-2,0,0), ('quadratic', 0, 4, 1, 4), ('quadratic', 2, 4, 2, 0)],
    "r_zh": [('cubic',2,-2,2,-4,1,-4),('cubic',0,-4,0,-2,0,0), ('quadratic', 0, 8, 1, 8), ('quadratic', 2, 8, 2, 0)],
    "l_sh": [('cubic',2,-2,2,-8,1,-8),('cubic',0,-8,0,-2,0,0), ('quadratic', 0, 4, 1, 4), ('quadratic', 2, 4, 2, 0)],
    "l_zh": [('cubic',2,-2,2,-8,1,-8),('cubic',0,-8,0,-2,0,0), ('quadratic', 0, 8, 1, 8), ('quadratic', 2, 8, 2, 0)],
    "s_n": [('quadratic', 0, -4, 1, -4), ('quadratic', 2, -4, 2, 0), ('cubic', 2, 2, 2, 4, 1, 4), ('cubic', 0, 4, 0, 2, 2, 0)],
    "z_n": [('quadratic', 0, -8, 1, -8), ('quadratic', 2, -8, 2, 0), ('cubic', 2, 2, 2, 4, 1, 4), ('cubic', 0, 4, 0, 2, 2, 0)],
    "s_ng": [('quadratic', 0, -4, 1, -4), ('quadratic', 2, -4, 2, 0), ('cubic', 2, 2, 2, 8, 1, 8), ('cubic', 0, 8, 0, 2, 2, 0)],
    "z_ng": [('quadratic', 0, -8, 1, -8), ('quadratic', 2, -8, 2, 0), ('cubic', 2, 2, 2, 8, 1, 8), ('cubic', 0, 8, 0, 2, 2, 0)],
    "sh_r": [('quadratic', 0, 4, 1, 4), ('quadratic', 2, 4, 2, 0), ('cubic', 2, -2, 2, -4, 1, -4), ('cubic', 0, -4, 0, -2, 2, 0)],
    "zh_r": [('quadratic', 0, 8, 1, 8), ('quadratic', 2, 8, 2, 0), ('cubic', 2, -2, 2, -4, 1, -4), ('cubic', 0, -4, 0, -2, 2, 0)],
    "sh_l": [('quadratic', 0, 4, 1, 4), ('quadratic', 2, 4, 2, 0), ('cubic', 2, -2, 2, -8, 1, -8), ('cubic', 0, -8, 0, -2, 2, 0)],
    "zh_l": [('quadratic', 0, 8, 1, 8), ('quadratic', 2, 8, 2, 0), ('cubic', 2, -2, 2, -8, 1, -8), ('cubic', 0, -8, 0, -2, 2, 0)],      

    "th_uv1": [('line',0,4),('line',0,2),('cubic',0,0,1*vowel_scale,-1*vowel_scale,2*vowel_scale,0)],
    "th_uv2": [('line',0,4),('line',0,2),('cubic',0,0,2*vowel_scale,-2*vowel_scale,4*vowel_scale,0)],
    "th_uv3": [('line',0,4),('line',0,2),('cubic',0,0,4*vowel_scale,-4*vowel_scale,8*vowel_scale,0)],
    "dh_uv1": [('line',0,8),('line',0,2),('cubic',0,0,1*vowel_scale,-1*vowel_scale,2*vowel_scale,0)],
    "dh_uv2": [('line',0,8),('line',0,2),('cubic',0,0,2*vowel_scale,-2*vowel_scale,4*vowel_scale,0)],
    "dh_uv3": [('line',0,8),('line',0,2),('cubic',0,0,4*vowel_scale,-4*vowel_scale,8*vowel_scale,0)],
    "lv1_t": [('cubic',1*vowel_scale,1*vowel_scale,2*vowel_scale,0,2*vowel_scale,-2),('line',2*vowel_scale,-4),('line',2*vowel_scale,0)],
    "lv2_t": [('cubic',2*vowel_scale,2*vowel_scale,4*vowel_scale,0,4*vowel_scale,-2),('line',4*vowel_scale,-4),('line',4*vowel_scale,0)],
    "lv3_t": [('cubic',4*vowel_scale,4*vowel_scale,8*vowel_scale,0,8*vowel_scale,-2),('line',8*vowel_scale,-4),('line',8*vowel_scale,0)],
    "lv1_d": [('cubic',1*vowel_scale,1*vowel_scale,2*vowel_scale,0,2*vowel_scale,-2),('line',2*vowel_scale,-8),('line',2*vowel_scale,0)],
    "lv2_d": [('cubic',2*vowel_scale,2*vowel_scale,4*vowel_scale,0,4*vowel_scale,-2),('line',4*vowel_scale,-8),('line',4*vowel_scale,0)],
    "lv3_d": [('cubic',4*vowel_scale,4*vowel_scale,8*vowel_scale,0,8*vowel_scale,-2),('line',8*vowel_scale,-8),('line',8*vowel_scale,0)],

    "s_f": [('quadratic', 0, -4, 1, -4), ('quadratic', 2, -4, 2, 0), ('quadratic', 2, 4, 1, 4), ('cubic', 2, 4, 2, 0, 3, 0)],
    "z_f": [('quadratic', 0, -8, 1, -8), ('quadratic', 2, -8, 2, 0), ('quadratic', 2, 4, 1, 4), ('cubic', 2, 4, 2, 0, 3, 0)],
    "s_v": [('quadratic', 0, -4, 1, -4), ('quadratic', 2, -4, 2, 0), ('quadratic', 2, 8, 1, 8), ('cubic', 2, 8, 2, 0, 3, 0)],
    "z_v": [('quadratic', 0, -8, 1, -8), ('quadratic', 2, -8, 2, 0), ('quadratic', 2, 8, 1, 8), ('cubic', 2, 8, 2, 0, 3, 0)],
    "h_s": [('cubic', 1, 0, 1, 4, 2, 4), ('quadratic', 1, 4, 1, 0), ('quadratic', 1, -4, 2, -4), ('quadratic', 3, -4, 3, 0)],
    "h_z": [('cubic', 1, 0, 1, 4, 2, 4), ('quadratic', 1, 4, 1, 0), ('quadratic', 1, -8, 2, -8), ('quadratic', 3, -8, 3, 0)],
    "x_s": [('cubic', 1, 0, 1, 8, 2, 8), ('quadratic', 1, 8, 1, 0), ('quadratic', 1, -4, 2, -4), ('quadratic', 3, -4, 3, 0)],
    "x_z": [('cubic', 1, 0, 1, 8, 2, 8), ('quadratic', 1, 8, 1, 0), ('quadratic', 1, -8, 2, -8), ('quadratic', 3, -8, 3, 0)],
    "sh_p": [('quadratic', 0, 4, 1, 4), ('quadratic', 2, 4, 2, 0), ('quadratic', 2, -4, 1, -4), ('cubic', 2, -4, 2, 0, 3, 0)],
    "zh_p": [('quadratic', 0, 8, 1, 8), ('quadratic', 2, 8, 2, 0), ('quadratic', 2, -4, 1, -4), ('cubic', 2, -4, 2, 0, 3, 0)],
    "sh_b": [('quadratic', 0, 4, 1, 4), ('quadratic', 2, 4, 2, 0), ('quadratic', 2, -8, 1, -8), ('cubic', 2, -8, 2, 0, 3, 0)],
    "zh_b": [('quadratic', 0, 8, 1, 8), ('quadratic', 2, 8, 2, 0), ('quadratic', 2, -8, 1, -8), ('cubic', 2, -8, 2, 0, 3, 0)],
    "k_sh": [('cubic', 1, 0, 1, -4, 2, -4), ('quadratic', 1, -4, 1, 0), ('quadratic', 1, 4, 2, 4), ('quadratic', 3, 4, 3, 0)],
    "k_zh": [('cubic', 1, 0, 1, -4, 2, -4), ('quadratic', 1, -4, 1, 0), ('quadratic', 1, 8, 2, 8), ('quadratic', 3, 8, 3, 0)],
    "g_sh": [('cubic', 1, 0, 1, -8, 2, -8), ('quadratic', 1, -8, 1, 0), ('quadratic', 1, 4, 2, 4), ('quadratic', 3, 4, 3, 0)],
    "g_zh": [('cubic', 1, 0, 1, -8, 2, -8), ('quadratic', 1, -8, 1, 0), ('quadratic', 1, 8, 2, 8), ('quadratic', 3, 8, 3, 0)],
        
    "v_r": [('quadratic', 2, 4, 0, 8), ('cubic', 2, 4, 0, 2, 1, 0), ('cubic', 2, -2, 2, -4, 1, -4), ('cubic', 0, -4, 0, -2, 1, 0)],
    "v_l": [('quadratic', 2, 4, 0, 8), ('cubic', 2, 4, 0, 2, 1, 0), ('cubic', 2, -4, 2, -8, 1, -8), ('cubic', 0, -8, 0, -4, 1, 0)],
    "f_r": [('quadratic', 2, 2, 0, 4), ('cubic', 2, 2, 0, 1, 1, 0), ('cubic', 2, -2, 2, -4, 1, -4), ('cubic', 0, -4, 0, -2, 1, 0)],
    "f_l": [('quadratic', 2, 2, 0, 4), ('cubic', 2, 2, 0, 1, 1, 0), ('cubic', 2, -4, 2, -8, 1, -8), ('cubic', 0, -8, 0, -4, 1, 0)],
    "n_k": [('cubic', 1, 2, 1, 4, 0, 4), ('cubic', -1, 4, -1, 2, 0, 0), ('cubic', 1, -1, -1, -2, 1, -4), ('quadratic', -1, -2, 1, 0)],
    "n_g": [('cubic', 1, 2, 1, 4, 0, 4), ('cubic', -1, 4, -1, 2, 0, 0), ('cubic', 1, -2, -1, -4, 1, -8), ('quadratic', -1, -4, 1, 0)],
    "ng_k": [('cubic', 1, 2, 1, 8, 0, 8), ('cubic', -1, 8, -1, 2, 0, 0), ('cubic', 1, -1, -1, -2, 1, -4), ('quadratic', -1, -2, 1, 0)],
    "ng_g": [('cubic', 1, 2, 1, 8, 0, 8), ('cubic', -1, 8, -1, 2, 0, 0), ('cubic', 1, -2, -1, -4, 1, -8), ('quadratic', -1, -4, 1, 0)],
    
    "f-beg_r": [('move', 0, 4), ('quadratic', 2, 3, 2, 0), ('cubic', 2, -2, 2, -4, 1, -4), ('cubic', 0, -4, 0, -2, 2, 0)],
    "f-beg_l": [('move', 0, 4), ('quadratic', 2, 3, 2, 0), ('cubic', 2, -4, 2, -8, 1, -8), ('cubic', 0, -8, 0, -4, 2, 0)],
    "n_k-end": [('cubic', 2, 2, 2, 4, 1, 4), ('cubic', 0, 4, 0, 2, 0, 0), ('quadratic', 0, -3, 2, -4), ('move', 2, 0)],
    "ng_k-end": [('cubic', 2, 4, 2, 8, 1, 8), ('cubic', 0, 8, 0, 4, 0, 0), ('quadratic', 0, -3, 2, -4), ('move', 2, 0)],

    "f_s": [('quadratic', 2, 2, 0, 4), ('cubic', 1, 3, 1.5, 2,1.5,0), ('quadratic', 1.5, -4, 2.5, -4), ('quadratic', 3.5, -4, 3.5, 0)],
    "f_z": [('quadratic', 2, 2, 0, 4), ('cubic', 1, 3, 1.5, 2,1.5,0), ('quadratic', 1.5, -8, 2.5, -8), ('quadratic', 3.5, -8, 3.5, 0)],   
    "v_s": [('quadratic', 2, 4, 0, 8), ('cubic', 1, 6, 1.5, 4,1.5,0), ('quadratic', 1.5, -4, 2.5, -4), ('quadratic', 3.5, -4, 3.5, 0)],
    "v_z": [('quadratic', 2, 4, 0, 8), ('cubic', 1, 6, 1.5, 4,1.5,0), ('quadratic', 1.5, -8, 2.5, -8), ('quadratic', 3.5, -8, 3.5, 0)],

    "f_t-end": [('quadratic', 2, 2, 0, 4), ('cubic', 1, 3, 1.5, 2,1.5,0), ('line', 1.5, -4), ('move', 1.5, 0)],
    "f_d-end": [('quadratic', 2, 2, 0, 4), ('cubic', 1, 3, 1.5, 2,1.5,0), ('line', 1.5, -8), ('move', 1.5, 0)],
    "v_t-end": [('quadratic', 2, 4, 0, 8), ('cubic', 1, 6, 1.5, 4,1.5,0), ('line', 1.5, -4), ('move', 1.5, 0)],
    "v_d-end": [('quadratic', 2, 4, 0, 8), ('cubic', 1, 6, 1.5, 4,1.5,0), ('line', 1.5, -8), ('move', 1.5, 0)],

    "f_t": [('quadratic', 2, 2, 0, 4), ('cubic', 2, 2, 0, 2, 2, 0), ('quadratic', 3, -1, 3, -2), ('line', 3, -4), ('line', 3, 0)],
    "f_d": [('quadratic', 2, 2, 0, 4), ('cubic', 2, 2, 0, 2, 2, 0), ('quadratic', 3, -1, 3, -2), ('line', 3, -8), ('line', 3, 0)],
    "v_t": [('quadratic', 2, 4, 0, 8), ('cubic', 2, 4, 0, 4, 2, 0), ('quadratic', 3, -2, 3, -3), ('line', 3, -4), ('line', 3, 0)],
    "v_d": [('quadratic', 2, 4, 0, 8), ('cubic', 2, 4, 0, 4, 2, 0), ('quadratic', 3, -2, 3, -3), ('line', 3, -8), ('line', 3, 0)],

    "m_s": [('cubic',1,1,1,2,0.5,2),('cubic',0,2,0,1,0,0), ('quadratic', 0, -4, 1, -4), ('quadratic', 2, -4, 2, 0)],
    "m_z": [('cubic',1,1,1,2,0.5,2),('cubic',0,2,0,1,0,0), ('quadratic', 0, -8, 1, -8), ('quadratic', 2, -8, 2, 0)],

    "s_m": [('quadratic', 0, -4, 1, -4), ('quadratic', 2, -4, 2, 0), ('cubic', 2, 1, 2, 2, 1.5, 2), ('cubic', 1, 2, 1, 1, 2, 0)],
    # th/dh rising straight into t/d, instead of a flat run between them ("withdrew")
    "th_t": [('line',0,4),('line',0,2),('quadratic',0,0,1,-2),('line',1,-4),('line',1,0)],
    "th_d": [('line',0,4),('line',0,2),('quadratic',0,0,1,-2),('line',1,-8),('line',1,0)],
    "dh_t": [('line',0,8),('line',0,2),('quadratic',0,0,1,-2),('line',1,-4),('line',1,0)],
    "dh_d": [('line',0,8),('line',0,2),('quadratic',0,0,1,-2),('line',1,-8),('line',1,0)],
    "th_t-end": [('line',0,4),('line',0,2),('quadratic',0,0,1,-2),('line',1,-4),('move',1,0)],
    "th_d-end": [('line',0,4),('line',0,2),('quadratic',0,0,1,-2),('line',1,-8),('move',1,0)],
    "dh_t-end": [('line',0,8),('line',0,2),('quadratic',0,0,1,-2),('line',1,-4),('move',1,0)],
    "dh_d-end": [('line',0,8),('line',0,2),('quadratic',0,0,1,-2),('line',1,-8),('move',1,0)],
    "z_m": [('quadratic', 0, -8, 1, -8), ('quadratic', 2, -8, 2, 0), ('cubic', 2, 1, 2, 2, 1.5, 2), ('cubic', 1, 2, 1, 1, 2, 0)]
}

def keep_some_y_w(in_string):
    return in_string.replace('wu','uWu').replace('ji','ɪYɪ').replace('iɪŋ','ɪɪYɪŋ').replace('iiŋ','ɪYɪŋ').replace("oʊ","ou").replace("aʊ","au")

# Pronunciation lookup.
#
# eng_to_ipa.convert() picks the alphabetically *last* variant of each word
# (cmu_to_ipa sorts them, get_top takes [-1]), which gives reduced or odd
# forms: "hundred" -> hənərd, "nice" -> nis, "us" -> U.S.  We query the CMU
# table ourselves so the dictionary's own primary pronunciation comes first.
import re
import sqlite3
from os.path import join, dirname
from eng_to_ipa.transcribe import cmu_to_ipa

_cmu_cursor = None
_cmu_cache = {}

def cmu_variants(word):
    """IPA pronunciations of a lower-case word, in CMU dictionary order ([] if unknown)."""
    global _cmu_cursor
    if word not in _cmu_cache:
        if _cmu_cursor is None:
            _cmu_cursor = sqlite3.connect(join(dirname(ipa.__file__), "resources", "CMU_dict.db")).cursor()
        rows = _cmu_cursor.execute("SELECT phonemes FROM dictionary WHERE word = ? ORDER BY id", (word,)).fetchall()
        _cmu_cache[word] = [cmu_to_ipa([[r[0]]])[0][0] for r in rows]
    return _cmu_cache[word]

# Words whose dictionary primary isn't what a reader expects.
pronunciation_overrides = {
    "us": "əs",
}

# Heteronyms whose pronunciation follows part of speech: (noun/adjective form, verb form).
# The verb form is used after a word that usually precedes a verb.
heteronyms = {
    "close": ("kloʊs", "kloʊz"),
    "use": ("jus", "juz"),
    "excuse": ("ɪkskjus", "ɪkskjuz"),
    "abuse": ("əbjus", "əbjuz"),
}
verb_cues = {"to", "will", "would", "could", "should", "shall", "can", "must", "might", "may",
             "did", "do", "does", "don't", "didn't", "won't", "i", "we", "you", "they", "let's", "please"}

letter_names = {
    "a": "eɪ", "b": "bi", "c": "si", "d": "di", "e": "i", "f": "ɛf", "g": "ʤi", "h": "eɪʧ",
    "i": "aɪ", "j": "ʤeɪ", "k": "keɪ", "l": "ɛl", "m": "ɛm", "n": "ɛn", "o": "oʊ", "p": "pi",
    "q": "kju", "r": "ɑr", "s": "ɛs", "t": "ti", "u": "ju", "v": "vi", "w": "dəbəlju",
    "x": "ɛks", "y": "waɪ", "z": "zi",
}

IPA_VOWELS = set("iɪɛeæʊəɑaouɔ")
VOICELESS = set("ptkfθ")
SIBILANTS = set("szʃʒʧʤ")

def _plural(base):
    end = base.rstrip("ˈˌ")[-1:]
    return base + ("ɪz" if end in SIBILANTS else "s" if end in VOICELESS else "z")

def _past(base):
    end = base.rstrip("ˈˌ")[-1:]
    return base + ("ɪd" if end in "td" else "t" if end in VOICELESS | set("sʃʧ") else "d")

# (suffix, how to rebuild, candidate stem endings to restore)
_suffixes = [
    ("'s", _plural, [""]),
    ("ness", lambda b: b + "nəs", ["", "y"]),
    ("less", lambda b: b + "ləs", [""]),
    ("ment", lambda b: b + "mənt", [""]),
    ("ful", lambda b: b + "fəl", [""]),
    ("ing", lambda b: b + "ɪŋ", ["", "e", "_"]),
    ("ly", lambda b: b + "li", ["", "le"]),
    ("ed", _past, ["", "e", "_"]),
    ("est", lambda b: b + "ɪst", ["", "e"]),
    ("er", lambda b: b + "ər", ["", "e", "_"]),
    ("es", _plural, [""]),
    ("s", _plural, [""]),
]
_prefixes = [("un", "ən"), ("re", "ri"), ("dis", "dɪs"), ("be", "bɪ"), ("over", "oʊvər"),
             ("under", "əndər"), ("non", "nɑn"), ("mis", "mɪs"), ("pre", "pri"), ("out", "aʊt")]

def _morph_guess(word, depth=0):
    """Pronounce an unknown word from known pieces: suffixes, prefixes, compounds."""
    if depth > 2:
        return None
    for suffix, rebuild, restores in _suffixes:
        if word.endswith(suffix) and len(word) - len(suffix) >= 2:
            stem = word[:-len(suffix)]
            for r in restores:
                if r == "_":  # doubled final consonant: "clanged" no, "lugged" -> lug
                    cand = stem[:-1] if len(stem) > 2 and stem[-1] == stem[-2] else None
                elif r:
                    cand = stem[:-1] + r if r == "le" or (r == "y" and stem.endswith("i")) else stem + r
                    if r == "y" and not stem.endswith("i"):
                        continue
                else:
                    cand = stem
                if cand:
                    base = lookup_word(cand, depth + 1, guess=False)
                    if base:
                        return rebuild(base)
    for prefix, sound in _prefixes:
        if word.startswith(prefix) and len(word) - len(prefix) >= 3:
            base = lookup_word(word[len(prefix):], depth + 1, guess=False)
            if base:
                return sound + base
    for i in range(3, len(word) - 2):
        left = lookup_word(word[:i], depth + 1, guess=False)
        if left:
            right = lookup_word(word[i:], depth + 1, guess=False)
            if right:
                return left + right
    return None

# Ordered spelling -> sound rules for words that aren't in the dictionary at all.
_letter_rules = [
    ("tch", "ʧ"), ("sch", "sk"), ("ch", "ʧ"), ("sh", "ʃ"), ("th", "θ"), ("ph", "f"), ("wh", "w"),
    ("ck", "k"), ("ng", "ŋ"), ("qu", "kw"), ("gh", ""), ("kn", "n"), ("wr", "r"),
    ("ee", "i"), ("ea", "i"), ("oo", "u"), ("ou", "aʊ"), ("ow", "aʊ"), ("ai", "eɪ"), ("ay", "eɪ"),
    ("oi", "ɔɪ"), ("oy", "ɔɪ"), ("au", "ɔ"), ("aw", "ɔ"), ("ie", "i"), ("ei", "eɪ"), ("ue", "u"),
    ("ew", "u"), ("oa", "oʊ"), ("er", "ər"), ("ir", "ər"), ("ur", "ər"), ("ar", "ɑr"), ("or", "ɔr"),
]
_long_vowel = {"a": "eɪ", "e": "i", "i": "aɪ", "o": "oʊ", "u": "u", "y": "aɪ"}
_short_vowel = {"a": "æ", "e": "ɛ", "i": "ɪ", "o": "ɑ", "u": "ə", "y": "ɪ"}
_consonants = set("bcdfghjklmnpqrstvwxz")

def spell_guess(word):
    """Rough letter-to-sound guess, using only sounds Grafoni can write (never 'x' or bare 'c')."""
    w = re.sub(r"[^a-z]", "", word.lower())
    w = re.sub(r"([bcdfgklmnprstvz])\1", r"\1", w)  # doubled consonants sound single
    silent_e = len(w) > 2 and w.endswith("e") and w[-2] in _consonants and w[-3] in "aeiouy"
    if silent_e:
        w = w[:-1]
    out = ""
    i = 0
    while i < len(w):
        for spelling, sound in _letter_rules:
            if w.startswith(spelling, i):
                out += sound
                i += len(spelling)
                break
        else:
            c = w[i]
            nxt = w[i + 1] if i + 1 < len(w) else ""
            if c in _long_vowel:
                if c == "y" and i == 0 and nxt in "aeiou" and nxt:
                    out += "j"
                elif c == "y" and i == len(w) - 1:
                    out += "i"
                elif silent_e and i == len(w) - 2:
                    out += _long_vowel[c]
                else:
                    out += _short_vowel[c]
            elif c == "c":
                out += "s" if nxt in ("e", "i", "y") and nxt else "k"
            elif c == "q":
                out += "k"
            elif c == "x":
                out += "z" if i == 0 else "ks"
            elif c == "j":
                out += "ʤ"
            elif c == "g" and nxt in ("e", "i", "y") and nxt and i == len(w) - 2:
                out += "ʤ"
            else:
                out += c
            i += 1
    return out

LOG_UNKNOWN_WORDS = None  # set to a filename to log words that needed a guessed pronunciation

def lookup_word(word, depth=0, guess=True):
    """IPA for one word (letters, digits and internal apostrophes), or None if guess=False and unknown."""
    lower = word.lower()
    if lower in pronunciation_overrides:
        return pronunciation_overrides[lower]
    if lower.isdigit():
        return lower
    variants = cmu_variants(lower)
    if variants:
        # Where the dictionary also records an ɔ form ("bought", "caught"), keep that distinction.
        open_o = variants[0].replace("ɑ", "ɔ")
        return open_o if open_o in variants[1:] else variants[0]
    morph = _morph_guess(lower, depth)
    if morph or not guess:
        return morph
    if LOG_UNKNOWN_WORDS:
        with open(LOG_UNKNOWN_WORDS, "a") as f:
            f.write(word + "\n")
    if 2 <= len(word) <= 5 and word.isupper() and word.isalpha():
        return "".join(letter_names[c] for c in lower)  # acronym: spell it out
    return spell_guess(lower)

def cleaner_ipa(in_string):
    # Separate punctuation that joins two words ("know--know", "ultra-wave").
    text = re.sub(r'([\w\'])([^\w\'\s]+)([\w\'])', r'\1\2 \3', in_string)
    tokens = text.split()
    words = []  # (leading punct, word, trailing punct)
    for tok in tokens:
        m = re.match(r"^([^A-Za-z0-9]*)(.*?)([^A-Za-z0-9]*)$", tok)
        words.append(m.groups())
    out = []
    for i, (before, word, after) in enumerate(words):
        lower = word.lower()
        prev = words[i - 1][1].lower() if i > 0 and not words[i - 1][2] else ""
        nxt = words[i + 1][1] if i + 1 < len(words) and not after else ""
        if not word:
            sound = ""
        elif lower == "the":
            following = lookup_word(nxt) if nxt else ""
            sound = "ði" if following.lstrip("ˈˌ")[:1] in IPA_VOWELS else "ðə"
        elif lower in heteronyms:
            sound = heteronyms[lower][1 if prev in verb_cues else 0]
        else:
            sound = lookup_word(word)
        out.append(before + sound + after)
    return " ".join(out)


def grafoni_spell(string):
    ipa_string = cleaner_ipa(string)
    ipa_string = keep_some_y_w(ipa_string)
    out = []
    for letter in ipa_string:
        if letter in convert_dict:
            out += convert_dict[letter]
        else:
            out += [letter]
    return out

# Anything that isn't a letter sound ends a word, so its neighbours get their start/end forms.
BOUNDARY = {" ", ",", ".", "-", ";", ":", "?", "!", '"', "'", "(", ")"}

def process_ends(in_grafoni):
    in_grafoni = [" "] + in_grafoni + [" "]
    out_grafoni = []
    for i in range(len(in_grafoni)-2):
        # beginning
        l, m, r = in_grafoni[i:i+3]
        if l in BOUNDARY and (m in ["k","g","t","d","p","b","h","x"]):
            m += "-beg"
        if l in BOUNDARY and m in ["th","dh"] and not r in ["uv1","uv2","uv3","mv1","mv2","mv3"]:
            m += "-beg"
        if l in BOUNDARY and m in ["f","v"] and not r in ["uv1","uv2","uv3"]:
            m += "-beg"
        # ending
        if r in BOUNDARY and m in ["p","b","h","x","th","dh","f","v"]:
            m += "-end"
        if r in BOUNDARY and m in ["t","d"] and not l in ["lv1","lv2","lv3","mv1","mv2","mv3"]:
            m += "-end"
        if r in BOUNDARY and m in ["k","g"] and not l in ["lv1","lv2","lv3"]:
            m += "-end"
        out_grafoni.append(m)
    return out_grafoni

# change last curve to be a little longer, and flat.  do nothing with negatives, but do something with non-negatives, including zero
def r_extend(strokes,length=1):
    strokes = strokes.copy()
    if length < 0:
        return strokes
    s = strokes[-1]
    if s[0] == 'move':
        strokes[-1] = ('move',s[1]+length,s[2])
    if s[0] == 'line':
        strokes[-1] = ('quadratic',s[1],s[2],s[1]+length,s[2])
    if s[0] == 'quadratic':
        strokes[-1] = ('cubic',s[1],s[2],s[3],s[4],s[3]+length,s[4])
    if s[0] == 'cubic':
        strokes[-1] = ('cubic',s[1],s[2],s[3],s[6],s[5]+length,s[6]) #note I kinda just flatten the end
    return strokes

# change first curve to be a little longer and flat, translate the rest
# assumes you start at 0,0 (as all should)
def l_extend(strokes,length = 1):
    strokes = strokes.copy()
    if length < 0:
        return strokes
    s = strokes[0]
    if s[0] == 'move':
        strokes[0] = ('move',s[1]+length,s[2])
    if s[0] == 'line':
        strokes[0] = ('quadratic',length,0,s[1]+length,s[2])
    if s[0] == 'quadratic':
        strokes[0] = ('cubic',length,0,s[1]+length,s[2],s[3]+length,s[4])
    if s[0] == 'cubic':
        strokes[0] = ('cubic',s[1]+length,0,s[3]+length,s[4],s[5]+length,s[6]) #note I kinda just flatten the end
    return [strokes[0]] + translate(strokes[1:],length,0)

def make_ligatures(in_list):
    out = []
    last = "None"
    for c in in_list:
        potential = last + "_" + c
        if potential in ligatures:
            out.append(potential) 
            last = "None"
        else:
            if last != "None":
                out.append(last)
            last = c
    if last != "None":
        out.append(last)
    return out

def first(string):
    parts = string.split("_")
    if len(parts) == 0:
        return " "
    else:
        return parts[0]

def last(string):
    parts = string.split("_")
    if len(parts) == 0:
        return " "
    else:
        return parts[-1]

def v_nudge(paths,nudge_size = 0.1):
    if nudge_size < 0:
        return paths
    paths = paths.copy()
    last = paths[-1]
    paths+=[('quadratic',last[-2]+nudge_size,last[-1],last[-2]+nudge_size,last[-1]+nudge_size),('line',last[-2]+nudge_size,last[-1])]
    return paths

nudge_kern = defaultdict(lambda:-1)
nudge_kern[('mv1','mv1')] = 1
nudge_kern[('mv2','mv1')] = 1
nudge_kern[('mv3','mv1')] = 1
nudge_kern[('mv1','mv2')] = 1
nudge_kern[('mv2','mv2')] = 1
nudge_kern[('mv3','mv2')] = 1
nudge_kern[('mv1','mv3')] = 1
nudge_kern[('mv2','mv3')] = 1
nudge_kern[('mv3','mv3')] = 1

def to_list(in_string):
    return make_ligatures(process_ends(grafoni_spell(in_string)))

def to_svg(in_string,wrap = 100,shear_val=-1/sqrt(3),line_space=20,v_scale=0.5):
    chars = in_string
    if isinstance(chars, str):
        chars = to_list(in_string)
    #print(" ".join(chars))
    out = [('move',0,0)]
    last_char = " "
    for l in chars:
        if l in letter_forms:
            l_kern,r_kern,n_val = pair_kerning(last_char,l)
            last_char = l
            out = concat(v_nudge(r_extend(out,l_kern),n_val),l_extend(letter_forms[l],r_kern))
        elif l in ligatures:
            l_kern,r_kern,n_val = pair_kerning(last_char,l)
            last_char = l
            out = concat(v_nudge(r_extend(out,l_kern),n_val),l_extend(ligatures[l],r_kern))
        else:
            print("Unsupported Character: " + l)
        if last_char == " "  and out[-1][-2] + shear_val*v_scale*out[-1][-1] > wrap:
            out.append(('move',-shear_val*v_scale*(out[-1][-1]+line_space),out[-1][-1]+line_space))
    return display(svgStrokes(shear(scale(out,1,v_scale),by=shear_val)))

def bounding_box(strokes):
    min_x = 0
    min_y = 0
    max_x = 0
    max_y = 0
    for stroke in strokes:
        if stroke[0] == 'move':
            min_x = min(min_x,stroke[1])
            min_y = min(min_y,stroke[2])
            max_x = max(max_x,stroke[1])
            max_y = max(max_y,stroke[2])
        if stroke[0] == 'line':
            min_x = min(min_x,stroke[1])
            min_y = min(min_y,stroke[2])
            max_x = max(max_x,stroke[1])
            max_y = max(max_y,stroke[2])
        if stroke[0] == 'quadratic':
            min_x = min(min_x,stroke[1],stroke[3])
            min_y = min(min_y,stroke[2],stroke[4])
            max_x = max(max_x,stroke[1],stroke[3])
            max_y = max(max_y,stroke[2],stroke[4])
        if stroke[0] == 'cubic':
            min_x = min(min_x,stroke[1],stroke[3],stroke[5])
            min_y = min(min_y,stroke[2],stroke[4],stroke[6])
            max_x = max(max_x,stroke[1],stroke[3],stroke[5])
            max_y = max(max_y,stroke[2],stroke[4],stroke[6])
    return min_x, min_y, max_x, max_y

def svgStrokes(strokes, scale = 4,padding = 1, stroke_width = 1.0/3):
    path = draw.Path(stroke='black', fill='none', stroke_width = stroke_width*scale, stroke_linecap='round', stroke_linejoin='round')
    min_x,min_y,max_x,max_y = bounding_box(strokes)
    for stroke in strokes:
        if stroke[0] == 'move':
            path.M(scale*(stroke[1]-min_x)+scale*padding,scale*(stroke[2]-min_y)+scale*padding)
        if stroke[0] == 'line':
            path.L(scale*(stroke[1]-min_x)+scale*padding,scale*(stroke[2]-min_y)+scale*padding)
        if stroke[0] == 'quadratic':
            path.Q(scale*(stroke[1]-min_x)+scale*padding,scale*(stroke[2]-min_y)+scale*padding,scale*(stroke[3]-min_x)+scale*padding,scale*(stroke[4]-min_y)+scale*padding)
        if stroke[0] == 'cubic':
            path.C(scale*(stroke[1]-min_x)+scale*padding,scale*(stroke[2]-min_y)+scale*padding,scale*(stroke[3]-min_x)+scale*padding,scale*(stroke[4]-min_y)+scale*padding,scale*(stroke[5]-min_x)+scale*padding,scale*(stroke[6]-min_y)+scale*padding)
    
    d = draw.Drawing(scale*(max_x-min_x)+2*scale*padding,scale*(max_y-min_y)+2*scale*padding)
    d.append(draw.Use(path,0,0))
    return d

def translate(strokes,dx,dy):
    out = []
    for s in strokes:
        if s[0] == 'move':
            out.append(('move',s[1]+dx,s[2]+dy))
        if s[0] == 'line':
            out.append(('line',s[1]+dx,s[2]+dy))
        if s[0] == 'quadratic':
            out.append(('quadratic',s[1]+dx,s[2]+dy,s[3]+dx,s[4]+dy))
        if s[0] == 'cubic':
            out.append(('cubic',s[1]+dx,s[2]+dy,s[3]+dx,s[4]+dy,s[5]+dx,s[6]+dy))
    return out

def scale(strokes,dx,dy):
    out = []
    for s in strokes:
        if s[0] == 'move':
            out.append(('move',s[1]*dx,s[2]*dy))
        if s[0] == 'line':
            out.append(('line',s[1]*dx,s[2]*dy))
        if s[0] == 'quadratic':
            out.append(('quadratic',s[1]*dx,s[2]*dy,s[3]*dx,s[4]*dy))
        if s[0] == 'cubic':
            out.append(('cubic',s[1]*dx,s[2]*dy,s[3]*dx,s[4]*dy,s[5]*dx,s[6]*dy))
    return out

def concat(strokes, new):
    last_x, last_y = strokes[-1][-2:]
    return strokes + translate(new,last_x,last_y)

def shear(strokes,by=-1):
    out = []
    for s in strokes:
        if s[0] == 'move':
            out.append(('move',s[1]+by*s[2],s[2]))
        if s[0] == 'line':
            out.append(('line',s[1]+by*s[2],s[2]))
        if s[0] == 'quadratic':
            out.append(('quadratic',s[1]+by*s[2],s[2],s[3]+by*s[4],s[4]))
        if s[0] == 'cubic':
            out.append(('cubic',s[1]+by*s[2],s[2],s[3]+by*s[4],s[4],s[5]+by*s[6],s[6]))
    return out