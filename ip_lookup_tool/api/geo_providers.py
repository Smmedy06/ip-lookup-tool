# api/geo_providers.py
import aiohttp
from typing import Dict, Any
from .base_provider import BaseProvider
from config import IPINFO_API_KEY, API_TIMEOUT

class IPInfoProvider(BaseProvider):
    """Fetches geolocation data from ipinfo.io."""
    async def fetch(self, ip: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        url = f"https://ipinfo.io/{ip}?token={IPINFO_API_KEY}"
        async with session.get(url, timeout=API_TIMEOUT) as response:
            response.raise_for_status()
            data = await response.json()
            return {
                "provider": "ipinfo.io", "ip": data.get("ip"), "hostname": data.get("hostname"),
                "city": data.get("city"), "region": data.get("region"), "country": data.get("country"),
                "loc": data.get("loc"), "org": data.get("org"), "postal": data.get("postal"),
            }

class IPApiComProvider(BaseProvider):
    """Fetches geolocation data from ip-api.com."""
    async def fetch(self, ip: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,city,lat,lon,isp,org,query,reverse"
        async with session.get(url, timeout=API_TIMEOUT) as response:
            response.raise_for_status()
            data = await response.json()
            if data.get("status") == "fail":
                raise ValueError(f"ip-api.com failed: {data.get('message')}")
            lat, lon = data.get('lat'), data.get('lon')
            return {
                "provider": "ip-api.com", "ip": data.get("query"), "hostname": data.get("reverse"),
                "city": data.get("city"), "country": data.get("country"), "loc": f"{lat},{lon}" if lat and lon else None,
                "org": data.get("org") or data.get("isp"),
            }

GEO_PROVIDERS = {"ipinfo": IPInfoProvider(), "ipapi.com": IPApiComProvider()}