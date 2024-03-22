import json
import asyncio
from io import BytesIO
from tempfile import SpooledTemporaryFile
from starlette.datastructures import Headers
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, UploadFile
from server.api_clients.unstructuredio import UnstructuredIOClient
from server.document import Document
from server.document.node.factories import unstructuredio_node_factory
from server.document.traversals import summarize_doc, embed_doc
from server import stashgres_client
from server.document.persist_stashgres import persist_to_stashgres

router = APIRouter(
    prefix="/parser",
    tags=["parser"]
)


class ParserManager:
    def __init__(self):
        self.client_connections: dict[str, WebSocket] = {}
        self.client_headers: dict[str, dict] = {}
        self.client_stahes: dict[str, str] = {}

        # TODO: for file uploads to be handled.
        # Start a separate process to handle file parsing for each client.
        self.client_documents: dict[str, str] = {}

        self.uns_api = UnstructuredIOClient()

    async def connect(self,
                      websocket: WebSocket,
                      client_id: str,
                      stash_id: str
                      ):

        try:
            await websocket.accept()
            # Since headers cannot be sent, the first message into the websocket
            # will be the headers.
            _client_headers_text = await websocket.receive_text()
            _client_headers: dict = json.loads(_client_headers_text)

            self.client_connections[client_id] = websocket
            self.client_headers[client_id] = _client_headers
            self.client_stahes[client_id] = stash_id
            await websocket.send_json({
                "status": "200",
                "message": "connected to the server.",
            })

        except Exception as e:
            await websocket.send_json({
                "status": "400",
                "message": "Bad request.",
            })
            await websocket.close()
            raise WebSocketDisconnect

    async def recieve_client_file(self, websocket: WebSocket, client_id: str):
        _fileheaders_text = await websocket.receive_text()
        _fileheaders: dict = json.loads(_fileheaders_text)

        # Receive text or file (bytes)
        max_file_size = 1024 * 1024
        tempfile = SpooledTemporaryFile(max_size=max_file_size)
        # tempfile.write(await websocket.receive_bytes())
        bytes = await websocket.receive_bytes()
        bytes_io = BytesIO(bytes)
        file = UploadFile(
            # file=tempfile,  # type: ignore[arg-type]
            file=bytes_io,
            size=0,
            filename=_fileheaders['file_name'],
            headers=Headers(raw=[(str.encode(_h[0]), str.encode(_h[1]))
                            for _h in _fileheaders['file_headers']]),
        )
        # await file.write(await websocket.receive_bytes())

        print(f"File received: {file.filename}")
        print(f"File size: {file.size}")
        print(f"File content type: {file.content_type}")
        print(f"File headers: {file.headers.items()}")

        # Send a confirmation or the file back
        await websocket.send_json({
            "status": "200",
            "message": "File received successfully.",
        })

        return bytes

    async def process_client_file(self, websocket: WebSocket, client_id: str, file: bytes):
        print(f'Processing file. {client_id}')
        _node_data = self.uns_api.request(
            files={'files': ('test.pdf', file)})
        _doc = Document(
            node_data=_node_data,
            node_factory=unstructuredio_node_factory,
            source_type='pdf',
            metadata={
                'filename': 'test.pdf',
            })
        print('performing summarization')
        await _doc.atraverse_and_apply(summarize_doc, direction='leaf', parallel=True)
        print('performing embedding')
        await _doc.atraverse_and_apply(embed_doc, direction='leaf', parallel=True)
        print('persisting to stashgres')
        with open('/Users/adithya/projects/stashmunk-org/stashmunk/storage/test.json', 'w') as f:
            json.dump(_doc.dump(), f, indent=4)
        await persist_to_stashgres(stashgres_client=stashgres_client, stash_name=self.client_stahes[client_id], document=_doc)
        file_data = {
            "status": "200",
            "message": "File processed successfully.",
        }
        await websocket.send_json(file_data)
        print(f'Processed file. {client_id}')

    async def send_client_message(self, client_id: str, message: dict):
        print('Sending message to client.')
        websocket = self.client_connections.get(client_id, None)
        if websocket:
            await websocket.send_json(message)
        else:
            print('Client not connected.')
        print('Message sent.')

    def disconnect(self, client_id: str):
        self.client_connections.pop(client_id)
        self.client_stahes.pop(client_id)


parser_manager = ParserManager()


@router.websocket("/{client_id}/{stash_id}")
async def parser_endpoint(
    websocket: WebSocket,
    client_id: str = 'asdasdasd',
    stash_id: str = 'sososo_id'
):
    try:
        query_params = websocket.query_params
        await parser_manager.connect(websocket, client_id, stash_id)
        file = await parser_manager.recieve_client_file(websocket, client_id)
        await parser_manager.process_client_file(websocket, client_id, file=file)
        # await parser_manager.send_client_message(
        #     client_id,
        #     {
        #         "message": "Hello, World!",
        #     })
        # while True:
        #     data = await websocket.receive_text()
        #     print(f"Data received: {data}")
        parser_manager.disconnect(client_id)
    except WebSocketDisconnect:
        parser_manager.disconnect(client_id)
