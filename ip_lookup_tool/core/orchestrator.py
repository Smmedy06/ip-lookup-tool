# core/orchestrator.py
import asyncio
import aiohttp
from typing import List, Dict, Any

from .ip_utils import is_private_ip
from api.geo_providers import GEO_PROVIDERS
from api.threat_providers import THREAT_PROVIDERS
from config import GEO_PROVIDER_FALLBACK_ORDER

class IPOrchestrator:
    def __init__(self, targets: List[str], no_threat: bool = False):
        self.targets = targets
        self.no_threat = no_threat

    async def _fetch_geo(self, ip: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        for provider_name in GEO_PROVIDER_FALLBACK_ORDER:
            try: return await GEO_PROVIDERS[provider_name].fetch(ip, session)
            except Exception: continue
        return {"error": "All geolocation providers failed."}

    async def _process_ip(self, ip: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        if is_private_ip(ip):
            return {"ip": ip, "error": "Private IP address"}
        
        tasks = [self._fetch_geo(ip, session)]
        if not self.no_threat:
            tasks.append(THREAT_PROVIDERS["abuseipdb"].fetch(ip, session))
        
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        geo_result = task_results[0] if not isinstance(task_results[0], Exception) else {"error": str(task_results[0])}
        threat_result = {}
        if not self.no_threat:
            threat_result = task_results[1] if not isinstance(task_results[1], Exception) else {"error": str(task_results[1])}
        
        return {"ip": ip, "geolocation": geo_result, "threat_intel": threat_result}

    async def run(self) -> List[Dict[str, Any]]:
        """Runs the orchestration for all target IPs."""
        async with aiohttp.ClientSession() as session:
            coroutines = [self._process_ip(ip, session) for ip in self.targets]
            results = await asyncio.gather(*coroutines)
        return results