import json
import click
import asyncio
import requests
import websockets
from websockets.client import WebSocketClientProtocol
from fastapi import UploadFile
from server.http_exceptions import BadRequestHttpException, ServerLimitHttpException


class WorkerClient:
    def __init__(self, name: str):
        self.name = name
        if name == "parser":
            self._host = "0.0.0.0:8001"
            self._ssl = False
            self._route = f"parser"

    async def send_file(self, ws: WebSocketClientProtocol, file: UploadFile) -> dict:
        await ws.send(json.dumps({
            'file_name': file.filename,
            'file_size': file.size,
            'file_content_type': file.content_type,
            'file_headers': file.headers.items(),
        }))
        await ws.send(file.file)
        _r = await ws.recv()
        _data = json.loads(_r)
        if _data['status'] == 200:
            print(_data['message'])

    async def run(self, client_id: str, stash_id: str, file: UploadFile) -> dict:
        _ws_client_url = f"ws{'s' if self._ssl else ''}://{self._host}/{self._route}/{client_id}/{stash_id}"
        try:
            async with websockets.connect(_ws_client_url) as websocket:
                client_headers = {
                    "Some-Header": f"Client deader info goes here."}
                await websocket.send(json.dumps(client_headers))
                _r_1 = await websocket.recv()
                _data = json.loads(_r_1)
                if _data['status'] == 200:
                    print(_data['message'])
                await self.send_file(websocket, file)

                while True:
                    _r = await websocket.recv()
                    try:
                        _data = json.loads(_r)
                    except:
                        _data = _r
                    if isinstance(_data, str) and _data == 'Unauthorized connection.':
                        raise Exception('Unable to run worker.')
                    if _data:
                        print('Data received. Returning.')
                        return _data
                    else:
                        continue
                    # Needn't close the connection within the context manager
                    # await websocket.close()
        except websockets.exceptions.ConnectionClosedError as e:
            print(e)
            raise BadRequestHttpException
        except Exception as e:
            print(e)
            raise ServerLimitHttpException


parser_client = WorkerClient(name="parser")
