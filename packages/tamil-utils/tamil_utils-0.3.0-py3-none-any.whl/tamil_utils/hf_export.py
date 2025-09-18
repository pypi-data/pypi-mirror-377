"""
HF Datasets export helpers (optional).

Create/save a Hugging Face `datasets.Dataset` from an iterable of dict records.
We import `datasets` only when needed, so tamil-utils stays lightweight.

Usage:
    from tamil_utils.hf_export import to_hf_dataset, save_hf_dataset

    records = [{"text": "இது ஒரு சோதனை 2025", "tokens": ["இது","ஒரு","சோதனை","2025"]}]
    ds = to_hf_dataset(records)      # returns datasets.Dataset
    save_hf_dataset(ds, "out_ds")    # writes to disk (arrow format)
"""

from __future__ import annotations
from typing import Iterable, Dict, Any

def _ensure_datasets():
    try:
        import datasets as _ds  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "Hugging Face `datasets` is not installed. "
            "Install with: pip install datasets"
        ) from e
    return _ds

def to_hf_dataset(records: Iterable[Dict[str, Any]]):
    """
    Build a datasets.Dataset from an iterable of dict records.
    Features are inferred automatically by `datasets`.
    """
    ds = _ensure_datasets()
    data = list(records)
    return ds.Dataset.from_list(data)

def save_hf_dataset(dataset, path: str):
    """
    Save a datasets.Dataset to disk (arrow format) so it can be reloaded with
    `datasets.load_from_disk(path)`.
    """
    dataset.save_to_disk(path)
