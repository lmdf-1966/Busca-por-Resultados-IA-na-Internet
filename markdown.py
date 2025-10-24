
from typing import List, Dict
import pathlib, datetime
from ..utils.io import OUT_DIR

def write_daily_report(items: List[Dict]) -> str:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    path = OUT_DIR / f"digest-{today}.md"
    lines = [f"# IA — Casos mensuráveis ({today})\n"]
    if not items:
        lines.append("_Nenhum item mensurável encontrado hoje._\n")
    for it in items:
        lines.append(f"## {it['title']}\n")
        lines.append(f"Fonte: **{it['source']}**  \nLink: {it['url']}\n")
        lines.append(f"Publicado: {it.get('published','')}\n")
        if it.get("value_signals"):
            lines.append(f"Sinais de valor: {it['value_signals']}\n")
        lines.append("\n---\n")
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)
