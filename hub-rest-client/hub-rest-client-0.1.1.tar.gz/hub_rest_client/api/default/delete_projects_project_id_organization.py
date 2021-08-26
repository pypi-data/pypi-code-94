from typing import Any, Dict

import httpx

from ...client import Client
from ...types import Response


def _get_kwargs(
    project_id: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/projects/{projectId}/organization".format(client.hub_base_url, projectId=project_id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _build_response(*, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=None,
    )


def sync_detailed(
    project_id: str,
    *,
    client: Client,
) -> Response[Any]:
    kwargs = _get_kwargs(
        project_id=project_id,
        client=client,
    )

    response = httpx.delete(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    project_id: str,
    *,
    client: Client,
) -> Response[Any]:
    kwargs = _get_kwargs(
        project_id=project_id,
        client=client,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.delete(**kwargs)

    return _build_response(response=response)
