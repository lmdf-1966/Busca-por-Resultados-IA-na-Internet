
import os, yaml, datetime
from typing import List, Dict
from dotenv import load_dotenv
from .searchers.rss import read_feeds
from .fetcher.html import fetch_and_extract
from .extractors.value_signals import extract_signals, is_measurable
from .utils.io import db, upsert_item, fetch_recent
from .reporters.markdown import write_daily_report
from .notifiers.emailer import send_mail

def load_sources() -> Dict:
    cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sources.yaml")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def filter_by_keywords(items: List[Dict], must_include: List[str], must_exclude: List[str], domain_exclude: List[str]) -> List[Dict]:
    out = []
    for it in items:
        text = ((it.get("title") or "") + " " + (it.get("summary") or "")).lower()
        url = (it.get("url") or "").lower()
        if any(dom in url for dom in (domain_exclude or [])):
            continue
        if must_include and not any(k.lower() in text for k in must_include):
            continue
        if must_exclude and any(k.lower() in text for k in must_exclude):
            continue
        out.append(it)
    return out

def run() -> str:
    load_dotenv()
    cfg = load_sources()
    feeds = cfg.get("feeds", [])
    must_include = cfg.get("must_include", [])
    must_exclude = cfg.get("must_exclude", [])
    domain_exclude = cfg.get("domain_exclude", [])

    # 1) Coletar
    raw_items = read_feeds(feeds)

    # 2) Filtrar por keywords/domínios
    filtered = filter_by_keywords(raw_items, must_include, must_exclude, domain_exclude)

    # 3) Baixar e extrair texto + sinais de valor
    conn = db()
    enriched = []
    for it in filtered[:50]:  # limite de cortesia por rodada
        content = fetch_and_extract(it["url"])
        signals = extract_signals(content)
        measurable = 1 if is_measurable(signals) else 0
        upsert_item(conn,
            source=it["source"],
            title=it["title"],
            url=it["url"],
            published=it.get("published",""),
            content=content[:5000],
            measurable=measurable,
            value_signals=str(signals)
        )
        if measurable:
            it["value_signals"] = signals
            enriched.append(it)

    # 4) Relatório (apenas mensuráveis)
    report_path = write_daily_report(enriched)

    # 5) E-mail opcional
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            body = f.read()
        send_mail("IA — Casos mensuráveis (digest)", body)
    except Exception:
        pass

    return report_path

if __name__ == "__main__":
    p = run()
    print("Relatório gerado em:", p)
