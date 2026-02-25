import re

STOPWORDS = {
    "on", "for", "in", "the", "a", "an", "and", "of", "to"
}

def normalize_topic(query: str) -> str:
    # Lowercase
    query = query.lower()

    # Remove non-alphanumeric characters
    query = re.sub(r"[^a-z0-9\s]", "", query)

    # Split into words
    words = query.split()

    # Remove stopwords
    words = [w for w in words if w not in STOPWORDS]

    # Sort words to create canonical form
    words.sort()

    return " ".join(words)