import uuid
import json
from uuid import uuid4
from dataclasses import asdict
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from fastapi import APIRouter, Depends, UploadFile
from server import stashgres_client
from server.document import Document, Node
from server.types.stash import Stash
from server.workers.parser.client import parser_client
import websockets

router = APIRouter()


@router.post("/add", response_model=dict)
# async def add_knowledge(stash: Stash, file: UploadFile):
async def add_knowledge(file: UploadFile):
    async with await psycopg.AsyncConnection.connect(stashgres_client.kv) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:

            # Get the stash id
            _query_stash = """
            SELECT id FROM stashes WHERE name = %s;
            """
            # _values_1 = [stash.name]
            _values_1 = ['my_stash_one']
            await acur.execute(_query_stash, _values_1)
            stash_id = await acur.fetchone()
            _insert_stash_id = str(stash_id['id']).replace('-', '_')

            _client_id = str(uuid4())

            # Send the file to the parser

            _parser_response = await parser_client.run(
                client_id=_client_id,
                stash_id=_insert_stash_id,
                file=file
            )

            print({'client_id': _client_id, 'stash_id': _insert_stash_id,
                  'parser_response': _parser_response})

            return {'client_id': _client_id, 'stash_id': _insert_stash_id, 'parser_response': _parser_response}

    #         # # insert the document
    #         # _ldoc: Document = Document.from_file('test_doc_dump.json')
    #         # TODO: Status of each node, stash-documents-metadata- embedding model, llm model, image model, embed dim, and so on.
    #         # _query_1 = f"""
    #         # INSERT INTO documents_{_insert_stash_id} (id, source_type, metadata) VALUES (%s, %s, %s);
    #         # """
    #         # _values_1 = [
    #         #     uuid.UUID(_ldoc.id, version=4),
    #         #     _ldoc.source_type,
    #         #     Jsonb(_ldoc.metadata),
    #         # ]
    #         # await acur.execute(_query_1, _values_1)

    #         # # insert nodes
    #         # _cols = '(id, doc_id, type, text, metadata, parent, children, level, filter, summary, branch_summary, text_embedding, summary_embedding, branch_embedding)'
    #         # async with acur.copy(f'COPY nodes_{_insert_stash_id} {_cols} FROM STDIN') as acopy:
    #         #     for node in _ldoc._node_list:
    #         #         _ndata = asdict(node)
    #         #         _write_data = (
    #         #             uuid.UUID(_ndata['id'], version=4),
    #         #             uuid.UUID(_ndata['doc_id'], version=4),
    #         #             _ndata['type'],
    #         #             _ndata['text'],
    #         #             Jsonb(_ndata['metadata']),
    #         #             uuid.UUID(
    #         #                 _ndata['parent'], version=4) if _ndata['parent'] is not None else None,
    #         #             [uuid.UUID(_c, version=4)
    #         #              for _c in _ndata['children']],
    #         #             _ndata['level'],
    #         #             _ndata['filter'],
    #         #             _ndata['summary'] if _ndata['summary'] is not None else None,
    #         #             _ndata['branch_summary'] if _ndata['branch_summary'] is not None else None,
    #         #             json.dumps(
    #         #                 _ndata['text_embedding']) if _ndata['text_embedding'] is not None else None,
    #         #             json.dumps(
    #         #                 _ndata['summary_embedding']) if _ndata['summary_embedding'] is not None else None,
    #         #             json.dumps(
    #         #                 _ndata['branch_embedding']) if _ndata['branch_embedding'] is not None else None,
    #         #         )
    #         #         await acopy.write_row(_write_data)

    #         # # Make the changes to the database persistent
    #         # await aconn.commit()
