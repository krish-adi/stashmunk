from server.document.base import Document
from server.document.node.base import Node
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from server import StashgresClient
import uuid
from dataclasses import asdict
import json


async def persist_to_stashgres(stashgres_client: StashgresClient, stash_name: str, document: Document):
    async with await psycopg.AsyncConnection.connect(stashgres_client.kv) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:

            # Get the stash id
            _query_stash = """
                SELECT id FROM stashes WHERE name = %s;
                """
            # _values_1 = ['my_stash_one']
            _values_1 = [stash_name]
            await acur.execute(_query_stash, _values_1)
            stash_id = await acur.fetchone()
            _insert_stash_id = str(stash_id['id']).replace('-', '_')

            _query_1 = f"""
            INSERT INTO documents_{_insert_stash_id} (id, source_type, metadata) VALUES (%s, %s, %s);
            """
            _values_1 = [
                uuid.UUID(document.id, version=4),
                document.source_type,
                Jsonb(document.metadata),
            ]
            await acur.execute(_query_1, _values_1)

            # insert nodes
            _cols = '(id, doc_id, type, text, metadata, parent, children, level, filter, summary, branch_summary, text_embedding, summary_embedding, branch_embedding)'
            async with acur.copy(f'COPY nodes_{_insert_stash_id} {_cols} FROM STDIN') as acopy:
                for node in document._node_list:
                    _ndata = asdict(node)
                    _write_data = (
                        uuid.UUID(_ndata['id'], version=4),
                        uuid.UUID(_ndata['doc_id'], version=4),
                        _ndata['type'],
                        _ndata['text'],
                        Jsonb(_ndata['metadata']),
                        uuid.UUID(
                            _ndata['parent'], version=4) if _ndata['parent'] is not None else None,
                        [uuid.UUID(_c, version=4)
                         for _c in _ndata['children']],
                        _ndata['level'],
                        _ndata['filter'],
                        _ndata['summary'] if _ndata['summary'] is not None else None,
                        _ndata['branch_summary'] if _ndata['branch_summary'] is not None else None,
                        json.dumps(
                            _ndata['text_embedding']) if _ndata['text_embedding'] is not None else None,
                        json.dumps(
                            _ndata['summary_embedding']) if _ndata['summary_embedding'] is not None else None,
                        json.dumps(
                            _ndata['branch_embedding']) if _ndata['branch_embedding'] is not None else None,
                    )
                    await acopy.write_row(_write_data)

            # Make the changes to the database persistent
            await aconn.commit()
