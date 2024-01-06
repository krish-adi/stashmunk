from fastapi import APIRouter, Depends
from server import stashgres_client
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

router = APIRouter()


@router.get("/list", response_model=list)
async def list_all_stashes():
    async with await psycopg.AsyncConnection.connect(stashgres_client.kv) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:
            _query_1 = "SELECT id, name FROM stashes;"
            await acur.execute(_query_1)
            _stashes = await acur.fetchall()

    return _stashes
