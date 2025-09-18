"""
spaCy hook: install a Tamil-aware tokenizer that mirrors tamil_utils tokenization.

This is OPTIONAL at runtime. We import spaCy only inside functions so that
tamil-utils keeps zero hard dependencies beyond 'regex'.

Usage:
    import spacy
    from tamil_utils.spacy_hook import install_tamil_tokenizer

    nlp = spacy.blank("xx")     # language-agnostic defaults are fine
    install_tamil_tokenizer(nlp)  # replaces nlp.tokenizer (with NFC normalize)
    doc = nlp("இது ஒரு சோதனை")
    print([t.text for t in doc])  # -> ['இது','ஒரு','சோதனை']
"""

from __future__ import annotations
import regex as re
from .core import normalize

__all__ = ["make_tamil_tokenizer", "install_tamil_tokenizer"]

# Tamil/Latin/digit word units: match the same segmentation as tamil_utils.tokens
_TOKEN_RE = re.compile(r"(?:\p{Tamil}+|[A-Za-z]+|\d+)", re.UNICODE)


def make_tamil_tokenizer(nlp):
    """
    Return a spaCy Tokenizer that:
      - keeps spaCy's default prefixes/suffixes/infixes
      - uses a token_match that glues Tamil sequences (and Latin/digits) as words
    """
    try:
        from spacy.tokenizer import Tokenizer
        from spacy.util import (
            compile_prefix_regex,
            compile_suffix_regex,
            compile_infix_regex,
        )
    except Exception as e:
        raise RuntimeError(
            "spaCy is not installed. `pip install spacy` to use the tokenizer hook."
        ) from e

    prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
    suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)
    infix_re = compile_infix_regex(nlp.Defaults.infixes)

    def token_match(text):
        # Use our unified regex to match Tamil/Latin/digits as single tokens
        return _TOKEN_RE.match(text)

    return Tokenizer(
        nlp.vocab,
        rules=nlp.Defaults.tokenizer_exceptions,
        prefix_search=prefix_re.search,
        suffix_search=suffix_re.search,
        infix_finditer=infix_re.finditer,
        token_match=token_match,
    )


def install_tamil_tokenizer(nlp, *, nfc_normalize: bool = True):
    """
    Replace nlp.tokenizer with a Tamil-aware tokenizer.
    If nfc_normalize=True (default), input text is NFC-normalized before tokenization
    to align with tamil_utils.normalize().
    """
    tok = make_tamil_tokenizer(nlp)

    if not nfc_normalize:
        nlp.tokenizer = tok
        return nlp

    # Wrap tokenizer to normalize text first (without altering spaCy pipeline APIs)
    def _norm_tokenizer(text):
        return tok(normalize(text))

    nlp.tokenizer = _norm_tokenizer
    return nlp
