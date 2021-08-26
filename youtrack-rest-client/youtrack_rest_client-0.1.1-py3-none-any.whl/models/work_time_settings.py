from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkTimeSettings")


@attr.s(auto_attribs=True)
class WorkTimeSettings:
    """Work schedule settings."""

    minutes_a_day: Union[Unset, int] = UNSET
    work_days: Union[Unset, int] = UNSET
    first_day_of_week: Union[Unset, int] = UNSET
    days_a_week: Union[Unset, int] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        minutes_a_day = self.minutes_a_day
        work_days = self.work_days
        first_day_of_week = self.first_day_of_week
        days_a_week = self.days_a_week
        id = self.id
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if minutes_a_day is not UNSET:
            field_dict["minutesADay"] = minutes_a_day
        if work_days is not UNSET:
            field_dict["workDays"] = work_days
        if first_day_of_week is not UNSET:
            field_dict["firstDayOfWeek"] = first_day_of_week
        if days_a_week is not UNSET:
            field_dict["daysAWeek"] = days_a_week
        if id is not UNSET:
            field_dict["id"] = id
        if type is not UNSET:
            field_dict["$type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        minutes_a_day = d.pop("minutesADay", UNSET)

        work_days = d.pop("workDays", UNSET)

        first_day_of_week = d.pop("firstDayOfWeek", UNSET)

        days_a_week = d.pop("daysAWeek", UNSET)

        id = d.pop("id", UNSET)

        type = d.pop("$type", UNSET)

        work_time_settings = cls(
            minutes_a_day=minutes_a_day,
            work_days=work_days,
            first_day_of_week=first_day_of_week,
            days_a_week=days_a_week,
            id=id,
            type=type,
        )

        work_time_settings.additional_properties = d
        return work_time_settings

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
