import sys, argparse, json
from .core import normalize, tokens, remove_stopwords, graphemes

def main():
    p = argparse.ArgumentParser(prog="tamil-utils", description="Tamil text utilities")
    sub = p.add_subparsers(dest="cmd", required=True)

    s_norm = sub.add_parser("normalize", help="NFC normalize & strip ZW chars")
    s_norm.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_tok = sub.add_parser("tokens", help="Tokenize Tamil/Latin/digits")
    s_tok.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_rs = sub.add_parser("rmstop", help="Remove Tamil stopwords")
    s_rs.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    s_gr = sub.add_parser("graphemes", help="Split into grapheme clusters")
    s_gr.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    args = p.parse_args()
    text = args.text if args.text is not None else sys.stdin.read()

    if args.cmd == "normalize":
        print(normalize(text))
    elif args.cmd == "tokens":
        print(json.dumps(tokens(text), ensure_ascii=False))
    elif args.cmd == "rmstop":
        print(json.dumps(remove_stopwords(tokens(text)), ensure_ascii=False))
    elif args.cmd == "graphemes":
        print(json.dumps(graphemes(text), ensure_ascii=False))
