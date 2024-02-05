import random
from typing import List

from schemas import HostGroupRequest
from schemas.zabbix_client import ZabbixClient
from settings import settings


def get_hostgroup_color(hostgroup: str):
    color = settings.COLOR_TEAM.get(hostgroup)
    if color is None:
        color = f"#{random.randint(0, 0xFFFFFF):06x};"
        settings.COLOR_TEAM[hostgroup] = color
    return color


async def get_hostgroups(zabbix_client: ZabbixClient) -> List[str]:
    groups = []
    for hg in [team for teams in settings.TEAMS.values() for team in teams]:
        request = HostGroupRequest(search={"name": hg})
        resp = await zabbix_client.call(
            request=request.model_dump(), method="hostgroup.get"
        )
        # Process response
        for item in resp["result"]:
            groups.append(item["name"])
    return groups
