from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="AgileStatus")


@attr.s(auto_attribs=True)
class AgileStatus:
    """Shows if the board has any configuration problems."""

    valid: Union[Unset, bool] = UNSET
    has_jobs: Union[Unset, bool] = UNSET
    errors: Union[Unset, str] = UNSET
    warnings: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        valid = self.valid
        has_jobs = self.has_jobs
        errors = self.errors
        warnings = self.warnings
        id = self.id
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if valid is not UNSET:
            field_dict["valid"] = valid
        if has_jobs is not UNSET:
            field_dict["hasJobs"] = has_jobs
        if errors is not UNSET:
            field_dict["errors"] = errors
        if warnings is not UNSET:
            field_dict["warnings"] = warnings
        if id is not UNSET:
            field_dict["id"] = id
        if type is not UNSET:
            field_dict["$type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        valid = d.pop("valid", UNSET)

        has_jobs = d.pop("hasJobs", UNSET)

        errors = d.pop("errors", UNSET)

        warnings = d.pop("warnings", UNSET)

        id = d.pop("id", UNSET)

        type = d.pop("$type", UNSET)

        agile_status = cls(
            valid=valid,
            has_jobs=has_jobs,
            errors=errors,
            warnings=warnings,
            id=id,
            type=type,
        )

        agile_status.additional_properties = d
        return agile_status

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
