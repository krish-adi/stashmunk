import json
import websockets
from websockets.client import WebSocketClientProtocol
from fastapi import UploadFile
from server.http_exceptions import BadRequestHttpException, ServerLimitHttpException, UnauthorizedHttpException


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

    async def run(self, client_id: str, stash_id: str, file: UploadFile) -> dict:
        _ws_client_url = f"ws{'s' if self._ssl else ''}://{self._host}/{self._route}/{client_id}/{stash_id}"
        try:
            async with websockets.connect(_ws_client_url) as websocket:
                # Step 01: Send client headers
                client_headers = {
                    "Some-Header": f"Client deader info goes here."}
                await websocket.send(json.dumps(client_headers))
                _data_1 = json.loads(await websocket.recv())
                if int(_data_1['status']) == 200:
                    print(_data_1['message'])
                elif int(_data_1['status']) == 403:
                    print(_data_1['message'])
                    raise UnauthorizedHttpException
                elif int(_data_1['status']) == 400:
                    print(_data_1['message'])
                    raise BadRequestHttpException

                # Step 02: Send the file
                await self.send_file(websocket, file)
                _data_2 = json.loads(await websocket.recv())
                if int(_data_2['status']) == 200:
                    print(_data_2['message'])
                elif int(_data_2['status']) == 403:
                    print(_data_2['message'])
                    raise UnauthorizedHttpException
                elif int(_data_2['status']) == 400:
                    print(_data_2['message'])
                    raise BadRequestHttpException

                # Step 03: Get the processed response
                _data_3 = json.loads(await websocket.recv())
                if int(_data_3['status']) == 200:
                    print(_data_3['message'])
                    return _data_3['message']
                elif int(_data_3['status']) == 403:
                    print(_data_3['message'])
                    raise UnauthorizedHttpException
                elif int(_data_3['status']) == 400:
                    print(_data_3['message'])
                    raise BadRequestHttpException

                # while True:
                #     _r = await websocket.recv()
                #     try:
                #         _data = json.loads(_r)
                #     except:
                #         raise ValueError

                print('Connection closed.')
                websocket.close()

        except websockets.exceptions.ConnectionClosedError as e:
            print(e)
            raise BadRequestHttpException
        except Exception as e:
            print(e)
            raise ServerLimitHttpException


parser_client = WorkerClient(name="parser")
