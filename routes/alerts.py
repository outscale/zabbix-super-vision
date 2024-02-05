import time
import asyncio
from typing import List, Optional

from fastapi import Request

from schemas import ServerStatuses
from schemas.notes import NoteManager
from schemas.alerts import ContextModel
from schemas.zabbix_client import ZabbixApiNotResponding
from settings import settings
from super_server import app, get_zabbix_client, templates
from utils import read_json_file
from utils.hostgroups import get_hostgroups
from utils.log import logger
from utils.problems import get_problems

def get_ttl_hash(seconds=45):
    return round(time.time() / seconds)


async def display_alerts(
    request: Request,
    team: Optional[str] = None,
    tv_mode: bool = False,
):
    try:
        global zabbix_client
        zabbix_client = await get_zabbix_client()
        start = asyncio.get_event_loop().time()
        if team:
            team_list = team.lower().split("+")
        else:
            team_list = [team.lower() for team in (await get_hostgroups(zabbix_client))]

        problems = await get_problems(zabbix_client, ttl_hash=get_ttl_hash())
        problems = [
            problem for problem in problems if problem.get("hostgroup").lower() in team_list
        ]
        problems = sorted(
            problems, key=lambda i: (i["priority"], i["lastchange"]), reverse=True
        )
        logger.info("[NB ALERTS] - {}".format(len(problems)))
        content = await read_json_file(
            f"{settings.DATA_DIR}/{settings.ZABBIX_SERVERS_JSON}"
        )
        check_servers = ServerStatuses.model_validate(content).root
        request_duration = asyncio.get_event_loop().time() - start
        context = ContextModel(
            zabbix_available=True,
            zabbix_url=settings.ZABBIX_URL,
            tv_mode=tv_mode,
            hostgroups=await get_hostgroups(zabbix_client),
            check_servers=check_servers,
            alerts=problems,
            total_alerts=len(problems),
            notes=await NoteManager().display_notes(team),
            request=request,
            teams=settings.TEAMS,
            accepted_latency=request_duration < settings.ZABBIX_API_ACCEPTED_LATENCY,
            config={
                "ZABBIX_API_TIMEOUT": settings.ZABBIX_API_TIMEOUT,
                "ZABBIX_API_LIMIT": settings.ZABBIX_API_LIMIT,
                "MIN_SEVERITY": settings.SEVERITY,
                "ZABBIX_API_ACCEPTED_LATENCY": settings.ZABBIX_API_ACCEPTED_LATENCY,
            }
        )
        return templates.TemplateResponse("index.html", context.dict())
    except ZabbixApiNotResponding:
        context = ContextModel(
            zabbix_available=False,
            zabbix_url=settings.ZABBIX_URL,
            tv_mode=tv_mode,
            notes=await NoteManager().display_notes(team),
            request=request,
            teams=settings.TEAMS,
            accepted_latency=True, # Already showing the API is down
            config={
                "ZABBIX_API_TIMEOUT": settings.ZABBIX_API_TIMEOUT,
                "ZABBIX_API_LIMIT": settings.ZABBIX_API_LIMIT,
                "MIN_SEVERITY": settings.SEVERITY,
                "ZABBIX_API_ACCEPTED_LATENCY": settings.ZABBIX_API_ACCEPTED_LATENCY,
            }
        )
        return templates.TemplateResponse("index.html", context.dict())


@app.get("/tv")
async def display_alerts_tv_mode(
    request: Request,
):
    return await display_alerts(
        request,
        team=None,  # or a default team if applicable
        tv_mode=True,
    )


@app.get("/tv/{team}")
async def display_alerts_without_team(
    request: Request,
    team: str,
):
    return await display_alerts(
        request,
        team=team,
        tv_mode=True,
    )


@app.get("/{team}")
async def display_alerts_without_team(
    request: Request,
    team: str,
):
    return await display_alerts(
        request,
        team=team,
        tv_mode=False,
    )


@app.get("/")
async def display_alerts_with_team(
    request: Request,
):
    return await display_alerts(
        request,
        team=None,
        tv_mode=False,
    )