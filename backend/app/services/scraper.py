import trafilatura


def extract_text(url: str):

    try:

        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return None

        text = trafilatura.extract(downloaded)

        return text

    except Exception:
        return None