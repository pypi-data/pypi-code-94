from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.state_bundle_element import StateBundleElement
else:
    StateBundleElement = "StateBundleElement"

from ..models.base_bundle import BaseBundle

T = TypeVar("T", bound="StateBundle")


@attr.s(auto_attribs=True)
class StateBundle(BaseBundle):
    """Represents a set of states in YouTrack."""

    values: Union[Unset, List[StateBundleElement]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        values: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.values, Unset):
            values = []
            for values_item_data in self.values:
                values_item = values_item_data.to_dict()

                values.append(values_item)

        field_dict: Dict[str, Any] = {}
        _BaseBundle_dict = super().to_dict()
        field_dict.update(_BaseBundle_dict)
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if values is not UNSET:
            field_dict["values"] = values

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        _BaseBundle_kwargs = super().from_dict(src_dict=d).to_dict()

        values = []
        _values = d.pop("values", UNSET)
        for values_item_data in _values or []:
            values_item = StateBundleElement.from_dict(values_item_data)

            values.append(values_item)

        state_bundle = cls(
            values=values,
            **_BaseBundle_kwargs,
        )

        state_bundle.additional_properties = d
        return state_bundle

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
