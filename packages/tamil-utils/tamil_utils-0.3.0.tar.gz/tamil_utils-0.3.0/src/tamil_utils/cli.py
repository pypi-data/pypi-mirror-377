import sys, argparse, json, io
from .core import (
    normalize, tokens, remove_stopwords, graphemes,
    sents, to_arabic_numerals, to_tamil_numerals,
    transliterate_iso15919, script_of, token_scripts, stopwords_preset,
    # v0.2
    ngrams, bigrams, trigrams, word_counts, syllables, sort_tamil
)
from .preprocess import preprocess_stream, PreprocessOptions  # v0.3

def main():
    p = argparse.ArgumentParser(prog="tamil-utils", description="Tamil text utilities")
    sub = p.add_subparsers(dest="cmd", required=True)

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

    s_tr = sub.add_parser("to-iso", help="Transliterate Tamil → ISO 15919 (lite)")
    s_tr.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_sc = sub.add_parser("script", help="Detect script of each token")
    s_sc.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    # --- v0.2 commands ---

    s_ng = sub.add_parser("ngrams", help="Generate n-grams from text tokens")
    s_ng.add_argument("text", nargs="?", help="Text (defaults to stdin)")
    s_ng.add_argument("-n", type=int, default=2, help="n for n-grams (default: 2)")

    s_bg = sub.add_parser("bigrams", help="Generate bigrams from text tokens")
    s_bg.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_tg = sub.add_parser("trigrams", help="Generate trigrams from text tokens")
    s_tg.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_freq = sub.add_parser("freq", help="Word/n-gram frequency")
    s_freq.add_argument("text", nargs="?", help="Text (defaults to stdin)")
    s_freq.add_argument("-n", type=int, default=1, help="n for n-grams (1,2,3; default: 1)")
    s_freq.add_argument("--top", type=int, default=None, help="Return top N items")
    s_freq.add_argument("--rmstop", action="store_true", help="Remove stopwords (only when n=1)")
    s_freq.add_argument("--preset", default="ta", help='Stopwords preset (default: "ta")')
    s_freq.add_argument("--jsonl", action="store_true", help="Output JSON Lines (one object per line)")

    s_syl = sub.add_parser("syllables", help="Approximate Tamil syllable units (grapheme-based)")
    s_syl.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_sort = sub.add_parser("sort", help="Sort words in Tamil order (ISO-15919 key)")
    s_sort.add_argument("words", nargs="*", help="Words to sort; if empty, read newline-separated from stdin")

    # --- v0.3 commands ---

    s_pp = sub.add_parser("preprocess", help="Stream preprocessor (lines → JSONL records)")
    s_pp.add_argument("--input", "-i", default="-", help="Input file path or '-' for stdin (default: '-')")
    s_pp.add_argument("--output", "-o", default="-", help="Output file path or '-' for stdout (default: '-')")
    s_pp.add_argument("--numerals", choices=["ar", "ta"], default=None,
                      help='Harmonize numerals: "ar" (Tamil→ASCII) or "ta" (ASCII→Tamil)')
    s_pp.add_argument("--rmstop", action="store_true", help="Also emit tokens_nostop using Tamil preset")
    s_pp.add_argument("--emit", default=None,
                      help='Comma-separated subset of fields to emit: text,sents,tokens,tokens_nostop')

    args = p.parse_args()

    # helper to get text from arg or stdin
    def _read_text(arg):
        return arg if arg is not None else sys.stdin.read()

    if args.cmd == "normalize":
        print(normalize(_read_text(args.text)))
    elif args.cmd == "tokens":
        txt = _read_text(args.text)
        toks = tokens(txt)
        if args.rmstop:
            sw = stopwords_preset("ta")
            toks = [t for t in toks if t not in sw]
        print(json.dumps(toks, ensure_ascii=False))
    elif args.cmd == "rmstop":
        txt = _read_text(args.text)
        print(json.dumps(remove_stopwords(tokens(txt), preset=args.preset), ensure_ascii=False))
    elif args.cmd == "graphemes":
        print(json.dumps(graphemes(_read_text(args.text)), ensure_ascii=False))
    elif args.cmd == "sents":
        print(json.dumps(sents(_read_text(args.text)), ensure_ascii=False))
    elif args.cmd == "to-arabic":
        print(to_arabic_numerals(_read_text(args.text)))
    elif args.cmd == "to-tamil":
        print(to_tamil_numerals(_read_text(args.text)))
    elif args.cmd == "to-iso":
        print(transliterate_iso15919(_read_text(args.text)))
    elif args.cmd == "script":
        txt = _read_text(args.text)
        print(json.dumps(token_scripts(tokens(txt)), ensure_ascii=False))

    # --- v0.2 dispatch ---
    elif args.cmd == "ngrams":
        txt = _read_text(args.text)
        if args.n < 1:
            raise SystemExit("n must be >= 1")
        toks = tokens(txt)
        if args.n == 1:
            items = toks
        elif args.n == 2:
            items = [" ".join(b) for b in bigrams(toks)]
        elif args.n == 3:
            items = [" ".join(t) for t in trigrams(toks)]
        else:
            items = [" ".join(g) for g in ngrams(toks, args.n)]
        print(json.dumps(items, ensure_ascii=False))
    elif args.cmd == "bigrams":
        txt = _read_text(args.text)
        toks = tokens(txt)
        items = [" ".join(b) for b in bigrams(toks)]
        print(json.dumps(items, ensure_ascii=False))
    elif args.cmd == "trigrams":
        txt = _read_text(args.text)
        toks = tokens(txt)
        items = [" ".join(t) for t in trigrams(toks)]
        print(json.dumps(items, ensure_ascii=False))
    elif args.cmd == "freq":
        txt = _read_text(args.text)
        if args.n < 1 or args.n > 5:
            raise SystemExit("n must be in 1..5")
        pairs = word_counts(txt, rmstop=args.rmstop, preset=args.preset, n=args.n, top=args.top)
        if args.jsonl:
            for k, v in pairs:
                print(json.dumps({"item": k, "count": v}, ensure_ascii=False))
        else:
            # output as list of [item, count]
            print(json.dumps([[k, v] for k, v in pairs], ensure_ascii=False))
    elif args.cmd == "syllables":
        print(json.dumps(syllables(_read_text(args.text)), ensure_ascii=False))
    elif args.cmd == "sort":
        if args.words:
            words = args.words
        else:
            words = [w.strip() for w in sys.stdin.read().splitlines() if w.strip()]
        print(json.dumps(sort_tamil(words), ensure_ascii=False))

    # --- v0.3 dispatch ---
    elif args.cmd == "preprocess":
        emit_list = None
        if args.emit:
            emit_list = [x.strip() for x in args.emit.split(",") if x.strip()]
        opts = PreprocessOptions(numerals=args.numerals, rmstop=args.rmstop, emit=emit_list)

        # input handle
        if args.input == "-" or args.input is None:
            fin = sys.stdin
        else:
            fin = open(args.input, "r", encoding="utf-8")

        # output handle
        if args.output == "-" or args.output is None:
            fout = sys.stdout
        else:
            fout = open(args.output, "w", encoding="utf-8")

        try:
            preprocess_stream(fin, fout, opts)
        finally:
            if fin is not sys.stdin:
                fin.close()
            if fout is not sys.stdout:
                fout.close()

if __name__ == "__main__":
    main()
