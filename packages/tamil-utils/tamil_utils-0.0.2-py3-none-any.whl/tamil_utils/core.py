import unicodedata
import regex as re

# Keep only ZERO WIDTH SPACE removable; preserve ZWJ/ZWNJ for ligatures/shaping
_ZW = dict.fromkeys(map(ord, ["\u200B"]), None)

# Tamil-aware word pattern; also matches Latin words & digits
_WORD_RE = re.compile(r"(?:\p{Tamil}+|[A-Za-z]+|\d+)", re.UNICODE)

# --- Stopwords preset (curated starter set; expand/replace as needed) ---
_STOPWORDS_TA = {
    "மற்றும்","ஒரு","இந்த","அந்த","என்று","எனும்","அது","இது","ஆகிய","உள்ள",
    "ஆனால்","அல்லது","மேலும்","போது","பிறகு","முன்","முன்னர்","இப்போது","இன்னும்",
    "அங்கு","இங்கு","எப்போது","எப்படி","ஏன்","எங்கே","எவர்","எது",
    "நான்","நீ","நீங்கள்","நாம்","அவர்","அவள்","அவர்கள்","என்","எங்கள்","உன்",
}

def stopwords_preset(name: str = "ta"):
    """Return a stopword set by preset name."""
    if name.lower() in {"ta", "tamil"}:
        return set(_STOPWORDS_TA)
    raise ValueError(f"Unknown stopwords preset: {name}")

# -------------------- Core API --------------------

def normalize(text: str) -> str:
    """NFC normalize + strip safe zero-width characters (preserves ZWJ/ZWNJ)."""
    if not isinstance(text, str):
        raise TypeError("normalize() expects str")
    text = unicodedata.normalize("NFC", text)
    return text.translate(_ZW)

def tokens(text: str):
    """Minimal Tamil/Latin/digit tokenization."""
    return _WORD_RE.findall(normalize(text))

def remove_stopwords(tok, stopwords=None, preset=None):
    """
    Filter out stopwords. If 'stopwords' not provided, you can pass preset="ta".
    """
    if stopwords is None and preset is not None:
        stopwords = stopwords_preset(preset)
    sw = set(stopwords) if stopwords else set()
    return [t for t in tok if t not in sw]

def graphemes(text: str):
    """Return Unicode grapheme clusters (handles combining marks & emoji)."""
    return re.findall(r"\X", normalize(text))

# -------------------- New in v0.0.2 --------------------

# Sentence splitter: split on . ! ? … । or newlines; keep punctuation with the sentence
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?…।])\s+|\n+")

def sents(text: str):
    """Split text into sentences (Tamil/Latin punctuation aware)."""
    if not text:
        return []
    text = normalize(text).strip()
    parts = [s.strip() for s in _SENT_SPLIT_RE.split(text) if s.strip()]
    return parts

# Numerals: Tamil (U+0BE6..U+0BEF) ↔ Arabic 0-9
_TA_DIGITS = "௦௧௨௩௪௫௬௭௮௯"
_AR_DIGITS = "0123456789"
_TA_TO_AR = {ord(t): a for t, a in zip(_TA_DIGITS, _AR_DIGITS)}
_AR_TO_TA = {ord(a): t for t, a in zip(_TA_DIGITS, _AR_DIGITS)}

def to_arabic_numerals(text: str) -> str:
    """Convert Tamil digits to ASCII digits."""
    return normalize(text).translate(_TA_TO_AR)

def to_tamil_numerals(text: str) -> str:
    """Convert ASCII digits to Tamil digits."""
    return normalize(text).translate(_AR_TO_TA)
