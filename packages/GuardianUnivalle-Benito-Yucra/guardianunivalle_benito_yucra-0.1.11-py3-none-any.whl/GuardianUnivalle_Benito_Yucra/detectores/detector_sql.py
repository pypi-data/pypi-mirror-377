# detector_sql.py
import re
import json
import time
import logging
from typing import Tuple
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

# ---------- Configuración de logging ----------
logger = logging.getLogger("sqlidefense")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()  # en prod usa FileHandler/RotatingFileHandler
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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
BLOCK_DURATION = getattr(settings, "SQL_DEFENSE_BLOCK_TTL", 30)  # segundos

# ---------- Excepciones y bypass ----------
EXEMPT_PATHS = getattr(settings, "SQLI_EXEMPT_PATHS", ["/api/login/"])
BYPASS_HEADER = "HTTP_X_SQLI_BYPASS"
BYPASS_MAX_AGE = getattr(settings, "SQLI_BYPASS_MAX_AGE", 30)  # segundos (muy corto)

# JWT support (optional)
try:
    from rest_framework_simplejwt.backends import TokenBackend

    SIMPLEJWT_AVAILABLE = True
except Exception:
    SIMPLEJWT_AVAILABLE = False


# ---------- Helpers ----------
def extract_payload_text(request) -> str:
    parts = []
    content_type = request.META.get("CONTENT_TYPE", "")
    try:
        if "application/json" in content_type:
            body_json = json.loads(request.body.decode("utf-8") or "{}")
            # 🔒 quitar campos sensibles antes de loguear/analizar
            for key in getattr(settings, "SQL_DEFENSE_SENSITIVE_KEYS", []):
                if key in body_json:
                    body_json[key] = "***"
            parts.append(json.dumps(body_json))
        else:
            parts.append(request.body.decode("utf-8", errors="ignore"))
    except Exception:
        pass

    if request.META.get("QUERY_STRING"):
        parts.append(request.META.get("QUERY_STRING"))

    parts.append(request.META.get("HTTP_USER_AGENT", ""))
    parts.append(request.META.get("HTTP_REFERER", ""))

    return " ".join([p for p in parts if p])


def detect_sqli_text(text: str) -> Tuple[bool, list]:
    matches = []
    for patt, message in PATTERNS:
        if patt.search(text):
            matches.append(message)
    return (len(matches) > 0, matches)


def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


def is_valid_jwt(request) -> bool:
    if not SIMPLEJWT_AVAILABLE:
        return False
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth or not auth.startswith("Bearer "):
        return False
    token = auth.split(" ", 1)[1].strip()
    try:
        tb = TokenBackend(
            algorithm=getattr(settings, "SIMPLE_JWT", {}).get("ALGORITHM", "HS256"),
            signing_key=getattr(settings, "SIMPLE_JWT", {}).get(
                "SIGNING_KEY", settings.SECRET_KEY
            ),
        )
        tb.decode(token, verify=True)
        return True
    except Exception:
        return False


def is_valid_signed_bypass(request) -> bool:
    signed = request.META.get(BYPASS_HEADER, "")
    if not signed:
        return False
    signer = TimestampSigner(settings.SECRET_KEY)
    try:
        signer.unsign(signed, max_age=BYPASS_MAX_AGE)
        return True
    except SignatureExpired:
        logger.info("Bypass token expirado")
        return False
    except BadSignature:
        logger.info("Bypass token inválido")
        return False


# ---------- Middleware ----------
class SQLIDefenseStrongMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path or ""
        client_ip = get_client_ip(request)

        # 1) Rutas exentas
        EXEMPT_PATHS = getattr(settings, "SQLI_EXEMPT_PATHS", [])
        for p in EXEMPT_PATHS:
            if path.startswith(p):
                return None

        # 2) IP bloqueada temporalmente
        if client_ip in TEMP_BLOCK:
            if time.time() - TEMP_BLOCK[client_ip] < BLOCK_DURATION:
                logger.warning(f"IP bloqueada temporalmente: {client_ip}")
                return JsonResponse(
                    {"detail": "Acceso temporalmente bloqueado"}, status=403
                )
            else:
                del TEMP_BLOCK[client_ip]

        # 3) Extraer payload
        text = extract_payload_text(request)
        if not text:
            return None

        # 4) Detectar SQLi
        flagged, matches = detect_sqli_text(text)
        if flagged:
            TEMP_BLOCK[client_ip] = time.time()
            logger.warning(
                f"Intento de ataque detectado desde IP: {client_ip}, detalles: {matches}, payload: {text}"
            )
            return JsonResponse(
                {
                    "detail": "Request bloqueado: posible inyección SQL",
                    "alerts": matches,
                },
                status=403,
            )

        return None
