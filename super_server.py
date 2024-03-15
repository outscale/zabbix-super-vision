import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from schemas.zabbix_client import ZabbixClient, ZabbixConfig
from settings import settings
from utils.background_tasks import check_servers
from utils.hostgroups import get_hostgroups

app = FastAPI()
zabbix_client: ZabbixClient = None

# Static Files
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")

templates = Jinja2Templates(directory="templates")


# Cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_zabbix_client() -> ZabbixClient:
    global zabbix_client
    config = ZabbixConfig(
        api_url=settings.ZABBIX_API_ENDPOINT,
        user=settings.ZABBIX_API_LOGIN,
        password=settings.ZABBIX_API_PASSWORD,
    )
    if zabbix_client and zabbix_client.is_logged_in():
        return zabbix_client
    else:
        client = ZabbixClient(config)
        await client.login()
        return client


async def check_teams_in_hostgroups():
    global zabbix_client
    zabbix_client = await get_zabbix_client()
    hostgroups = await get_hostgroups(zabbix_client)
    all_team_members = [
        member for members in settings.TEAMS.values() for member in members
    ]
    for member in all_team_members:
        if member not in hostgroups:
            raise Exception(f"The hostgroup '{member}' does not exist in Zabbix")


@app.on_event("startup")
async def on_startup():
    global background_task

    await check_teams_in_hostgroups()
    background_task = asyncio.create_task((check_servers()))


@app.on_event("shutdown")
async def on_shutdown():
    if background_task:
        background_task.cancel()
        await background_task


@app.get("/healthcheck")
async def health_check():
    return {"status": "online"}


from routes.alerts import *
from routes.notes import *
