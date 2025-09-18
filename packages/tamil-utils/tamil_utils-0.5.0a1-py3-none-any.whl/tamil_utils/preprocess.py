"""
Lightweight dataset preprocessor (stream-friendly, JSONL-ready).

Usage pattern (programmatic):
    from tamil_utils.preprocess import preprocess_lines, PreprocessOptions
    opts = PreprocessOptions(numerals="ar", rmstop=True)
    for rec in preprocess_lines(open("input.txt", "r", encoding="utf-8"), opts):
        print(rec)  # dict with text/sents/tokens/tokens_nostop

This module is intentionally dependency-free and works line-by-line so it can
scale via simple shell pipelines (we’ll add a CLI subcommand next).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Iterator, TextIO, Dict, Any, Optional, List
import json

from .core import (
    normalize,
    sents,
    tokens,
    remove_stopwords,
    to_arabic_numerals,
    to_tamil_numerals,
)

__all__ = [
    "PreprocessOptions",
    "clean_text",
    "preprocess_record",
    "preprocess_lines",
    "preprocess_stream",
]


@dataclass
class PreprocessOptions:
    """
    Options controlling the preprocessing pipeline.

    numerals:
        - None: leave numerals as-is
        - "ar": convert Tamil digits -> ASCII 0-9
        - "ta": convert ASCII 0-9 -> Tamil digits
    rmstop:
        - If True, also emit 'tokens_nostop' using preset="ta"
    emit:
        - Which fields to include in each record
          (subset of {"text","sents","tokens","tokens_nostop"})
    """
    numerals: Optional[str] = None  # None | "ar" | "ta"
    rmstop: bool = False
    emit: Optional[List[str]] = None  # default: ["text","sents","tokens","tokens_nostop"] if rmstop else without tokens_nostop

    def effective_emit(self) -> List[str]:
        if self.emit:
            return self.emit
        base = ["text", "sents", "tokens"]
        if self.rmstop:
            base.append("tokens_nostop")
        return base


def clean_text(text: str, *, numerals: Optional[str] = None) -> str:
    """
    Normalize text and (optionally) harmonize numerals.

    numerals="ar" converts Tamil digits to ASCII.
    numerals="ta" converts ASCII digits to Tamil digits.
    """
    t = normalize(text)
    if numerals == "ar":
        t = to_arabic_numerals(t)
    elif numerals == "ta":
        t = to_tamil_numerals(t)
    return t


def preprocess_record(text: str, opts: Optional[PreprocessOptions] = None) -> Dict[str, Any]:
    """
    Process a single text block into a small dict suitable for JSONL.

    Fields (subject to 'emit'):
        - text: cleaned text (normalized, numerals harmonized)
        - sents: list[str] sentence segmentation
        - tokens: list[str] tokens
        - tokens_nostop: list[str] tokens with Tamil stopwords removed (if rmstop=True)
    """
    if opts is None:
        opts = PreprocessOptions()

    cleaned = clean_text(text, numerals=opts.numerals)
    out: Dict[str, Any] = {}
    emit = set(opts.effective_emit())

    if "text" in emit:
        out["text"] = cleaned

    # Sentences first; tokens can be computed either from full text or per sentence.
    if "sents" in emit:
        out["sents"] = sents(cleaned)

    toks: Optional[List[str]] = None
    if "tokens" in emit or "tokens_nostop" in emit:
        toks = tokens(cleaned)

    if "tokens" in emit:
        out["tokens"] = toks or []

    if "tokens_nostop" in emit:
        if opts.rmstop:
            out["tokens_nostop"] = remove_stopwords(toks or [], preset="ta")
        else:
            # if requested but rmstop False, just duplicate tokens to be explicit
            out["tokens_nostop"] = toks or []

    return out


def preprocess_lines(lines: Iterable[str], opts: Optional[PreprocessOptions] = None) -> Iterator[Dict[str, Any]]:
    """
    Process an iterable of lines (e.g., file object). Each input line becomes one record.
    Empty lines produce an empty-text record (still normalized), so downstream joins stay aligned.
    """
    if opts is None:
        opts = PreprocessOptions()

    for line in lines:
        # Preserve original segmentation by line; strip trailing newline only.
        text = line.rstrip("\n")
        yield preprocess_record(text, opts)


def preprocess_stream(in_fp: TextIO, out_fp: TextIO, opts: Optional[PreprocessOptions] = None) -> None:
    """
    Stream lines from in_fp to out_fp as JSONL. Useful for CLI and shell pipelines.

    Example:
        with open("in.txt","r",encoding="utf-8") as fin, open("out.jsonl","w",encoding="utf-8") as fout:
            preprocess_stream(fin, fout, PreprocessOptions(numerals="ar", rmstop=True))
    """
    if opts is None:
        opts = PreprocessOptions()

    for rec in preprocess_lines(in_fp, opts):
        out_fp.write(json.dumps(rec, ensure_ascii=False) + "\n")
        out_fp.flush()
