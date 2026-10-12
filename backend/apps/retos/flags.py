"""Hashing de flags con pepper (nunca se guardan en claro)."""
import hashlib
import hmac

from django.conf import settings


def normalizar(flag: str) -> str:
    return (flag or "").strip()


def calcular_hash(flag: str) -> str:
    pepper = settings.PEPPER_FLAGS.encode()
    return hmac.new(pepper, normalizar(flag).encode(), hashlib.sha256).hexdigest()


def comprobar_flag(flag: str, hash_guardado: str) -> bool:
    if not hash_guardado:
        return False
    return hmac.compare_digest(calcular_hash(flag), hash_guardado)
