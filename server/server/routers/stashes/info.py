from fastapi import APIRouter, Depends
from server import stashgres_client
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

router = APIRouter()


@router.get("/info", response_model=dict)
async def information_of_stash(name: str = 'my_stash_one'):
    async with await psycopg.AsyncConnection.connect(stashgres_client.kv) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:
            # Check if stash with name exists and return it's info:
            _query_1 = "SELECT * FROM stashes WHERE name = %s;"
            _values_1 = [name]
            await acur.execute(_query_1, _values_1)
            _stashes = await acur.fetchall()

            if len(_stashes) == 0:
                raise Exception('No stash found with the given name')
            elif len(_stashes) > 1:
                raise Exception('More than one stash found with the same name')
            else:
                _stash = _stashes[0]

    return _stash
