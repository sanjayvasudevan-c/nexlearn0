from duckduckgo_search import DDGS


def search_web(query: str):

    results = []

    with DDGS() as ddgs:

        for r in ddgs.text(query + " study notes", max_results=10):
            results.append(r["href"])

    return results