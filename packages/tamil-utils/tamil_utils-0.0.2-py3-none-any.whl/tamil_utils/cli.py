import sys, argparse, json
from .core import (
    normalize, tokens, remove_stopwords, graphemes,
    sents, to_arabic_numerals, to_tamil_numerals
)

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

    args = p.parse_args()
    text = args.text if args.text is not None else sys.stdin.read()

    if args.cmd == "normalize":
        print(normalize(text))
    elif args.cmd == "tokens":
        toks = tokens(text)
        if args.rmstop:
            from .core import stopwords_preset
            toks = [t for t in toks if t not in stopwords_preset("ta")]
        print(json.dumps(toks, ensure_ascii=False))
    elif args.cmd == "rmstop":
        print(json.dumps(remove_stopwords(tokens(text), preset=args.preset), ensure_ascii=False))
    elif args.cmd == "graphemes":
        print(json.dumps(graphemes(text), ensure_ascii=False))
    elif args.cmd == "sents":
        print(json.dumps(sents(text), ensure_ascii=False))
    elif args.cmd == "to-arabic":
        print(to_arabic_numerals(text))
    elif args.cmd == "to-tamil":
        print(to_tamil_numerals(text))
