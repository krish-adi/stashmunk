from server.exceptions import ModelError
from typing import Dict, Optional, Tuple, Union
import aiohttp
import requests
import requests.adapters
import urllib.parse
import json
from server.settings import server_settings
from typing import Dict, Optional, Tuple, NamedTuple, Union
import aiohttp
import requests
import requests.adapters
import json
from time import time


class APIRequest(NamedTuple):
    method: str
    url: str
    headers: Optional[Dict[str, str]]
    data: bytes
    files: Optional[Dict[str, bytes]]
    stream: bool
    timeout: Optional[Union[float, Tuple[float, float]]]


def handle_request_error(status_code: int, content: str) -> None:
    try:
        formatted_content = json.loads(content)
    except json.decoder.JSONDecodeError:
        formatted_content = content

    status_code_messages = {
        403: "Unauthorized: Authententication error.",
        500: "The server had an error while processing your request.",
    }

    if isinstance(formatted_content, dict) and "error" in formatted_content:
        if formatted_content["error"]["message"] != "":
            _message = formatted_content["error"]["message"]
            raise ModelError(status_code, _message, "MODEL-API-ERROR")

    if status_code in status_code_messages:
        _message = status_code_messages[status_code]
    elif isinstance(formatted_content, str):
        _message = formatted_content
    else:
        _message = "An unknown error has occurred."

    raise ModelError(status_code, _message, "MODEL-API-ERROR")


class UnstructuredIOClient():
    def __init__(
        self,
        api_key: str = server_settings.unstructuredio_api_key,
        api_url: str = server_settings.unstructuredio_url,
        proxy_url: Optional[str] = None,
        request_timeout: Optional[Union[float,
                                        Tuple[float, float]]] = 600,
    ):
        self.api_key = api_key
        # self.api_url = api_url
        self.api_url = 'http://localhost:8080/general/v0/general'
        self.proxy_url = proxy_url
        self.request_timeout = request_timeout

        self._retries = 2
        self._session: Optional[requests.Session] = None

        self._setup_session()

    def _setup_session(self) -> requests.Session:
        self._session = requests.Session()
        if self.proxy_url:
            self._session.proxies = {"https": self.proxy_url}
        self._session.mount(
            "https://",
            requests.adapters.HTTPAdapter(
                max_retries=self._retries),
        )

    def _request_middleware(self, params: dict, files: dict) -> APIRequest:
        method = "post"
        abs_url = urllib.parse.urljoin(self.api_url, '')
        final_headers: dict[str, str] = {
            'accept': 'application/json',
            'unstructured-api-key': f'{self.api_key}'
        }

        data = None
        stream = None
        return APIRequest(
            method,
            abs_url,
            final_headers,
            data,
            files,
            stream,
            self.request_timeout,
        )

    def _response_middleware(self, response: Union[requests.Response, aiohttp.ClientResponse], content: str) -> dict:
        if isinstance(response, requests.Response):
            if response.status_code != 200:
                handle_request_error(response.status_code, content)

        if isinstance(response, aiohttp.ClientResponse):
            if response.status != 200:
                handle_request_error(response.status, content)

        return json.loads(content)

    def request(
        self,
        params: dict = None,
        files: dict = None
    ) -> dict:
        request = self._request_middleware(params, files)

        _try_count = 0
        _retry_error_log = []
        start_time = time()
        while (_try_count <= self._retries):
            try:
                _response: requests.Response = self._session.request(
                    request.method,
                    request.url,
                    headers=request.headers,
                    data=request.data,
                    stream=request.stream,
                    timeout=request.timeout,
                    files=request.files,
                )
                # content = _response.content.decode("utf-8")
                content = _response.content
                request_time = time() - start_time

                return self._response_middleware(_response, content)
            except Exception as e:
                _retry_error_log.append(e)
                _try_count += 1

        raise ValueError(f"Model failed to run.")

    async def arequest(
        self,
        params: dict,
        files: dict = None,  # TODO: implement in async
    ) -> dict:
        request = self._request_middleware(params, files)

        if files is not None:
            _data = aiohttp.FormData()
            for k, v in request.data.items():
                _data.add_field(k, str(v))
            for k, v in request.files.items():
                _data.add_field(k, v[1])
        else:
            _data = request.data
        async with aiohttp.ClientSession() as session:

            _try_count = 0
            _retry_error_log = []
            start_time = time()
            while (_try_count <= self._retries):
                try:
                    async with session.request(
                        request.method,
                        request.url,
                        headers=request.headers,
                        data=_data,
                        timeout=request.timeout,
                        proxy=self.proxy_url,
                    ) as _response:
                        # content = await _response.text()
                        content = await _response.read()
                        request_time = time() - start_time

                        return self._response_middleware(_response, content)
                except Exception as e:
                    _retry_error_log.append(e)
                    _try_count += 1

        raise ValueError(f"Model failed to run.")
