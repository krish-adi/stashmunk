import json
from tempfile import SpooledTemporaryFile
from starlette.datastructures import Headers
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, UploadFile

router = APIRouter(
    prefix="/parser",
    tags=["parser"]
)


class ConnectionManager:
    def __init__(self):
        self.client_connections: dict[str, WebSocket] = {}
        self.client_headers: dict[str, dict] = {}
        self.client_stahes: dict[str, str] = {}

        # TODO: for file uploads to be handled.
        # Start a separate process to handle file parsing for each client.
        self.client_documents: dict[str, str] = {}

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
            await websocket.send_text('Unauthorized connection.')
            await websocket.close()
            raise WebSocketDisconnect

    async def recieve_client_file(self, websocket: WebSocket):
        while True:
            _fileheaders_text = await websocket.receive_text()
            _fileheaders: dict = json.loads(_fileheaders_text)
            print(_fileheaders)
            # Receive text or file (bytes)
            max_file_size = 1024 * 1024
            tempfile = SpooledTemporaryFile(max_size=max_file_size)
            file = UploadFile(
                file=tempfile,  # type: ignore[arg-type]
                size=0,
                filename=_fileheaders['file_name'],
                headers=Headers(raw=[(str.encode(_h[0]), str.encode(_h[1]))
                                for _h in _fileheaders['file_headers']]),
            )
            await file.write(await websocket.receive_bytes())

            print(f"File received: {file.filename}")
            print(f"File size: {file.size}")
            print(f"File content type: {file.content_type}")
            print(f"File headers: {file.headers.items()}")

            # Send a confirmation or the file back
            await websocket.send_json({
                "status": "200",
                "message": "file received successfully.",
            })

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


connection_manager = ConnectionManager()


@router.websocket("/{client_id}/{stash_id}")
async def parser_endpoint(
    websocket: WebSocket,
    client_id: str = 'asdasdasd',
    stash_id: str = 'sososo_id'
):
    try:
        query_params = websocket.query_params
        await connection_manager.connect(websocket, client_id, stash_id)
        await connection_manager.recieve_client_file(websocket)
        await connection_manager.send_client_message(
            client_id,
            {
                "message": "Hello, World!",
            })
        while True:
            data = await websocket.receive_text()
            print(f"Data received: {data}")
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)
