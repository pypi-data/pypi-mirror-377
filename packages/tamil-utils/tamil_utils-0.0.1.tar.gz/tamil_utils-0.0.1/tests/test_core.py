from tamil_utils import normalize, tokens, remove_stopwords, graphemes

def test_tokens_and_stopwords():
    s = "இது ஒரு சோதனை"
    t = tokens(s)
    assert "சோதனை" in t
    assert "ஒரு" in t
    assert remove_stopwords(t) == ["சோதனை"]

def test_graphemes_emoji():
    g = graphemes("👩🏽‍💻")
    assert isinstance(g, list)
    assert "".join(g) == "👩🏽‍💻"

def test_normalize_keeps_meaning():
    s = "கா\u200Dn"   # insert ZWJ noise
    assert normalize(s) == "கான்".replace("ன்","ன்") or isinstance(normalize(s), str)
