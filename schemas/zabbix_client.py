import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from settings import settings


import aiohttp

from utils.log import logger


@dataclass
class ZabbixConfig:
    api_url: str
    user: str
    password: str


class ZabbixApiNotResponding(Exception):
    pass

async def on_request_start(session, trace_config_ctx, params):
    trace_config_ctx.start = asyncio.get_event_loop().time()


async def on_request_end(session, trace_config_ctx, params):
    request_duration = asyncio.get_event_loop().time() - trace_config_ctx.start
    if request_duration > 1:
        logger.info(f"Request took {request_duration:.2f} seconds")


class ZabbixClient:
    _instance = None

    def __init__(self, config: ZabbixConfig):
        self.config = config
        self.token: Optional[str] = None
        self.trace_config = aiohttp.TraceConfig()
        self.trace_config.on_request_start.append(on_request_start)
        self.trace_config.on_request_end.append(on_request_end)

    async def login(self) -> None:
        payload = self._construct_payload(
            "user.login", {"user": self.config.user, "password": self.config.password}
        )
        response_data = await self._send_request(payload)
        self.token = response_data.get("result")

    def is_logged_in(self) -> bool:
        return bool(self.token)

    async def call(self, request: Dict[str, Any], method: str) -> Any:
        if not self.token:
            await self.login()

        payload = self._construct_payload(method, request, auth=self.token)
        return await self._send_request(payload)

    def _construct_payload(
        self, method: str, params: Dict[str, Any], auth: Optional[str] = None
    ) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "auth": auth,
            "id": 1,
        }

    async def _send_request(self, payload: Dict[str, Any]) -> Any:
        timeout = aiohttp.ClientTimeout(total=settings.ZABBIX_API_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout, trace_configs=[self.trace_config]) as session:
            for attempt in range(settings.ZABBIX_API_RETRY):
                try:
                    async with session.post(
                        f"{self.config.api_url}/api_jsonrpc.php", json=payload
                    ) as response:
                        if response.status == 200:
                            ret = await response.json()
                            ret["success"] = True
                            return ret
                        else:
                            raise Exception(f"HTTP Error: {response.status}")
                except Exception as e:
                    logger.error(f"[ERR] - {datetime.now()} Retry #{attempt + 1}: {e}")
                    await asyncio.sleep(attempt + 1)
                else:
                    break
            else:
                logger.error(
                    f"Failed after {settings.ZABBIX_API_RETRY} retries. Last method attempted: '{payload['method']}'."
                )
                raise ZabbixApiNotResponding("The Zabbix API is not respoding")
