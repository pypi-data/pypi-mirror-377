"""
Sharokey API client.

Main client class for interacting with the Sharokey API.
Methods are named consistently with CLI commands for intuitive usage.
"""

import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import json
import aiohttp
import aiofiles

from .models import SecretCreate, Attachment, SecretRequestCreate
from .crypto import SharokeyCrypto, EncryptionResult
from .exceptions import (
    SharokeyError, 
    AuthenticationError, 
    ValidationError, 
    NotFoundError, 
    NetworkError,
    AttachmentError
)


class SharokeyClient:
    """Sharokey API client with CLI-consistent method naming.
    
    Methods mirror CLI commands:
    - client.create() -> sharokey create
    - client.list() -> sharokey list  
    - client.get() -> sharokey get
    - client.delete() -> sharokey delete
    - client.stats() -> sharokey stats
    """
    
    def __init__(
        self, 
        token: str,
        api_url: str = "https://api.sharokey.com/api/v1",
        timeout: int = 30,
    ):
        """Initialize Sharokey client.
        
        Args:
            token: Authentication token (required)
            api_url: API base URL (default: production)
            timeout: Request timeout in seconds
            
        Raises:
            ValidationError: If token is missing
        """
        if not token:
            raise ValidationError("Token is required")
            
        self.token = token
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.crypto = SharokeyCrypto()
        
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Sharokey API.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            
        Returns:
            JSON response data
            
        Raises:
            AuthenticationError: Invalid token (401)
            NotFoundError: Resource not found (404) 
            NetworkError: Network/API errors
        """
        url = f"{self.api_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Sharokey-Python-1.0.0'
        }
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if method.upper() == 'GET':
                    async with session.get(url, headers=headers) as response:
                        return await self._handle_response(response)
                elif method.upper() == 'POST':
                    async with session.post(url, headers=headers, json=data) as response:
                        return await self._handle_response(response)
                elif method.upper() == 'DELETE':
                    async with session.delete(url, headers=headers) as response:
                        return await self._handle_response(response)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                    
        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {e}")
        except asyncio.TimeoutError:
            raise NetworkError("Request timeout")
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle HTTP response and errors.
        
        Args:
            response: aiohttp response object
            
        Returns:
            JSON response data
            
        Raises:
            AuthenticationError: 401 errors
            NotFoundError: 404 errors  
            SharokeyError: Other API errors
        """
        try:
            response_data = await response.json()
        except Exception:
            response_data = {"message": await response.text()}
        
        if response.status == 401:
            raise AuthenticationError("Invalid token or authentication failed")
        elif response.status == 404:
            raise NotFoundError("Secret not found")
        elif response.status == 429:
            raise NetworkError("Rate limit exceeded. Please wait and try again.")
        elif not response.ok:
            error_msg = response_data.get('message', f'HTTP {response.status}')
            raise SharokeyError(f"API Error: {error_msg}")
            
        return response_data

    def _validate_create_params(self, content: str, hours: int, views: int) -> None:
        """Validate secret creation parameters (like CLI validation).
        
        Args:
            content: Secret content
            hours: Expiration hours
            views: Maximum views
            
        Raises:
            ValidationError: Invalid parameters
        """
        if not content or not content.strip():
            raise ValidationError("Content is required and must be non-empty")
            
        if not isinstance(hours, int) or hours < 1 or hours > 8760:
            raise ValidationError("Hours must be between 1 and 8760")
            
        if not isinstance(views, int) or views < 1 or views > 1000:
            raise ValidationError("Views must be between 1 and 1000")

    def _validate_security_params(self, ip_whitelist: Optional[str], geolocation: Optional[str]) -> None:
        """Validate security parameters with extended field lengths.
        
        Args:
            ip_whitelist: IP whitelist string (max 255 characters)
            geolocation: Geolocation string (max 255 characters)
            
        Raises:
            ValidationError: Invalid parameters
        """
        # Validate IP whitelist length (extended to 255 characters)
        if ip_whitelist and len(ip_whitelist) > 255:
            raise ValidationError("IP whitelist must be 255 characters or less")
            
        # Validate geolocation length (extended to 255 characters)
        if geolocation and len(geolocation) > 255:
            raise ValidationError("Geolocation must be 255 characters or less")
            
        # Optional format validation for IP whitelist
        if ip_whitelist:
            import re
            ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$')
            ips = [ip.strip() for ip in ip_whitelist.split(',')]
            for ip in ips:
                if not ip_pattern.match(ip) and not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
                    raise ValidationError(f"Invalid IP format: {ip}. Use format: 192.168.1.1 or 192.168.1.0/24")
                    
        # Optional format validation for geolocation (ISO country codes)
        if geolocation:
            import re
            country_pattern = re.compile(r'^[A-Z]{2}$')
            countries = [c.strip().upper() for c in geolocation.split(',')]
            for country in countries:
                if not country_pattern.match(country):
                    raise ValidationError(f"Invalid country code: {country}. Use ISO 2-letter codes like FR,US,CA")

    async def _process_attachments(
        self, 
        attachments: List[Union[str, Path]], 
        full_key: str, 
        iv: str, 
        salt: str
    ) -> List[Attachment]:
        """Process and encrypt attachments.
        
        Args:
            attachments: List of file paths
            full_key: Combined keyA + keyB
            iv: Base64 IV from content encryption
            salt: Base64 salt from content encryption
            
        Returns:
            List of encrypted Attachment objects
            
        Raises:
            AttachmentError: File processing errors
        """
        if not attachments:
            return []
            
        # Validate attachment constraints
        if len(attachments) > 10:
            raise AttachmentError(f"Too many attachments. Maximum 10 files allowed, got {len(attachments)}")
        
        processed_attachments = []
        total_size = 0
        max_total_size = 10 * 1024 * 1024  # 10MB
        
        for file_path in attachments:
            path = Path(file_path)
            
            if not path.exists():
                raise AttachmentError(f"File not found: {file_path}")
                
            file_size = path.stat().st_size
            total_size += file_size
            
            if total_size > max_total_size:
                raise AttachmentError(f"Total attachments size too large: {total_size / (1024*1024):.1f}MB. Maximum 10MB allowed")
            
            try:
                async with aiofiles.open(path, 'rb') as f:
                    file_data = await f.read()
                    
                encrypted_data = self.crypto.encrypt_file(file_data, full_key, iv, salt)
                
                processed_attachments.append(Attachment(
                    name=path.name,
                    data=encrypted_data,
                    size=file_size  # Taille originale du fichier
                ))
                
            except Exception as e:
                raise AttachmentError(f"Failed to process file {path.name}: {e}")
                
        return processed_attachments

    # =============================================================================
    # CLI-CONSISTENT API METHODS
    # =============================================================================

    async def create(
        self,
        content: str,
        hours: int = 24,
        views: int = 1,
        *,
        description: Optional[str] = None,
        message: Optional[str] = None,
        password: Optional[str] = None,
        otp_email: Optional[str] = None,
        otp_phone: Optional[str] = None,
        captcha: Optional[bool] = None,
        ip_whitelist: Optional[str] = None,
        geolocation: Optional[str] = None,
        attachments: Optional[List[Union[str, Path]]] = None
    ) -> Dict[str, Any]:
        """Create a secret (equivalent to: sharokey create).
        
        Args:
            content: Secret content to encrypt
            hours: Hours until expiration (1-8760)
            views: Maximum number of views (1-1000)
            description: Optional description
            message: Optional message for recipient
            password: Optional additional password protection
            otp_email: Optional email for OTP (mutually exclusive with otp_phone)
            otp_phone: Optional phone for OTP (mutually exclusive with otp_email)
            captcha: Optional CAPTCHA verification requirement
            ip_whitelist: Optional comma-separated list of allowed IPs/CIDR ranges
            geolocation: Optional comma-separated list of allowed country codes
            attachments: Optional list of file paths to attach
            
        Returns:
            Raw JSON response from API with complete secret data
            
        Raises:
            ValidationError: Invalid parameters
            AttachmentError: File processing errors
            SharokeyError: API errors
            
        Example:
            # Simple secret
            secret = await client.create("My secret", 24, 1)
            
            # With attachments and security features
            secret = await client.create(
                "Confidential docs",
                hours=48,
                views=3,
                description="Contract files",
                otp_email="admin@company.com",
                captcha=True,
                ip_whitelist="192.168.1.0/24,10.0.0.1",
                geolocation="FR,US,CA",
                attachments=["contract.pdf", "terms.docx"]
            )
        """
        # Validate parameters (same as CLI)
        self._validate_create_params(content, hours, views)
        
        if otp_email and otp_phone:
            raise ValidationError("Cannot use both otp_email and otp_phone simultaneously")
        
        # Validate security parameters
        self._validate_security_params(ip_whitelist, geolocation)
        
        # Generate keys and encrypt content
        key_a, key_b = self.crypto.generate_keys()
        full_key = key_a + key_b
        
        encrypted = self.crypto.encrypt_message(content, full_key)
        
        # Process attachments if provided
        processed_attachments = []
        total_size = 0
        if attachments:
            processed_attachments = await self._process_attachments(
                attachments, full_key, encrypted.iv, encrypted.salt
            )
            # Calculate total size for API
            total_size = sum(Path(f).stat().st_size for f in attachments)
        
        # Create API request
        request = SecretCreate(
            content=encrypted.ciphertext,
            iv=encrypted.iv,
            salt=encrypted.salt,
            key=encrypted.key_a,
            maximum_views=views,
            expiration_hours=hours,
            description=description,
            message=message,
            password=password,
            otp_email=otp_email,
            otp_phone=otp_phone,
            captcha=captcha,
            ip_whitelist=ip_whitelist,
            geolocation=geolocation,
            attachments=processed_attachments,
            attachments_total_size=total_size
        )
        
        # Send to API
        response = await self._make_request('POST', '/secrets', request.to_dict())
        
        # Add share_url to raw response
        if 'data' in response and 'access_url' in response['data']:
            response['data']['share_url'] = f"{response['data']['access_url']}#{encrypted.key_b}"
            
        return response

    async def list(
        self,
        *,
        limit: int = 50,
        status: Optional[str] = None,
        creator: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List secrets (equivalent to: sharokey list).
        
        Args:
            limit: Maximum number of secrets to return (default 50)
            status: Filter by status ('active' or 'expired')
            creator: Filter by creator email
            search: Search in descriptions
            
        Returns:
            Raw JSON response from API with secrets list
            
        Example:
            # List all active secrets
            secrets = await client.list(status='active', limit=10)
            
            for secret in secrets.data:
                print(f"{secret.slug}: {secret.description}")
        """
        params = {}
        if limit != 50:
            params['limit'] = limit
        if status:
            params['status'] = status
        if creator:
            params['creator'] = creator
        if search:
            params['search'] = search
            
        query_string = '&'.join(f'{k}={v}' for k, v in params.items())
        endpoint = f'/secrets?{query_string}' if query_string else '/secrets'
        
        response = await self._make_request('GET', endpoint)
        return response

    async def get(self, slug: str) -> Dict[str, Any]:
        """Get secret details (equivalent to: sharokey get SLUG).
        
        Args:
            slug: Secret identifier
            
        Returns:
            Raw JSON response from API with secret details
            
        Raises:
            NotFoundError: Secret not found
            ValidationError: Invalid slug
            
        Example:
            secret = await client.get("ABC123XYZ")
            print(f"Views: {secret.current_views}/{secret.maximum_views}")
        """
        if not slug or not slug.strip():
            raise ValidationError("Secret slug is required")
            
        response = await self._make_request('GET', f'/secrets/{slug.strip()}')
        return response

    async def delete(self, slug: str) -> Dict[str, Any]:
        """Delete a secret (equivalent to: sharokey delete SLUG).
        
        Args:
            slug: Secret identifier
            
        Returns:
            Raw JSON response from API
            
        Raises:
            NotFoundError: Secret not found
            ValidationError: Invalid slug
            
        Example:
            success = await client.delete("ABC123XYZ")
            if success:
                print("Secret deleted successfully")
        """
        if not slug or not slug.strip():
            raise ValidationError("Secret slug is required")
            
        response = await self._make_request('DELETE', f'/secrets/{slug.strip()}')
        return response

    async def stats(self) -> Dict[str, Any]:
        """Get usage statistics (equivalent to: sharokey stats).
            
        Returns:
            Raw JSON response from API with statistics
            
        Example:
            stats = await client.stats()
            print(f"Total secrets: {stats.total_secrets}")
            print(f"Active secrets: {stats.active_secrets}")
        """
        response = await self._make_request('GET', '/secrets-stats')
        return response


    # =============================================================================
    # UTILITY METHODS (like CLI utilities)
    # =============================================================================


    async def test_connection(self) -> bool:
        """Test API connectivity.
        
        Returns:
            True if connection successful
        """
        try:
            await self._make_request('GET', '/secrets-stats')
            return True
        except Exception:
            return False

    # =============================================================================
    # SECRET REQUEST METHODS
    # =============================================================================

    async def create_request(
        self,
        *,
        message: Optional[str] = None,
        description: Optional[str] = None,
        secret_expiration_hours: int = 24,
        request_expiration_hours: int = 48,
        maximum_views: int = 1,
        email_to: Optional[str] = None,
        email_reply: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a secret request.
        
        Args:
            message: Message for the recipient
            description: Description for internal use
            secret_expiration_hours: Hours until secret expiration (1-1000)
            request_expiration_hours: Hours until request expiration (1-1000)
            maximum_views: Maximum number of views for the secret (1-10)
            email_to: Email to send the request to
            email_reply: Email for automatic reply
            
        Returns:
            Raw JSON response from API with created secret request
            
        Raises:
            ValidationError: Invalid parameters
            SharokeyError: API errors
            
        Example:
            request = await client.create_request(
                message="Please share the contract details",
                description="Contract request for Q4",
                secret_expiration_hours=48,
                request_expiration_hours=72,
                maximum_views=3,
                email_to="vendor@company.com",
                email_reply="no-reply@company.com"
            )
        """
        # Validate parameters
        if secret_expiration_hours < 1 or secret_expiration_hours > 1000:
            raise ValidationError("Secret expiration hours must be between 1 and 1000")
        
        if request_expiration_hours < 1 or request_expiration_hours > 1000:
            raise ValidationError("Request expiration hours must be between 1 and 1000")
        
        if maximum_views < 1 or maximum_views > 10:
            raise ValidationError("Maximum views must be between 1 and 10")
        
        if description and len(description) > 255:
            raise ValidationError("Description must be 255 characters or less")
        
        if message and len(message) > 255:
            raise ValidationError("Message must be 255 characters or less")
        
        if email_to and not self._is_valid_email(email_to):
            raise ValidationError("Email to must be a valid email address")
        
        if email_reply and not self._is_valid_email(email_reply):
            raise ValidationError("Email reply must be a valid email address")
        
        # Create API request
        request_data = SecretRequestCreate(
            message=message,
            description=description,
            secret_expiration_hours=secret_expiration_hours,
            request_expiration_hours=request_expiration_hours,
            maximum_views=maximum_views,
            email_to=email_to,
            email_reply=email_reply
        )
        
        # Send to API
        response = await self._make_request('POST', '/requests', request_data.to_dict())
        return response

    async def list_requests(
        self,
        *,
        limit: int = 50,
        status: Optional[str] = None,
        creator: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List secret requests.
        
        Args:
            limit: Maximum number of requests to return (default 50)
            status: Filter by status ('active' or 'expired')
            creator: Filter by creator email
            search: Search in descriptions/messages
            
        Returns:
            Raw JSON response from API with requests list
            
        Example:
            requests = await client.list_requests(status='active', limit=10)
            
            for request in requests.data:
                print(f"{request.token}: {request.description}")
        """
        params = {}
        if limit != 50:
            params['limit'] = limit
        if status:
            params['status'] = status
        if creator:
            params['creator'] = creator
        if search:
            params['search'] = search
            
        query_string = '&'.join(f'{k}={v}' for k, v in params.items())
        endpoint = f'/requests?{query_string}' if query_string else '/requests'
        
        response = await self._make_request('GET', endpoint)
        return response

    async def get_request(self, token: str) -> Dict[str, Any]:
        """Get secret request details.
        
        Args:
            token: Request token identifier
            
        Returns:
            Raw JSON response from API with request details
            
        Raises:
            NotFoundError: Request not found
            ValidationError: Invalid token
            
        Example:
            request = await client.get_request("abc123token456")
            print(f"Status: {request.status}")
        """
        if not token or not isinstance(token, str):
            raise ValidationError("Request token must be a non-empty string")
            
        response = await self._make_request('GET', f'/requests/{token.strip()}')
        return response

    async def delete_request(self, token: str) -> Dict[str, Any]:
        """Delete a secret request.
        
        Args:
            token: Request token identifier
            
        Returns:
            Raw JSON response from API
            
        Raises:
            NotFoundError: Request not found
            ValidationError: Invalid token
            
        Example:
            success = await client.delete_request("abc123token456")
            if success:
                print("Request deleted successfully")
        """
        if not token or not isinstance(token, str):
            raise ValidationError("Request token must be a non-empty string")
            
        response = await self._make_request('DELETE', f'/requests/{token.strip()}')
        return response

    async def request_stats(self) -> Dict[str, Any]:
        """Get secret request statistics.
            
        Returns:
            Raw JSON response from API with statistics about secret requests
            
        Example:
            stats = await client.request_stats()
            print(f"Total requests: {stats.get('total_requests', 0)}")
        """
        response = await self._make_request('GET', '/requests-stats')
        return response

    def _is_valid_email(self, email: str) -> bool:
        """Simple email validation."""
        import re
        pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        return re.match(pattern, email) is not None

    # =============================================================================
    # UTILITY METHODS (like JavaScript simple version)
    # =============================================================================

    async def search(self, query: str, *, limit: int = 50, status: Optional[str] = None) -> Dict[str, Any]:
        """Search secrets by description or message content.
        
        Args:
            query: Search term
            limit: Maximum results (default 50)
            status: Filter by status ('active' or 'expired')
            
        Returns:
            Raw JSON response from API with matching secrets
            
        Example:
            # Search for database credentials
            results = await client.search("database", limit=20, status="active")
            for secret in results.data:
                print(f"Found: {secret.slug} - {secret.description}")
        """
        return await self.list(limit=limit, status=status, search=query)
    
    async def get_active_secrets(self, *, limit: int = 50) -> Dict[str, Any]:
        """Get only active (non-expired) secrets.
        
        Args:
            limit: Maximum results (default 50)
            
        Returns:
            Raw JSON response from API with only active secrets
            
        Example:
            active_secrets = await client.get_active_secrets(limit=100)
            print(f"Found {len(active_secrets.data)} active secrets")
        """
        return await self.list(limit=limit, status="active")
    
    async def health(self) -> Dict[str, Any]:
        """Check API health status (simple health check).
        
        Returns:
            API health response
            
        Example:
            health = await client.health()
            print(f"Status: {health.get('status', 'unknown')}")
        """
        try:
            response = await self._make_request('GET', '/health')
            return response
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def test(self) -> Dict[str, Any]:
        """Comprehensive test and diagnostics (like JavaScript version).
        
        Performs 6 comprehensive checks:
        1. Configuration check
        2. Network connectivity 
        3. Authentication
        4. Read access
        5. Write access
        6. Statistics access
        
        Returns:
            Test results with details
            
        Example:
            results = await client.test()
            print(f"Tests passed: {results['passed']}/{results['total']}")
            for detail in results['details']:
                print(f"  {detail['name']}: {'✅' if detail['success'] else '❌'}")
        """
        results = {
            "passed": 0,
            "total": 6,
            "details": []
        }
        
        # 1. Configuration check
        config_test = {
            "name": "Configuration",
            "success": bool(self.token),
            "message": "API token is configured" if self.token else "API token is missing"
        }
        results["details"].append(config_test)
        if config_test["success"]:
            results["passed"] += 1
        
        # 2. Network connectivity
        try:
            await self.health()
            network_test = {"name": "Network", "success": True, "message": "Server connectivity OK"}
            results["passed"] += 1
        except Exception as e:
            network_test = {"name": "Network", "success": False, "message": f"Network error: {e}"}
        results["details"].append(network_test)
        
        # 3. Authentication
        try:
            await self.stats()
            auth_test = {"name": "Authentication", "success": True, "message": "Token authentication OK"}
            results["passed"] += 1
        except Exception as e:
            if "Invalid token" in str(e) or "authentication failed" in str(e).lower():
                auth_test = {"name": "Authentication", "success": False, "message": "Invalid token"}
            else:
                auth_test = {"name": "Authentication", "success": False, "message": f"Auth error: {e}"}
        results["details"].append(auth_test)
        
        # 4. Read access
        try:
            await self.list(limit=1)
            read_test = {"name": "Read Access", "success": True, "message": "Secrets listing OK"}
            results["passed"] += 1
        except Exception as e:
            read_test = {"name": "Read Access", "success": False, "message": f"Read error: {e}"}
        results["details"].append(read_test)
        
        # 5. Write access (create and delete test secret)
        try:
            test_secret = await self.create("SDK test secret - safe to delete", 1, 1, description="Python SDK test")
            secret_slug = test_secret['data']['slug']
            await self.delete(secret_slug)
            write_test = {"name": "Write Access", "success": True, "message": "Secret creation/deletion OK"}
            results["passed"] += 1
        except Exception as e:
            write_test = {"name": "Write Access", "success": False, "message": f"Write error: {e}"}
        results["details"].append(write_test)
        
        # 6. Statistics access
        try:
            await self.stats()
            stats_test = {"name": "Statistics", "success": True, "message": "Statistics endpoint OK"}
            results["passed"] += 1
        except Exception as e:
            stats_test = {"name": "Statistics", "success": False, "message": f"Stats error: {e}"}
        results["details"].append(stats_test)
        
        return results
    
    def get_info(self) -> Dict[str, Any]:
        """Get SDK information and features.
        
        Returns:
            Dictionary with SDK version, features, and capabilities
            
        Example:
            info = client.get_info()
            print(f"SDK Version: {info['version']}")
            print(f"Features: {', '.join(info['features'])}")
        """
        return {
            "name": "Sharokey Python SDK",
            "version": "1.0.0",
            "language": "Python",
            "platform": "Cross-platform",
            "features": [
                "Zero Knowledge encryption",
                "AES-GCM-256 + PBKDF2", 
                "File attachments",
                "OTP authentication", 
                "IP/geolocation filtering",
                "Secret requests",
                "Comprehensive testing",
                "Async/await support",
                "Type hints"
            ],
            "methods": [
                "create", "list", "get", "delete", "stats",
                "create_request", "list_requests", "get_request", "delete_request", "request_stats",
                "search", "get_active_secrets", "health", "test", "get_info",
                "test_connection"
            ],
            "encryption": {
                "algorithm": "AES-GCM-256",
                "key_derivation": "PBKDF2",
                "iterations": 10000,
                "zero_knowledge": True
            }
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current client configuration (without token for security).
        
        Returns:
            Configuration dictionary without sensitive data
            
        Example:
            config = client.get_config()
            print(f"API URL: {config['api_url']}")
            print(f"Has token: {config['has_token']}")
        """
        return {
            "api_url": self.api_url,
            "timeout": self.timeout,
            "has_token": bool(self.token),
            "token_length": len(self.token) if self.token else 0
        }