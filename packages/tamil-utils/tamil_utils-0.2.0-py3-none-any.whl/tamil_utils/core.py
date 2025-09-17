import unicodedata
import regex as re
from collections import Counter
from typing import Iterable, List, Tuple

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

# -------------------- v0.2: Developer-quality utilities --------------------

def ngrams(seq: Iterable[str], n: int) -> List[Tuple[str, ...]]:
    """Return n-grams as tuples from a sequence of tokens."""
    seq = list(seq)
    if n <= 0:
        raise ValueError("n must be >= 1")
    return [tuple(seq[i:i+n]) for i in range(len(seq)-n+1)]

def bigrams(seq: Iterable[str]) -> List[Tuple[str, str]]:
    return ngrams(seq, 2)

def trigrams(seq: Iterable[str]) -> List[Tuple[str, str, str]]:
    return ngrams(seq, 3)

def word_counts(text_or_tokens, *, rmstop: bool = False, preset: str = "ta",
                n: int = 1, top: int | None = None) -> List[Tuple[str, int]]:
    """
    Count token or n-gram frequencies.
    - text_or_tokens: raw string or a token iterable
    - rmstop: remove stopwords using preset (when n==1)
    - n: 1 for unigrams (default), 2/3 for bi/tri-grams
    - top: return only top N (most common), else all
    Returns a list of (item, count) sorted by count desc.
    """
    if isinstance(text_or_tokens, str):
        toks = tokens(text_or_tokens)
    else:
        toks = list(text_or_tokens)

    if n == 1 and rmstop:
        toks = remove_stopwords(toks, preset=preset)

    if n >= 2:
        items = [" ".join(g) for g in ngrams(toks, n)]
    else:
        items = toks

    c = Counter(items)
    most = c.most_common(top)
    return most

def syllables(text: str) -> List[str]:
    """
    Approximate syllable (akshara/uyirmei) segmentation for Tamil.
    Uses grapheme clusters and filters to Tamil script clusters.
    """
    return [g for g in graphemes(text) if _TAMIL_RE.search(g)]

def _iso_collation_key(s: str) -> str:
    """
    Build an ASCII-ish key from ISO-15919 so Tamil vowels sort as:
    a < ā < i < ī < u < ū < e < ē < ai < o < ō < au
    and diacritic consonants get stable order.
    """
    t = transliterate_iso15919(normalize(s))
    # Handle vowel digraphs first (map to placeholders that sort after ē/ō)
    t = t.replace("ai", "e~~").replace("au", "o~~")
    # Long vowels sort after shorts
    t = (t.replace("ā", "a~")
           .replace("ī", "i~")
           .replace("ū", "u~")
           .replace("ē", "e~")
           .replace("ō", "o~"))
    # Stabilize consonants with diacritics
    t = (t.replace("ṭ", "t~")
           .replace("ṇ", "n~")
           .replace("ṅ", "ng")
           .replace("ñ", "ny")
           .replace("ḷ", "l~")
           .replace("ḻ", "lz")
           .replace("ṟ", "r~")
           .replace("ṉ", "n`")
           .replace("ṣ", "s~"))
    return t

def sort_tamil(words: Iterable[str]) -> List[str]:
    """
    Sort words in a consistent Tamil-first order (lightweight collation).
    Implemented by building a custom ISO-15919-based collation key.
    """
    return sorted(words, key=_iso_collation_key)
