# middleware_sql_defense.py
import re
import json
from typing import Tuple
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

# ---------- Patrones y normalización ----------
_literal_single = re.compile(r"'([^'\\]|\\.)*'")
_literal_double = re.compile(r'"([^"\\]|\\.)*"')
_comment_sql = re.compile(r"(--[^\n]*|/\*.*?\*/)", re.S)

PATTERNS = [
    (re.compile(r"\bunion\b\s+(all\s+)?\bselect\b", re.I), 0.95),
    (re.compile(r"(?<!\w)or(?=\s+1=1)", re.I), 0.99),
    (re.compile(r"\b(select\b.*\bfrom\b.*\bwhere\b.*\b(or|and)\b.*=)", re.I), 0.7),
    (re.compile(r"\b(drop|truncate|delete|insert|update)\b", re.I), 0.8),
    (re.compile(r"(--|#|;)", re.I), 0.4),
]


# ---------- Helpers ----------
def normalize_text(s: str) -> str:
    """Quita literales y comentarios para reducir falsos positivos"""
    if not s:
        return ""
    s = _comment_sql.sub(" ", s)
    s = _literal_single.sub("''", s)
    s = _literal_double.sub('""', s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_payload_text(request) -> str:
    """Extrae texto potencialmente peligroso del request"""
    parts = []
    try:
        # query params
        if request.META.get("QUERY_STRING"):
            parts.append(request.META.get("QUERY_STRING"))
        # body
        content_type = request.META.get("CONTENT_TYPE", "")
        if "application/json" in content_type:
            try:
                body_json = json.loads(request.body.decode("utf-8") or "{}")
                parts.append(json.dumps(body_json))
            except Exception:
                parts.append((request.body or b"").decode("utf-8", errors="ignore"))
        else:
            try:
                parts.append(request.body.decode("utf-8", errors="ignore"))
            except Exception:
                pass
        # headers sospechosos
        parts.append(request.META.get("HTTP_USER_AGENT", ""))
        parts.append(request.META.get("HTTP_REFERER", ""))
    except Exception:
        pass
    return " ".join([p for p in parts if p])


def detect_sqli_text(text: str) -> Tuple[bool, list]:
    """Detecta patrones en un texto normalizado"""
    q = normalize_text(text)
    matches = []
    for patt, sev in PATTERNS:
        if patt.search(q):
            matches.append((patt.pattern, float(sev)))
    return (len(matches) > 0, matches)


# ---------- Middleware ----------
class SQLIDefenseMiddleware(MiddlewareMixin):
    def process_request(self, request):
        text = extract_payload_text(request)
        if not text:
            return None

        flagged, matches = detect_sqli_text(text)
        if flagged:
            # Bloqueo inmediato solo para pruebas
            return JsonResponse(
                {
                    "detail": "Request bloqueado: posible inyección SQL detectada",
                    "matches": matches,
                },
                status=403,
            )
        return None
