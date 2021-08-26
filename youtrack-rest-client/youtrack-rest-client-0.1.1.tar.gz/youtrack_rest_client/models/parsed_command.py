from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ParsedCommand")


@attr.s(auto_attribs=True)
class ParsedCommand:
    """Represents the command that was parsed from the provided query."""

    description: Union[Unset, str] = UNSET
    error: Union[Unset, bool] = UNSET
    delete: Union[Unset, bool] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        description = self.description
        error = self.error
        delete = self.delete
        id = self.id
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if error is not UNSET:
            field_dict["error"] = error
        if delete is not UNSET:
            field_dict["delete"] = delete
        if id is not UNSET:
            field_dict["id"] = id
        if type is not UNSET:
            field_dict["$type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        description = d.pop("description", UNSET)

        error = d.pop("error", UNSET)

        delete = d.pop("delete", UNSET)

        id = d.pop("id", UNSET)

        type = d.pop("$type", UNSET)

        parsed_command = cls(
            description=description,
            error=error,
            delete=delete,
            id=id,
            type=type,
        )

        parsed_command.additional_properties = d
        return parsed_command

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
