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

# -------------------- v0.0.2: Sentences & Numerals --------------------

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

# -------------------- v0.1: Script detection --------------------

_TAMIL_RE = re.compile(r"\p{Tamil}", re.UNICODE)
_LATIN_RE = re.compile(r"\p{Latin}", re.UNICODE)
_DIGIT_RE = re.compile(r"\p{Nd}", re.UNICODE)

def script_of(text: str) -> str:
    """Return 'Tamil', 'Latin', 'Mixed', or 'Other' for a string."""
    s = normalize(text)
    has_ta = bool(_TAMIL_RE.search(s))
    has_la = bool(_LATIN_RE.search(s))
    has_dg = bool(_DIGIT_RE.search(s))
    kinds = sum([has_ta, has_la, has_dg])
    if kinds >= 2:
        return "Mixed"
    if has_ta:
        return "Tamil"
    if has_la:
        return "Latin"
    return "Other"

def token_scripts(tok):
    """Return [(token, script_tag), ...]."""
    return [(t, script_of(t)) for t in tok]

# -------------------- v0.1: Transliteration (Tamil -> ISO 15919 lite) --------------------

# Independent vowels
_VOW_INDEP = {
    "அ":"a","ஆ":"ā","இ":"i","ஈ":"ī","உ":"u","ஊ":"ū",
    "எ":"e","ஏ":"ē","ஐ":"ai","ஒ":"o","ஓ":"ō","ஔ":"au",
}
# Vowel signs
_VOW_SIGNS = {
    "ா":"ā","ி":"i","ீ":"ī","ு":"u","ூ":"ū",
    "ெ":"e","ே":"ē","ை":"ai","ொ":"o","ோ":"ō","ௌ":"au",
}
# Consonants (basic set)
_CONS = {
    "க":"k","ங":"ṅ","ச":"c","ஞ":"ñ","ட":"ṭ","ண":"ṇ","த":"t","ந":"n",
    "ப":"p","ம":"m","ய":"y","ர":"r","ல":"l","வ":"v",
    "ழ":"ḻ","ள":"ḷ","ற":"ṟ","ன":"ṉ",
    "ஜ":"j","ஷ":"ṣ","ஸ":"s","ஹ":"h",
}
_VIRAMA = "\u0BCD"  # pulli
_AYTHAM = "ஃ"      # visarga-like; ISO often "ḥ"
_ANUSVARA = "ஂ"    # ISO 15919 uses "ṃ"

# Vowel set for detecting "between vowels" context
_VOWELS_LAT = {"a","ā","i","ī","u","ū","e","ē","ai","o","ō","au"}

def transliterate_iso15919(text: str) -> str:
    """
    Tamil -> ISO 15919 (lite, deterministic). Heuristic: soften த (t) to 'd'
    when it occurs between vowels (intervocalic).
    """
    out = []
    for g in re.findall(r"\X", normalize(text)):
        # Independent vowels
        if g in _VOW_INDEP:
            out.append(_VOW_INDEP[g])
            continue

        # Consonant cluster: base consonant + optional vowel sign or virama
        if g and g[0] in _CONS:
            base = _CONS[g[0]]  # default base
            vowel = None
            has_virama = False
            for ch in g[1:]:
                if ch in _VOW_SIGNS:
                    vowel = _VOW_SIGNS[ch]
                    break
                if ch == _VIRAMA:
                    has_virama = True
                    break

            # inherent vowel if nothing specified & no virama
            if vowel is None and not has_virama:
                vowel = "a"
            if has_virama:
                vowel = ""

            # Softening heuristic: த -> d between vowels (if current has a vowel)
            if g[0] == "த" and vowel != "":
                if out:
                    prev = out[-1]
                    if any(prev.endswith(v) for v in _VOWELS_LAT):
                        base = "d"

            out.append(base + vowel)
            continue

        # Special signs
        if g == _AYTHAM:
            out.append("ḥ"); continue
        if g == _ANUSVARA:
            out.append("ṃ"); continue

        # Pass-through (spaces, punctuation, etc.)
        out.append(g)

    return "".join(out)
