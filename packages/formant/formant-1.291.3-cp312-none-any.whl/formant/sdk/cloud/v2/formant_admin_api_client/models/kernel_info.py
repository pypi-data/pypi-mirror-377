from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="KernelInfo")

@attr.s(auto_attribs=True)
class KernelInfo:
    """
    Attributes:
        version (Union[Unset, str]):
        release (Union[Unset, str]):
        architecture (Union[Unset, str]):
    """

    version: Union[Unset, str] = UNSET
    release: Union[Unset, str] = UNSET
    architecture: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        version = self.version
        release = self.release
        architecture = self.architecture

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if version is not UNSET:
            field_dict["version"] = version
        if release is not UNSET:
            field_dict["release"] = release
        if architecture is not UNSET:
            field_dict["architecture"] = architecture

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        version = d.pop("version", UNSET)

        release = d.pop("release", UNSET)

        architecture = d.pop("architecture", UNSET)

        kernel_info = cls(
            version=version,
            release=release,
            architecture=architecture,
        )

        kernel_info.additional_properties = d
        return kernel_info

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
