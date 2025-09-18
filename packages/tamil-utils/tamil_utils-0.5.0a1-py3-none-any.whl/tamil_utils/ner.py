"""
tamil_utils.ner
---------------

Thin wrapper over a HuggingFace token-classification model (e.g., IndicNER)
with sensible defaults, Unicode-safe normalization, and simple batch APIs.

Usage:
    from tamil_utils.ner import NERTagger
    tagger = NERTagger()  # defaults to ai4bharat/IndicNER
    spans = tagger.predict_spans("தமிழ்நாடு அரசு அறிவிப்பு …")
    # [{'label': 'LOC', 'text': 'தமிழ்நாடு', 'start': 0, 'end': 9, 'score': 0.98}, ...]

Notes:
- Requires optional dependency: transformers
  pip install "tamil-utils[hf]"   # if you added this extra
  or: pip install transformers accelerate torch --upgrade
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Iterable, Union

from .core import normalize

# Optional imports guarded for graceful error messages
try:
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline  # type: ignore
except Exception as e:  # pragma: no cover
    AutoTokenizer = None  # type: ignore
    AutoModelForTokenClassification = None  # type: ignore
    pipeline = None  # type: ignore
    _IMPORT_ERR = e
else:
    _IMPORT_ERR = None


__all__ = [
    "NERSpan",
    "NERTagger",
    "ner_predict_spans",
    "ner_predict_json",
]


DEFAULT_MODEL = "ai4bharat/IndicNER"  # override via NERTagger(model=...)
AGGREGATION = "simple"  # 'simple' | 'first' | 'average' | 'max'


@dataclass
class NERSpan:
    label: str
    text: str
    start: int
    end: int
    score: float

    def to_dict(self) -> Dict[str, Union[str, int, float]]:
        return {"label": self.label, "text": self.text, "start": self.start, "end": self.end, "score": self.score}


class NERTagger:
    """
    HuggingFace pipeline wrapper for token-classification models.

    Parameters
    ----------
    model : str
        HF repo or local path. Default: ai4bharat/IndicNER
    device : Optional[int]
        Torch device index; -1 for CPU. If None, pipeline picks automatically.
    aggregation_strategy : str
        Passed to HF pipeline; defaults to 'simple'.

    Methods
    -------
    predict_spans(text) -> List[NERSpan]
    predict_spans_batch(texts) -> List[List[NERSpan]]
    predict_json(text) -> List[Dict]
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        *,
        device: Optional[int] = None,
        aggregation_strategy: str = AGGREGATION,
        revision: Optional[str] = None,
        trust_remote_code: bool = False,
    ):
        if pipeline is None:  # pragma: no cover
            raise ImportError(
                "transformers is required for NER. Install with:\n"
                '  pip install "tamil-utils[hf]"  # if extras are defined\n'
                "or: pip install transformers accelerate torch --upgrade\n"
                f"Original import error: {_IMPORT_ERR!r}"
            )

        # Load tokenizer/model explicitly to avoid repeated downloads if multiple instances are created.
        tok = AutoTokenizer.from_pretrained(model, revision=revision, trust_remote_code=trust_remote_code)
        mdl = AutoModelForTokenClassification.from_pretrained(model, revision=revision, trust_remote_code=trust_remote_code)

        kwargs: Dict[str, Any] = {
            "task": "token-classification",
            "model": mdl,
            "tokenizer": tok,
            "aggregation_strategy": aggregation_strategy,
        }
        if device is not None:
            kwargs["device"] = device

        self._pipe = pipeline(**kwargs)

    # --------- public API ---------

    def predict_spans(self, text: str) -> List[NERSpan]:
        """
        Return entity spans for a single string.
        """
        if not text:
            return []
        t = normalize(text)
        outs = self._pipe(t)
        spans: List[NERSpan] = []
        for o in outs:
            # HF returns dicts like: {'entity_group': 'PER', 'score': 0.99, 'word': '...', 'start': 12, 'end': 18}
            label = o.get("entity_group") or o.get("entity") or ""
            spans.append(
                NERSpan(
                    label=str(label),
                    text=o.get("word", ""),
                    start=int(o.get("start", 0)),
                    end=int(o.get("end", 0)),
                    score=float(o.get("score", 0.0)),
                )
            )
        return spans

    def predict_spans_batch(self, texts: Iterable[str]) -> List[List[NERSpan]]:
        """
        Batched prediction for efficiency.
        """
        batch = [normalize(x) for x in texts]
        outs = self._pipe(batch)
        results: List[List[NERSpan]] = []
        for item in outs:
            spans: List[NERSpan] = []
            for o in item:
                label = o.get("entity_group") or o.get("entity") or ""
                spans.append(
                    NERSpan(
                        label=str(label),
                        text=o.get("word", ""),
                        start=int(o.get("start", 0)),
                        end=int(o.get("end", 0)),
                        score=float(o.get("score", 0.0)),
                    )
                )
            results.append(spans)
        return results

    def predict_json(self, text: str) -> List[Dict[str, Any]]:
        """
        Dict representation (JSON-ready).
        """
        return [s.to_dict() for s in self.predict_spans(text)]


# ---------- convenience functions ----------

# Simple module-level cache so repeated calls don't reload weights in short-lived processes.
_GLOBAL_TAGGER: Optional[NERTagger] = None

def _get_global(model: str = DEFAULT_MODEL) -> NERTagger:
    global _GLOBAL_TAGGER
    if _GLOBAL_TAGGER is None or getattr(_GLOBAL_TAGGER, "_model_name", None) != model:
        _GLOBAL_TAGGER = NERTagger(model=model)
        _GLOBAL_TAGGER._model_name = model  # type: ignore[attr-defined]
    return _GLOBAL_TAGGER


def ner_predict_spans(text: str, model: str = DEFAULT_MODEL) -> List[NERSpan]:
    """
    One-shot helper that uses a cached pipeline.
    """
    return _get_global(model).predict_spans(text)


def ner_predict_json(text: str, model: str = DEFAULT_MODEL) -> List[Dict[str, Any]]:
    """
    One-shot helper that uses a cached pipeline.
    """
    return [s.to_dict() for s in ner_predict_spans(text, model=model)]
