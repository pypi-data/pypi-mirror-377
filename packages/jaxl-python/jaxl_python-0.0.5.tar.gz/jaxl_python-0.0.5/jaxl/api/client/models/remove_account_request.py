"""
Copyright (c) 2010-present by Jaxl Innovations Private Limited.

All rights reserved.

Redistribution and use in source and binary forms,
with or without modification, is strictly prohibited.
"""

from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset


T = TypeVar("T", bound="RemoveAccountRequest")


@attr.s(auto_attribs=True)
class RemoveAccountRequest:
    """
    Attributes:
        id (int): User ID
        identifier (str): Signed email ID
        usage (Union[Unset, None, str]):
        currency (Union[Unset, None, int]):
    """

    id: int
    identifier: str
    usage: Union[Unset, None, str] = UNSET
    currency: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        identifier = self.identifier
        usage = self.usage
        currency = self.currency

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "identifier": identifier,
            }
        )
        if usage is not UNSET:
            field_dict["usage"] = usage
        if currency is not UNSET:
            field_dict["currency"] = currency

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        identifier = d.pop("identifier")

        usage = d.pop("usage", UNSET)

        currency = d.pop("currency", UNSET)

        remove_account_request = cls(
            id=id,
            identifier=identifier,
            usage=usage,
            currency=currency,
        )

        remove_account_request.additional_properties = d
        return remove_account_request

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
