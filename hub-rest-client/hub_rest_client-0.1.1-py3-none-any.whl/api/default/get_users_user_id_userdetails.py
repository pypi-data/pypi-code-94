from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.userdetails_page import UserdetailsPage
from ...types import UNSET, Response, Unset


def _get_kwargs(
    user_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,authModuleName,lastAccessTime,lastAccessAddress,lastAccessUserAgent",
) -> Dict[str, Any]:
    url = "{}/users/{userId}/userdetails".format(client.hub_base_url, userId=user_id)

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


def _parse_response(*, response: httpx.Response) -> Optional[UserdetailsPage]:
    if response.status_code == 200:
        response_200 = UserdetailsPage.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[UserdetailsPage]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    user_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,authModuleName,lastAccessTime,lastAccessAddress,lastAccessUserAgent",
) -> Response[UserdetailsPage]:
    kwargs = _get_kwargs(
        user_id=user_id,
        client=client,
        fields=fields,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    user_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,authModuleName,lastAccessTime,lastAccessAddress,lastAccessUserAgent",
) -> Optional[UserdetailsPage]:
    """ """

    return sync_detailed(
        user_id=user_id,
        client=client,
        fields=fields,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,authModuleName,lastAccessTime,lastAccessAddress,lastAccessUserAgent",
) -> Response[UserdetailsPage]:
    kwargs = _get_kwargs(
        user_id=user_id,
        client=client,
        fields=fields,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    user_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,authModuleName,lastAccessTime,lastAccessAddress,lastAccessUserAgent",
) -> Optional[UserdetailsPage]:
    """ """

    return (
        await asyncio_detailed(
            user_id=user_id,
            client=client,
            fields=fields,
        )
    ).parsed
