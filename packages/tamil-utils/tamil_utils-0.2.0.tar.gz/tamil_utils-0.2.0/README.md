````markdown
# tamil-utils

Tiny **Tamil-first** text utilities for Unicode-safe text handling and preprocessing.

[![PyPI](https://img.shields.io/pypi/v/tamil-utils)](https://pypi.org/project/tamil-utils/)
[![CI](https://github.com/arulnidhii/tamil-utils/actions/workflows/ci.yml/badge.svg)](https://github.com/arulnidhii/tamil-utils/actions)
[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://arulnidhii.github.io/tamil-utils/)

---

## Features

- **Core**: `normalize`, `tokens`, `remove_stopwords`, `graphemes`
- **Sentences & numerals**: `sents`, `to_arabic_numerals`, `to_tamil_numerals`
- **Script & transliteration**: `script_of`, `token_scripts`, `transliterate_iso15919`
- **v0.2 (WIP)**: `ngrams`, `bigrams`, `trigrams`, `word_counts`, `syllables`, `sort_tamil`

---

## Install

```bash
pip install tamil-utils
````

---

## Quick start (Python)

```python
from tamil_utils import (
    normalize, tokens, remove_stopwords, graphemes,
    sents, to_arabic_numerals, to_tamil_numerals,
    script_of, token_scripts, transliterate_iso15919,
    # v0.2 (WIP)
    word_counts, sort_tamil
)

s = "இது ஒரு சோதனை. இது இரண்டாம்? சரி! ௨௦௨௫"
print(tokens(s))                                # ['இது','ஒரு','சோதனை','இது','இரண்டாம்','சரி','௨௦௨௫']
print(remove_stopwords(tokens(s), preset="ta")) # stopwords removed
print(graphemes("👩🏽‍💻"))                         # emoji-safe graphemes
print(sents(s))                                  # sentence split
print(to_arabic_numerals("௨௦௨௫"))                 # "2025"
print(transliterate_iso15919("தமிழ்"))             # "tamiḻ"
print(token_scripts(tokens("கோட்123 hello")))     # [('கோட்123','Mixed'), ('hello','Latin')]

# v0.2 (WIP)
print(word_counts("தமிழ் NLP தமிழ் பயன்பாடு தமிழ் NLP", n=2, top=2))  # bigram freq
print(sort_tamil(["இலங்கை","ஆதி","அடி"]))                         # ['அடி','ஆதி','இலங்கை']
```

---

## CLI

```bash
# tokens / stopwords / graphemes / sents
python -m tamil_utils.cli tokens "இது ஒரு சோதனை"
python -m tamil_utils.cli tokens --rmstop "இது ஒரு சோதனை"
python -m tamil_utils.cli graphemes "👩🏽‍💻"
python -m tamil_utils.cli sents "இது ஒரு வாக்கியம். இது இரண்டாம்? சரி!"

# numerals
python -m tamil_utils.cli to-arabic "௨௦௨௫"   # -> 2025
python -m tamil_utils.cli to-tamil "123"     # -> ௧௨௩

# transliteration & script tags
python -m tamil_utils.cli to-iso "தமிழ்"
python -m tamil_utils.cli script "கோட்123 hello"

# v0.2 (WIP): n-grams, frequency, syllables, sort
python -m tamil_utils.cli ngrams -n 3 "தமிழ் NLP பயன்பாடு"
python -m tamil_utils.cli freq -n 2 --top 5 "தமிழ் NLP தமிழ் பயன்பாடு தமிழ் NLP"
python -m tamil_utils.cli syllables "தமிழ்🙂 test 123"
# sort: pass words as args or via stdin
python -m tamil_utils.cli sort இலங்கை ஆதி அடி
type words.txt | python -m tamil_utils.cli sort
```

---

## Status

* **PyPI**: [https://pypi.org/project/tamil-utils/](https://pypi.org/project/tamil-utils/)
* **Docs**: [https://arulnidhii.github.io/tamil-utils/](https://arulnidhii.github.io/tamil-utils/)

---


