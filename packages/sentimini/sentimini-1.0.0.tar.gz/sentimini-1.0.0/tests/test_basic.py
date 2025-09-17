from sentimini import polarity, score

def test_positive():
    assert polarity("I love this!") == "positive"

def test_negative():
    assert polarity("This is terrible") == "negative"

def test_neutral():
    assert polarity("It is okay.") == "neutral"

def test_score():
    result = score("I really love this!")
    assert result["polarity"] == "positive"
    assert 0 < result["score"] <= 1
