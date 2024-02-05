from typing import Optional

from fastapi import Form
from fastapi.responses import RedirectResponse

from schemas.notes import Note, NoteManager
from super_server import app


@app.post("/post")
async def post_note(
    name: str = Form(...),
    msg: str = Form(...),
    url: Optional[str] = Form(None),
    lvl: str = Form(...),
    team: str = Form(...),
    save: Optional[str] = Form(None),
):
    note = Note(name=name, msg=msg, url=url, lvl=lvl, team=team, save=save)
    await NoteManager().add_note(note)
    return RedirectResponse(url="/", status_code=303)


@app.post("/del")
async def del_note(
    note_id: Optional[str] = Form(None), url: Optional[str] = Form(None)
):
    await NoteManager().delete_note(note_id)
    return RedirectResponse(url="/", status_code=303)
