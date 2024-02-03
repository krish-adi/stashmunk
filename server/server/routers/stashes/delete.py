from fastapi import APIRouter, Depends
from server import stashgres_client
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

router = APIRouter()


@router.delete("/delete", response_model=dict)
async def delete_stash(name: str = 'my_stash_one'):
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

            _del_stash = _stashes[0]
            _query_2 = "DELETE FROM stashes WHERE id = %s;"
            _values_2 = [_del_stash['id']]
            await acur.execute(_query_2, _values_2)

            _del_stash_id = str(_del_stash['id']).replace('-', '_')
            # TODO: create a stored function on trigger
            _query_3 = f"DROP TABLE documents_{_del_stash_id};"
            _query_3_N = f"DROP TABLE nodes_{_del_stash_id};"
            _query_3_I = f"DROP TABLE images_{_del_stash_id};"
            _query_3_A = f"DROP TABLE audio_{_del_stash_id};"
            _query_4 = f"DROP TABLE filestore_{_del_stash_id};"
            # TODO: check if the following tables are dropped            
            await acur.execute(_query_3)
            await acur.execute(_query_3_N)
            await acur.execute(_query_3_I)
            await acur.execute(_query_3_A)
            await acur.execute(_query_4)

            # Make the changes to the database persistent
            await aconn.commit()

    return _del_stash
