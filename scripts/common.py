REPLACE_MAP = {
    ":": "COLON",
    ",": "COMMA",
    ".": "PERIOD",
    ";": "SEMICOLON",
    "-": "HYPHEN",
    "[": "LSB",
    "]": "RSB",
    "(": "LRB",
    ")": "RRB",
    "{": "LCB",
    "}": "RCB",
    "!": "EXC",
    "?": "QUE",
    "'": "SQ",
    '"': "DQ",
    "/": "PER",
    "\\": "BSL",
    "#": "HASHTAG",
    "%": "PERCENT",
    "&": "ET",
    "@": "AT",
    "$": "DOLLAR",
    "*": "ASTERISK",
    "^": "CAP",
    "`": "IQ",
    "+": "=",
    "|": "PIPE",
    "~": "TILDE",
    "<": "LESS",
    ">": "MORE",
    "=": "EQ",
    '¢': 'cent',
    '£': 'pound ',
    '¥': 'yen',
    '¨': 'umlaut',
    '°': 'degrees',
    '²': '^2',
    'º': ' degrees',
    '¼': ' 1/4',
    '½': ' 1/2 ',
    '¾': ' 3/4 ',
    'à': 'a',
    'â': 'a',
    'ç': 'c',
    'è': 'e',
    'é': 'e',
    'ê': 'e',
    'ñ': 'nj',
    'ô': 'o',
    'ŋ': 'nh',
    'ə': 'e',
    'ˈ': 'SQ',
    'ˌ': ',',
    'β': 'beta',
    'π': 'pi',
    '–': '-',
    '♭': 'b',
    '〃': 'repeat',
    '₂': '2',
    '™': 'TM'
    }

KEYWORDS = set(["feature", "interpretation"])

dict_pos_to_irtg_pos = {
    'adj': 'ADJ',
    'adv': 'ADV',
    'adj, adv': ['ADJ', 'ADV'],
    'adv, prep': ['ADV', 'ADP'],
    'auxiliary verb': 'AUX',
    'conjunction': ['CCONJ', 'SCONJ'],
    'definite article': 'DET',
    'determiner': 'DET',
    'indefinite article': 'DET',
    'interjection': 'INTJ',
    'modal verb': 'AUX',
    'n': ['NOUN', 'PROPN'],
    'n,v': ['NOUN', 'PROPN', 'VERB', 'AUX'],
    'noun': ['NOUN', 'PROPN'],
    'number': 'NUM',
    'possessive adj': 'DET',
    'possessive pron': 'PRON',
    'predeterminer': 'DET',
    'prefix': 'ADP',
    'prep': 'ADP',
    'pron': 'PRON',
    'quantifier': 'NUM',
    'suffix': 'ADP',
    'v': ['VERB', 'AUX'],
    'X': 'X',
    '-': 'X',
    'ADJ': 'ADJ',
    'ADP': 'ADP',
    'ADV': 'ADV',
    'AUX': 'AUX',
    'CCONJ': 'CCONJ',
    'DET': 'DET',
    'INTJ': 'INTJ',
    'NOUN': 'NOUN',
    'NUM': 'NUM',
    'PART': 'PART',
    'PRON': 'PRON',
    'PROPN': 'PROPN',
    'PUNCT': 'PUNCT',
    'SCONJ': 'SCONJ',
    'SYM': 'SYM',
    'VERB': 'VERB'
}


def switch_key_and_value(dict_):
    new_dict = {}
    for key, value in dict_.items():
        new_dict[value] = key
    return new_dict


def sanitize_word(word):
    for patt, tgt in REPLACE_MAP.items():
        word = word.replace(patt, tgt)
    for digit in "0123456789":
        word = word.replace(digit, "DIGIT")
    if word in KEYWORDS:
        word = word.upper()
    return word


def desanitize_word(word):
    dict_ = switch_key_and_value(REPLACE_MAP)
    for patt, tgt in dict_.items():
        word = word.replace(patt, tgt)
    if word.lower() in KEYWORDS:
        word = word.lower()
    return word
