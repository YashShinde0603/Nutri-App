# app/services/usda_client.py

import httpx
from app.config import settings
from typing import Optional
import time

BASE = "https://api.nal.usda.gov/fdc/v1"

class USDAClient:
    def __init__(self, api_key: Optional[str] = None, timeout: int = 15):
        self.api_key = api_key or settings.FDC_API_KEY
        self.client = httpx.Client(timeout=timeout)
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour cache

    def _cache_get(self, key):
        item = self._cache.get(key)
        if not item:
            return None

        ts, value = item
        if time.time() - ts > self._cache_ttl:
            self._cache.pop(key, None)
            return None

        return value

    def _cache_set(self, key, value):
        self._cache[key] = (time.time(), value)

    def search_foods(self, query: str, page_size: int = 25, page_number: int = 1):
        url = f"{BASE}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": page_size,
            "pageNumber": page_number,
        }
        r = self.client.get(url, params=params)

        # If the API fails → give clear message
        try:
            r.raise_for_status()
        except Exception:
            raise RuntimeError(f"USDA Search failed: {r.text}")

        return r.json()

    def get_food(self, fdc_id: int):
        """Always returns a dictionary or raises an exception."""

        if fdc_id is None or fdc_id <= 0:
            raise ValueError(f"Invalid FDC ID: {fdc_id}")

        cache_key = f"food:{fdc_id}"
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        url = f"{BASE}/foods/{fdc_id}"
        params = {"api_key": self.api_key}

        r = self.client.get(url, params=params)

        if r.status_code == 404:
            raise ValueError(f"USDA: Food with FDC ID {fdc_id} not found.")

        try:
            r.raise_for_status()
        except Exception:
            raise RuntimeError(f"USDA get_food failed: {r.text}")

        data = r.json()

        if not isinstance(data, dict):
            raise RuntimeError(f"USDA returned unexpected data format for {fdc_id}")

        self._cache_set(cache_key, data)
        return data
