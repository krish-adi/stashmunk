from uuid import uuid4
from fastapi import APIRouter, UploadFile
from server.types.stash import Stash
from server.workers.parser.client import parser_client


router = APIRouter()


@router.post("/add", response_model=dict)
# async def add_knowledge(stash: Stash, file: UploadFile):
async def add_knowledge(file: UploadFile):
    _parser_response = await parser_client.run(
        client_id=str(uuid4()),
        stash_id='my_stash_one',
        file=file
    )
    return {'status': '200', 'message': 'success', 'data': _parser_response}
