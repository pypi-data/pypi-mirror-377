# tamil-utils

Tiny **Tamil-first** text utilities that make Unicode correctness & tokenization *boringly reliable*.

[![PyPI](https://img.shields.io/pypi/v/tamil-utils)](https://pypi.org/project/tamil-utils/)
[![CI](https://github.com/arulnidhii/tamil-utils/actions/workflows/ci.yml/badge.svg)](https://github.com/arulnidhii/tamil-utils/actions)

---

## Features

* **Core:** `normalize`, `tokens`, `remove_stopwords`, `graphemes`, `sents`, Tamil⇄ASCII **numerals**, **syllables** (approx), **Tamil collation** (ISO-15919 key)
* **Counts:** `ngrams`, `word_counts` (uni/bi/tri-grams, optional stopwords)
* **Pipelines:** JSONL **preprocessor** (CLI + Python) for RAG/ML corpora
* **Integrations (optional):**

  * **spaCy** tokenizer hook to mirror `tamil_utils.tokens`
  * **Hugging Face Datasets** export helper

> Docs: **[https://arulnidhii.github.io/tamil-utils/](https://arulnidhii.github.io/tamil-utils/)**

---

## Install

```bash
pip install tamil-utils

# optional extras
pip install "tamil-utils[spacy]"   # spaCy hook
pip install datasets               # HF datasets helper
```

---

## Quick start

```python
from tamil_utils import (
    normalize, tokens, remove_stopwords, graphemes, sents,
    to_arabic_numerals, syllables, sort_tamil, word_counts
)

s = "இது ஒரு சோதனை 👩🏽‍💻 ௨௦௨௫"

print(tokens(s))                                # ['இது','ஒரு','சோதனை','👩🏽‍💻','௨௦௨௫']
print(remove_stopwords(tokens(s), preset="ta")) # ['சோதனை','👩🏽‍💻','௨௦௨௫']
print(graphemes("👩🏽‍💻"))                       # ['👩🏽‍💻']
print(sents("இது ஒன்று. இது இரண்டு? சரி!"))      # ['இது ஒன்று.', 'இது இரண்டு?', 'சரி!']
print(to_arabic_numerals("௨௦௨௫"))                 # "2025"
print(syllables("தமிழ்"))                         # approx syllable-ish groups
print(sort_tamil(["இலங்கை","ஆதி","அடி"]))         # ['அடி','ஆதி','இலங்கை']
print(word_counts("தமிழ் NLP தமிழ் NLP", n=2, top=3))
```

---

## CLI

```bash
# JSONL preprocessor (one record per line)
python -m tamil_utils.cli preprocess --numerals ar --rmstop < input.txt > out.jsonl

# Word/n-gram counts
python -m tamil_utils.cli freq -n 2 --top 5 "தமிழ் NLP தமிழ் NLP"

# Tamil collation sort (ISO-15919 key)
python -m tamil_utils.cli sort "இலங்கை" "ஆதி" "அடி"
```

### Windows PowerShell

When piping Tamil text, prefer UTF-8 files or run with `python -X utf8`.

---

## spaCy tokenizer (optional)

```python
import spacy
from tamil_utils.spacy_hook import install_tamil_tokenizer

nlp = spacy.blank("xx")
install_tamil_tokenizer(nlp)
[t.text for t in nlp("இது ஒரு சோதனை 2025")]
# ['இது','ஒரு','சோதனை','2025']
```

---

## Hugging Face Datasets (optional)

```python
from tamil_utils.hf_export import to_hf_dataset  # requires: pip install datasets

records = [{"text": "இது ஒரு சோதனை 2025",
            "tokens": ["இது","ஒரு","சோதனை","2025"]}]
ds = to_hf_dataset(records)
print(ds)
```


## License

MIT © Arulnidhi Karunanidhi
