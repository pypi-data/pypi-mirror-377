# sentimini – Sentiment Analyzer
Sentiment analysis package is very lightweight package for analysis sentiment.

Uses rule-based + lexicon approach for quick polarity detection.

## Installation

```bash
pip install sentimini
```

## Usage

```bash
from sentimini import polarity, score

print(polarity("I love this product!"))   # positive
print(polarity("This is terrible..."))    # negative
print(polarity("It is okay."))            # neutral

print(score("I really love this!"))
# { "polarity": "positive", "score": 0.8 }
```

## Features

✅ Tiny & fast (no ML models)

✅ Works offline

✅ Rule-based with lexicon

✅ Supports negations & intensifiers

✅ Extensible word lists