from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
try:
    from platformdirs import user_config_dir, user_state_dir  # type: ignore

    def _user_config_dir(app: str) -> Path:
        return Path(user_config_dir(app))

    def _user_state_dir(app: str) -> Path:
        return Path(user_state_dir(app))
except Exception:
    # Fallbacks when platformdirs is not available (graceful for global installs)
    def _user_config_dir(app: str) -> Path:
        return Path.home() / ".config" / app

    def _user_state_dir(app: str) -> Path:
        return Path.home() / ".local" / "share" / app

APP = "edge-assistant"
CFG_DIR = _user_config_dir(APP)
STATE_DIR = _user_state_dir(APP)
CFG_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR.mkdir(parents=True, exist_ok=True)

STATE_PATH = STATE_DIR / "state.json"

def _load() -> Dict[str, Any]:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {}

def _save(d: Dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(d, indent=2))

def get_thread_id(name: Optional[str]) -> Optional[str]:
    s = _load()
    if name:
        return s.get("threads", {}).get(name)
    return s.get("last_response_id")

def set_thread_id(resp_id: str, name: Optional[str]) -> None:
    s = _load()
    s.setdefault("threads", {})
    if name:
        s["threads"][name] = resp_id
    s["last_response_id"] = resp_id
    _save(s)

def kb_ids() -> List[str]:
    s = _load()
    return s.get("kb_file_ids", [])

def add_kb_ids(ids: List[str]) -> None:
    s = _load()
    prev = set(s.get("kb_file_ids", []))
    prev.update(ids)
    s["kb_file_ids"] = sorted(prev)
    _save(s)

def get_kb_vector_store_id() -> Optional[str]:
    """Get the vector store ID for knowledge base."""
    s = _load()
    return s.get("kb_vector_store_id")

def set_kb_vector_store_id(vector_store_id: str) -> None:
    """Set the vector store ID for knowledge base."""
    s = _load()
    s["kb_vector_store_id"] = vector_store_id
    _save(s)

# ---------- VISION THREAD MANAGEMENT ----------

# ---------- MULTIMODAL THREAD MANAGEMENT ----------

def get_multimodal_thread_info(name: str) -> Dict[str, Any]:
    """Get information about a multimodal thread including content counts and metadata."""
    s = _load()
    multimodal_threads = s.get("multimodal_threads", {})
    return multimodal_threads.get(name, {
        "content_counts": {"text": 0, "image": 0, "audio": 0, "video": 0, "file": 0},
        "last_activity": 0,
        "response_id": None,
        "model_used": None,
        "total_interactions": 0
    })

def update_multimodal_thread(name: str, response_id: str, content_type: str, model: str) -> None:
    """Update multimodal thread metadata with content type tracking."""
    s = _load()
    s.setdefault("multimodal_threads", {})
    
    thread_info = s["multimodal_threads"].get(name, {
        "content_counts": {"text": 0, "image": 0, "audio": 0, "video": 0, "file": 0},
        "last_activity": 0,
        "response_id": None,
        "model_used": None,
        "total_interactions": 0
    })
    
    # Update content count
    if content_type in thread_info["content_counts"]:
        thread_info["content_counts"][content_type] += 1
    
    # Update metadata
    thread_info["last_activity"] = int(time.time())
    thread_info["response_id"] = response_id
    thread_info["model_used"] = model
    thread_info["total_interactions"] += 1
    
    s["multimodal_threads"][name] = thread_info
    _save(s)

def clear_multimodal_thread(name: str) -> bool:
    """Clear a specific multimodal thread. Returns True if thread existed."""
    s = _load()
    multimodal_threads = s.get("multimodal_threads", {})
    if name in multimodal_threads:
        del multimodal_threads[name]
        s["multimodal_threads"] = multimodal_threads
        _save(s)
        return True
    return False

def cleanup_old_multimodal_threads(max_age_days: int = 7) -> int:
    """Remove multimodal threads older than max_age_days. Returns count of cleaned threads."""
    s = _load()
    multimodal_threads = s.get("multimodal_threads", {})
    
    cutoff_time = int(time.time()) - (max_age_days * 24 * 60 * 60)
    old_threads = [name for name, info in multimodal_threads.items() 
                   if info.get("last_activity", 0) < cutoff_time]
    
    for name in old_threads:
        del multimodal_threads[name]
    
    if old_threads:
        s["multimodal_threads"] = multimodal_threads
        _save(s)
    
    return len(old_threads)

def get_multimodal_thread_id(name: str) -> Optional[str]:
    """Get the response ID for a multimodal thread."""
    thread_info = get_multimodal_thread_info(name)
    return thread_info.get("response_id")

def get_thread_content_summary(name: str) -> str:
    """Get a human-readable summary of thread content."""
    thread_info = get_multimodal_thread_info(name)
    counts = thread_info["content_counts"]
    total = thread_info["total_interactions"]
    
    if total == 0:
        return "Empty thread"
    
    # Build summary of content types
    content_parts = []
    for content_type, count in counts.items():
        if count > 0:
            content_parts.append(f"{count} {content_type}")
    
    summary = ", ".join(content_parts) if content_parts else "text only"
    return f"{total} interactions ({summary})"

# ---------- LEGACY VISION THREAD SUPPORT (for backward compatibility) ----------

def get_vision_thread_info(name: str) -> Dict[str, Any]:
    """Legacy: Get vision thread info. Redirects to multimodal thread info."""
    thread_info = get_multimodal_thread_info(name)
    return {
        "image_count": thread_info["content_counts"]["image"],
        "last_activity": thread_info["last_activity"],
        "response_id": thread_info["response_id"]
    }

def update_vision_thread(name: str, response_id: str, increment_images: bool = True) -> None:
    """Legacy: Update vision thread. Redirects to multimodal thread update."""
    if increment_images:
        update_multimodal_thread(name, response_id, "image", "gpt-4o")

def clear_vision_thread(name: str) -> bool:
    """Legacy: Clear vision thread. Redirects to multimodal thread clear."""
    return clear_multimodal_thread(name)

def cleanup_old_vision_threads(max_age_days: int = 7) -> int:
    """Legacy: Cleanup old vision threads. Redirects to multimodal cleanup."""
    return cleanup_old_multimodal_threads(max_age_days)

def get_vision_thread_id(name: str) -> Optional[str]:
    """Legacy: Get vision thread ID. Redirects to multimodal thread ID."""
    return get_multimodal_thread_id(name)
