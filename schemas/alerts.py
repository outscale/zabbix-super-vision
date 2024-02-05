from typing import List, Any, Dict, Union, Optional

from pydantic import BaseModel
from schemas.notes import Note

class Group(BaseModel):
    groupid: str
    name: str


class Host(BaseModel):
    host: str


class Tag(BaseModel):
    value: str


class Event(BaseModel):
    eventid: str
    source: str
    object: str
    objectid: str
    clock: str
    value: str
    acknowledged: str
    acknowledges: Optional[List[Any]] = []
    ns: str
    name: str
    severity: str


class Trigger(BaseModel):
    description: str
    priority: str
    triggerid: str
    lastchange: str
    hosts: List[Host]
    groups: List[Group]
    tags: List[Tag]
    url: str
    lastEvent: Event


class ContextModel(BaseModel):
    zabbix_url: str
    tv_mode: bool
    hostgroups: Optional[List[str]] = []
    check_servers: Optional[Dict] = {}
    alerts: Optional[List] = []
    total_alerts: Optional[int] = -1
    notes: Any
    request: Any
    notes: List[Note]
    teams: Union[List, Dict]
    accepted_latency: Optional[bool] = False
    config: Dict[str, Any]
    zabbix_available: bool
