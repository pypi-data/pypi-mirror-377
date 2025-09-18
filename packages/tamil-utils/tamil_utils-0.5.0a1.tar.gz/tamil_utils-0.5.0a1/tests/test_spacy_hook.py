import pytest

spacy = pytest.importorskip("spacy", reason="spaCy not installed; skipping tokenizer hook tests")

from tamil_utils.spacy_hook import install_tamil_tokenizer

def test_spacy_tamil_tokenizer_basic():
    nlp = spacy.blank("xx")        # language-agnostic
    install_tamil_tokenizer(nlp)   # replace tokenizer (with NFC normalize)
    doc = nlp("இது ஒரு சோதனை 2025")
    assert [t.text for t in doc] == ["இது", "ஒரு", "சோதனை", "2025"]

def test_spacy_tamil_tokenizer_mixed_scripts():
    nlp = spacy.blank("xx")
    install_tamil_tokenizer(nlp)
    doc = nlp("Tamil + தமிழ் 123")
    assert [t.text for t in doc] == ["Tamil", "தமிழ்", "123"]
