import os
from cryptography.fernet import Fernet
import json
from typing import Any

# Global Fernet instance
_fernet = None

def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable is not set")
        _fernet = Fernet(key.encode())
    return _fernet

def encrypt_dict(data: dict) -> str:
    """Encrypts a dictionary into a string using Fernet symmetric encryption."""
    f = _get_fernet()
    json_str = json.dumps(data)
    encrypted_bytes = f.encrypt(json_str.encode())
    return encrypted_bytes.decode()

def decrypt_dict(encrypted_str: str) -> dict:
    """Decrypts a Fernet encrypted string back into a dictionary."""
    if not encrypted_str:
        return {}
    
    try:
        f = _get_fernet()
        decrypted_bytes = f.decrypt(encrypted_str.encode())
        return json.loads(decrypted_bytes.decode())
    except Exception as e:
        # Fallback for unencrypted legacy dicts that might be stored as string
        try:
            return json.loads(encrypted_str)
        except:
            return {}
