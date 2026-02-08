import os
import base64
import hashlib
import hmac
from typing import Tuple

# Format: pbkdf2_sha256$iterations$salt_b64$hash_b64
_DEFAULT_ITERATIONS = 310_000  # zeitgemäß, aber noch schnell genug für Desktop
_SALT_BYTES = 16
_DKLEN = 32

def hash_password(password: str, iterations: int = _DEFAULT_ITERATIONS) -> str:
    if not isinstance(password, str) or not password:
        raise ValueError("Password darf nicht leer sein.")
    salt = os.urandom(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=_DKLEN)
    return "pbkdf2_sha256$%d$%s$%s" % (
        iterations,
        base64.urlsafe_b64encode(salt).decode("ascii").rstrip("="),
        base64.urlsafe_b64encode(dk).decode("ascii").rstrip("="),
    )

def _b64d(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

def verify_password(password: str, stored: str) -> Tuple[bool, str | None]:
    """Returns (ok, upgraded_hash_if_needed)."""
    if not stored:
        return False, None

    # New format
    if stored.startswith("pbkdf2_sha256$"):
        try:
            _, it_s, salt_s, hash_s = stored.split("$", 3)
            iterations = int(it_s)
            salt = _b64d(salt_s)
            expected = _b64d(hash_s)
            dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=len(expected))
            ok = hmac.compare_digest(dk, expected)
            # Optional: Upgrade iterations if too low
            if ok and iterations < _DEFAULT_ITERATIONS:
                return True, hash_password(password, _DEFAULT_ITERATIONS)
            return ok, None
        except Exception:
            return False, None

    # Legacy: SHA256 hex (64 chars)
    if len(stored) == 64 and all(c in "0123456789abcdef" for c in stored.lower()):
        legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
        ok = hmac.compare_digest(legacy, stored.lower())
        if ok:
            return True, hash_password(password, _DEFAULT_ITERATIONS)
        return False, None

    return False, None
