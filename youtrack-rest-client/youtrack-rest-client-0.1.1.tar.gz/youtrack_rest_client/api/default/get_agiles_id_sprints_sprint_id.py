from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.sprint import Sprint
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    sprint_id: str,
    *,
    client: Client,
    fields: Union[Unset, None, str] = "$type,archived,finish,id,isDefault,name,start",
) -> Dict[str, Any]:
    url = "{}/agiles/{id}/sprints/{sprintId}".format(client.youtrack_base_url, id=id, sprintId=sprint_id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "fields": fields,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Sprint]:
    if response.status_code == 200:
        response_200 = Sprint.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[Sprint]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    id: str,
    sprint_id: str,
    *,
    client: Client,
    fields: Union[Unset, None, str] = "$type,archived,finish,id,isDefault,name,start",
) -> Response[Sprint]:
    kwargs = _get_kwargs(
        id=id,
        sprint_id=sprint_id,
        client=client,
        fields=fields,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    id: str,
    sprint_id: str,
    *,
    client: Client,
    fields: Union[Unset, None, str] = "$type,archived,finish,id,isDefault,name,start",
) -> Optional[Sprint]:
    """ """

    return sync_detailed(
        id=id,
        sprint_id=sprint_id,
        client=client,
        fields=fields,
    ).parsed


async def asyncio_detailed(
    id: str,
    sprint_id: str,
    *,
    client: Client,
    fields: Union[Unset, None, str] = "$type,archived,finish,id,isDefault,name,start",
) -> Response[Sprint]:
    kwargs = _get_kwargs(
        id=id,
        sprint_id=sprint_id,
        client=client,
        fields=fields,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    id: str,
    sprint_id: str,
    *,
    client: Client,
    fields: Union[Unset, None, str] = "$type,archived,finish,id,isDefault,name,start",
) -> Optional[Sprint]:
    """ """

    return (
        await asyncio_detailed(
            id=id,
            sprint_id=sprint_id,
            client=client,
            fields=fields,
        )
    ).parsed
