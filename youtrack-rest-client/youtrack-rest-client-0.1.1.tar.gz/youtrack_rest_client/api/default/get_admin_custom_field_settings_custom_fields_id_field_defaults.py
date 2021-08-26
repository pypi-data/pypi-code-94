from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.custom_field_defaults import CustomFieldDefaults
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    client: Client,
    fields: Union[
        Unset, None, str
    ] = "$type,bundle($type,id),canBeEmpty,defaultValues($type,id,name),emptyFieldText,id,isPublic",
) -> Dict[str, Any]:
    url = "{}/admin/customFieldSettings/customFields/{id}/fieldDefaults".format(client.youtrack_base_url, id=id)

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


def _parse_response(*, response: httpx.Response) -> Optional[CustomFieldDefaults]:
    if response.status_code == 200:
        response_200 = CustomFieldDefaults.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[CustomFieldDefaults]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: Client,
    fields: Union[
        Unset, None, str
    ] = "$type,bundle($type,id),canBeEmpty,defaultValues($type,id,name),emptyFieldText,id,isPublic",
) -> Response[CustomFieldDefaults]:
    kwargs = _get_kwargs(
        id=id,
        client=client,
        fields=fields,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    id: str,
    *,
    client: Client,
    fields: Union[
        Unset, None, str
    ] = "$type,bundle($type,id),canBeEmpty,defaultValues($type,id,name),emptyFieldText,id,isPublic",
) -> Optional[CustomFieldDefaults]:
    """ """

    return sync_detailed(
        id=id,
        client=client,
        fields=fields,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: Client,
    fields: Union[
        Unset, None, str
    ] = "$type,bundle($type,id),canBeEmpty,defaultValues($type,id,name),emptyFieldText,id,isPublic",
) -> Response[CustomFieldDefaults]:
    kwargs = _get_kwargs(
        id=id,
        client=client,
        fields=fields,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    id: str,
    *,
    client: Client,
    fields: Union[
        Unset, None, str
    ] = "$type,bundle($type,id),canBeEmpty,defaultValues($type,id,name),emptyFieldText,id,isPublic",
) -> Optional[CustomFieldDefaults]:
    """ """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            fields=fields,
        )
    ).parsed
