import json
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, UploadFile

router = APIRouter(
    prefix="/parser",
    tags=["parser"]
)


class ConnectionManager:
    def __init__(self):
        self.client_connections: dict[str, WebSocket] = {}
        self.client_stahes: dict[str, str] = {}

        # TODO: for file uploads to be handled.
        # Start a separate process to handle file parsing for each client.
        self.client_documents: dict[str, str] = {}

    async def connect(self,
                      websocket: WebSocket,
                      client_id: str,
                      stash_id: str
                      ):
        await websocket.accept()
        # Since headers cannot be sent, the first message into the websocket
        # will be the headers.
        _headers_text = await websocket.receive_text()
        _headers: dict = json.loads(_headers_text)
        _some_header = _headers.get(
            'Some-Header', 'Default header information.')

        try:
            print(_some_header)
            self.client_connections[client_id] = websocket
            self.client_stahes[client_id] = stash_id

            print(self.client_connections)
            print(self.client_stahes)

        except Exception as e:
            await websocket.send_text('Unauthorized connection.')
            await websocket.close()
            raise WebSocketDisconnect

    def disconnect(self, client_id: str):
        self.client_connections.pop(client_id)
        self.client_stahes.pop(client_id)

    async def send_client_message(self, client_id: str, message: dict):
        print('Sending message to client.')
        websocket = self.client_connections.get(client_id, None)
        if websocket:
            await websocket.send_json(message)
        else:
            print('Client not connected.')
        print('Message sent.')


connection_manager = ConnectionManager()


@router.websocket("/{client_id}/{stash_id}")
async def trigger_endpoint(
    websocket: WebSocket,
    client_id: str = 'asdasdasd',
    stash_id: str = 'sososo_id',
    # file: UploadFile = None,
):
    try:
        query_params = websocket.query_params
        await connection_manager.connect(websocket, client_id, stash_id)
        print('Connected')
        await connection_manager.send_client_message(
            client_id, {"message": "Hello, World!"})
        while True:
            print('Message sent. and Waiting for message.')
            data = await websocket.receive_text()
            print(data)
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)
