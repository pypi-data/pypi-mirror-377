import json
import pytest

datasets = pytest.importorskip("datasets", reason="HF datasets not installed")

from tamil_utils.hf_export import to_hf_dataset, save_hf_dataset

def test_to_hf_dataset_and_roundtrip(tmp_path):
    records = [
        {"text": "இது ஒரு சோதனை 2025", "tokens": ["இது", "ஒரு", "சோதனை", "2025"]},
        {"text": "தமிழ் NLP", "tokens": ["தமிழ்", "NLP"]},
    ]

    ds = to_hf_dataset(records)
    assert len(ds) == 2
    assert set(ds.column_names) >= {"text", "tokens"}
    assert ds[0]["text"].startswith("இது")

    out_dir = tmp_path / "out_ds"
    save_hf_dataset(ds, str(out_dir))

    # reload and verify
    reloaded = datasets.load_from_disk(str(out_dir))
    assert len(reloaded) == 2
    assert reloaded[1]["tokens"] == ["தமிழ்", "NLP"]
