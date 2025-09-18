"""
Corpus utilities for Tamil-first text processing.

Includes:
- normalize_punct: quote/ellipsis/spacing harmonization
- dedup_lines: stable de-duplication of text lines
- filter_by_length: character / token length filters
- window_sents: sliding windows of sentences for RAG-style chunks
"""

from __future__ import annotations
from typing import Iterable, Iterator, List, Optional
import regex as re

from .core import normalize, tokens, sents

# --- Punctuation normalization ------------------------------------------------

# Map curly quotes / guillemets / ellipsis to simple ASCII
_PUNCT_MAP = str.maketrans({
    "“": '"', "”": '"', "„": '"', "«": '"', "»": '"',
    "‘": "'", "’": "'", "‚": "'", "‹": "'", "›": "'",
    "…": "...",  # convert Unicode ellipsis to three dots
})

# Characters that should have:
# - no space BEFORE them
# - exactly one space AFTER them (unless EOL), but NOT when followed by punctuation
_AFTER_CHARS = r",.!?:;"
_CLOSE_CHARS = r")]}"

_WS_RE = re.compile(r"[^\S\r\n]+")  # collapse internal whitespace (preserve newlines)

# remove spaces before punctuation and closers
_SPACE_BEFORE_PUNCT_RE = re.compile(rf"\s+([{_AFTER_CHARS}])")
_SPACE_BEFORE_CLOSE_RE = re.compile(rf"\s+([{_CLOSE_CHARS}])")

# add one space after punctuation ONLY if next char is not whitespace and not punctuation
_SPACE_AFTER_PUNCT_RE = re.compile(rf"([{_AFTER_CHARS}])([^\s{_AFTER_CHARS}])")


def normalize_punct(text: str) -> str:
    """
    Harmonize quotes/ellipsis and tidy common spacing around ASCII/Tamil punctuation.

    - Curly quotes/guillemets → straight quotes
    - Ellipsis (…) → "..." and enforced as a token with a space on both sides
    - Collapse internal whitespace
    - Remove spaces *before* .,!?:; and closing brackets )]}
    - Ensure a single space *after* .,!?:; when followed by a non-space, non-punct char
    """
    if not text:
        return text

    s = normalize(text).translate(_PUNCT_MAP)

    # collapse internal spaces (leave newlines intact)
    s = _WS_RE.sub(" ", s)

    # no space before .,!?;: and closing brackets
    s = _SPACE_BEFORE_PUNCT_RE.sub(r"\1", s)
    s = _SPACE_BEFORE_CLOSE_RE.sub(r"\1", s)

    # exactly one space after .,!?;: if not followed by whitespace or punctuation
    s = _SPACE_AFTER_PUNCT_RE.sub(r"\1 \2", s)

    # --- Ellipsis handling LAST: enforce spaces around '...' without breaking inside ---
    # (1) collapse any surrounding spaces to exactly one on each side
    # leading/trailing spaces will be trimmed by final strip
    s = re.sub(r"\s*\.\.\.\s*", " ... ", s)

    # collapse any accidental double spaces introduced
    s = re.sub(r"[^\S\r\n]{2,}", " ", s)

    return s.strip()


# --- De-duplication -----------------------------------------------------------

def dedup_lines(lines: Iterable[str], *, casefold: bool = True, strip: bool = True) -> List[str]:
    """
    Stable de-duplication of lines.

    Args:
        lines: iterable of text lines
        casefold: if True, casefold key (affects Latin)
        strip: if True, strip key

    Returns:
        List of unique lines preserving first occurrence order.
    """
    seen = set()
    out: List[str] = []
    for line in lines:
        key = line
        if strip:
            key = key.strip()
        if casefold:
            key = key.casefold()
        if key not in seen:
            seen.add(key)
            out.append(line)
    return out


# --- Length filters -----------------------------------------------------------

def filter_by_length(
    texts: Iterable[str],
    *,
    min_chars: Optional[int] = None,
    max_chars: Optional[int] = None,
    min_tokens: Optional[int] = None,
    max_tokens: Optional[int] = None,
) -> Iterator[str]:
    """
    Yield texts that satisfy character/token length constraints.

    Tokens use tamil_utils.tokens() on normalized text.
    """
    for t in texts:
        T = normalize(t)
        if min_chars is not None and len(T) < min_chars:
            continue
        if max_chars is not None and len(T) > max_chars:
            continue
        if min_tokens is not None or max_tokens is not None:
            n = len(tokens(T))
            if min_tokens is not None and n < min_tokens:
                continue
            if max_tokens is not None and n > max_tokens:
                continue
        yield t


# --- Sentence windows for RAG -------------------------------------------------

def window_sents(
    text: str,
    *,
    k: int = 3,
    stride: int = 1,
    join_with: str = " ",
) -> List[str]:
    """
    Slide over sentence list and join K sentences per window.

    Example:
        >>> window_sents("A. B. C. D.", k=2, stride=1)
        ['A. B.', 'B. C.', 'C. D.']
    """
    ss = sents(normalize(text))
    if not ss:
        return []
    out: List[str] = []
    i = 0
    while i + k <= len(ss):
        out.append(join_with.join(ss[i:i+k]))
        i += max(1, stride)
    return out
