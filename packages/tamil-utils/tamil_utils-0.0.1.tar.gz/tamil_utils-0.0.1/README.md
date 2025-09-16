# tamil-utils

Tiny **Tamil** text utilities: `normalize`, `tokens`, `remove_stopwords`, `graphemes`.

```python
from tamil_utils import normalize, tokens, remove_stopwords, graphemes

s = "இது ஒரு சோதனை 👋🏽"
print(tokens(s))                        # ['இது', 'ஒரு', 'சோதனை']
print(remove_stopwords(tokens(s)))      # ['சோதனை']
print(graphemes("👩🏽‍💻"))               # ['👩🏽‍💻']
