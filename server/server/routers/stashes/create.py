from fastapi import APIRouter, Depends
from server import stashgres_client
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

router = APIRouter()


@router.post("/create", response_model=dict)
async def create_stash(name: str = 'my_stash_one'):
    async with await psycopg.AsyncConnection.connect(stashgres_client.kv) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:
            _query_1 = "INSERT INTO stashes (name, metadata) VALUES (%s, %s) RETURNING *;"
            _values_1 = [name, Jsonb({"foo": ["bar", 42]})]

            await acur.execute(_query_1, _values_1)
            _new_stash = await acur.fetchone()
            _new_stash_id = str(_new_stash['id']).replace('-', '_')

            # TODO: add a trigger to update the updated_at in stashes
            _query_2 = f"""
            CREATE TABLE knowledge_{_new_stash_id} (
                id UUID NOT NULL PRIMARY KEY,
                doc_id UUID,
                parent UUID,
                children UUID[],
                source TEXT,
                text TEXT,
                type TEXT,
                level INTEGER,
                summary TEXT,
                text_branch TEXT,
                summary_branch TEXT,
                embedding vector(1536),
                summary_embedding vector(1536),
                summary_branch_embedding vector(1536),
                metadata JSONB,
                created_at TIMESTAMPTZ DEFAULT timezone ('utc', now()) NOT NULL
            );
            """
            _query_3 = f"""
            CREATE TABLE filestore_{_new_stash_id} (
                id UUID NOT NULL PRIMARY KEY,
                node_id UUID,
                doc_id UUID,
                filename TEXT,
                filetype TEXT,
                filesize_mb FLOAT,
                bucket TEXT,
                metadata JSONB,
                created_at TIMESTAMPTZ DEFAULT timezone ('utc', now()) NOT NULL
            );
            """
            # TODO: check if the table is created
            await acur.execute(_query_2)
            # TODO: check if the table is created
            await acur.execute(_query_3)

            # Make the changes to the database persistent
            await aconn.commit()

    return {'id': _new_stash_id, 'name': name}
