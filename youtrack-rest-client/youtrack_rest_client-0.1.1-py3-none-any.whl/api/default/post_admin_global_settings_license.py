from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.license_ import License
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    json_body: License,
    fields: Union[Unset, None, str] = "$type,error,id,license,username",
) -> Dict[str, Any]:
    url = "{}/admin/globalSettings/license".format(client.youtrack_base_url)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "fields": fields,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[License]:
    if response.status_code == 200:
        response_200 = License.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[License]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: License,
    fields: Union[Unset, None, str] = "$type,error,id,license,username",
) -> Response[License]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        fields=fields,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    json_body: License,
    fields: Union[Unset, None, str] = "$type,error,id,license,username",
) -> Optional[License]:
    """ """

    return sync_detailed(
        client=client,
        json_body=json_body,
        fields=fields,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: License,
    fields: Union[Unset, None, str] = "$type,error,id,license,username",
) -> Response[License]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        fields=fields,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    json_body: License,
    fields: Union[Unset, None, str] = "$type,error,id,license,username",
) -> Optional[License]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
            fields=fields,
        )
    ).parsed
