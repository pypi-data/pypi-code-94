from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="FieldStyle")


@attr.s(auto_attribs=True)
class FieldStyle:
    """Represents the style settings of the field in YouTrack."""

    background: Union[Unset, str] = UNSET
    foreground: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        background = self.background
        foreground = self.foreground
        id = self.id
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if background is not UNSET:
            field_dict["background"] = background
        if foreground is not UNSET:
            field_dict["foreground"] = foreground
        if id is not UNSET:
            field_dict["id"] = id
        if type is not UNSET:
            field_dict["$type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        background = d.pop("background", UNSET)

        foreground = d.pop("foreground", UNSET)

        id = d.pop("id", UNSET)

        type = d.pop("$type", UNSET)

        field_style = cls(
            background=background,
            foreground=foreground,
            id=id,
            type=type,
        )

        field_style.additional_properties = d
        return field_style

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
