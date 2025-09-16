import asyncio
import uuid
from json import JSONDecodeError
from typing import Any, Dict, Optional

import httpx
import structlog
import curlify2
from swagger_coverage_py.request_schema_handler import RequestSchemaHandler
from swagger_coverage_py.uri import URI

from packages.restclient.configuration import Configuration
from packages.restclient.utilities import allure_attach


# class RestClient:
#     def __init__(self, configuration: Configuration = Configuration) -> None:
#         self.host: str = configuration.host
#         self.set_headers(configuration.headers)
#         self.disable_log: bool = configuration.disable_log
#         self.session: httpx.AsyncClient = httpx.AsyncClient(verify=False)
#         self.log = structlog.get_logger(__name__).bind(service="api")
#
#     def set_headers(self, headers: Optional[Dict[str, str]]) -> None:
#         if headers:
#             self.session.headers.update(headers)
class RestClient:
    def __init__(self, configuration: Configuration) -> None:
        self.host: str = configuration.host
        self.set_headers(configuration.headers)
        self.disable_log: bool = configuration.disable_log
        self.session: httpx.AsyncClient = httpx.AsyncClient(verify=False)
        self.log = structlog.get_logger(__name__).bind(service="api")

    def set_headers(self, headers: Optional[Dict[str, str]]) -> None:
        if headers:
            self.session.headers.update(headers)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._send_request(method="POST", path=path, **kwargs)

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._send_request(method="GET", path=path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._send_request(method="PUT", path=path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._send_request(method="DELETE", path=path, **kwargs)

    @allure_attach
    async def _send_request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        log = self.log.bind(event_id=str(uuid.uuid4()))
        full_url = self.host + path

        if self.disable_log:
            return await self.session.request(method=method, url=full_url, **kwargs)

        log.msg(
            event="Request",
            method=method,
            full_url=full_url,
            params=kwargs.get("params"),
            headers=kwargs.get("headers"),
            json=kwargs.get("json"),
            data=kwargs.get("data"),
        )
        rest_response: httpx.Response = await self.session.request(method=method, url=full_url, **kwargs)
        rest_response.raise_for_status()
        curl = curlify2.Curlify(rest_response.request).to_curl()

        uri = URI(
            host=self.host,
            base_path="",
            unformatted_path=path,
            uri_params=kwargs.get("params"),
        )
        handler = RequestSchemaHandler(uri, method.lower(), rest_response, kwargs)
        await asyncio.to_thread(handler.write_schema)

        print(curl)
        log.msg(
            event="Response",
            status_code=rest_response.status_code,
            headers=rest_response.headers,
            json=self._get_json(rest_response),
        )
        rest_response.raise_for_status()
        return rest_response

    @staticmethod
    def _get_json(rest_response: httpx.Response) -> Dict[str, Any]:
        try:
            return rest_response.json()
        except JSONDecodeError:
            return {}
