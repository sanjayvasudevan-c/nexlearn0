from app.services.scraper import extract_text
from app.services.ai_summarizer import summarize_text
from app.services.web_search import search_web


def generate_ai_notes(topic: str):

    urls = search_web(topic)

    collected_text = []

    for url in urls[:5]:

        text = extract_text(url)

        if text:
            collected_text.append(text[:4000])

    if not collected_text:
        return None

    combined_text = "\n".join(collected_text)

    summary = summarize_text(topic, combined_text)

    return {
        "topic": topic,
        "summary": summary,
        "sources": urls[:5]
    }