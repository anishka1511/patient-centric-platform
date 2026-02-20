"""
Geolocation Service
Auto-detects user location based on IP address
"""
import os
import httpx
from typing import Optional, Dict, Any
from config.logging_config import logger
from fastapi import Request


class GeolocationService:
    """Service for detecting user location from IP address"""
    
    def __init__(self):
        self.ipinfo_api_key = os.getenv("IPINFO_API_KEY", "")
        self.enabled = os.getenv("ENABLE_AUTO_LOCATION", "true").lower() == "true"
        self.timeout = 5.0  # seconds
    
    async def get_location_from_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Get location data from IP address
        
        Args:
            ip_address: User's IP address
            
        Returns:
            Location dictionary or None if detection fails
        """
        if not self.enabled:
            logger.debug("Auto-location disabled")
            return None
        
        # Skip localhost/private IPs
        if self._is_private_ip(ip_address):
            logger.debug(f"Private IP detected: {ip_address}, using default location")
            return self._get_default_location()
        
        try:
            # Try ipinfo.io first (if API key provided)
            if self.ipinfo_api_key:
                location = await self._fetch_from_ipinfo(ip_address)
                if location:
                    return location
            
            # Fallback to free ipapi.co
            location = await self._fetch_from_ipapi(ip_address)
            if location:
                return location
            
            # Fallback to ip-api.com
            location = await self._fetch_from_ipapi_com(ip_address)
            return location
            
        except Exception as e:
            logger.error(f"Geolocation error: {e}")
            return None
    
    async def _fetch_from_ipinfo(self, ip: str) -> Optional[Dict[str, Any]]:
        """Fetch from ipinfo.io (requires API key)"""
        try:
            url = f"https://ipinfo.io/{ip}/json?token={self.ipinfo_api_key}"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    loc = data.get("loc", "").split(",")
                    
                    return {
                        "latitude": float(loc[0]) if len(loc) > 0 else None,
                        "longitude": float(loc[1]) if len(loc) > 1 else None,
                        "city": data.get("city"),
                        "state": data.get("region"),
                        "country": data.get("country"),
                        "postal_code": data.get("postal"),
                        "source": "ipinfo.io"
                    }
        except Exception as e:
            logger.warning(f"ipinfo.io failed: {e}")
        return None
    
    async def _fetch_from_ipapi(self, ip: str) -> Optional[Dict[str, Any]]:
        """Fetch from ipapi.co (free, no key needed, 1000/day)"""
        try:
            url = f"https://ipapi.co/{ip}/json/"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    return {
                        "latitude": data.get("latitude"),
                        "longitude": data.get("longitude"),
                        "city": data.get("city"),
                        "state": data.get("region"),
                        "country": data.get("country_name"),
                        "postal_code": data.get("postal"),
                        "source": "ipapi.co"
                    }
        except Exception as e:
            logger.warning(f"ipapi.co failed: {e}")
        return None
    
    async def _fetch_from_ipapi_com(self, ip: str) -> Optional[Dict[str, Any]]:
        """Fetch from ip-api.com (free, no key needed, 45/min)"""
        try:
            url = f"http://ip-api.com/json/{ip}"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "success":
                        return {
                            "latitude": data.get("lat"),
                            "longitude": data.get("lon"),
                            "city": data.get("city"),
                            "state": data.get("regionName"),
                            "country": data.get("country"),
                            "postal_code": data.get("zip"),
                            "source": "ip-api.com"
                        }
        except Exception as e:
            logger.warning(f"ip-api.com failed: {e}")
        return None
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private/localhost"""
        if not ip:
            return True
        
        private_prefixes = [
            "127.", "10.", "172.", "192.168.",
            "localhost", "::1", "0.0.0.0"
        ]
        
        return any(ip.startswith(prefix) for prefix in private_prefixes)
    
    def _get_default_location(self) -> Dict[str, Any]:
        """Return default location for localhost testing"""
        return {
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "source": "default (localhost)"
        }
    
    async def get_location_from_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Extract and geolocate IP from FastAPI request
        
        Args:
            request: FastAPI Request object
            
        Returns:
            Location dictionary
        """
        # Get IP from request (handles proxies)
        ip = request.client.host if request.client else None
        
        # Check for forwarded IP (if behind proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            ip = real_ip
        
        logger.info(f"Detecting location for IP: {ip}")
        
        if ip:
            location = await self.get_location_from_ip(ip)
            if location:
                logger.info(f"Location detected: {location.get('city')}, {location.get('state')} (source: {location.get('source')})")
                return location
        
        return None


# Singleton instance
geolocation_service = GeolocationService()
