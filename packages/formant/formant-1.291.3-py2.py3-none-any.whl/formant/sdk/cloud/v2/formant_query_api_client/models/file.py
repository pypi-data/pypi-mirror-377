from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="File")

@attr.s(auto_attribs=True)
class File:
    """
    Attributes:
        url (str):
        filename (str):
        size (int):
        preview_url (Union[Unset, str]):
    """

    url: str
    filename: str
    size: int
    preview_url: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        url = self.url
        filename = self.filename
        size = self.size
        preview_url = self.preview_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "url": url,
            "filename": filename,
            "size": size,
        })
        if preview_url is not UNSET:
            field_dict["previewUrl"] = preview_url

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        url = d.pop("url")

        filename = d.pop("filename")

        size = d.pop("size")

        preview_url = d.pop("previewUrl", UNSET)

        file = cls(
            url=url,
            filename=filename,
            size=size,
            preview_url=preview_url,
        )

        file.additional_properties = d
        return file

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
