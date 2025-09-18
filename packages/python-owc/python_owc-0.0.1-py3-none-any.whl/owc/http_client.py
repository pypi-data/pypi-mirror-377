from __future__ import annotations
import uuid
from typing import Any, Mapping
import asyncio

from aiohttp import ClientSession, ClientConnectionError, ClientResponse

from owc import OWC, end_process


class Response:
    def __init__(self) -> None:
        self._uuid = str(uuid.uuid4())
        self.content: ClientResponse | None = None
        self.successful = None

    @property
    def uuid(self) -> str:
        return self._uuid

    def end_process(self) -> None:
        end_process(self.uuid)

    def __repr__(self) -> str:
        return "Response()"


class HTTPClient:
    def __init__(
        self, *, base_url: str = None, headers: Mapping[str, Any] = None
    ) -> None:
        self.session = ClientSession(base_url=base_url, headers=headers)

    async def close(self) -> None:
        await self.session.close()

    async def __aenter__(self) -> HTTPClient:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def __request(
        self,
        *,
        response: Response,
        url: str,
        method: str,
        headers: Mapping[str, Any] = None,
        data: Mapping[str, Any] = None,
        expires: int = None,
        delay: int = 60,
    ) -> None:
        async for _ in OWC(uuid=response.uuid, expires=expires, delay=delay):
            try:
                response.content = await self.session.request(
                    url=url, method=method, headers=headers, json=data
                )
                response.successful = True
                response.end_process()
                return
            except ClientConnectionError:
                continue
            except Exception as error:
                response.successful = False
                response.end_process()
                raise error
        response.successful = False

    async def request(
        self,
        *,
        url: str,
        method: str,
        headers: Mapping[str, Any] = None,
        data: Mapping[str, Any] = None,
        expires: int = None,
        delay: int = 60,
    ) -> Response:
        response = Response()
        asyncio.create_task(
            self.__request(
                response=response,
                url=url,
                method=method,
                headers=headers,
                data=data,
                delay=delay,
                expires=expires,
            )
        )
        return response

    async def get(
        self,
        url: str,
        *,
        headers: Mapping[str, Any] = None,
        expires: int = None,
        delay: int = 60,
    ) -> Response:
        return await self.request(
            url=url, method="GET", headers=headers, expires=expires, delay=delay
        )

    async def post(
        self,
        url: str,
        *,
        headers: Mapping[str, Any] = None,
        data: Mapping[str, Any] = None,
        expires: int = None,
        delay: int = 60,
    ) -> Response:
        return await self.request(
            url=url,
            method="POST",
            headers=headers,
            data=data,
            expires=expires,
            delay=delay,
        )

    async def put(
        self,
        url: str,
        *,
        headers: Mapping[str, Any] = None,
        data: Mapping[str, Any] = None,
        expires: int = None,
        delay: int = 60,
    ) -> Response:
        return await self.request(
            url=url,
            method="PUT",
            headers=headers,
            data=data,
            expires=expires,
            delay=delay,
        )

    async def patch(
        self,
        url: str,
        *,
        headers: Mapping[str, Any] = None,
        data: Mapping[str, Any] = None,
        expires: int = None,
        delay: int = 60,
    ) -> Response:
        return await self.request(
            url=url,
            method="PATCH",
            headers=headers,
            data=data,
            expires=expires,
            delay=delay,
        )

    async def delete(
        self,
        url: str,
        *,
        headers: Mapping[str, Any] = None,
        expires: int = None,
        delay: int = 60,
    ) -> Response:
        return await self.request(
            url=url, method="DELETE", headers=headers, expires=expires, delay=delay
        )

    def __repr__(self) -> str:
        return "HTTPClient()"
