# auto-keyword-ranker
[![PyPI version](https://img.shields.io/pypi/v/auto-keyword-ranker)](https://pypi.org/project/auto-keyword-ranker)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Lightweight Python package to extract and rank the most relevant keywords and keyphrases from text.

**Goal:** One-line call to get ranked keywords for articles, blog posts, or short documents.  
Core approach uses **TF-IDF**; optional re-ranking with **sentence-transformer embeddings**.

---

## Installation

```bash
pip install auto-keyword-ranker
```

With optional embedding-based re-ranking:
```bash
pip install auto-keyword-ranker[embed]
```



---
Quickstart

```python
from autokeyword import rank_keywords

text = """
Artificial intelligence is transforming industries by enabling new capabilities
such as natural language processing, computer vision, and advanced data analytics.
"""

# Simple TF-IDF keyword ranking
keywords = rank_keywords(text, top_n=5)
print(keywords)
```


Output

A list of (keyword, score) pairs, for example:



```python
[('artificial intelligence', 0.42),
 ('data analytics', 0.33),
 ('natural language processing', 0.29),
 ('computer vision', 0.25),
 ('industries', 0.21)]
```
---
API

rank_keywords(texts, top_n=10, method='tfidf', ngram_range=(1,2), stop_words=True, use_embeddings=False, embedding_model=None, combine_score_alpha=0.6)

See docstrings in autokeyword/core.py for full parameter descriptions.

---
CLI

You can also run the CLI (after installation):
```python
python -m autokeyword.cli --text "Your article text here" --top 10
```


---

How It Works
TF-IDF scoring formula:

$$
\text{TF-IDF}(t, d) = \text{TF}(t, d) \times \log \frac{N}{1 + \text{DF}(t)}
$$

Where:
- \( t \) = term  
- \( d \) = document  
- \( N \) = total number of documents  


---
License


[MIT License](LICENSE) © 2025 Reya Oberoi