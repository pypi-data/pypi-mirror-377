# auto-keyword-ranker
[![PyPI version](https://img.shields.io/pypi/v/auto-keyword-ranker)](https://pypi.org/project/auto-keyword-ranker)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)


Lightweight Python package to extract and rank the most relevant keywords and keyphrases from text.


**Goal:** One-line call to get ranked keywords for articles, blog posts, or short documents. Core approach uses TF-IDF; optional re-ranking with sentence-transformer embeddings.


## Install


Core (TF-IDF only):


```bash
pip install autokeyword