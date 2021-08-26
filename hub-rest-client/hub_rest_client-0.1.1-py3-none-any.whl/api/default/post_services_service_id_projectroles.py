from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.project_role import ProjectRole
from ...types import UNSET, Response, Unset


def _get_kwargs(
    service_id: str,
    *,
    client: AuthenticatedClient,
    json_body: ProjectRole,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Dict[str, Any]:
    url = "{}/services/{serviceId}/projectroles".format(client.hub_base_url, serviceId=service_id)

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


def _parse_response(*, response: httpx.Response) -> Optional[ProjectRole]:
    if response.status_code == 200:
        response_200 = ProjectRole.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[ProjectRole]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    service_id: str,
    *,
    client: AuthenticatedClient,
    json_body: ProjectRole,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Response[ProjectRole]:
    kwargs = _get_kwargs(
        service_id=service_id,
        client=client,
        json_body=json_body,
        fields=fields,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    service_id: str,
    *,
    client: AuthenticatedClient,
    json_body: ProjectRole,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Optional[ProjectRole]:
    """ """

    return sync_detailed(
        service_id=service_id,
        client=client,
        json_body=json_body,
        fields=fields,
    ).parsed


async def asyncio_detailed(
    service_id: str,
    *,
    client: AuthenticatedClient,
    json_body: ProjectRole,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Response[ProjectRole]:
    kwargs = _get_kwargs(
        service_id=service_id,
        client=client,
        json_body=json_body,
        fields=fields,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    service_id: str,
    *,
    client: AuthenticatedClient,
    json_body: ProjectRole,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Optional[ProjectRole]:
    """ """

    return (
        await asyncio_detailed(
            service_id=service_id,
            client=client,
            json_body=json_body,
            fields=fields,
        )
    ).parsed
