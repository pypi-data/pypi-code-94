from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="RestCorsSettings")


@attr.s(auto_attribs=True)
class RestCorsSettings:
    """Represents the Resource Sharing (CORS) configuration of the service."""

    allowed_origins: Union[Unset, str] = UNSET
    allow_all_origins: Union[Unset, bool] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allowed_origins = self.allowed_origins
        allow_all_origins = self.allow_all_origins
        id = self.id
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allowed_origins is not UNSET:
            field_dict["allowedOrigins"] = allowed_origins
        if allow_all_origins is not UNSET:
            field_dict["allowAllOrigins"] = allow_all_origins
        if id is not UNSET:
            field_dict["id"] = id
        if type is not UNSET:
            field_dict["$type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        allowed_origins = d.pop("allowedOrigins", UNSET)

        allow_all_origins = d.pop("allowAllOrigins", UNSET)

        id = d.pop("id", UNSET)

        type = d.pop("$type", UNSET)

        rest_cors_settings = cls(
            allowed_origins=allowed_origins,
            allow_all_origins=allow_all_origins,
            id=id,
            type=type,
        )

        rest_cors_settings.additional_properties = d
        return rest_cors_settings

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
