import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import yaml
from pathlib import Path

import aiohttp
from pydantic import BaseModel, Field, validator
from dataclasses import dataclass

from dram_sentry.config.settings import settings

logger = logging.getLogger(__name__)

class DRAMPrice(BaseModel):
    """Structured representation of DRAM pricing data."""
    supplier: str = "DRAMeXchange"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    price_usd_gb: float
    part_number: str
    capacity_gb: int = Field(..., gt=0)
    supplier_specific_id: str
    source_url: str = ""

    @validator('capacity_gb')
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError("Capacity must be positive")
        return v

class DRAMeXchangeClient:
    """Async client for DRAMeXchange API with proper resource management."""

    BASE_URL = "https://api.dramexchange.com/v1"
    DEFAULT_TIMEOUT = 10
    USER_AGENT = "dram-sentry/1.0"

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        session: Optional[aiohttp.ClientSession] = None
    ):
        self.api_key = api_key or settings.dramexchange_api_key
        self.timeout = timeout
        self.session = session
        self.headers = {
            "Accept": "application/json",
            "User-Agent": self.USER_AGENT,
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    async def __aenter__(self):
        """Initialize client session in async context."""
        self.session = self.session or aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up client session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generic API request handler with error handling."""
        if not self.session:
            raise RuntimeError("Client session not initialized")

        url = f"{self.BASE_URL}/{endpoint}"
        try:
            async with self.session.get(url, params=params, timeout=self.timeout) as resp:
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as e:
            logger.error(f"DRAMeXchange API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in DRAMeXchange request: {e}")
            raise

    async def fetch_spot_prices(self) -> Dict[str, Any]:
        """Fetch raw spot price data from API."""
        return await self._request("spot-prices")

    async def extract_price_records(self) -> List[DRAMPrice]:
        """Convert raw API response to structured price records."""
        raw_data = await self.fetch_spot_prices()
        records = []

        # Handle different response formats gracefully
        items = raw_data.get("prices", raw_data.get("data", {}).get("items", []))

        for item in items:
            try:
                price = DRAMPrice(
                    price_usd_gb=float(item["price"]),
                    part_number=str(item.get("part_number", "")),
                    capacity_gb=int(str(item.get("capacity", "0")).replace("GB", "")),
                    supplier_specific_id=str(item.get("id", "")),
                    source_url=str(item.get("source", "")),
                )
                records.append(price)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Skipping malformed DRAMeXchange record: {e}")
                continue

        logger.info(f"Extracted {len(records)} valid price records")
        return records

async def poll_dramexchange_once() -> List[DRAMPrice]:
    """Single polling operation that returns structured price data."""
    async with DRAMeXchangeClient() as client:
        return await client.extract_price_records()

async def run_poller(interval_minutes: int = 5, config_path: str = None):
    """
    Continuous polling service with proper error handling and logging.

    Args:
        interval_minutes: Polling interval in minutes
        config_path: Optional path to config file (defaults to settings)
    """
    while True:
        try:
            prices = await poll_dramexchange_once()

            # TODO: Integrate with message queue/timeseries DB
            for price in prices:
                logger.info(
                    f"DRAMeXchange price: ${price.price_usd_gb}/GB "
                    f"({price.part_number}, {price.capacity_gb}GB) "
                    f"at {price.timestamp.isoformat()}"
                )

            # Add cooldown if no prices were fetched
            if not prices:
                logger.warning("No prices fetched in this cycle")
                await asyncio.sleep(interval_minutes * 60)
                continue

        except Exception as e:
            logger.exception("DRAMeXchange poller failed in cycle")
            # Exponential backoff for transient failures
            await asyncio.sleep(min(60, interval_minutes * 60))

        await asyncio.sleep(interval_minutes * 60)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_poller())