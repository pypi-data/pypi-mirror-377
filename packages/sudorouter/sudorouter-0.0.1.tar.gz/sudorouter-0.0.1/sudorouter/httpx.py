from typing import Iterator, AsyncIterator

import httpx
import urllib3

from .tls import mutual_ssl_context


class ByteStream(httpx.SyncByteStream):
    def __init__(self, resp: urllib3.HTTPResponse) -> None:
        self._resp = resp

    def __iter__(self) -> Iterator[bytes]:
        for chunk in self._resp.stream(decode_content=False):
            yield chunk

    def close(self) -> None:
        self._resp.release_conn()


class TeeTransport(httpx.BaseTransport):
    def __init__(self, ssl_context) -> None:
        self._pool = urllib3.PoolManager(
            ssl_context=ssl_context,
            assert_hostname=False,
            num_pools=10,
            maxsize=10,
            block=False,
        )

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        timeouts = request.extensions.get("timeout", {})
        response = self._pool.request(
            method=request.method,
            url=str(request.url),
            body=request.content,
            headers=urllib3.HTTPHeaderDict({name: value for name, value in request.headers.multi_items()}),
            redirect=False,
            preload_content=False,
            timeout=urllib3.Timeout(
                connect=timeouts.get("connect", None),
                read=timeouts.get("read", None),
            ),
        )
        return httpx.Response(
            status_code=response.status,
            headers=httpx.Headers([(name, value) for name, value in response.headers.iteritems()]),
            content=ByteStream(response),
            extensions={"urllib3_response": response},
        )


class AsyncByteStream(httpx.AsyncByteStream):
    def __init__(self, resp: urllib3.HTTPResponse) -> None:
        self._resp = resp

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self._resp.stream(decode_content=False):
            yield chunk

    async def aclose(self) -> None:
        return self._resp.close()


class AsyncTeeTransport(httpx.AsyncBaseTransport):
    def __init__(self, ssl_context) -> None:
        self._pool = urllib3.PoolManager(
            ssl_context=ssl_context,
            assert_hostname=False,
            num_pools=10,
            maxsize=10,
            block=False,
        )

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        timeouts = request.extensions.get("timeout", {})
        response = self._pool.request(
            method=request.method,
            url=str(request.url),
            body=request.content,
            headers=urllib3.HTTPHeaderDict({name: value for name, value in request.headers.multi_items()}),
            redirect=False,
            preload_content=False,
            timeout=urllib3.Timeout(
                connect=timeouts.get("connect", None),
                read=timeouts.get("read", None),
            ),
        )
        return httpx.Response(
            status_code=response.status,
            headers=httpx.Headers([(name, value) for name, value in response.headers.iteritems()]),
            content=AsyncByteStream(response),
            extensions={"urllib3_response": response},
        )


class TeeClient(httpx.Client):
    def __init__(self, user_id: int, private_key_der: str, **kwargs):
        kwargs.setdefault("transport", TeeTransport(ssl_context=mutual_ssl_context(user_id, private_key_der)))
        super().__init__(**kwargs)


class AsyncTeeClient(httpx.AsyncClient):
    def __init__(self, user_id: int, private_key_der: str, **kwargs):
        kwargs.setdefault("transport", TeeTransport(ssl_context=mutual_ssl_context(user_id, private_key_der)))
        super().__init__(**kwargs)
