from fastapi import FastAPI, HTTPException
from enum import Enum
from contextlib import asynccontextmanager
from app.db import init_journal_store, get_entry, upsert_entry, list_entries
from pydantic import BaseModel

class EntryUpdate(BaseModel):
    content: str

class EntryType(str, Enum):
    JOURNAL = "journal"
    STUDY = "study"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_journal_store()
    yield

app = FastAPI(lifespan = lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/entries/{user_id}/{entry_date}/{entry_type}")
def return_entry(user_id: str, entry_date: str, entry_type: EntryType):
    entry = get_entry(user_id, entry_date, entry_type.value)
    if entry is None:
        raise HTTPException(status_code = 404, detail = "Entry not found")
    return entry


@app.put("/entries/{user_id}/{entry_date}/{entry_type}")
def insert_entry(user_id: str, entry_date: str, entry_type: EntryType, payload: EntryUpdate):
    entry = upsert_entry(user_id, entry_date, entry_type.value, payload.content)
    return entry

@app.get("/entries/{user_id}")
def get_entries(user_id: str, start: str | None = None, end: str | None = None, entry_type: EntryType | None = None):
    entries = list_entries(user_id, start, end, entry_type.value if entry_type else None)
    return entries
