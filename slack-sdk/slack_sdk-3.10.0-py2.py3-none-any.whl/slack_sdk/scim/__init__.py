"""SCIM API is a set of APIs for provisioning and managing user accounts and groups.
SCIM is used by Single Sign-On (SSO) services and identity providers to manage people across a variety of tools,
including Slack.

Refer to https://slack.dev/python-slack-sdk/scim/ for details.
"""
from .v1.client import SCIMClient  # noqa
from .v1.response import SCIMResponse  # noqa
from .v1.response import SearchUsersResponse, ReadUserResponse  # noqa
from .v1.response import SearchGroupsResponse, ReadGroupResponse  # noqa
from .v1.user import User  # noqa
from .v1.group import Group  # noqa
