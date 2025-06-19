# api/threat_providers.py
import aiohttp
from typing import Dict, Any
from .base_provider import BaseProvider
from config import ABUSEIPDB_API_KEY, API_TIMEOUT

class AbuseIPDBProvider(BaseProvider):
    """Fetches threat intelligence data from AbuseIPDB."""
    async def fetch(self, ip: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        if not ABUSEIPDB_API_KEY or ABUSEIPDB_API_KEY == "YOUR_ABUSEIPDB_API_KEY_HERE":
            return {"error": "AbuseIPDB API key not configured."}
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"}
        params = {"ipAddress": ip, "maxAgeInDays": "90"}
        async with session.get(url, headers=headers, params=params, timeout=API_TIMEOUT) as response:
            response.raise_for_status()
            data = (await response.json()).get("data", {})
            return {
                "provider": "AbuseIPDB", "is_whitelisted": data.get("isWhitelisted"),
                "abuse_confidence_score": data.get("abuseConfidenceScore"),
                "total_reports": data.get("totalReports"), "usage_type": data.get("usageType"),
            }

THREAT_PROVIDERS = {"abuseipdb": AbuseIPDBProvider()}