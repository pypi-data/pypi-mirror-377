"""
OAuth configuration for MCP Server

Fully configurable OAuth settings supporting multiple providers
and authentication flows.
"""

import os
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class OAuthProvider(Enum):
    """Supported OAuth providers"""
    CUSTOM = "custom"
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"
    OKTA = "okta"
    AUTH0 = "auth0"


@dataclass
class OAuthConfig:
    """
    Complete OAuth configuration for MCP server
    
    This configuration supports:
    - Multiple OAuth providers
    - Custom authorization servers
    - Configurable scopes and audiences
    - Token validation settings
    - PKCE support
    """
    
    # Basic OAuth settings
    enabled: bool = False
    provider: OAuthProvider = OAuthProvider.CUSTOM
    
    # Client credentials
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    
    # OAuth endpoints (for custom provider)
    authorization_endpoint: Optional[str] = None
    token_endpoint: Optional[str] = None
    userinfo_endpoint: Optional[str] = None
    jwks_uri: Optional[str] = None
    
    # Discovery endpoint (alternative to manual endpoints)
    discovery_endpoint: Optional[str] = None
    
    # Redirect URI for OAuth flow
    redirect_uri: Optional[str] = None
    
    # Scopes and permissions
    scopes: List[str] = field(default_factory=lambda: ["openid", "profile", "email"])
    
    # Token settings
    audience: Optional[str] = None
    issuer: Optional[str] = None
    
    # Security settings
    require_pkce: bool = True
    require_state: bool = True
    validate_token: bool = True
    
    # Token validation settings
    token_validation_leeway: int = 60  # seconds
    require_https: bool = True
    
    # Session settings
    session_timeout: int = 3600  # seconds (1 hour)
    refresh_token_enabled: bool = True
    
    # Access control
    allowed_domains: List[str] = field(default_factory=list)
    allowed_emails: List[str] = field(default_factory=list)
    require_email_verification: bool = False
    
    # Custom claims mapping
    user_id_claim: str = "sub"
    email_claim: str = "email"
    name_claim: str = "name"
    
    # MCP-specific settings
    mcp_resource_id: Optional[str] = None
    authorization_servers: List[str] = field(default_factory=list)
    
    @classmethod
    def from_env(cls) -> "OAuthConfig":
        """
        Create OAuth configuration from environment variables
        
        Environment variables:
        - OAUTH_ENABLED: Enable OAuth (true/false)
        - OAUTH_PROVIDER: Provider type (custom, google, github, etc.)
        - OAUTH_CLIENT_ID: OAuth client ID
        - OAUTH_CLIENT_SECRET: OAuth client secret
        - OAUTH_AUTHORIZATION_ENDPOINT: Authorization endpoint URL
        - OAUTH_TOKEN_ENDPOINT: Token endpoint URL
        - OAUTH_USERINFO_ENDPOINT: UserInfo endpoint URL
        - OAUTH_JWKS_URI: JWKS URI for token validation
        - OAUTH_DISCOVERY_ENDPOINT: OpenID Connect discovery endpoint
        - OAUTH_REDIRECT_URI: Redirect URI for OAuth flow
        - OAUTH_SCOPES: Comma-separated list of scopes
        - OAUTH_AUDIENCE: Expected audience for tokens
        - OAUTH_ISSUER: Expected token issuer
        - OAUTH_REQUIRE_PKCE: Require PKCE (true/false)
        - OAUTH_ALLOWED_DOMAINS: Comma-separated list of allowed email domains
        - OAUTH_ALLOWED_EMAILS: Comma-separated list of allowed emails
        """
        config = cls()
        
        # Basic settings
        config.enabled = os.getenv("OAUTH_ENABLED", "false").lower() == "true"
        
        provider_str = os.getenv("OAUTH_PROVIDER", "custom").lower()
        try:
            config.provider = OAuthProvider(provider_str)
        except ValueError:
            config.provider = OAuthProvider.CUSTOM
        
        # Client credentials
        config.client_id = os.getenv("OAUTH_CLIENT_ID")
        config.client_secret = os.getenv("OAUTH_CLIENT_SECRET")
        
        # OAuth endpoints
        config.authorization_endpoint = os.getenv("OAUTH_AUTHORIZATION_ENDPOINT")
        config.token_endpoint = os.getenv("OAUTH_TOKEN_ENDPOINT")
        config.userinfo_endpoint = os.getenv("OAUTH_USERINFO_ENDPOINT")
        config.jwks_uri = os.getenv("OAUTH_JWKS_URI")
        config.discovery_endpoint = os.getenv("OAUTH_DISCOVERY_ENDPOINT")
        
        # Redirect URI
        config.redirect_uri = os.getenv("OAUTH_REDIRECT_URI")
        
        # Scopes
        scopes_str = os.getenv("OAUTH_SCOPES", "openid,profile,email")
        config.scopes = [s.strip() for s in scopes_str.split(",")]
        
        # Token settings
        config.audience = os.getenv("OAUTH_AUDIENCE")
        config.issuer = os.getenv("OAUTH_ISSUER")
        
        # Security settings
        config.require_pkce = os.getenv("OAUTH_REQUIRE_PKCE", "true").lower() == "true"
        config.require_state = os.getenv("OAUTH_REQUIRE_STATE", "true").lower() == "true"
        config.validate_token = os.getenv("OAUTH_VALIDATE_TOKEN", "true").lower() == "true"
        
        # Session settings
        if session_timeout := os.getenv("OAUTH_SESSION_TIMEOUT"):
            config.session_timeout = int(session_timeout)
        
        config.refresh_token_enabled = os.getenv("OAUTH_REFRESH_TOKEN", "true").lower() == "true"
        
        # Access control
        if allowed_domains := os.getenv("OAUTH_ALLOWED_DOMAINS"):
            config.allowed_domains = [d.strip() for d in allowed_domains.split(",")]
        
        if allowed_emails := os.getenv("OAUTH_ALLOWED_EMAILS"):
            config.allowed_emails = [e.strip() for e in allowed_emails.split(",")]
        
        config.require_email_verification = os.getenv("OAUTH_REQUIRE_EMAIL_VERIFICATION", "false").lower() == "true"
        
        # Apply provider-specific defaults
        config._apply_provider_defaults()
        
        return config
    
    @classmethod
    def from_file(cls, file_path: str) -> "OAuthConfig":
        """
        Load OAuth configuration from JSON file
        
        Args:
            file_path: Path to JSON configuration file
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        config = cls()
        
        # Map JSON data to config attributes
        for key, value in data.items():
            if hasattr(config, key):
                if key == "provider":
                    config.provider = OAuthProvider(value)
                else:
                    setattr(config, key, value)
        
        config._apply_provider_defaults()
        return config
    
    def _apply_provider_defaults(self):
        """Apply provider-specific default settings"""
        
        if self.provider == OAuthProvider.GOOGLE:
            if not self.discovery_endpoint:
                self.discovery_endpoint = "https://accounts.google.com/.well-known/openid-configuration"
            if not self.issuer:
                self.issuer = "https://accounts.google.com"
                
        elif self.provider == OAuthProvider.GITHUB:
            if not self.authorization_endpoint:
                self.authorization_endpoint = "https://github.com/login/oauth/authorize"
            if not self.token_endpoint:
                self.token_endpoint = "https://github.com/login/oauth/access_token"
            if not self.userinfo_endpoint:
                self.userinfo_endpoint = "https://api.github.com/user"
                
        elif self.provider == OAuthProvider.MICROSOFT:
            if not self.discovery_endpoint:
                self.discovery_endpoint = "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration"
            if not self.issuer:
                self.issuer = "https://login.microsoftonline.com/common/v2.0"
                
        elif self.provider == OAuthProvider.AUTH0:
            # Auth0 requires domain to be set
            domain = os.getenv("OAUTH_AUTH0_DOMAIN")
            if domain:
                if not self.discovery_endpoint:
                    self.discovery_endpoint = f"https://{domain}/.well-known/openid-configuration"
                if not self.issuer:
                    self.issuer = f"https://{domain}/"
                    
        elif self.provider == OAuthProvider.OKTA:
            # Okta requires domain to be set
            domain = os.getenv("OAUTH_OKTA_DOMAIN")
            if domain:
                if not self.discovery_endpoint:
                    self.discovery_endpoint = f"https://{domain}/.well-known/openid-configuration"
                if not self.issuer:
                    self.issuer = f"https://{domain}"
    
    def validate(self) -> List[str]:
        """
        Validate the OAuth configuration
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.enabled:
            return errors  # No validation needed if OAuth is disabled
        
        # Basic validation
        if not self.client_id:
            errors.append("OAuth client_id is required")
        
        # For confidential clients, client_secret is required
        if not self.client_secret and self.provider != OAuthProvider.GITHUB:
            errors.append("OAuth client_secret is required for confidential clients")
        
        # Endpoint validation
        if not self.discovery_endpoint:
            if not self.authorization_endpoint:
                errors.append("Either discovery_endpoint or authorization_endpoint is required")
            if not self.token_endpoint:
                errors.append("Either discovery_endpoint or token_endpoint is required")
        
        # Redirect URI validation
        if not self.redirect_uri:
            errors.append("OAuth redirect_uri is required")
        elif self.require_https and not self.redirect_uri.startswith("https://"):
            if not self.redirect_uri.startswith("http://localhost"):
                errors.append("Redirect URI must use HTTPS (except for localhost)")
        
        # Scope validation
        if not self.scopes:
            errors.append("At least one OAuth scope is required")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "enabled": self.enabled,
            "provider": self.provider.value,
            "client_id": self.client_id,
            "authorization_endpoint": self.authorization_endpoint,
            "token_endpoint": self.token_endpoint,
            "userinfo_endpoint": self.userinfo_endpoint,
            "jwks_uri": self.jwks_uri,
            "discovery_endpoint": self.discovery_endpoint,
            "redirect_uri": self.redirect_uri,
            "scopes": self.scopes,
            "audience": self.audience,
            "issuer": self.issuer,
            "require_pkce": self.require_pkce,
            "require_state": self.require_state,
            "validate_token": self.validate_token,
            "allowed_domains": self.allowed_domains,
            "allowed_emails": self.allowed_emails,
            "require_email_verification": self.require_email_verification,
            "mcp_resource_id": self.mcp_resource_id,
            "authorization_servers": self.authorization_servers
        }