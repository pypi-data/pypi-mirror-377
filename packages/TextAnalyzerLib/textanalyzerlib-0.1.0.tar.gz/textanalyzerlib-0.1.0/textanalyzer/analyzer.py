from collections import Counter
import string

def count_words(text: str) -> int:
    return len(text.split())

def count_sentences(text: str) -> int:
    return text.count('.') + text.count('!') + text.count('?')

def count_characters(text: str) -> int:
    return len(text)

def word_frequency(text: str) -> dict:
    words = [word.strip(string.punctuation).lower() for word in text.split()]
    return dict(Counter(words))

def analyze_text(text: str) -> dict:
    return {
        "words": count_words(text),
        "sentences": count_sentences(text),
        "characters": count_characters(text),
        "frequency": word_frequency(text)
    }
