# detector_sql.py
# =====================================================
# Importaciones de librerías
# =====================================================

# Módulo para trabajar con expresiones regulares (regex)
# Permite buscar patrones de texto dentro de cadenas.
import re

# Módulo para trabajar con datos en formato JSON
# Permite convertir cadenas JSON a objetos Python y viceversa.
import json

# Módulo para manejo de logs (registro de eventos)
# Permite registrar alertas, información o errores en la consola o en archivos.
import logging

# Tipado estático
# Permite indicar tipos de datos de variables o valores de retorno en funciones.
from typing import Tuple

# Clase de Django para enviar respuestas HTTP en formato JSON
# Se usa para devolver mensajes al cliente en caso de error o detección de ataques.
from django.http import JsonResponse

# Clase base para crear middlewares en Django (compatible con versiones antiguas)
# Permite definir métodos como process_request o process_response para interceptar solicitudes y respuestas.
from django.utils.deprecation import MiddlewareMixin

# Permite acceder a las configuraciones de Django (settings.py)
# Se usa para obtener rutas excluidas u otras configuraciones personalizadas.
from django.conf import settings


# ==============================
# CONFIGURACIÓN DEL LOG
# ==============================
logger = logging.getLogger(
    "sqlidefense"
)  # logger para registrar eventos de SQL Injection
logger.setLevel(logging.INFO)
if not logger.handlers:
    # Si no tiene manejadores, agregar uno por defecto a consola
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ==============================
# PATRONES DE ATAQUE SQL
# ==============================
# Cada tupla contiene (expresión regular, descripción del ataque)
PATTERNS = [
    (re.compile(r"\bunion\b\s+(all\s+)?\bselect\b", re.I), "UNION SELECT"),
    (
        re.compile(r"\bselect\b.*\bfrom\b.*\bwhere\b.*\b(or|and)\b.*=", re.I),
        "SELECT con OR/AND",
    ),
    (re.compile(r"\b(or|and)\s+\d+\s*=\s*\d+", re.I), "OR/AND 1=1"),
    (
        re.compile(r"\b(drop|truncate|delete|insert|update)\b", re.I),
        "Manipulación de tabla",
    ),
    (re.compile(r"(--|#|;)", re.I), "Comentario o terminador sospechoso"),
    (re.compile(r"exec\s*\(", re.I), "Ejecución de procedimiento"),
]

# ==============================
# FUNCIONES AUXILIARES
# ==============================


def extract_payload_text(request) -> str:
    """
    Extrae texto de la solicitud que será analizado por patrones SQL Injection.
    Se considera:
        - Cuerpo de la solicitud (JSON o texto plano)
        - Query String (parámetros GET)
        - User-Agent
        - Referer
    """
    parts = []
    content_type = request.META.get("CONTENT_TYPE", "")

    try:
        # Si es JSON, decodificarlo
        if "application/json" in content_type:
            body_json = json.loads(request.body.decode("utf-8") or "{}")
            parts.append(json.dumps(body_json))
        else:
            parts.append(request.body.decode("utf-8", errors="ignore"))
    except Exception:
        # Ignorar errores al decodificar
        pass

    # Agregar Query String
    if request.META.get("QUERY_STRING"):
        parts.append(request.META.get("QUERY_STRING"))

    # Agregar User-Agent y Referer
    parts.append(request.META.get("HTTP_USER_AGENT", ""))
    parts.append(request.META.get("HTTP_REFERER", ""))

    # Retornar todo el texto concatenado
    return " ".join([p for p in parts if p])


def detect_sqli_text(text: str) -> Tuple[bool, list]:
    """
    Detecta si un texto contiene patrones de SQL Injection.
    Retorna:
        - flagged (bool): True si se detecta algún patrón
        - matches (list): lista de descripciones de patrones detectados
    """
    matches = []
    for patt, message in PATTERNS:
        if patt.search(text):
            matches.append(message)
    return (len(matches) > 0, matches)


# ==============================
# MIDDLEWARE
# ==============================


class SQLIDefenseMiddleware(MiddlewareMixin):
    """
    Middleware para proteger la aplicación contra ataques de SQL Injection.
    Analiza cada solicitud entrante y bloquea si detecta patrones maliciosos,
    excepto en rutas definidas como confiables en settings.SQLI_DEFENSE_EXCLUDED_PATHS.
    """

    def process_request(self, request):
        # Obtener rutas excluidas desde settings
        excluded_paths = getattr(settings, "SQLI_DEFENSE_EXCLUDED_PATHS", [])

        # Saltar verificación si la ruta está excluida
        if any(request.path.startswith(p) for p in excluded_paths):
            return None

        # Extraer texto de la solicitud
        text = extract_payload_text(request)
        if not text:
            return None

        # Detectar patrones SQL Injection
        flagged, matches = detect_sqli_text(text)
        if flagged:
            # Registrar evento en log
            logger.warning(f"Ataque detectado: {matches}, payload: {text}")

            # Bloquear la solicitud y devolver mensaje
            return JsonResponse(
                {"mensaje": "Ataque detectado", "tipos": matches}, status=403
            )

        return None


"""
Notas adicionales:
- Se puede aplicar cifrado AES-256 para guardar consultas auditadas.
- Se puede usar hash SHA-256 para verificar integridad de registros.
- Índice de amenaza:
    S_sql = w_sql * detecciones_sql
    donde w_sql es el peso asignado a SQL Injection
          detecciones_sql es la cantidad de patrones detectados
"""
