# middleware_sql_defense.py
import re
import json
import time
from typing import Tuple
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import redis

# ---------- CONFIGURABLES (poner en settings.py preferiblemente) ----------
W_SQL = getattr(settings, "SQL_DEFENSE_W_SQL", 1.0)
THRESHOLD = getattr(settings, "SQL_DEFENSE_THRESHOLD", 0.8)  # score normalizado 0..1
WINDOW_SEC = getattr(
    settings, "SQL_DEFENSE_WINDOW_SEC", 300
)  # ventana para conteo (ej. 5min)
MAX_EXPECTED_DETECTIONS = getattr(settings, "SQL_DEFENSE_MAX_EXPECTED_DETECTIONS", 10)
BLOCK_TTL = getattr(
    settings, "SQL_DEFENSE_BLOCK_TTL", 600
)  # bloqueo por IP en segundos (ej. 10min)

REDIS_URL = getattr(settings, "SQL_DEFENSE_REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

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
def get_client_ip(request) -> str:
    """Obtiene la IP real (si hay proxies, usa X-Forwarded-For)"""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # X-Forwarded-For puede contener lista de IPs
        ip = xff.split(",")[0].strip()
        return ip
    return request.META.get("REMOTE_ADDR", "")


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
    """
    Extrae texto potencialmente peligroso del request:
    - query string
    - body (JSON o form)
    - headers sospechosos (User-Agent, Referer)
    """
    parts = []
    try:
        # query params
        if request.META.get("QUERY_STRING"):
            parts.append(request.META.get("QUERY_STRING"))
        # body: intenta json, si no, raw text
        content_type = request.META.get("CONTENT_TYPE", "")
        if "application/json" in content_type:
            try:
                body_json = json.loads(request.body.decode("utf-8") or "{}")
                parts.append(json.dumps(body_json))
            except Exception:
                parts.append((request.body or b"").decode("utf-8", errors="ignore"))
        else:
            # form-encoded or other text
            try:
                parts.append(request.body.decode("utf-8", errors="ignore"))
            except Exception:
                pass
        # headers
        parts.append(request.META.get("HTTP_USER_AGENT", ""))
        parts.append(request.META.get("HTTP_REFERER", ""))
    except Exception:
        pass
    return " ".join([p for p in parts if p])


def detect_sqli_text(text: str) -> Tuple[bool, list]:
    """Detecta patrones en un texto normalizado; devuelve matches con severidad."""
    q = normalize_text(text)
    matches = []
    for patt, sev in PATTERNS:
        if patt.search(q):
            matches.append((patt.pattern, float(sev)))
    return (len(matches) > 0, matches)


# ---------- Redis keys ----------
def redis_count_key(ip: str) -> str:
    return f"sqli:count:{ip}"


def redis_block_key(ip: str) -> str:
    return f"sqli:block:{ip}"


# ---------- Cálculo de score S_sql/ip ----------
def compute_s_sql_ip(detections_count: int) -> float:
    """
    Convertir conteo a una puntuación normalizada 0..1.
    Usamos saturación en MAX_EXPECTED_DETECTIONS.
    """
    norm = min(float(detections_count) / float(MAX_EXPECTED_DETECTIONS), 1.0)
    score = float(W_SQL) * norm
    # Normalizamos a 0..1 si W_SQL puede ser mayor que 1
    return min(score, 1.0)


# ---------- Middleware ----------
class SQLIDefenseMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 1) obtener IP y comprobar si está bloqueada
        ip = get_client_ip(request)
        if not ip:
            return None  # no podemos hacer mucho sin IP

        # comprobar bloqueo en Redis
        block_key = redis_block_key(ip)
        if redis_client.exists(block_key):
            ttl = redis_client.ttl(block_key)
            return JsonResponse(
                {
                    "detail": "Acceso denegado (bloqueado por actividad sospechosa)",
                    "block_ttl_s": ttl,
                },
                status=403,
            )

        # 2) extraer texto y detectar patrones
        text = extract_payload_text(request)
        if not text:
            return None

        flagged, matches = detect_sqli_text(text)
        if flagged:
            # incrementar contador con TTL (ventana)
            count_key = redis_count_key(ip)
            # INCR y asegurar expiration
            new_count = redis_client.incr(count_key)
            # establecer TTL si fue creado de nuevo
            if redis_client.ttl(count_key) == -1:
                redis_client.expire(count_key, WINDOW_SEC)

            # calcular score
            current_count = int(new_count)
            s_sql_ip = compute_s_sql_ip(current_count)

            # registrar evento (puedes ampliar con logging o envío a SIEM)
            # guardamos metadata mínima
            event = {
                "time": int(time.time()),
                "ip": ip,
                "count": current_count,
                "score": s_sql_ip,
                "matches": matches,
            }
            # Puedes push a lista en Redis o a un logger
            redis_client.lpush("sqli:events", json.dumps(event))
            redis_client.ltrim("sqli:events", 0, 999)  # mantener últimos 1000 eventos

            # Si supera THRESHOLD -> bloquear ip
            if s_sql_ip >= float(THRESHOLD):
                redis_client.set(redis_block_key(ip), "1", ex=BLOCK_TTL)
                # opcional: publicar alerta en canal pubsub o webhook
                return JsonResponse(
                    {"detail": "IP bloqueada por actividad sospechosa", "ip": ip},
                    status=403,
                )
            else:
                # no bloqueo todavía: permitir continuar pero devolver alerta en header (opcional)
                # Puedes añadir header para que la vista/log lo capture
                request.META["X-SQLI-ALERT"] = json.dumps(event)
                return None

        return None
