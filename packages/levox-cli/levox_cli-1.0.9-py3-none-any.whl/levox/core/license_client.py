"""
License Client for Levox CLI
Connects to the Levox License Server for validation and feature gating.
"""

import os
import json
import time
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone
import jwt
from dataclasses import dataclass

from .exceptions import LicenseError, ErrorCode
from .config import LicenseTier


@dataclass
class LicenseInfo:
    """License information structure."""
    license_key: str
    tier: LicenseTier
    email: str
    device_limit: int
    expires_at: datetime
    current_devices: int
    is_valid: bool
    jwt_token: str


class LicenseClient:
    """Client for communicating with Levox License Server."""
    
    def __init__(self, server_url: str = None):
        # Default to environment variable(s) or fallback URL
        if server_url is None:
            server_url = (
                os.getenv('LEVOX_SERVER_URL')
                or os.getenv('LEVOX_LICENSE_SERVER')
                or 'https://levox.aifenrix.com'
            )
        self.server_url = server_url.rstrip('/')
        self.logger = logging.getLogger(__name__)
        self.license_cache_file = Path.home() / ".levox" / "license_cache.json"
        self.device_fingerprint = self._generate_device_fingerprint()
        
        # Ensure cache directory exists
        self.license_cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _generate_device_fingerprint(self) -> str:
        """Generate a unique device fingerprint."""
        import platform
        import hashlib
        
        # Create fingerprint from system info
        system_info = f"{platform.node()}-{platform.system()}-{platform.processor()}"
        return hashlib.sha256(system_info.encode()).hexdigest()[:16]
    
    def _make_request(self, endpoint: str, method: str = "POST", 
                     data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to license server."""
        url = f"{self.server_url}/api/{endpoint}"
        
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Levox-CLI/0.9.0"
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=10)
            else:
                response = requests.get(url, headers=default_headers, timeout=10)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"License server request failed: {e}")
            raise LicenseError(f"Failed to connect to license server: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response from license server: {e}")
            raise LicenseError("Invalid response from license server")
    
    def verify_license(self, license_key: str) -> LicenseInfo:
        """Verify license with the server."""
        try:
            # Step 1: Get JWT token from license key
            token_response = self._make_request("get-license-token", "POST", {
                "license_key": license_key
            })
            
            if not token_response.get("ok"):
                raise LicenseError(f"License lookup failed: {token_response.get('error', 'Unknown error')}")
            
            jwt_token = token_response["data"]["jwt"]
            
            # Step 2: Verify the JWT token with device fingerprint
            verify_response = self._make_request("verify-license", "POST", {
                "token": jwt_token,
                "device_fingerprint": self.device_fingerprint
            })
            
            if not verify_response.get("ok"):
                raise LicenseError(f"License verification failed: {verify_response.get('error', 'Unknown error')}")
            
            verify_data = verify_response["data"]
            
            # Parse expiration date
            expires_at = datetime.fromisoformat(token_response["data"]["expires_at"].replace('Z', '+00:00'))

            # Determine tier from JWT payload
            try:
                jwt_payload = jwt.decode(jwt_token, options={"verify_signature": False})
            except AttributeError:
                # Fallback for older PyJWT versions
                jwt_payload = jwt.decode(jwt_token, verify=False)
            tier_str = jwt_payload.get("tier", "standard")
            tier = LicenseTier._from_string(tier_str) or LicenseTier.STARTER
            
            license_info = LicenseInfo(
                license_key=license_key,
                tier=tier,
                email=jwt_payload.get("sub", ""),
                device_limit=verify_data.get("device_limit", 1),
                expires_at=expires_at,
                current_devices=verify_data.get("current_devices_count", 0),
                is_valid=verify_data.get("valid", False),
                jwt_token=jwt_token
            )
            
            # Cache the valid license
            self._cache_license(license_info)
            
            return license_info
            
        except Exception as e:
            if isinstance(e, LicenseError):
                raise
            self.logger.error(f"License verification error: {e}")
            raise LicenseError(f"License verification failed: {e}")
    
    def _cache_license(self, license_info: LicenseInfo) -> None:
        """Cache license information locally."""
        try:
            cache_data = {
                "license_key": license_info.license_key,
                "tier": license_info.tier.value,
                "email": license_info.email,
                "device_limit": license_info.device_limit,
                "expires_at": license_info.expires_at.isoformat(),
                "current_devices": license_info.current_devices,
                "jwt_token": license_info.jwt_token,
                "cached_at": datetime.now(timezone.utc).isoformat(),
                "device_fingerprint": self.device_fingerprint
            }
            
            with open(self.license_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Failed to cache license: {e}")
    
    def _load_cached_license(self) -> Optional[LicenseInfo]:
        """Load license from cache if valid."""
        try:
            if not self.license_cache_file.exists():
                return None
            
            with open(self.license_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is for this device
            if cache_data.get("device_fingerprint") != self.device_fingerprint:
                return None
            
            # Check if cached license is expired
            cached_at = datetime.fromisoformat(cache_data["cached_at"])
            if (datetime.now(timezone.utc) - cached_at).total_seconds() > 86400:  # 24 hour cache
                return None
            
            # Check if license itself is expired
            expires_at = datetime.fromisoformat(cache_data["expires_at"])
            if expires_at < datetime.now(timezone.utc):
                return None
            
            tier = LicenseTier._from_string(cache_data["tier"]) or LicenseTier.STARTER
            
            return LicenseInfo(
                license_key=cache_data["license_key"],
                tier=tier,
                email=cache_data["email"],
                device_limit=cache_data["device_limit"],
                expires_at=expires_at,
                current_devices=cache_data["current_devices"],
                is_valid=True,
                jwt_token=cache_data["jwt_token"]
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to load cached license: {e}")
            return None
    
    def get_license_tier(self) -> Optional[LicenseTier]:
        """Get the current license tier."""
        try:
            license_info = self.get_license_info()
            return license_info.tier if license_info else None
        except Exception:
            return None
    
    def get_license_info(self, license_key: Optional[str] = None) -> LicenseInfo:
        """Get license information, using cache if available."""
        # Try to load from cache first
        cached_license = self._load_cached_license()
        if cached_license and (not license_key or cached_license.license_key == license_key):
            return cached_license
        
        # If no license key provided, try environment variable
        if not license_key:
            license_key = os.getenv("LEVOX_LICENSE_KEY")
        
        if not license_key:
            # Return default standard license for demo purposes
            self.logger.warning("No license key found, using standard tier")
            return LicenseInfo(
                license_key="demo",
                tier=LicenseTier.STARTER,
                email="demo@levox.com",
                device_limit=1,
                expires_at=datetime.now(timezone.utc),
                current_devices=1,
                is_valid=False,
                jwt_token=""
            )
        
        # Verify license with server
        return self.verify_license(license_key)
    
    def validate_license_for_feature(self, feature: str, license_info: Optional[LicenseInfo] = None) -> bool:
        """Check if current license supports a specific feature."""
        if not license_info:
            license_info = self.get_license_info()
        
        # Feature mapping based on tier (aligned with website plans)
        # Starter: Basic regex + basic reporting only
        # Pro: AST, Context, CFG, Advanced Reporting, Custom Rules
        # Enterprise: Full 7-stage incl Dataflow, ML, API/Integrations, Compliance, Enterprise logging
        feature_map = {
            LicenseTier.STARTER: [
                "regex_detection", "basic_logging", "file_scanning",
                "basic_reporting"
            ],
            LicenseTier.PRO: [
                "regex_detection", "basic_logging", "file_scanning",
                "ast_analysis", "context_analysis", "cfg_analysis",
                "advanced_reporting", "custom_rules", "multi_language",
                "performance_metrics"
            ],
            LicenseTier.ENTERPRISE: [
                "regex_detection", "basic_logging", "file_scanning",
                "ast_analysis", "context_analysis", "cfg_analysis",
                "advanced_reporting", "custom_rules", "multi_language",
                "performance_metrics", "ml_filtering", "dataflow_analysis",
                "api_integration", "enterprise_logging", "compliance_audit",
                "gdpr_analysis", "compliance_reporting", "crypto_verification",
                "custom_integrations"
            ]
        }
        
        allowed_features = feature_map.get(license_info.tier, [])
        return feature in allowed_features
    
    def clear_cache(self) -> None:
        """Clear cached license information."""
        try:
            if self.license_cache_file.exists():
                self.license_cache_file.unlink()
                self.logger.info("License cache cleared")
        except Exception as e:
            self.logger.warning(f"Failed to clear license cache: {e}")


# Global license client instance
_license_client: Optional[LicenseClient] = None

def get_license_client() -> LicenseClient:
    """Get global license client instance."""
    global _license_client
    if _license_client is None:
        _license_client = LicenseClient()
    return _license_client


def validate_license() -> LicenseInfo:
    """Validate current license and return info."""
    client = get_license_client()
    return client.get_license_info()


def check_feature_available(feature: str) -> bool:
    """Check if a feature is available with current license."""
    client = get_license_client()
    license_info = client.get_license_info()
    return client.validate_license_for_feature(feature, license_info)
