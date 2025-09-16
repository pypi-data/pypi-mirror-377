from __future__ import annotations
import difflib, re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def unified(a: str, b: str, path: str) -> str:
    diff = difflib.unified_diff(
        a.splitlines(True),
        b.splitlines(True),
        fromfile=f"{path} (original)",
        tofile=f"{path} (proposed)",
        lineterm=""
    )
    return "".join(diff)


def extract_between(text: str, start_tag: str, end_tag: str) -> Optional[str]:
    m = re.search(re.escape(start_tag) + r"(.*?)" + re.escape(end_tag), text, re.DOTALL)
    return m.group(1).strip() if m else None


def extract_urls_from_response(resp: Any) -> List[Tuple[str, str]]:
    urls: List[Tuple[str, str]] = []
    # Try annotations if present
    try:
        outputs = getattr(resp, "output", []) or []
        for item in outputs:
            content = getattr(item, "content", []) or []
            for c in content:
                anns = c.get("annotations") if isinstance(c, dict) else getattr(c, "annotations", None)
                if not anns:
                    continue
                for a in anns:
                    t = a.get("type") if isinstance(a, dict) else getattr(a, "type", "")
                    if t == "url_citation":
                        title = a.get("title", "")
                        url = a.get("url", "")
                        if url: urls.append((title, url))
    except Exception:
        pass
    # Fallback: scrape URLs from text
    text = getattr(resp, "output_text", "") or ""
    for u in re.findall(r"https?://\S+", text):
        urls.append(("", u.rstrip(").,]")))
    # Dedup
    seen = set(); out = []
    for t, u in urls:
        if u not in seen:
            seen.add(u); out.append((t, u))
    return out


def function_tools() -> List[Dict[str, Any]]:
    return [
        {"type": "function", "function": {
            "name": "fs_write",
            "description": "Write a UTF-8 text file to disk. Use sparingly and only when user intent is clear.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"],
                "additionalProperties": False
            }
        }},
    ]
