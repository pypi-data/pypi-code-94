from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.projectroles_page import ProjectrolesPage
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_team_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Dict[str, Any]:
    url = "{}/projectteams/{projectTeamId}/projectroles".format(client.hub_base_url, projectTeamId=project_team_id)

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


def _parse_response(*, response: httpx.Response) -> Optional[ProjectrolesPage]:
    if response.status_code == 200:
        response_200 = ProjectrolesPage.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[ProjectrolesPage]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    project_team_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Response[ProjectrolesPage]:
    kwargs = _get_kwargs(
        project_team_id=project_team_id,
        client=client,
        fields=fields,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    project_team_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Optional[ProjectrolesPage]:
    """ """

    return sync_detailed(
        project_team_id=project_team_id,
        client=client,
        fields=fields,
    ).parsed


async def asyncio_detailed(
    project_team_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Response[ProjectrolesPage]:
    kwargs = _get_kwargs(
        project_team_id=project_team_id,
        client=client,
        fields=fields,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    project_team_id: str,
    *,
    client: AuthenticatedClient,
    fields: Union[Unset, None, str] = "id,teamMember",
) -> Optional[ProjectrolesPage]:
    """ """

    return (
        await asyncio_detailed(
            project_team_id=project_team_id,
            client=client,
            fields=fields,
        )
    ).parsed
