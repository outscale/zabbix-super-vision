import time
from datetime import datetime, timedelta
from typing import List

from async_lru import alru_cache

from schemas.alerts import Event, Trigger
from schemas.zabbix_client import ZabbixClient
from settings import settings
from utils import time_since_event
from utils.hostgroups import get_hostgroup_color, get_hostgroups
from utils.log import logger


@alru_cache
async def get_problems(zabbix_client: ZabbixClient, ttl_hash=None) -> List[dict]:
    problems = []
    limit = settings.ZABBIX_API_LIMIT
    groups = [group.lower() for group in await get_hostgroups(zabbix_client)]
    team_list = [team for teams in settings.TEAMS.values() for team in teams]

    groupids = await get_group_ids(zabbix_client, team_list)
    trigger_data = await get_triggers(zabbix_client, limit, groupids)
    triggers = [Trigger.parse_obj(trigger) for trigger in trigger_data]

    # Getting events
    event_ids = [trigger.lastEvent.eventid for trigger in triggers]
    request_event = {
        "eventids": event_ids,
        "select_acknowledges": "extend",
        "select_related_users": "extend",
    }
    events: List[Event] = (await zabbix_client.call(request=request_event, method="event.get"))['result']

    for trigger in triggers:
        if trigger.hosts:
            for group in trigger.groups:
                if int(group.groupid) in groupids:
                    problems += await process_trigger_data(zabbix_client, trigger, events, group.name, groups)

            for tag in trigger.tags:
                if tag.value.lower() in groups:
                    problems += await process_trigger_data(zabbix_client, trigger, events, tag.value, groups)

    logger.info(f"[INFO] - {datetime.now()}: Refresh...")
    return problems


async def get_group_ids(zabbix_client, team_list):
    groupids = []
    for hostgroup_name in team_list:
        request = {
            "output": "extend",
            "search": {"name": hostgroup_name},
            "searchWildcardsEnabled": 1,
        }
        response = (await zabbix_client.call(request=request, method="hostgroup.get"))[
            "result"
        ]
        groupids.extend(int(group["groupid"]) for group in response)
    return groupids


async def get_triggers(zabbix_client, limit, groupids):
    request = {
        "limit": limit,
        "groupids": groupids,
        "monitored": 1,
        "maintenance": False,
        "active": 1,
        "min_severity": settings.SEVERITY,
        "output": "extend",
        "expandData": 1,
        "selectHosts": "extend",
        "selectGroups": "extend",
        "expandDescription": 1,
        "only_true": 1,
        "skipDependent": 1,
        "withUnacknowledgedEvents": 1,
        "withLastEventUnacknowledged": 1,
        "selectTags": "extend",
        "filter": {"value": 1},
        "sortfield": ["priority", "lastchange"],
        "sortorder": ["DESC"],
        "output": "extend",
        "selectLastEvent": "extend"
    }
    return (await zabbix_client.call(request=request, method="trigger.get"))["result"]


async def process_trigger_data(
    zabbix_client: ZabbixClient, trigger: Trigger, events: List[Event], hostgroup_name: str, groups: List[str]
) -> List[dict]:
    color = get_hostgroup_color(hostgroup_name)
    time_difference = int(time.time()) - int(trigger.lastchange)
    event_time = datetime.fromtimestamp(time.time()) - timedelta(
        seconds=time_difference
    )
    since = time_since_event(event_time)
    event_data = next((event for event in events if event["eventid"] == trigger.lastEvent.eventid), None)
    if event_data:
        try:
            username = event_data.get("acknowledges")[0].get("alias")
            message = event_data.get("acknowledges")[0].get("message")
        except IndexError:
            username = None
            message = None
    else:
        username = None
        message = None
    return [
        {
            "description": trigger.description,
            "host": trigger.hosts[0].host,
            "priority": trigger.priority,
            "triggerid": trigger.triggerid,
            "since": since,
            "hostgroup": hostgroup_name,
            "color": color,
            "lastchange": trigger.lastchange,
            "url": trigger.url,
            "acknowledge": {
                "username": username,
                "message": message,
            }
        }
    ]
