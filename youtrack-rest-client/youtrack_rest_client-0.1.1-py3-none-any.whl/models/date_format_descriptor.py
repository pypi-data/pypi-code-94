from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="DateFormatDescriptor")


@attr.s(auto_attribs=True)
class DateFormatDescriptor:
    """Represents date format."""

    presentation: Union[Unset, str] = UNSET
    pattern: Union[Unset, str] = UNSET
    date_pattern: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        presentation = self.presentation
        pattern = self.pattern
        date_pattern = self.date_pattern
        id = self.id
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if presentation is not UNSET:
            field_dict["presentation"] = presentation
        if pattern is not UNSET:
            field_dict["pattern"] = pattern
        if date_pattern is not UNSET:
            field_dict["datePattern"] = date_pattern
        if id is not UNSET:
            field_dict["id"] = id
        if type is not UNSET:
            field_dict["$type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        presentation = d.pop("presentation", UNSET)

        pattern = d.pop("pattern", UNSET)

        date_pattern = d.pop("datePattern", UNSET)

        id = d.pop("id", UNSET)

        type = d.pop("$type", UNSET)

        date_format_descriptor = cls(
            presentation=presentation,
            pattern=pattern,
            date_pattern=date_pattern,
            id=id,
            type=type,
        )

        date_format_descriptor.additional_properties = d
        return date_format_descriptor

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
