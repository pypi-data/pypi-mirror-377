import io, json
from tamil_utils.preprocess import (
    clean_text,
    PreprocessOptions,
    preprocess_record,
    preprocess_stream,
)

def test_clean_text_numerals_ar():
    # Tamil digits -> ASCII
    assert clean_text("௨௦௨௫", numerals="ar") == "2025"

def test_clean_text_numerals_ta():
    # ASCII -> Tamil digits
    assert clean_text("123", numerals="ta") == "௧௨௩"

def test_preprocess_record_basic_and_rmstop():
    opts = PreprocessOptions(numerals="ar", rmstop=True)
    rec = preprocess_record("இது ஒரு சோதனை ௨௦௨௫", opts)
    # expected fields
    assert set(rec.keys()) >= {"text", "sents", "tokens", "tokens_nostop"}
    # numerals normalized to ASCII
    assert "2025" in rec["text"]
    # stopwords removed
    assert "ஒரு" not in rec["tokens_nostop"]

def test_preprocess_emit_subset():
    # Only emit text and tokens
    opts = PreprocessOptions(emit=["text", "tokens"])
    rec = preprocess_record("இது ஒரு சோதனை", opts)
    assert set(rec.keys()) == {"text", "tokens"}

def test_preprocess_stream_jsonl_roundtrip():
    src = "இது ஒரு சோதனை\n123\n\n"
    fin = io.StringIO(src)
    fout = io.StringIO()
    opts = PreprocessOptions(numerals="ta", rmstop=True)  # 123 -> ௧௨௩

    preprocess_stream(fin, fout, opts)

    fout.seek(0)
    lines = [ln for ln in fout.read().splitlines() if ln.strip()]
    # 3 input lines (including empty) -> 3 JSONL records (empty text allowed)
    assert len(lines) == 3

    rec0 = json.loads(lines[0])
    rec1 = json.loads(lines[1])
    rec2 = json.loads(lines[2])

    # line 0: normal Tamil text
    assert "சோதனை" in rec0["text"]
    assert "tokens_nostop" in rec0  # rmstop=True adds this

    # line 1: ASCII numerals converted to Tamil
    assert rec1["text"] == "௧௨௩"

    # line 2: empty input line preserved as empty text
    assert rec2["text"] == ""
