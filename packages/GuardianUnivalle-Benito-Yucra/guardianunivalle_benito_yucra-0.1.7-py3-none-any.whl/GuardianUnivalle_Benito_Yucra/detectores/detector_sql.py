import re
import json
import time
from typing import Tuple
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

# ---------- Patrones de ataques SQL ----------
PATTERNS = [
    (
        re.compile(r"\bunion\b\s+(all\s+)?\bselect\b", re.I),
        "Intento de UNION SELECT detectado",
    ),
    (
        re.compile(r"\bselect\b.*\bfrom\b.*\bwhere\b.*\b(or|and)\b.*=", re.I),
        "Intento de SELECT con OR/AND detectado",
    ),
    (
        re.compile(r"\b(or|and)\s+\d+\s*=\s*\d+", re.I),
        "Intento de OR/AND 1=1 detectado",
    ),
    (
        re.compile(r"\b(drop|truncate|delete|insert|update)\b", re.I),
        "Intento de manipulación de tabla detectado",
    ),
    (
        re.compile(r"(--|#|;)", re.I),
        "Comentario o terminador de sentencia sospechoso detectado",
    ),
    (re.compile(r"exec\s*\(", re.I), "Intento de ejecución de procedimiento detectado"),
]

# ---------- Bloqueo temporal por IP ----------
TEMP_BLOCK = {}  # {ip: timestamp}
BLOCK_DURATION = 30  # segundos


# ---------- Helpers ----------
def extract_payload_text(request) -> str:
    """Extrae todo el contenido que podría contener inyecciones"""
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


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# ---------- Middleware ----------
class SQLIDefenseStrongMiddleware(MiddlewareMixin):
    def process_request(self, request):
        client_ip = get_client_ip(request)

        # Revisa si la IP está temporalmente bloqueada
        if client_ip in TEMP_BLOCK:
            if time.time() - TEMP_BLOCK[client_ip] < BLOCK_DURATION:
                return JsonResponse(
                    {
                        "detail": "Acceso temporalmente bloqueado por actividad sospechosa",
                        "alerts": ["IP bloqueada temporalmente"],
                    },
                    status=403,
                )
            else:
                del TEMP_BLOCK[client_ip]

        text = extract_payload_text(request)
        if not text:
            return None

        flagged, matches = detect_sqli_text(text)
        if flagged:
            # Bloquea temporalmente la IP
            TEMP_BLOCK[client_ip] = time.time()
            # <-- Aquí puedes agregar la impresión o el log -->
            print("IP detectada:", client_ip)
            # O usando logging
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"Intento de ataque detectado desde IP: {client_ip}, detalles: {matches}"
            )
            return JsonResponse(
                {
                    "detail": "Request bloqueado: posible intento de inyección SQL detectado",
                    "alerts": matches,
                },
                status=403,
            )
        return None
