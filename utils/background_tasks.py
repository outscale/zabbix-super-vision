import asyncio
import socket
from typing import Dict, Tuple

from schemas import ServerStatuses, ZabbixServer
from settings import settings
from utils import write_json_file
from utils.log import logger


def socket_connect(ip: str, port: int) -> int:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result
    except Exception as e:
        return -1  # or any other suitable error code


async def check_server(server: ZabbixServer) -> Tuple[str, bool]:
    try:
        result = await asyncio.to_thread(socket_connect, server.ip, server.port)
        if result == 0:
            logger.info(f"[INFO] - Port {server.port} OK: {server.ip}")
            return (server.ip, True)
        else:
            logger.info(f"[ERR] - Port {server.port} KO: {server.ip}")
            return (server.ip, False)
    except Exception as e:
        logger.info(f"[ERR] - Connection Failed: {server.ip}, Error: {e}")
        return (server.ip, False)


async def check_servers() -> None:
    while True:
        servers: Dict[str, bool] = {}
        tasks = [check_server(server) for server in settings.ZABBIX_SERVERS_CHECK]
        results_list = await asyncio.gather(*tasks)
        for ip, status in results_list:
            servers[ip] = status
        server_statuses = ServerStatuses(servers)
        await write_json_file(
            f"{settings.DATA_DIR}/{settings.ZABBIX_SERVERS_JSON}", server_statuses.root
        )
        await asyncio.sleep(60)
