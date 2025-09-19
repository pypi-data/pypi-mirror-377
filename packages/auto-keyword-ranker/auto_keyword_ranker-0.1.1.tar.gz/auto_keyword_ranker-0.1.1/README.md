# auto-keyword-ranker
[![PyPI version](https://img.shields.io/pypi/v/auto-keyword-ranker)](https://pypi.org/project/auto-keyword-ranker)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Lightweight Python package to extract and rank the most relevant keywords and keyphrases from text.

**Goal:** One-line call to get ranked keywords for articles, blog posts, or short documents.  
Core approach uses TF-IDF; optional re-ranking with sentence-transformer embeddings.

## Install

Core (TF-IDF only):

```bash
pip install auto-keyword-ranker


Quickstart

from autokeyword import rank_keywords

text = """
Artificial intelligence is transforming industries by enabling new capabilities 
such as natural language processing, computer vision, and advanced data analytics.
"""

# Simple TF-IDF keyword ranking
keywords = rank_keywords(text, top_n=5)
print(keywords)


Output

A list of (keyword, score) pairs, for example:

[('artificial intelligence', 0.42),
 ('data analytics', 0.33),
 ('natural language processing', 0.29),
 ('computer vision', 0.25),
 ('industries', 0.21)]


How It Works

TF-IDF scoring formula:


$$
\mathrm{TF\!-\!IDF}(t,d)=\mathrm{TF}(t,d)\times
\log \frac{N}{1+\mathrm{DF}(t)}
$$

TF(t,d) – Term frequency of term t in document d
DF(t) – Number of documents containing term t
N – Total number of documents


License

MIT License – see LICENSE file.