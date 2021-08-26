from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.project_role import ProjectRole
from ...types import UNSET, Response, Unset


def _get_kwargs(
    user_group_id: str,
    project_role_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Dict[str, Any]:
    url = "{}/usergroups/{userGroupId}/transitiveprojectroles/{projectRoleId}".format(
        client.hub_base_url, userGroupId=user_group_id, projectRoleId=project_role_id
    )

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
    user_group_id: str,
    project_role_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Response[ProjectRole]:
    kwargs = _get_kwargs(
        user_group_id=user_group_id,
        project_role_id=project_role_id,
        client=client,
        fields=fields,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    user_group_id: str,
    project_role_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Optional[ProjectRole]:
    """ """

    return sync_detailed(
        user_group_id=user_group_id,
        project_role_id=project_role_id,
        client=client,
        fields=fields,
    ).parsed


async def asyncio_detailed(
    user_group_id: str,
    project_role_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Response[ProjectRole]:
    kwargs = _get_kwargs(
        user_group_id=user_group_id,
        project_role_id=project_role_id,
        client=client,
        fields=fields,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    user_group_id: str,
    project_role_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Optional[ProjectRole]:
    """ """

    return (
        await asyncio_detailed(
            user_group_id=user_group_id,
            project_role_id=project_role_id,
            client=client,
            fields=fields,
        )
    ).parsed
