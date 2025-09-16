import unicodedata
import regex as re

# Zero-width characters: ZWSP, ZWNJ, ZWJ, WJ
_ZW = dict.fromkeys(map(ord, ["\u200B"]), None)

# Tamil-aware word pattern; keeps Tamil words intact; also matches Latin words & digits
_WORD_RE = re.compile(r"(?:\p{Tamil}+|[A-Za-z]+|\d+)", re.UNICODE)

# Small demo stopword set (replace/extend later)
_DEFAULT_STOPWORDS = {
    "மற்றும்", "ஒரு", "இந்த", "என்று", "அது", "இது", "ஆகிய", "உள்ள",
}

def normalize(text: str) -> str:
    """NFC normalize + strip zero-width characters."""
    if not isinstance(text, str):
        raise TypeError("normalize() expects str")
    text = unicodedata.normalize("NFC", text)
    return text.translate(_ZW)

def tokens(text: str):
    """Minimal Tamil/Latin/digit tokenization."""
    return _WORD_RE.findall(normalize(text))

def remove_stopwords(tok, stopwords=None):
    """Filter out Tamil stopwords."""
    sw = set(stopwords) if stopwords else _DEFAULT_STOPWORDS
    return [t for t in tok if t not in sw]

def graphemes(text: str):
    """Return Unicode grapheme clusters (handles combining marks & emoji)."""
    # Uses the 'regex' module's \X which matches extended grapheme clusters
    return re.findall(r"\X", normalize(text))
