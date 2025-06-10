import os
import json
import fitz  # PyMuPDF
import re

from pathlib import Path

LIBRARY_DIR = Path('library')
CATALOG_FILE = LIBRARY_DIR / 'catalog.json'

# Mapping of trigger words to keywords
KEYWORD_MAP = {
    "jesus": ["christianity", "abrahamic"],
    "christ": ["christianity"],
    "jehovah": ["abrahamic", "christianity"],
    "yahweh": ["abrahamic"],
    "allah": ["abrahamic", "islam"],
    "muhammad": ["islam"],
    "torah": ["judaism"],
    "talmud": ["judaism"],
    "end-times": ["eschatology"],
    "apocalypse": ["eschatology"],
    "prophecy": ["eschatology"],
    "baptism": ["christianity"],
    "eucharist": ["catholicism"],
    "vatican": ["catholicism"],
    "heaven": ["eschatology"],
    "hell": ["eschatology"],
    "soul": ["philosophy"],
    "logos": ["philosophy"],
    "metaphysics": ["philosophy"],
    "revelation": ["eschatology"]
}

# Normalize keyword map for matching
TRIGGER_WORDS = {k.lower(): v for k, v in KEYWORD_MAP.items()}

def extract_text(path):
    try:
        with fitz.open(path) as doc:
            return " ".join(page.get_text() for page in doc[:3])  # limit to first 3 pages
    except Exception as e:
        print(f"Failed to extract text from {path}: {e}")
        return ""

def extract_metadata_from_filename(path):
    rel = path.relative_to(LIBRARY_DIR)
    section = rel.parts[0].lower()
    filename = rel.name
    match = re.match(r"(.+)_([^_]+)\\.pdf$", filename)
    if not match:
        print(f"Filename does not match pattern: {filename}")
        return None
    title, author = match.groups()
    title = title.replace('_', ' ').strip()
    author = author.replace('_', ' ').strip()
    return title, author, section

def infer_keywords(text):
    text = text.lower()
    found = set()
    for word, keywords in TRIGGER_WORDS.items():
        if word in text:
            found.update(keywords)
    return sorted(found)

def build_catalog():
    catalog = []
    for pdf_path in LIBRARY_DIR.rglob("*.pdf"):
        meta = extract_metadata_from_filename(pdf_path)
        if not meta:
            continue
        title, author, section = meta
        text = extract_text(pdf_path)
        keywords = infer_keywords(text)
        catalog.append({
            "title": title,
            "author": author,
            "section": section,
            "keywords": keywords,
            "path": str(pdf_path).replace('\\', '/')
        })
    return catalog

def save_catalog(entries):
    with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    catalog = build_catalog()
    save_catalog(catalog)
    print(f"Catalog updated with {len(catalog)} entries.")
