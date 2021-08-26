from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.notifications_user_profile import NotificationsUserProfile
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    client: Client,
    json_body: NotificationsUserProfile,
    fields: Union[Unset, None, str] = "$type,id",
) -> Dict[str, Any]:
    url = "{}/users/{id}/profiles/notifications".format(client.youtrack_base_url, id=id)

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


def _parse_response(*, response: httpx.Response) -> Optional[NotificationsUserProfile]:
    if response.status_code == 200:
        response_200 = NotificationsUserProfile.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[NotificationsUserProfile]:
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
    json_body: NotificationsUserProfile,
    fields: Union[Unset, None, str] = "$type,id",
) -> Response[NotificationsUserProfile]:
    kwargs = _get_kwargs(
        id=id,
        client=client,
        json_body=json_body,
        fields=fields,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    id: str,
    *,
    client: Client,
    json_body: NotificationsUserProfile,
    fields: Union[Unset, None, str] = "$type,id",
) -> Optional[NotificationsUserProfile]:
    """ """

    return sync_detailed(
        id=id,
        client=client,
        json_body=json_body,
        fields=fields,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: Client,
    json_body: NotificationsUserProfile,
    fields: Union[Unset, None, str] = "$type,id",
) -> Response[NotificationsUserProfile]:
    kwargs = _get_kwargs(
        id=id,
        client=client,
        json_body=json_body,
        fields=fields,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    id: str,
    *,
    client: Client,
    json_body: NotificationsUserProfile,
    fields: Union[Unset, None, str] = "$type,id",
) -> Optional[NotificationsUserProfile]:
    """ """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            json_body=json_body,
            fields=fields,
        )
    ).parsed
