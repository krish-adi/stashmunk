import json
import click
import asyncio
import requests
import websockets
from websockets.client import WebSocketClientProtocol
from server.http_exceptions import BadRequestHttpException, ServerLimitHttpException


class WorkerClient:
    def __init__(self, name: str):
        self.name = name
        if name == "parser":
            self._host = "0.0.0.0:8001"
            self._ssl = False
            self._route = f"parser"

    async def run(self, client_id: str, stash_id: str) -> dict:
        _ws_client_url = f"ws{'s' if self._ssl else ''}://{self._host}/{self._route}/{client_id}/{stash_id}"
        try:
            async with websockets.connect(_ws_client_url) as websocket:
                headers_send = {"Some-Header": f"Header info goes here."}
                await websocket.send(json.dumps(headers_send))
                while True:
                    print('Waiting for response.')
                    _r = await websocket.recv()
                    print('Response received. Parsing.')
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
