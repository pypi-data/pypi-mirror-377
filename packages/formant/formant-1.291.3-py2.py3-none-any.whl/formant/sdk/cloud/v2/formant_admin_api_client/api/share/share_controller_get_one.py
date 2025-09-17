from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.share import Share
from ...types import Response


def _get_kwargs(
    code: str,
    *,
    client: Client,

) -> Dict[str, Any]:
    url = "{}/shares/{code}".format(
        client.base_url,code=code)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    

    

    

    

    

    return {
	    "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Share]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Share.from_dict(response.json())



        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[Share]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    code: str,
    *,
    client: Client,

) -> Response[Share]:
    """Get one

     Get a share

    Args:
        code (str):

    Returns:
        Response[Share]
    """


    kwargs = _get_kwargs(
        code=code,
client=client,

    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)

def sync(
    code: str,
    *,
    client: Client,

) -> Optional[Share]:
    """Get one

     Get a share

    Args:
        code (str):

    Returns:
        Response[Share]
    """


    return sync_detailed(
        code=code,
client=client,

    ).parsed

async def asyncio_detailed(
    code: str,
    *,
    client: Client,

) -> Response[Share]:
    """Get one

     Get a share

    Args:
        code (str):

    Returns:
        Response[Share]
    """


    kwargs = _get_kwargs(
        code=code,
client=client,

    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(
            **kwargs
        )

    return _build_response(response=response)

async def asyncio(
    code: str,
    *,
    client: Client,

) -> Optional[Share]:
    """Get one

     Get a share

    Args:
        code (str):

    Returns:
        Response[Share]
    """


    return (await asyncio_detailed(
        code=code,
client=client,

    )).parsed

