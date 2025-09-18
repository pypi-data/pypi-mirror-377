import re
import time
from typing import Dict, List, Optional, Tuple

import httpx

from .database import Database
from .utils import sha256_hex


def _split_into_words(text: str) -> List[str]:
    return re.findall(r"\S+", text)


def chunk_text_words(text: str, min_tokens: int = 700, max_tokens: int = 900) -> List[str]:
    words = _split_into_words(text)
    chunks: List[str] = []
    i = 0
    n = len(words)
    while i < n:
        size = min(max_tokens, n - i)
        # Prefer a split near max but at sentence boundary
        end = i + size
        if end < n:
            # Try to move backward to nearest sentence end
            back = end
            while back > i + min_tokens and not re.search(r"[.!?]$", words[back - 1]):
                back -= 1
            if back > i + min_tokens:
                end = back
        chunk = " ".join(words[i:end])
        chunks.append(chunk)
        i = end
    return chunks


def sanitize_html_to_text(html: str) -> str:
    # Drop script/style
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.IGNORECASE)
    # Remove tags
    text = re.sub(r"<[^>]+>", " ", html)
    # Unescape basic entities
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def register_doc(db: Database, title: str, text: str, source: Optional[str] = None, project_id: Optional[int] = None, version: int = 1) -> Dict:
    doc_id = db.create_doc(title=title, source=source, project_id=project_id, version=version)
    chunks = chunk_text_words(text, 700, 900)
    for idx, chunk in enumerate(chunks):
        db.add_doc_chunk(doc_id=doc_id, chunk_index=idx, text=chunk, sha256=sha256_hex(chunk.encode("utf-8")))
    return {"doc_id": doc_id, "chunks": len(chunks)}


def register_doc_url(db: Database, url: str, title: Optional[str] = None, project_id: Optional[int] = None) -> Dict:
    with httpx.Client(timeout=15) as client:
        resp = client.get(url)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "").lower()
        text: str
        if "html" in content_type:
            text = sanitize_html_to_text(resp.text)
        else:
            text = resp.text
    return register_doc(db=db, title=title or url, text=text, source=url, project_id=project_id, version=1)


def search_docs(db: Database, query: str, limit: int = 20, offset: int = 0) -> List[Dict]:
    return db.search_docs(query=query, limit=limit, offset=offset)


def get_doc_chunk(db: Database, doc_id: int, chunk_index: int) -> Optional[Dict]:
    return db.get_doc_chunk(doc_id=doc_id, chunk_index=chunk_index)
