"""
SNMP Credential Encryption/Decryption
Uses Fernet (AES-128) for symmetric encryption
"""

import os
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# Get encryption key from environment
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise RuntimeError(
        "ENCRYPTION_KEY environment variable is required but was not found. "
        "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
    )

# Check if key is a placeholder
if ENCRYPTION_KEY.startswith("change_me") or len(ENCRYPTION_KEY) < 40:
    raise RuntimeError(
        f"ENCRYPTION_KEY appears to be invalid or a placeholder. "
        f"Generate a valid Fernet key with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
    )

# Initialize Fernet cipher
try:
    # Fernet key should be bytes or a valid base64 string
    if isinstance(ENCRYPTION_KEY, str):
        # Try to decode to validate it's proper base64
        key_bytes = ENCRYPTION_KEY.encode('utf-8')
    else:
        key_bytes = ENCRYPTION_KEY
    
    cipher = Fernet(key_bytes)
except ValueError as e:
    logger.error(f"Failed to initialize Fernet cipher: {e}")
    logger.error(f"ENCRYPTION_KEY must be a valid Fernet key (32 url-safe base64-encoded bytes)")
    logger.error(f"Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'")
    raise RuntimeError(
        f"Invalid ENCRYPTION_KEY format. Fernet key must be 32 url-safe base64-encoded bytes. "
        f"Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
    ) from e
except Exception as e:
    logger.error(f"Failed to initialize Fernet cipher: {e}")
    raise


def encrypt_credential(plaintext: str) -> str:
    """Encrypt a credential string

    Args:
        plaintext: The plaintext credential (community string, password, etc.)

    Returns:
        Base64-encoded encrypted string
    """
    if not plaintext:
        return ""

    try:
        encrypted = cipher.encrypt(plaintext.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise


def decrypt_credential(ciphertext: str) -> str:
    """Decrypt a credential string

    Args:
        ciphertext: The base64-encoded encrypted string

    Returns:
        Decrypted plaintext string
    """
    if not ciphertext:
        return ""

    try:
        decrypted = cipher.decrypt(ciphertext.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise
