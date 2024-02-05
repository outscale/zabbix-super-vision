from typing import Dict

from pydantic import BaseModel, Field, RootModel


class ZabbixServer(BaseModel):
    ip: str
    port: int


ServerStatuses = RootModel[Dict[str, bool]]


class HostGroupRequest(BaseModel):
    output: str = "extend"
    search: dict = Field(default_factory=lambda: {"name": ""})
    searchWildcardsEnabled: bool = Field(default=True, alias="searchWildcardsEnabled")
