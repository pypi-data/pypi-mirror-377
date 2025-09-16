# tamil-utils

Tiny **Tamil** text utilities: `normalize`, `tokens`, `remove_stopwords`, `graphemes`.

```python
from tamil_utils import normalize, tokens, remove_stopwords, graphemes

s = "இது ஒரு சோதனை 👋🏽"
print(tokens(s))                        # ['இது', 'ஒரு', 'சோதனை']
print(remove_stopwords(tokens(s)))      # ['சோதனை']
print(graphemes("👩🏽‍💻"))               # ['👩🏽‍💻']
```

## Installation
pip install tamil-utils
# Windows CLI (module form avoids PATH issues)
python -m tamil_utils.cli tokens "இது ஒரு சோதனை"

### New in v0.0.2
```bash
# Sentence split
python -m tamil_utils.cli sents "இது ஒரு வாக்கியம். இது இரண்டாம்? சரி!"

# Numerals
python -m tamil_utils.cli to-arabic "௨௦௨௫"   # -> 2025
python -m tamil_utils.cli to-tamil "123"     # -> ௧௨௩

# Tokens with stopwords removed (preset)
python -m tamil_utils.cli tokens --rmstop "இது ஒரு சோதனை"


[![PyPI version](https://img.shields.io/pypi/v/tamil-utils)](https://pypi.org/project/tamil-utils/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/tamil-utils)
