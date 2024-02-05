import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict

import aiofiles
import aiofiles.os as async_os


async def write_json_file(file_path: str, data: Any) -> None:
    await async_os.makedirs(os.path.dirname(file_path), exist_ok=True)
    json_data = json.dumps(data, indent=4)
    async with aiofiles.open(file_path, mode="w") as file:
        await file.write(json_data)


async def read_json_file(filepath: str) -> Dict[str, Any]:
    try:
        async with aiofiles.open(filepath, "r") as file:
            content = await file.read()
            return json.loads(content)
    except FileNotFoundError:
        return {}


def time_since_event(event_time: datetime) -> str:
    now: datetime = datetime.now()
    time_difference: timedelta = now - event_time
    days: int = time_difference.days
    seconds: int = time_difference.seconds

    if days > 0:
        return f"{days} day(s)"

    hours: int = seconds // 3600
    if hours > 0:
        return f"{hours} hour(s)"

    minutes: int = (seconds % 3600) // 60
    if minutes > 0:
        return f"{minutes} minute(s)"

    return f"{seconds} second(s)"
