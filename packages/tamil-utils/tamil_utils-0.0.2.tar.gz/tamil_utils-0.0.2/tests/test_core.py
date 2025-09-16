from tamil_utils import (
    normalize, tokens, remove_stopwords, graphemes,
    sents, to_arabic_numerals, to_tamil_numerals, stopwords_preset
)

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
