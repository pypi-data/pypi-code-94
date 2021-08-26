from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="DashboardPermissionImport")


@attr.s(auto_attribs=True)
class DashboardPermissionImport:
    """ """

    id: Union[Unset, str] = UNSET
    principal: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    permission: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        principal = self.principal
        type = self.type
        permission = self.permission

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if principal is not UNSET:
            field_dict["principal"] = principal
        if type is not UNSET:
            field_dict["type"] = type
        if permission is not UNSET:
            field_dict["permission"] = permission

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        id = d.pop("id", UNSET)

        principal = d.pop("principal", UNSET)

        type = d.pop("type", UNSET)

        permission = d.pop("permission", UNSET)

        dashboard_permission_import = cls(
            id=id,
            principal=principal,
            type=type,
            permission=permission,
        )

        dashboard_permission_import.additional_properties = d
        return dashboard_permission_import

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
