# middleware_sql_defense.py
import re
import json
from typing import Tuple
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

# ---------- Patrones de ataques SQL ----------
PATTERNS = [
    (
        re.compile(r"\bunion\b\s+(all\s+)?\bselect\b", re.I),
        "Intento de UNION SELECT detectado",
    ),
    (re.compile(r"or\s+\d+\s*=\s*\d+", re.I), "Intento de OR 1=1 detectado"),
    (
        re.compile(r"\b(select\b.*\bfrom\b.*\bwhere\b.*\b(or|and)\b.*=)", re.I),
        "Intento de SELECT con OR/AND detectado",
    ),
    (
        re.compile(r"\b(drop|truncate|delete|insert|update)\b", re.I),
        "Intento de manipulación de tabla detectado",
    ),
    (
        re.compile(r"(--|#|;)", re.I),
        "Comentario o terminador de sentencia sospechoso detectado",
    ),
]


# ---------- Helpers ----------
def extract_payload_text(request) -> str:
    """Extrae texto potencialmente peligroso del request"""
    parts = []
    # Query params
    if request.META.get("QUERY_STRING"):
        parts.append(request.META.get("QUERY_STRING"))
    # Body
    try:
        content_type = request.META.get("CONTENT_TYPE", "")
        if "application/json" in content_type:
            body_json = json.loads(request.body.decode("utf-8") or "{}")
            parts.append(json.dumps(body_json))
        else:
            parts.append(request.body.decode("utf-8", errors="ignore"))
    except Exception:
        pass
    # Headers
    parts.append(request.META.get("HTTP_USER_AGENT", ""))
    parts.append(request.META.get("HTTP_REFERER", ""))
    return " ".join([p for p in parts if p])


def detect_sqli_text(text: str) -> Tuple[bool, list]:
    """Detecta ataques SQL en el texto"""
    matches = []
    for patt, message in PATTERNS:
        if patt.search(text):
            matches.append(message)
    return (len(matches) > 0, matches)


# ---------- Middleware ----------
class SQLIDefenseMiddleware(MiddlewareMixin):
    def process_request(self, request):
        text = extract_payload_text(request)
        if not text:
            return None

        flagged, matches = detect_sqli_text(text)
        if flagged:
            # Mensaje estandarizado
            return JsonResponse(
                {
                    "detail": "Request bloqueado: posible intento de inyección SQL detectado",
                    "alerts": matches,
                },
                status=403,
            )
        return None
