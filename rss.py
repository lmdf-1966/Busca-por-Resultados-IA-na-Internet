
from typing import List, Dict, Any
import feedparser

def read_feeds(feeds: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    items = []
    for f in feeds:
        try:
            parsed = feedparser.parse(f["url"])
            for e in parsed.entries:
                items.append({
                    "source": f["name"],
                    "title": getattr(e, "title", ""),
                    "url": getattr(e, "link", ""),
                    "published": getattr(e, "published", "") or getattr(e, "updated", ""),
                    "summary": getattr(e, "summary", ""),
                })
        except Exception as ex:
            # Swallow and continue
            pass
    return items
