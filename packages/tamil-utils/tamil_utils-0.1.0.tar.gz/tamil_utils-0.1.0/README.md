# tamil-utils

Tiny **Tamil** text utilities: `normalize`, `tokens`, `remove_stopwords`, `graphemes`.

```python
from tamil_utils import normalize, tokens, remove_stopwords, graphemes

s = "இது ஒரு சோதனை 👋🏽"
print(tokens(s))                              # ['இது', 'ஒரு', 'சோதனை']
print(remove_stopwords(tokens(s), preset="ta"))  # ['சோதனை']
print(graphemes("👩🏽‍💻"))                       # ['👩🏽‍💻']
                      # ['👩🏽‍💻']

```
## Installation

```python
pip install tamil-utils
```
# Windows CLI (module form)
```python
python -m tamil_utils.cli tokens "இது ஒரு சோதனை"
```
# Sentence split
```python
python -m tamil_utils.cli sents "இது ஒரு வாக்கியம். இது இரண்டாம்? சரி!"
```

# Numerals
```python
python -m tamil_utils.cli to-arabic "௨௦௨௫"   # -> 2025
python -m tamil_utils.cli to-tamil "123"     # -> ௧௨௩
```

# Tokens with stopwords removed (preset)
python -m tamil_utils.cli tokens --rmstop "இது ஒரு சோதனை"

## Status
[![PyPI](https://img.shields.io/pypi/v/tamil-utils)](https://pypi.org/project/tamil-utils/)
[![CI](https://github.com/arulnidhii/tamil-utils/actions/workflows/ci.yml/badge.svg)](https://github.com/arulnidhii/tamil-utils/actions)
