"""
OAuth handler for MCP Server authentication

Handles OAuth flows, token validation, and session management
"""

import asyncio
import hashlib
import secrets
import base64
import json
import time
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode, parse_qs, urlparse

import httpx
import jwt
from jwt import PyJWKClient

from .oauth_config import OAuthConfig


class OAuthHandler:
    """
    Handles OAuth authentication flows and token validation
    """
    
    def __init__(self, config: OAuthConfig):
        """
        Initialize OAuth handler with configuration
        
        Args:
            config: OAuth configuration
        """
        self.config = config
        self._discovery_cache = None
        self._discovery_cache_time = 0
        self._jwks_client = None
        self._sessions = {}  # Store active sessions
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient()
        
    async def close(self):
        """Clean up resources"""
        await self.http_client.aclose()
    
    async def get_discovery_document(self) -> Dict[str, Any]:
        """
        Fetch and cache OpenID Connect discovery document
        
        Returns:
            Discovery document as dictionary
        """
        if not self.config.discovery_endpoint:
            return {}
        
        # Check cache (refresh every hour)
        if self._discovery_cache and (time.time() - self._discovery_cache_time) < 3600:
            return self._discovery_cache
        
        response = await self.http_client.get(self.config.discovery_endpoint)
        response.raise_for_status()
        
        self._discovery_cache = response.json()
        self._discovery_cache_time = time.time()
        
        # Update endpoints from discovery if not already set
        if not self.config.authorization_endpoint:
            self.config.authorization_endpoint = self._discovery_cache.get("authorization_endpoint")
        if not self.config.token_endpoint:
            self.config.token_endpoint = self._discovery_cache.get("token_endpoint")
        if not self.config.userinfo_endpoint:
            self.config.userinfo_endpoint = self._discovery_cache.get("userinfo_endpoint")
        if not self.config.jwks_uri:
            self.config.jwks_uri = self._discovery_cache.get("jwks_uri")
        
        return self._discovery_cache
    
    def generate_state(self) -> str:
        """Generate secure random state for OAuth flow"""
        return secrets.token_urlsafe(32)
    
    def generate_pkce_challenge(self) -> Tuple[str, str]:
        """
        Generate PKCE code verifier and challenge
        
        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        
        return code_verifier, code_challenge
    
    async def get_authorization_url(self, state: Optional[str] = None) -> Dict[str, str]:
        """
        Generate OAuth authorization URL
        
        Args:
            state: Optional state parameter (generated if not provided)
            
        Returns:
            Dictionary with URL and related parameters
        """
        # Ensure we have discovery document if using discovery
        if self.config.discovery_endpoint:
            await self.get_discovery_document()
        
        if not self.config.authorization_endpoint:
            raise ValueError("Authorization endpoint not configured")
        
        # Generate state if not provided
        if not state:
            state = self.generate_state()
        
        # Build authorization parameters
        params = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scopes),
            "state": state,
        }
        
        # Add PKCE if required
        code_verifier = None
        if self.config.require_pkce:
            code_verifier, code_challenge = self.generate_pkce_challenge()
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        
        # Add audience if configured
        if self.config.audience:
            params["audience"] = self.config.audience
        
        # Add resource parameter for MCP
        if self.config.mcp_resource_id:
            params["resource"] = self.config.mcp_resource_id
        
        # Build authorization URL
        auth_url = f"{self.config.authorization_endpoint}?{urlencode(params)}"
        
        return {
            "url": auth_url,
            "state": state,
            "code_verifier": code_verifier
        }
    
    async def exchange_code_for_token(
        self, 
        code: str, 
        code_verifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from OAuth callback
            code_verifier: PKCE code verifier (if PKCE was used)
            
        Returns:
            Token response including access_token
        """
        if not self.config.token_endpoint:
            raise ValueError("Token endpoint not configured")
        
        # Build token request
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.redirect_uri,
            "client_id": self.config.client_id,
        }
        
        # Add client secret for confidential clients
        if self.config.client_secret:
            data["client_secret"] = self.config.client_secret
        
        # Add PKCE verifier if provided
        if code_verifier:
            data["code_verifier"] = code_verifier
        
        # Add resource parameter for MCP
        if self.config.mcp_resource_id:
            data["resource"] = self.config.mcp_resource_id
        
        # Exchange code for token
        response = await self.http_client.post(
            self.config.token_endpoint,
            data=data,
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        
        return response.json()
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate and decode an access token
        
        Args:
            token: Access token to validate
            
        Returns:
            Decoded token claims
            
        Raises:
            ValueError: If token is invalid
        """
        if not self.config.validate_token:
            # Skip validation if disabled (not recommended)
            return jwt.decode(token, options={"verify_signature": False})
        
        # Get JWKS client
        if not self._jwks_client and self.config.jwks_uri:
            self._jwks_client = PyJWKClient(self.config.jwks_uri)
        
        if self._jwks_client:
            # Validate with JWKS
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.config.audience,
                issuer=self.config.issuer,
                leeway=self.config.token_validation_leeway
            )
        else:
            # Fallback to unverified decode (not recommended for production)
            claims = jwt.decode(token, options={"verify_signature": False})
            
            # Manual validation of claims
            if self.config.audience and claims.get("aud") != self.config.audience:
                raise ValueError("Token audience mismatch")
            if self.config.issuer and claims.get("iss") != self.config.issuer:
                raise ValueError("Token issuer mismatch")
            
            # Check expiration
            if "exp" in claims and claims["exp"] < time.time():
                raise ValueError("Token has expired")
        
        return claims
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Fetch user information from userinfo endpoint
        
        Args:
            access_token: Valid access token
            
        Returns:
            User information dictionary
        """
        if not self.config.userinfo_endpoint:
            # Try to extract from token claims
            return await self.validate_token(access_token)
        
        response = await self.http_client.get(
            self.config.userinfo_endpoint,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        
        return response.json()
    
    def check_user_access(self, user_info: Dict[str, Any]) -> bool:
        """
        Check if user has access based on configuration
        
        Args:
            user_info: User information from token or userinfo endpoint
            
        Returns:
            True if user has access, False otherwise
        """
        # Extract email from claims
        email = user_info.get(self.config.email_claim)
        
        if not email:
            return False
        
        # Check email verification if required
        if self.config.require_email_verification:
            if not user_info.get("email_verified", False):
                return False
        
        # Check allowed emails
        if self.config.allowed_emails:
            if email not in self.config.allowed_emails:
                return False
        
        # Check allowed domains
        if self.config.allowed_domains:
            domain = email.split("@")[-1]
            if domain not in self.config.allowed_domains:
                return False
        
        return True
    
    def create_session(self, user_info: Dict[str, Any], access_token: str) -> str:
        """
        Create a session for authenticated user
        
        Args:
            user_info: User information
            access_token: Access token
            
        Returns:
            Session ID
        """
        session_id = secrets.token_urlsafe(32)
        
        self._sessions[session_id] = {
            "user_info": user_info,
            "access_token": access_token,
            "created_at": time.time(),
            "last_accessed": time.time()
        }
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Validate and return session information
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            Session information if valid, None otherwise
        """
        session = self._sessions.get(session_id)
        
        if not session:
            return None
        
        # Check session timeout
        if (time.time() - session["created_at"]) > self.config.session_timeout:
            del self._sessions[session_id]
            return None
        
        # Update last accessed time
        session["last_accessed"] = time.time()
        
        return session
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token response
        """
        if not self.config.refresh_token_enabled:
            raise ValueError("Refresh token not enabled")
        
        if not self.config.token_endpoint:
            raise ValueError("Token endpoint not configured")
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.config.client_id,
        }
        
        if self.config.client_secret:
            data["client_secret"] = self.config.client_secret
        
        response = await self.http_client.post(
            self.config.token_endpoint,
            data=data,
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        
        return response.json()
    
    def get_www_authenticate_header(self) -> str:
        """
        Generate WWW-Authenticate header for 401 responses
        
        Returns:
            WWW-Authenticate header value
        """
        # Build header parts
        parts = ['Bearer']
        
        if self.config.mcp_resource_id:
            parts.append(f'realm="{self.config.mcp_resource_id}"')
        
        if self.config.authorization_servers:
            servers = ",".join(f'"{s}"' for s in self.config.authorization_servers)
            parts.append(f'authorization_servers=[{servers}]')
        
        return " ".join(parts)