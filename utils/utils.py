import re
import os

EXCLUDED_EXTENSIONS = {".mp3", ".csv", ".doc", ".xlsx"}

def is_valid_url(url: str) -> bool:
    """Checks if a URL should be processed."""
    return not any(url.endswith(ext) for ext in EXCLUDED_EXTENSIONS) and '/es' not in url

def load_urls(filename: str = "resources/urls.txt") -> list:
    """Loads URLs from a file, filtering out unwanted extensions."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found.")

    with open(filename, "r") as file:
        urls = [line.strip() for line in file.readlines()]
    return [url for url in urls if is_valid_url(url)]

def preprocess_text(text: str) -> str:
    text = remove_links(text)
    text = remove_footnotes_policymanual(text)
    text = strip_text(text)

    return text

def strip_text(text: str) -> str:
    text = text.strip()
    return text

def remove_links(text: str) -> str:

    # Regular expression to remove the links but keep the text
    pattern = r"\[([^\]]+)\]\(https?://[^\)]+\)"

    # Replace links with just the text inside the brackets
    cleaned_text = re.sub(pattern, r"\1", text)

    return cleaned_text

def remove_footnotes_policymanual(text: str) -> str:
    marker = "## Footnotes"
    idx = text.find(marker)
    if idx != -1:
        text = text[:idx].rstrip()
    return text

