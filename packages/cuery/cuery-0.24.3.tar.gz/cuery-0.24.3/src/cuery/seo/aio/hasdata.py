import json
import os
import re
from collections.abc import Iterable
from typing import Any

import requests

from ...search import SearchResult, Source
from ...utils import LOG


def _clean_text(text: str) -> str:
    """Normalize whitespace inside extracted snippets.

    Collapses multiple spaces, trims each line and removes trailing spaces while
    preserving single newlines. Empty lines are kept only once.
    """
    if not text:
        return ""
    # Replace non-breaking spaces etc.
    text = text.replace("\u00a0", " ")
    # Collapse internal whitespace sequences (but not newlines)
    text = re.sub(r"[ \t]+", " ", text)
    # Strip line ends
    lines = [line.strip() for line in text.splitlines()]
    # Remove duplicate empty lines
    cleaned: list[str] = []
    for line in lines:
        if line or (cleaned and cleaned[-1]):
            cleaned.append(line)
    return "\n".join(cleaned).strip()


def _iter_list_items(items: Iterable[dict], indent: int = 0) -> Iterable[str]:
    """Yield bullet-point lines from a (possibly nested) list block structure."""
    prefix = "  " * indent + "- "
    for obj in items:
        title = obj.get("title", "") or ""
        snippet = obj.get("snippet", "") or ""
        # Avoid duplicate colon spacing (title often ends with ':')
        if title and snippet and title.endswith(":"):
            line = f"{title} {snippet}".strip()
        else:
            line = " ".join(part for part in [title, snippet] if part).strip()
        if line:
            yield prefix + _clean_text(line)
        # Nested items
        if "list" in obj and isinstance(obj["list"], list):
            yield from _iter_list_items(obj["list"], indent + 1)


def _format_table(block: dict) -> str:
    rows: list[list[str]] = block.get("rows") or []
    if not rows:
        return ""
    out: list[str] = []
    header = rows[0]
    out.append(" | ".join(header))
    for row in rows[1:]:
        out.append(" | ".join(row))
    return "\n".join(out)


def _format_code(block: dict) -> str:
    lang = block.get("language") or ""
    snippet = block.get("snippet") or ""
    if not snippet:
        return ""
    header = f"[Code{(': ' + lang) if lang else ''}]"
    return f"{header}\n{snippet.strip()}"


def parse_aio(aio: dict) -> SearchResult:
    """Parse HasData ``aiOverview`` object into a unified ``SearchResult``.

    Documentation: https://docs.hasdata.com/apis/google-serp-api/rich-snippets/ai-overview

    We concatenate textual content from the following block *types* in order:
    paragraph, list (including nested lists), table, code, video (snippet), carousel (ignored –
    mostly images). Unknown types are skipped silently to remain forward-compatible.

    Lists are flattened into bullet points. Tables become pipe-delimited lines with the
    first row treated as a header. Code blocks are prefixed with a ``[Code:<lang>]`` marker.
    Whitespace is normalized and excessive blank lines removed.
    """
    text_blocks: list[dict] = (
        aio.get("textBlocks") or aio.get("aiOverview", {}).get("textBlocks") or []
    )
    # Support case when caller passes whole response object instead of only aiOverview

    parts: list[str] = []
    handlers = {
        "paragraph": lambda b: _clean_text(b.get("snippet", "")),
        "list": lambda b: "\n".join(_iter_list_items(b.get("list") or [])),
        "table": _format_table,
        "code": _format_code,
    }
    for block in text_blocks:
        # Fallback to paragraph if snippet but no explicit type
        btype = block.get("type") or ("paragraph" if "snippet" in block else None)
        if not btype or btype == "carousel":  # skip carousels
            continue
        handler = handlers.get(btype)
        if handler:
            rendered = handler(block)
            if rendered:
                parts.append(rendered)
        else:
            # Generic fallback: use snippet if present (covers video etc.)
            snippet = block.get("snippet") or ""
            if snippet:
                parts.append(_clean_text(snippet))

    # Deduplicate consecutive identical parts
    deduped: list[str] = []
    for p in parts:
        if not deduped or deduped[-1] != p:
            deduped.append(p)

    answer = _clean_text("\n\n".join(deduped))

    # References -> sources
    refs = aio.get("references") or aio.get("aiOverview", {}).get("references") or []
    sources: list[Source] = []
    for r in refs:
        link = r.get("link") or r.get("url")
        title = r.get("title") or (link or "")
        if link:
            sources.append(Source(title=title, url=link))

    result = SearchResult(answer=answer, sources=sources)
    result._raw_response = aio  # type: ignore[attr-defined]
    return result


def aio_request_params(aio: dict) -> dict | None:
    """Check if we need to make a second request to get the actual AI overview.

    https://docs.hasdata.com/apis/google-serp-api/rich-snippets/ai-overview#ai-overview-with-extra-request
    """
    keys = set(aio.keys())
    if keys == {"pageToken", "hasdataLink"}:
        return {"pageToken": aio["pageToken"]}

    return None


def query_hasdata(
    prompt: str,
    country: str | None = None,  # 2-letter country code, e.g. "us"
    language: str | None = None,  # 2-letter language code, e.g. "en"
    validate: bool = True,
    timeout: int = 10,
) -> SearchResult | dict[str, Any]:
    """Execute a Google search via HasData and extract AI Overview.

    When ``validate`` is True (default) returns a ``SearchResult`` with plain text
    concatenated from all supported AI Overview blocks plus structured sources
    (citations). If ``validate`` is False the raw ``aiOverview`` dictionary is
    returned for debugging.
    """
    api_key = os.environ["HASDATA_API_KEY"]
    serp_endpoint = "https://api.hasdata.com/scrape/google/serp"
    aio_endpoint = "https://api.hasdata.com/scrape/google/ai-overview"

    params = {"q": prompt}
    if country:
        params["gl"] = country
    if language:
        params["hl"] = language

    # First request, may or may not contain the AI overview
    headers = {"x-api-key": api_key}
    resp = requests.get(
        serp_endpoint,
        params=params,
        timeout=timeout,
        headers=headers,
    )
    resp.raise_for_status()
    content = resp.json()
    print(f"Request URL: {resp.request.url}")
    print("Response:")
    print(json.dumps(content, indent=2))

    aio = content.get("aiOverview") or {}
    if aio_params := aio_request_params(aio):
        # Need to make second request
        LOG.warning(f"Need second request to get AI overview for prompt: {prompt}")
        headers = {"x-api-key": api_key, "Content-Type": "application/json"}
        resp = requests.get(
            aio_endpoint,
            params=aio_params,
            timeout=timeout,
            headers=headers,
        )
        resp.raise_for_status()
        content = resp.json()
        print(f"Second Request URL: {resp.request.url}")
        print("Second request response:")
        print(json.dumps(content, indent=2))
        aio = content.get("aiOverview") or {}

    if validate:
        return parse_aio(aio)

    return aio
