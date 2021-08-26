from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.metrics import Metrics
else:
    Metrics = "Metrics"

from ..models.base_page import BasePage

T = TypeVar("T", bound="MetricsPage")


@attr.s(auto_attribs=True)
class MetricsPage(BasePage):
    """ """

    metrics: Union[Unset, List[Metrics]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        metrics: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.metrics, Unset):
            metrics = []
            for metrics_item_data in self.metrics:
                metrics_item = metrics_item_data.to_dict()

                metrics.append(metrics_item)

        field_dict: Dict[str, Any] = {}
        _BasePage_dict = super(BasePage).to_dict()
        field_dict.update(_BasePage_dict)
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if metrics is not UNSET:
            field_dict["metrics"] = metrics

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        _BasePage_kwargs = super(BasePage).from_dict(src_dict=d).to_dict()

        metrics = []
        _metrics = d.pop("metrics", UNSET)
        for metrics_item_data in _metrics or []:
            metrics_item = Metrics.from_dict(metrics_item_data)

            metrics.append(metrics_item)

        metrics_page = cls(
            metrics=metrics,
            **_BasePage_kwargs,
        )

        metrics_page.additional_properties = d
        return metrics_page

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
