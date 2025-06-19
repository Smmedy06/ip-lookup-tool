# api/base_provider.py
from abc import ABC, abstractmethod
import aiohttp
from typing import Dict, Any

class BaseProvider(ABC):
    """Abstract base class for all API providers."""
    
    @abstractmethod
    async def fetch(self, ip: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Fetches data for a given IP address."""
        pass