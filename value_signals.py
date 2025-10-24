
import re
from typing import Dict, List

MONEY_PATTERNS = [
    r"\bR\$ ?[\d\.\,]+(?: ?milh(?:ão|oes|ões))?",
    r"\$ ?[\d\.\,]+(?: ?million| ?billion)?",
    r"\b\d+ ?milh(?:ão|oes|ões) de (?:reais|dólares)",
]
PCT_PATTERNS = [
    r"\b\d{1,3} ?%",
    r"\bROI de ?\d{1,3} ?%",
]
TIME_PATTERNS = [
    r"\b\d+ (?:horas|h|minutos|min|dias|semanas) (?:economizadas|poupadas|salvas)",
    r"\breduz(?:iu|em) o tempo em \d+ ?%",
]
VALUE_WORDS = [
    "economia de", "ganho de produtividade", "redução de custos", "aumento de receita",
    "eficiência", "payback", "ROI", "retorno sobre investimento"
]

REGEXES = [re.compile(p, re.I) for p in MONEY_PATTERNS + PCT_PATTERNS + TIME_PATTERNS]

def extract_signals(text: str) -> Dict[str, List[str]]:
    hits = []
    for rx in REGEXES:
        hits += rx.findall(text or "")
    # lightweight contextual words
    ctx = [w for w in VALUE_WORDS if w in (text or "").lower()]
    return {"matches": list(dict.fromkeys(hits)), "context": ctx}

def is_measurable(signals: Dict[str, List[str]]) -> bool:
    return bool(signals.get("matches") or signals.get("context"))
