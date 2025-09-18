import sys, argparse, json, os
from typing import List, Dict, Any

from .core import (
    normalize, tokens, remove_stopwords, graphemes,
    sents, to_arabic_numerals, to_tamil_numerals,
    transliterate_iso15919, script_of, token_scripts
)

# Optional imports are guarded inside command handlers.

def _read_text_or_stdin(arg_text: str | None) -> str:
    return arg_text if arg_text is not None else sys.stdin.read()

def main():
    p = argparse.ArgumentParser(prog="tamil-utils", description="Tamil text utilities")
    sub = p.add_subparsers(dest="cmd", required=True)

    # --- Core ---
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

    # --- v0.2+ extras already in your tree (freq etc.) ---
    s_freq = sub.add_parser("freq", help="N-gram frequency")
    s_freq.add_argument("text", nargs="?", help="Text (defaults to stdin)")
    s_freq.add_argument("-n", type=int, default=1, help="n-gram size (default 1)")
    s_freq.add_argument("--top", type=int, default=None, help="Top-K")
    s_freq.add_argument("--rmstop", action="store_true", help="Remove stopwords before counting")
    s_freq.add_argument("--jsonl", action="store_true", help="Stream as JSONL (one per line)")

    # --- v0.3 preprocess pipeline ---
    s_pp = sub.add_parser("preprocess", help="Normalize → sents → tokens → (stopwords/numerals)")
    s_pp.add_argument("--numerals", choices=["ar", "ta", "none"], default="none",
                      help="ar: Tamil→ASCII, ta: ASCII→Tamil, none: keep")
    s_pp.add_argument("--rmstop", action="store_true", help="Remove Tamil stopwords")
    s_pp.add_argument("--emit", nargs="+", default=["text","sents","tokens","tokens_nostop"],
                      help="Fields to emit (default: text sents tokens tokens_nostop)")
    s_pp.add_argument("text", nargs="?", help="Text (defaults to stdin)")

    # --- v0.4 corpus helpers ---
    s_cd = sub.add_parser("corpus-dedup", help="Remove duplicate lines (stable)")
    s_cd.add_argument("--file", required=False, help="Input file (or stdin)")

    s_cf = sub.add_parser("corpus-filter", help="Filter lines by token length bounds")
    s_cf.add_argument("--file", required=False, help="Input file (or stdin)")
    s_cf.add_argument("--min-tokens", type=int, default=1)
    s_cf.add_argument("--max-tokens", type=int, default=9999)

    s_cw = sub.add_parser("corpus-windows", help="Sentence windows (k, stride) for RAG")
    s_cw.add_argument("--file", required=False, help="Input file (one document per line; or stdin)")
    s_cw.add_argument("--k", type=int, default=3, help="window size")
    s_cw.add_argument("--stride", type=int, default=1, help="stride")

    # --- NEW: NER over HF IndicNER ---
    s_ner = sub.add_parser("ner", help="Named Entity Recognition (HF: ai4bharat/IndicNER)")
    s_ner.add_argument("text", nargs="?", help="Text (defaults to stdin)")
    s_ner.add_argument("--model", default="ai4bharat/IndicNER", help="HF repo or local path")
    s_ner.add_argument("--device", type=int, default=None, help="-1 for CPU, otherwise CUDA index")

    # --- NEW: light eval harness (Naamapadam) ---
    s_eval = sub.add_parser("eval-ner", help="Quick eval on Naamapadam (sampled)")
    s_eval.add_argument("--model", default="ai4bharat/IndicNER", help="HF repo or local path")
    s_eval.add_argument("--split", default="validation", help="HF split (default: validation)")
    s_eval.add_argument("--lang", default="ta", help="language code to sample (default: ta)")
    s_eval.add_argument("--limit", type=int, default=50, help="number of rows (default: 50)")
    s_eval.add_argument("--save-jsonl", default=None, help="save predictions to JSONL path")

    args = p.parse_args()
    text = _read_text_or_stdin(getattr(args, "text", None))

    # ----------------- handlers -----------------

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

    elif args.cmd == "to-iso":
        print(transliterate_iso15919(text))

    elif args.cmd == "script":
        print(json.dumps(token_scripts(tokens(text)), ensure_ascii=False))

    elif args.cmd == "freq":
        from .v02_counts import word_counts  # your existing helper
        out = word_counts(text, rmstop=args.rmstop, n=args.n, top=args.top)
        if args.jsonl:
            for gram, cnt in out:
                print(json.dumps({"ngram": gram, "count": cnt}, ensure_ascii=False))
        else:
            print(json.dumps(out, ensure_ascii=False))

    elif args.cmd == "preprocess":
        from .preprocess import PreprocessOptions, preprocess_record
        opts = PreprocessOptions(
            numerals=args.numerals if args.numerals != "none" else None,
            rmstop=args.rmstop,
            emit=args.emit
        )
        rec = preprocess_record(text, opts)
        print(json.dumps(rec, ensure_ascii=False))

    elif args.cmd == "corpus-dedup":
        data = sys.stdin.read() if not args.file else open(args.file, "r", encoding="utf-8").read()
        seen = set()
        for line in data.splitlines():
            if line not in seen:
                print(line)
                seen.add(line)

    elif args.cmd == "corpus-filter":
        data = sys.stdin.read() if not args.file else open(args.file, "r", encoding="utf-8").read()
        for line in data.splitlines():
            toks = tokens(line)
            if args.min_tokens <= len(toks) <= args.max_tokens:
                print(line)

    elif args.cmd == "corpus-windows":
        from .corpus import window_sents, normalize_punct
        data = sys.stdin.read() if not args.file else open(args.file, "r", encoding="utf-8").read()
        for doc in data.splitlines():
            clean = normalize_punct(doc)
            for w in window_sents(clean, k=args.k, stride=args.stride):
                print(w)

    elif args.cmd == "ner":
        try:
            from .ner import NERTagger
        except Exception as e:
            print(f"ERROR: transformers not installed or failed to import: {e}", file=sys.stderr)
            sys.exit(2)
        tagger = NERTagger(model=args.model, device=args.device)
        spans = tagger.predict_json(text)
        print(json.dumps(spans, ensure_ascii=False))

    elif args.cmd == "eval-ner":
        # Best-effort, sample-based harness over ai4bharat/naamapadam. :contentReference[oaicite:2]{index=2}
        try:
            from datasets import load_dataset  # type: ignore
        except Exception as e:
            print("ERROR: datasets not installed. Try: pip install datasets", file=sys.stderr)
            sys.exit(2)
        try:
            from .ner import NERTagger
        except Exception as e:
            print(f"ERROR: transformers not installed or failed to import: {e}", file=sys.stderr)
            sys.exit(2)

        ds = load_dataset("ai4bharat/naamapadam", split=args.split)  # :contentReference[oaicite:3]{index=3}
        # The dataset covers many Indic languages curated by AI4Bharat; it underpins IndicNER. :contentReference[oaicite:4]{index=4}
        rows = [r for r in ds if (r.get("lang") or r.get("language") or "").lower().startswith(args.lang.lower())]
        if args.limit:
            rows = rows[: args.limit]

        tagger = NERTagger(model=args.model, device=None)
        preds: List[Dict[str, Any]] = []
        for r in rows:
            txt = r.get("text") or r.get("sentence") or ""
            spans = tagger.predict_json(txt)
            out = {"text": txt, "pred_spans": spans}
            # If BIO tags exist, attach for optional downstream eval tooling
            if "tokens" in r and "ner_tags" in r:
                out["tokens"] = r["tokens"]
                out["ner_tags"] = r["ner_tags"]
            preds.append(out)
            print(json.dumps(out, ensure_ascii=False))

        # Optional quick metric (best-effort): requires seqeval; builds gold spans if BIO tags exist.
        try:
            import seqeval.metrics as sq  # type: ignore
        except Exception:
            sq = None

        if sq and len([1 for r in preds if "tokens" in r and "ner_tags" in r]) >= 1:
            # Construct label sequences (BIO) and naive predicted BIO from char spans using token offsets.
            # NOTE: This is intentionally simple and approximate for quick checks.
            def bio_from_spans(tokens: List[str], spans: List[Dict[str, Any]], text: str) -> List[str]:
                # Map token char ranges, then mark B-/I- for any predicted span that fully covers that token.
                bio = ["O"] * len(tokens)
                # Build naive char offset map for tokens
                offs = []
                idx = 0
                for i, tok in enumerate(tokens):
                    # find tok in text starting from idx
                    j = text.find(tok, idx)
                    if j < 0:
                        # fallback: skip alignment
                        offs.append((None, None))
                        continue
                    offs.append((j, j + len(tok)))
                    idx = j + len(tok)
                # apply spans
                for sp in spans:
                    s, e, lab = sp.get("start"), sp.get("end"), sp.get("label", "ENT")
                    if not isinstance(s, int) or not isinstance(e, int):
                        continue
                    first = True
                    for i, (a, b) in enumerate(offs):
                        if a is None:
                            continue
                        if a >= s and b <= e:
                            bio[i] = ("B-" if first else "I-") + lab
                            first = False
                return bio

            gold, pred = [], []
            for r in preds:
                if "tokens" not in r or "ner_tags" not in r:  # skip if gold absent
                    continue
                g_seq = [r["ner_tags"]] if isinstance(r["ner_tags"][0], str) else [r["ner_tags"]]
                # r["ner_tags"] may already be BIO strings; some variants store ints → keep as strings
                g_labels = g_seq[0]
                p_labels = bio_from_spans(r.get("tokens", []), r.get("pred_spans", []), r.get("text", ""))
                gold.append(g_labels)
                pred.append(p_labels)

            if gold and pred:
                f1 = sq.f1_score(gold, pred)
                print(json.dumps({"samples": len(preds), "approx_span_F1": f1}, ensure_ascii=False), file=sys.stderr)
        # Save JSONL if requested
        if args.save_jsonl:
            with open(args.save_jsonl, "w", encoding="utf-8") as w:
                for o in preds:
                    w.write(json.dumps(o, ensure_ascii=False) + "\n")

    else:
        p.error(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
