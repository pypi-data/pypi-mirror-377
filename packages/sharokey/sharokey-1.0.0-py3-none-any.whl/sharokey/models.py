"""
Sharokey data models.

Defines the data structures used by the Sharokey Python SDK.
"""

from datetime import datetime
from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field


@dataclass
class Attachment:
    """Represents a file attachment."""
    name: str
    data: str  # Base64 encoded encrypted data
    size: int  # Original file size in bytes


@dataclass
class Secret:
    """Represents a secret from the API."""
    slug: str
    description: Optional[str] = None
    message: Optional[str] = None
    creator: Optional[str] = None
    maximum_views: int = 1
    current_views: int = 0
    expiration: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    has_attachments: bool = False
    has_password: bool = False
    attachments_count: int = 0
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    access_url: Optional[str] = None
    share_url: Optional[str] = None  # Complete URL with keyB fragment
    expires_in_hours: Optional[int] = None  # Only for creation response
    # Security features
    captcha: bool = False
    otp_type: Optional[str] = None
    ip_whitelist: Optional[str] = None
    geolocation: Optional[str] = None
    is_expired: bool = False
    status: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Secret':
        """Create Secret instance from API response dictionary."""
        # Convertir les valeurs string en int quand nécessaire
        max_views = data.get('maximum_views', 1)
        if isinstance(max_views, str):
            max_views = int(max_views) if max_views and max_views != 'null' else 1
        
        curr_views = data.get('current_views', 0)
        if isinstance(curr_views, str):
            curr_views = int(curr_views) if curr_views else 0
            
        attachments_count = data.get('attachments_count', 0)
        if isinstance(attachments_count, str):
            attachments_count = int(attachments_count) if attachments_count else 0
        
        return cls(
            slug=data.get('slug', ''),
            description=data.get('description'),
            message=data.get('message'),
            creator=data.get('creator'),
            maximum_views=max_views,
            current_views=curr_views,
            expiration=data.get('expiration'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            has_attachments=data.get('has_attachments', False),
            has_password=data.get('has_password', False),
            attachments_count=attachments_count,
            attachments=data.get('attachments', []),
            access_url=data.get('access_url'),
            share_url=data.get('share_url'),
            expires_in_hours=data.get('expires_in_hours'),
            # Security features
            captcha=data.get('captcha', False),
            otp_type=data.get('otp_type'),
            ip_whitelist=data.get('ip_whitelist'),
            geolocation=data.get('geolocation'),
            is_expired=data.get('is_expired', False),
            status=data.get('status')
        )


@dataclass
class SecretCreate:
    """Request data for creating a secret."""
    content: str
    iv: str
    salt: str
    key: str  # keyA only
    maximum_views: int = 1
    expiration_hours: int = 24
    description: Optional[str] = None
    message: Optional[str] = None
    password: Optional[str] = None
    otp_email: Optional[str] = None
    otp_phone: Optional[str] = None
    captcha: Optional[bool] = None
    ip_whitelist: Optional[str] = None
    geolocation: Optional[str] = None
    attachments: List[Attachment] = field(default_factory=list)
    attachments_total_size: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        data = {
            'content': self.content,
            'iv': self.iv,
            'salt': self.salt,
            'key': self.key,
            'maximum_views': self.maximum_views,
            'expiration_hours': self.expiration_hours,
        }
        
        if self.description:
            data['description'] = self.description
        if self.message:
            data['message'] = self.message
        if self.password:
            data['password'] = self.password
        if self.otp_email:
            data['otp_type'] = 'email'
            data['otp_receiver'] = self.otp_email
        if self.otp_phone:
            data['otp_type'] = 'phone'
            data['otp_receiver'] = self.otp_phone
        if self.captcha:
            data['captcha'] = self.captcha
        if self.ip_whitelist:
            data['ip_whitelist'] = self.ip_whitelist
        if self.geolocation:
            data['geolocation'] = self.geolocation
        if self.attachments:
            data['attachments'] = [{'name': a.name, 'data': a.data, 'size': a.size} for a in self.attachments]
            data['attachments_total_size'] = self.attachments_total_size
            
        return data


@dataclass
class SecretList:
    """Response data for listing secrets."""
    success: bool
    count: int
    data: List[Secret] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, response_data: Dict[str, Any]) -> 'SecretList':
        """Create SecretList instance from API response."""
        # L'API retourne les secrets dans data.items
        data_section = response_data.get('data', {})
        if isinstance(data_section, dict):
            secrets_list = data_section.get('items', [])
            pagination = data_section.get('pagination', {})
            count = pagination.get('total', len(secrets_list))
        else:
            # Fallback si data n'est pas un dict
            secrets_list = data_section if isinstance(data_section, list) else []
            count = len(secrets_list)
            
        secrets = [Secret.from_dict(s) for s in secrets_list]
        return cls(
            success=response_data.get('success', True),
            count=count,
            data=secrets
        )


@dataclass
class Stats:
    """Statistics from the API."""
    total_secrets: int = 0
    active_secrets: int = 0
    expired_secrets: int = 0
    total_views: int = 0
    secrets_with_password: int = 0
    secrets_created_today: int = 0
    secrets_created_this_week: int = 0
    secrets_created_this_month: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stats':
        """Create Stats instance from API response dictionary."""
        stats_data = data.get('data', {})
        
        # Convertir les strings en int si nécessaire
        total_views = stats_data.get('total_views', 0)
        if isinstance(total_views, str):
            total_views = int(total_views) if total_views else 0
            
        return cls(
            total_secrets=stats_data.get('total_secrets', 0),
            active_secrets=stats_data.get('active_secrets', 0),
            expired_secrets=stats_data.get('expired_secrets', 0),
            total_views=total_views,
            secrets_with_password=stats_data.get('secrets_with_password', 0),
            secrets_created_today=stats_data.get('secrets_created_today', 0),
            secrets_created_this_week=stats_data.get('secrets_created_this_week', 0),
            secrets_created_this_month=stats_data.get('secrets_created_this_month', 0)
        )


# ===== SECRET REQUEST MODELS =====

@dataclass
class SecretRequest:
    """Represents a secret request from the API."""
    id: int
    token: str
    message: Optional[str] = None
    description: Optional[str] = None
    secret_expiration_hours: int = 24
    request_expiration_hours: int = 48
    maximum_views: int = 1
    email_to: Optional[str] = None
    email_reply: Optional[str] = None
    creator: Optional[str] = None
    secret_expiration: Optional[str] = None
    request_expiration: Optional[str] = None
    status: str = "active"
    url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecretRequest':
        """Create SecretRequest instance from API response dictionary."""
        # L'API retourne les données sous data.request, pas directement data
        request_data = data.get('request', data)  # Fallback si pas de structure imbriquée
        
        return cls(
            id=request_data.get('id', 0),
            token=request_data.get('token', ''),
            message=request_data.get('message'),
            description=request_data.get('description'),
            secret_expiration_hours=request_data.get('secret_expiration_hours', 24),
            request_expiration_hours=request_data.get('request_expiration_hours', 48),
            maximum_views=request_data.get('maximum_views', 1),
            email_to=request_data.get('email_to'),
            email_reply=request_data.get('email_reply'),
            creator=request_data.get('creator'),
            secret_expiration=request_data.get('secret_expiration'),
            request_expiration=request_data.get('request_expiration'),
            status=request_data.get('status', 'active'),
            url=request_data.get('url'),
            created_at=request_data.get('created_at'),
            updated_at=request_data.get('updated_at')
        )
    
    def is_active(self) -> bool:
        """Check if the request is still active."""
        return self.status == 'active'
    
    def is_expired(self) -> bool:
        """Check if the request has expired."""
        return self.status == 'expired'
    
    def get_share_url(self) -> str:
        """Get the share URL for this request."""
        return self.url or ''


@dataclass
class SecretRequestCreate:
    """Request data for creating a secret request."""
    message: Optional[str] = None
    description: Optional[str] = None
    secret_expiration_hours: int = 24
    request_expiration_hours: int = 48
    maximum_views: int = 1
    email_to: Optional[str] = None
    email_reply: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        data = {
            'secret_expiration_hours': self.secret_expiration_hours,
            'request_expiration_hours': self.request_expiration_hours,
            'maximum_views': self.maximum_views,
        }
        
        if self.message:
            data['message'] = self.message
        if self.description:
            data['description'] = self.description
        if self.email_to:
            data['email_to'] = self.email_to
        if self.email_reply:
            data['email_reply'] = self.email_reply
            
        return data


@dataclass
class SecretRequestList:
    """Response data for listing secret requests."""
    success: bool
    count: int
    data: List[SecretRequest] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, response_data: Dict[str, Any]) -> 'SecretRequestList':
        """Create SecretRequestList instance from API response."""
        data_section = response_data.get('data', {})
        if isinstance(data_section, dict):
            requests_list = data_section.get('requests', data_section.get('items', []))
            pagination = data_section.get('pagination', {})
            count = pagination.get('total', len(requests_list))
        else:
            # Fallback if data is not a dict
            requests_list = data_section if isinstance(data_section, list) else []
            count = len(requests_list)
            
        requests = [SecretRequest.from_dict(r) for r in requests_list]
        return cls(
            success=response_data.get('success', True),
            count=count,
            data=requests
        )