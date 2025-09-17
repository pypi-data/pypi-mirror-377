import logging
import aiohttp
from datetime import datetime
from xecution.models.config import RuntimeConfig
from xecution.models.topic import DataTopic
from xecution.common.datasource_constants import RexilionConstants
from typing import Optional

class RexilionClient:
    """
    Calls endpoints like:
      /v1/btc/market-data/coinbase-premium-gap
    Only supports window & limit. No datetime/start_time parsing, no sorting.
    """
    def __init__(self, config: RuntimeConfig, data_map: dict):
        self.config   = config
        self.data_map = data_map
        self.headers  = {
            "X-API-Key": f"{self.config.rexilion_api_key}", 
        }

    async def fetch_all(
        self,
        data_topic: DataTopic,
        limit: Optional[int] = None,
    ):
        """
        - If `limit` is provided (and >0), use it.
        - Otherwise, use `self.config.data_count`.
        Returns the raw list (no transforms) and stores it in data_map[data_topic].
        """
        if '?' in data_topic.url:
            path, qs = data_topic.url.split('?', 1)
            base_params = dict(part.split('=', 1) for part in qs.split('&') if '=' in part)
        else:
            path = data_topic.url
            base_params = {}

        # decide limit
        effective_limit = limit if (isinstance(limit, int) and limit > 0) else self.config.data_count

        url = RexilionConstants.BASE_URL + path
        params = {**base_params, "limit": effective_limit}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers, timeout=50) as resp:
                    resp.raise_for_status()
                    raw = await resp.json()
        except Exception as e:
            logging.error(f"[{datetime.now()}] Error fetching {url} {params}: {e}")
            self.data_map[data_topic] = []
            return []

        # Accept either a plain list or {result:{data:[...]}} shapes.
        result = raw.get("result", raw) if isinstance(raw, dict) else raw
        data   = result.get("data") if isinstance(result, dict) else result
        items  = data if isinstance(data, list) else ([data] if data is not None else [])

        self.data_map[data_topic] = items
        return items

