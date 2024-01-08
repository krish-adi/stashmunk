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
            CREATE TABLE documents_{_new_stash_id} (
                id UUID NOT NULL PRIMARY KEY,   
                source_type TEXT,
                metadata JSONB,
                created_at TIMESTAMPTZ DEFAULT timezone ('utc', now()) NOT NULL
            );
            """
            _query_3 = f"""
            CREATE TABLE nodes_{_new_stash_id} (
                id UUID NOT NULL PRIMARY KEY,
                doc_id UUID REFERENCES documents_{_new_stash_id}(id),
                type TEXT,
                text TEXT,
                metadata JSONB,
                parent UUID,
                children UUID[],
                level INTEGER,
                filter BOOLEAN,
                summary TEXT,
                branch_summary TEXT,
                text_embedding vector(1536),
                summary_embedding vector(1536),
                branch_embedding vector(1536),
                created_at TIMESTAMPTZ DEFAULT timezone ('utc', now()) NOT NULL
            );
            """
            # Multimodal images nodes, references the node. If audio, node could have
            # parent, children root, and the aduio_stasg will contain it's actual source
            # in a bucket, this table could just have the embedding, bucket_link & metadata.
            # _query_3_I = f"""
            # CREATE TABLE images_{_new_stash_id} (
            #     id UUID NOT NULL PRIMARY KEY REFERENCES nodes_{_new_stash_id}(id),
            #     doc_id UUID REFERENCES documents_{_new_stash_id}(id),
            #     ... filestore_id, embedding, metadata, etc
            #     created_at TIMESTAMPTZ DEFAULT timezone ('utc', now()) NOT NULL
            # );
            # """
            # If id == doc_id then it is the complete file, if not then it points to a node
            _query_4 = f"""
            CREATE TABLE filestore_{_new_stash_id} (
                id UUID NOT NULL PRIMARY KEY,
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
            # TODO: check if the table is created
            await acur.execute(_query_4)

            # Make the changes to the database persistent
            await aconn.commit()

    return {'id': str(_new_stash['id']), 'name': name}
