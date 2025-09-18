import sys, argparse, json
from typing import List, Iterable

from .core import (
    normalize, tokens, remove_stopwords, graphemes,
    sents, to_arabic_numerals, to_tamil_numerals,
    transliterate_iso15919, script_of, token_scripts,
    word_counts, sort_tamil, syllables
)
from .preprocess import PreprocessOptions, preprocess_stream
from .corpus import dedup_lines, filter_by_length, window_sents


def _read_text_stdin_or_arg(text_arg: str | None) -> str:
    return text_arg if text_arg is not None else sys.stdin.read()


def _read_lines_from_file_or_stdin(path: str | None) -> List[str]:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    return sys.stdin.read().splitlines(keepends=True)


def main():
    p = argparse.ArgumentParser(prog="tamil-utils", description="Tamil text utilities")
    sub = p.add_subparsers(dest="cmd", required=True)

    # --- Core ops ---
    s_norm = sub.add_parser("normalize", help="NFC normalize & strip ZWSP")
    s_norm.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_tok = sub.add_parser("tokens", help="Tokenize Tamil/Latin/digits")
    s_tok.add_argument("text", nargs="?", help="Text (defaults to stdin)")
    s_tok.add_argument("--rmstop", action="store_true", help="Remove Tamil stopwords (preset)")

    s_rs = sub.add_parser("rmstop", help="Remove stopwords from tokens")
    s_rs.add_argument("text", nargs="?", help="Text (defaults to stdin)")
    s_rs.add_argument("--preset", default="ta", help='Stopwords preset (default: "ta")')

    s_gr = sub.add_parser("graphemes", help="Split into grapheme clusters")
    s_gr.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_se = sub.add_parser("sents", help="Sentence split")
    s_se.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_toar = sub.add_parser("to-arabic", help="Convert Tamil digits → ASCII digits")
    s_toar.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_tota = sub.add_parser("to-tamil", help="Convert ASCII digits → Tamil digits")
    s_tota.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_tr = sub.add_parser("to-iso", help="Transliterate Tamil -> ISO 15919")
    s_tr.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_sc = sub.add_parser("script", help="Detect script of each token")
    s_sc.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_syl = sub.add_parser("syllables", help="Approximate Tamil syllable splits")
    s_syl.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    # --- Frequency / n-grams ---
    s_freq = sub.add_parser("freq", help="n-gram frequency (default: unigrams)")
    s_freq.add_argument("text", nargs="?", help="Text (defaults to stdin)")
    s_freq.add_argument("-n", type=int, default=1, help="n-gram size (1,2,3)")
    s_freq.add_argument("--top", type=int, default=None, help="Top-K to show")
    s_freq.add_argument("--rmstop", action="store_true", help="Remove Tamil stopwords for unigrams")
    s_freq.add_argument("--jsonl", action="store_true", help="Emit as JSON lines (pair per line)")

    # --- Sort (Tamil collation via ISO-15919 key) ---
    s_sort = sub.add_parser("sort", help="Sort words in Tamil order (ISO-15919 key)")
    s_sort.add_argument("words", nargs="+", help="Words to sort")

    # --- Preprocess (JSONL) ---
    s_pp = sub.add_parser("preprocess", help="JSONL preprocessor for RAG/ML")
    s_pp.add_argument("--numerals", choices=["ar", "ta"], default=None, help="Harmonize numerals")
    s_pp.add_argument("--rmstop", action="store_true", help="Emit tokens_nostop with Tamil preset")
    s_pp.add_argument("--emit", default=None, help="Comma-separated subset: text,sents,tokens,tokens_nostop")

    # --- Corpus utilities (new) ---
    s_cd = sub.add_parser("corpus-dedup", help="Deduplicate lines (stable order)")
    s_cd.add_argument("--file", default=None, help="Read from file (default: stdin)")
    s_cd.add_argument("--no-strip", action="store_true", help="Don't strip keys before dedup")
    s_cd.add_argument("--no-casefold", action="store_true", help="Don't casefold keys (affects Latin)")

    s_cf = sub.add_parser("corpus-filter", help="Filter lines by char/token length")
    s_cf.add_argument("--file", default=None, help="Read from file (default: stdin)")
    s_cf.add_argument("--min-chars", type=int, default=None)
    s_cf.add_argument("--max-chars", type=int, default=None)
    s_cf.add_argument("--min-tokens", type=int, default=None)
    s_cf.add_argument("--max-tokens", type=int, default=None)

    s_cw = sub.add_parser("corpus-windows", help="Sentence windows from text (RAG chunks)")
    s_cw.add_argument("text", nargs="?", help="Text (defaults to stdin)")
    s_cw.add_argument("--file", default=None, help="Read full text from file")
    s_cw.add_argument("--k", type=int, default=3, help="Sentences per window (default 3)")
    s_cw.add_argument("--stride", type=int, default=1, help="Stride between windows (default 1)")
    s_cw.add_argument("--sep", default=" ", help="Join windows with this separator (default space)")

    args = p.parse_args()

    # ---------- Dispatch ----------
    if args.cmd == "normalize":
        print(normalize(_read_text_stdin_or_arg(args.text)))

    elif args.cmd == "tokens":
        t = tokens(_read_text_stdin_or_arg(args.text))
        if args.rmstop:
            from .core import stopwords_preset
            t = [w for w in t if w not in stopwords_preset("ta")]
        print(json.dumps(t, ensure_ascii=False))

    elif args.cmd == "rmstop":
        print(json.dumps(remove_stopwords(tokens(_read_text_stdin_or_arg(args.text)), preset=args.preset), ensure_ascii=False))

    elif args.cmd == "graphemes":
        print(json.dumps(graphemes(_read_text_stdin_or_arg(args.text)), ensure_ascii=False))

    elif args.cmd == "sents":
        print(json.dumps(sents(_read_text_stdin_or_arg(args.text)), ensure_ascii=False))

    elif args.cmd == "to-arabic":
        print(to_arabic_numerals(_read_text_stdin_or_arg(args.text)))

    elif args.cmd == "to-tamil":
        print(to_tamil_numerals(_read_text_stdin_or_arg(args.text)))

    elif args.cmd == "to-iso":
        print(transliterate_iso15919(_read_text_stdin_or_arg(args.text)))

    elif args.cmd == "script":
        print(json.dumps(token_scripts(tokens(_read_text_stdin_or_arg(args.text))), ensure_ascii=False))

    elif args.cmd == "syllables":
        print(json.dumps(syllables(_read_text_stdin_or_arg(args.text)), ensure_ascii=False))

    elif args.cmd == "freq":
        txt = _read_text_stdin_or_arg(args.text)
        # only apply stopwords for unigrams
        rmstop = bool(args.rmstop) if args.n == 1 else False
        pairs = word_counts(txt, rmstop=rmstop, preset="ta" if rmstop else None, n=args.n, top=args.top)
        if args.jsonl:
            for gram, cnt in pairs:
                print(json.dumps({"ngram": gram, "count": cnt}, ensure_ascii=False))
        else:
            print(json.dumps(pairs, ensure_ascii=False))

    elif args.cmd == "sort":
        print(json.dumps(sort_tamil(args.words), ensure_ascii=False))

    elif args.cmd == "preprocess":
        emit = None
        if args.emit:
            emit = [x.strip() for x in args.emit.split(",") if x.strip()]
        opts = PreprocessOptions(numerals=args.numerals, rmstop=args.rmstop, emit=emit)
        preprocess_stream(sys.stdin, sys.stdout, opts)

    elif args.cmd == "corpus-dedup":
        lines = _read_lines_from_file_or_stdin(args.file)
        uniq = dedup_lines(
            lines,
            casefold=not args.no_casefold,
            strip=not args.no_strip,
        )
        # Write exactly as lines came (dedup preserves original content/newlines)
        for ln in uniq:
            sys.stdout.write(ln)

    elif args.cmd == "corpus-filter":
        lines = _read_lines_from_file_or_stdin(args.file)
        # Process per line (emit those that pass)
        for ln in filter_by_length(
            (l.rstrip("\n") for l in lines),
            min_chars=args.min_chars, max_chars=args.max_chars,
            min_tokens=args.min_tokens, max_tokens=args.max_tokens,
        ):
            sys.stdout.write(ln + ("\n" if not ln.endswith("\n") else ""))

    elif args.cmd == "corpus-windows":
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                full = f.read()
        else:
            full = _read_text_stdin_or_arg(args.text)
        wins = window_sents(full, k=args.k, stride=args.stride, join_with=args.sep)
        for w in wins:
            print(w)

    else:
        p.error(f"Unknown command: {args.cmd}")
