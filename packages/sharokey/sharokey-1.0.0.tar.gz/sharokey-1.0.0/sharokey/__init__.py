"""
Sharokey Python SDK

A Python library for secure secret sharing with Zero Knowledge encryption.
Compatible with the Sharokey API and returns JSON responses for maximum flexibility.

Example:
    import sharokey
    
    # Configure client
    client = sharokey.SharokeyClient(token="your-token")
    
    # Create a secret - returns JSON
    response = await client.create("My secret", hours=24, views=1)
    print(f"Share URL: {response['data']['share_url']}")
    print(f"Secret slug: {response['data']['slug']}")
    
    # List secrets - returns JSON
    response = await client.list()
    for secret in response['data']['items']:
        print(f"{secret['slug']}: {secret.get('description', 'No description')}")
"""

from .client import SharokeyClient
from .models import SecretCreate, Attachment, SecretRequestCreate
from .exceptions import SharokeyError, AuthenticationError, ValidationError, NotFoundError, NetworkError, AttachmentError
from .crypto import SharokeyCrypto

__version__ = "1.0.0"
__author__ = "Sharokey Team"
__email__ = "support@sharokey.com"

__all__ = [
    "SharokeyClient",
    "SecretCreate",
    "Attachment", 
    "SecretRequestCreate",
    "SharokeyError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "NetworkError",
    "AttachmentError",
    "SharokeyCrypto",
]