import re
from .lexicon import POSITIVE_WORDS, NEGATIVE_WORDS, NEGATIONS, INTENSIFIERS

# Allow user to extend lexicon dynamically
def add_words(positive=None, negative=None):
    if positive:
        POSITIVE_WORDS.update(positive)
    if negative:
        NEGATIVE_WORDS.update(negative)

def tokenize(text: str):
    return re.findall(r"\b\w+\b", text.lower())

def score(text: str):
    tokens = tokenize(text)
    total, negate, boost = 0, False, 1

    for word in tokens:
        if word in NEGATIONS:
            negate = True
            continue
        if word in INTENSIFIERS:
            boost = 2
            continue

        if word in POSITIVE_WORDS:
            total += (1 if not negate else -1) * boost
            negate, boost = False, 1
        elif word in NEGATIVE_WORDS:
            total += (-1 if not negate else 1) * boost
            negate, boost = False, 1

    # Punctuation as booster
    if "!" in text:
        total *= 1.2

    # Normalize
    if total > 0:
        return {"polarity": "positive", "score": round(min(total / 5, 1), 2)}
    elif total < 0:
        return {"polarity": "negative", "score": round(max(total / 5, -1), 2)}
    else:
        return {"polarity": "neutral", "score": 0.0}

def polarity(text: str) -> str:
    return score(text)["polarity"]
