import time
from typing import Dict, List, Optional

from pydantic import BaseModel

from settings import settings
from utils import read_json_file, write_json_file


class Note(BaseModel):
    name: str
    msg: str
    url: Optional[str] = None
    lvl: str
    team: str
    save: Optional[bool] = None
    ts: Optional[int] = None


class NoteManager:
    def __init__(self):
        self.file_path = f"{settings.DATA_DIR}/{settings.NOTES_JSON}"

    async def add_note(self, note: Note) -> None:
        note.ts = int(time.time())
        new_note = {note.ts: [note.dict()]}

        existing_data = await self.read_file()
        existing_data.update(new_note)
        await self.write_file(existing_data)

    async def delete_note(self, note_id: str) -> None:
        data = await self.read_file()
        if note_id in data:
            del data[note_id]
            await self.write_file(data)

    async def display_notes(self, teams: Optional[str]) -> List[Note]:
        notes_data = await self.read_file()
        return [
            Note(**note)
            for _, notes in notes_data.items()
            for note in notes
            if note["team"] in [teams, "all"]
        ]

    async def read_file(self) -> Dict:
        return await read_json_file(self.file_path)

    async def write_file(self, data: Note) -> None:
        await write_json_file(self.file_path, data)
