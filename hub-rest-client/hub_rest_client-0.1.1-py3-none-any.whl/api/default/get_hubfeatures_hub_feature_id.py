from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.hub_feature import HubFeature
from ...types import UNSET, Response, Unset


def _get_kwargs(
    hub_feature_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "key,name,description,restartRequired,enabled",
) -> Dict[str, Any]:
    url = "{}/hubfeatures/{hubFeatureId}".format(client.hub_base_url, hubFeatureId=hub_feature_id)

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


def _parse_response(*, response: httpx.Response) -> Optional[HubFeature]:
    if response.status_code == 200:
        response_200 = HubFeature.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[HubFeature]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    hub_feature_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "key,name,description,restartRequired,enabled",
) -> Response[HubFeature]:
    kwargs = _get_kwargs(
        hub_feature_id=hub_feature_id,
        client=client,
        fields=fields,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    hub_feature_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "key,name,description,restartRequired,enabled",
) -> Optional[HubFeature]:
    """ """

    return sync_detailed(
        hub_feature_id=hub_feature_id,
        client=client,
        fields=fields,
    ).parsed


async def asyncio_detailed(
    hub_feature_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "key,name,description,restartRequired,enabled",
) -> Response[HubFeature]:
    kwargs = _get_kwargs(
        hub_feature_id=hub_feature_id,
        client=client,
        fields=fields,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    hub_feature_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "key,name,description,restartRequired,enabled",
) -> Optional[HubFeature]:
    """ """

    return (
        await asyncio_detailed(
            hub_feature_id=hub_feature_id,
            client=client,
            fields=fields,
        )
    ).parsed
