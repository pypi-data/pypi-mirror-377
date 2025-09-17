"""
Sharokey cryptography module.

Implements Zero Knowledge encryption compatible with the reference JavaScript
implementation from REPRISE_CONVERSATION.md.

Uses AES-GCM-256 + PBKDF2 with the same parameters as the CLI and web versions.
"""

import base64
import os
import secrets
import struct
from typing import Tuple, NamedTuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .exceptions import EncryptionError


# Constants matching REPRISE_CONVERSATION.md specs
CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
PBKDF2_ITERATIONS = 10000
AES_KEY_LENGTH = 32  # 256 bits
IV_LENGTH = 12       # 96 bits for AES-GCM
SALT_LENGTH = 16     # 128 bits
KEY_A_LENGTH = 8     # Server key length
KEY_B_LENGTH = 24    # Client key length


class EncryptionResult(NamedTuple):
    """Result of encryption operation."""
    ciphertext: str      # Base64 encoded
    iv: str             # Base64 encoded
    salt: str           # Base64 encoded
    key_a: str          # First part of key (sent to server)
    key_b: str          # Second part of key (kept client-side)


class SharokeyCrypto:
    """Cryptography implementation for Sharokey.
    
    Provides Zero Knowledge encryption compatible with the reference
    JavaScript implementation and CLI versions.
    """
    
    @staticmethod
    def generate_alphanumeric_key(length: int) -> str:
        """Generate a random alphanumeric key of specified length.
        
        Uses the same charset as the JavaScript reference implementation.
        
        Args:
            length: Length of the key to generate
            
        Returns:
            Random alphanumeric string
        """
        return ''.join(secrets.choice(CHARSET) for _ in range(length))
    
    @staticmethod
    def generate_keys() -> Tuple[str, str]:
        """Generate keyA and keyB pair.
        
        Returns:
            Tuple of (keyA, keyB) where keyA goes to server, keyB stays client-side
        """
        key_a = SharokeyCrypto.generate_alphanumeric_key(KEY_A_LENGTH)
        key_b = SharokeyCrypto.generate_alphanumeric_key(KEY_B_LENGTH)
        return key_a, key_b
    
    @staticmethod
    def encrypt_message(content: str, full_key: str) -> EncryptionResult:
        """Encrypt a message using AES-GCM with PBKDF2 key derivation.
        
        Follows the exact same process as the JavaScript reference implementation
        in REPRISE_CONVERSATION.md.
        
        Args:
            content: Message to encrypt
            full_key: Combined keyA + keyB
            
        Returns:
            EncryptionResult with all necessary data
            
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Generate salt and IV (same as JavaScript reference)
            salt = os.urandom(SALT_LENGTH)
            iv = os.urandom(IV_LENGTH)
            
            # PBKDF2 key derivation (same parameters as JavaScript)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=AES_KEY_LENGTH,
                salt=salt,
                iterations=PBKDF2_ITERATIONS,
            )
            derived_key = kdf.derive(full_key.encode('utf-8'))
            
            # AES-GCM encryption
            aesgcm = AESGCM(derived_key)
            message_bytes = content.encode('utf-8')
            ciphertext = aesgcm.encrypt(iv, message_bytes, None)
            
            # Convert to base64 (compatible with JavaScript btoa())
            ciphertext_b64 = base64.b64encode(ciphertext).decode('ascii')
            iv_b64 = base64.b64encode(iv).decode('ascii')
            salt_b64 = base64.b64encode(salt).decode('ascii')
            
            # Split keys
            key_a = full_key[:KEY_A_LENGTH]
            key_b = full_key[KEY_A_LENGTH:]
            
            return EncryptionResult(
                ciphertext=ciphertext_b64,
                iv=iv_b64,
                salt=salt_b64,
                key_a=key_a,
                key_b=key_b
            )
            
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt message: {e}")
    
    @staticmethod
    def encrypt_file(file_data: bytes, full_key: str, iv_b64: str, salt_b64: str) -> str:
        """Encrypt file data using the same IV and salt as the main content.
        
        This follows the attachment encryption specification from REPRISE_CONVERSATION.md
        where attachments use the same IV and salt as the main message.
        
        Rejects files smaller than 64 bytes to ensure proper entropy validation.
        
        Args:
            file_data: Raw file bytes to encrypt
            full_key: Combined keyA + keyB
            iv_b64: Base64 encoded IV from main content encryption
            salt_b64: Base64 encoded salt from main content encryption
            
        Returns:
            Base64 encoded encrypted file data
            
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Decode IV and salt from base64
            iv = base64.b64decode(iv_b64.encode('ascii'))
            salt = base64.b64decode(salt_b64.encode('ascii'))
            
            # Reject files that are too small for proper entropy validation
            # This prevents potential security issues and keeps the SDK simple
            if len(file_data) < 64:  # Minimum file size for good entropy
                raise EncryptionError(f"File too small for secure encryption: {len(file_data)} bytes. Minimum size is 64 bytes.")
            
            # Use file data as-is for encryption (no padding needed)
            data_to_encrypt = file_data
            
            # PBKDF2 key derivation (same as main content)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=AES_KEY_LENGTH,
                salt=salt,
                iterations=PBKDF2_ITERATIONS,
            )
            derived_key = kdf.derive(full_key.encode('utf-8'))
            
            # AES-GCM encryption
            aesgcm = AESGCM(derived_key)
            ciphertext = aesgcm.encrypt(iv, data_to_encrypt, None)
            
            # Convert to base64
            return base64.b64encode(ciphertext).decode('ascii')
            
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt file: {e}")
    
