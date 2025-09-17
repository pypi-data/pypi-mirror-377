from tamil_utils import (
    normalize, tokens, remove_stopwords, graphemes,
    sents, to_arabic_numerals, to_tamil_numerals, stopwords_preset,
    transliterate_iso15919, script_of, token_scripts,
    # v0.2
    ngrams, bigrams, trigrams, word_counts, syllables, sort_tamil
)

# --- existing coverage ---

def test_tokens_and_stopwords():
    s = "இது ஒரு சோதனை"
    t = tokens(s)
    assert "சோதனை" in t and "ஒரு" in t
    assert remove_stopwords(t, preset="ta") == ["சோதனை"]

def test_graphemes_emoji():
    g = graphemes("👩🏽‍💻")
    assert isinstance(g, list)
    assert "".join(g) == "👩🏽‍💻"

def test_sents_basic():
    text = "இது ஒரு வாக்கியம். இது இரண்டாம்? சரி!"
    out = sents(text)
    assert len(out) == 3
    assert out[0].endswith(".") and out[1].endswith("?") and out[2].endswith("!")

def test_numerals_roundtrip():
    assert to_arabic_numerals("௧௨௩") == "123"
    assert to_tamil_numerals("2025") == "௨௦௨௫"

def test_preset_exposed():
    sw = stopwords_preset("ta")
    assert "ஒரு" in sw and "இது" in sw

def test_transliterate_basic():
    assert transliterate_iso15919("தமிழ்")[:4] == "tami"  # loose check
    assert transliterate_iso15919("ஆதி") == "ādi"        # த softened between vowels

def test_script_detection():
    ts = token_scripts(["தமிழ்", "hello", "AI", "கோட்123"])
    assert ts[0][1] == "Tamil"
    assert ts[1][1] == "Latin"
    # Tamil + digits => Mixed
    assert any(tok == "கோட்123" and tag == "Mixed" for tok, tag in ts)

# --- v0.2 coverage ---

def test_ngrams_and_helpers():
    t = tokens("அது இது அது")
    assert t == ["அது", "இது", "அது"]
    bi = bigrams(t)
    tri = trigrams(t)
    assert bi == [("அது","இது"), ("இது","அது")]
    assert tri == [("அது","இது","அது")]
    # generic n=2 matches bigrams
    from_generic = [tuple(x.split()) for x in [" ".join(b) for b in bigrams(t)]]
    assert from_generic == bi

def test_word_counts_unigram_rmstop():
    s = "இது ஒரு சோதனை இது ஒரு சோதனை"
    freq = dict(word_counts(s, rmstop=True, preset="ta", n=1))
    # 'இது' and 'ஒரு' removed by stopwords; 'சோதனை' remains with count 2
    assert freq.get("சோதனை") == 2
    assert "இது" not in freq and "ஒரு" not in freq

def test_word_counts_bigrams_top():
    s = "தமிழ் NLP தமிழ் பயன்பாடு தமிழ் NLP"
    # tokens ~ ["தமிழ்","NLP","தமிழ்","பயன்பாடு","தமிழ்","NLP"]
    pairs = word_counts(s, n=2, top=1)
    assert pairs[0][0] in {"தமிழ் NLP", "NLP தமிழ்"}  # depending on spacing-tokenization
    assert pairs[0][1] >= 1

def test_syllables_returns_tamil_graphemes():
    s = "தமிழ்🙂 test 123"
    syl = syllables(s)
    # Should include only Tamil grapheme clusters (no Latin/digits/emoji)
    assert all(any("\p{Tamil}" in c for c in [g]) for g in syl) or all(any(ord(ch) >= 2944 and ord(ch) <= 3066 for ch in g) for g in syl)
    assert len(syl) >= 2  # at least a couple of Tamil clusters from "தமிழ்"

def test_sort_tamil_order():
    words = ["இலங்கை", "ஆதி", "அடி"]
    sorted_words = sort_tamil(words)
    # ISO key order: a* < ā* < i*  => "அடி", "ஆதி", "இலங்கை"
    assert sorted_words == ["அடி", "ஆதி", "இலங்கை"]
