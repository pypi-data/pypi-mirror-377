import pytest

from tamil_utils.corpus import (
    normalize_punct,
    dedup_lines,
    filter_by_length,
    window_sents,
)


def test_normalize_punct_basic():
    # Curly quotes + ellipsis + messy spacing before/after punctuation
    s = ' “இது”  ஒரு  சோதனை …  சரி  !  இது  இரண்டாம்  ? '
    out = normalize_punct(s)
    # Straight quotes, "..." ellipsis, no space before .!?;:, exactly one after
    assert out == '"இது" ஒரு சோதனை ... சரி! இது இரண்டாம்?'

    # Idempotent
    assert normalize_punct(out) == out


def test_dedup_lines_stable_order():
    lines = [
        "தமிழ் NLP\n",
        "தமிழ் nlp\n",
        "  தமிழ் NLP\n",
        "Tamil nlp\n",
    ]
    # default: strip + casefold → first unique kept, order preserved
    out = dedup_lines(lines)
    assert out == ["தமிழ் NLP\n", "Tamil nlp\n"]

    # If we disable strip/casefold, more items survive
    out2 = dedup_lines(lines, casefold=False, strip=False)
    assert out2 == lines  # nothing collapses


def test_filter_by_length_chars_and_tokens():
    data = ["இது", "இது ஒரு", "இது ஒரு சோதனை", "சரி!"]  # tokens: 1, 2, 3, 1-ish
    # min_chars filter
    kept = list(filter_by_length(data, min_chars=5))
    assert "இது" not in kept and "சரி!" not in kept

    # token bounds
    kept2 = list(filter_by_length(data, min_tokens=2, max_tokens=3))
    assert kept2 == ["இது ஒரு", "இது ஒரு சோதனை"]


def test_window_sents_basic_and_empty():
    txt = "இது ஒன்று. இது இரண்டு? சரி! முடிந்தது."
    # k=2, stride=1
    w = window_sents(txt, k=2, stride=1)
    assert w == ["இது ஒன்று. இது இரண்டு?", "இது இரண்டு? சரி!", "சரி! முடிந்தது."]

    # empty text
    assert window_sents("") == []
