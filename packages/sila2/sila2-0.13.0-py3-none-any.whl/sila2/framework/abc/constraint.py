from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.abc.data_type import DataType
    from sila2.framework.feature import Feature


T = TypeVar("T")


class Constraint(ABC, Generic[T]):
    @abstractmethod
    def validate(self, value: T) -> bool:
        """Return True if the given values are valid, False otherwise"""

    @classmethod
    @abstractmethod
    def from_fdl_node(cls, fdl_node, parent_feature: Feature, base_type: DataType):
        identifier = xpath_sila(fdl_node, "name()")
        if identifier == "AllowedTypes":
            from sila2.framework.constraints.allowed_types import AllowedTypes  # noqa: PLC0415 (local import)

            return AllowedTypes.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "ContentType":
            from sila2.framework.constraints.content_type import ContentType  # noqa: PLC0415 (local import)

            return ContentType.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "ElementCount":
            from sila2.framework.constraints.element_count import ElementCount  # noqa: PLC0415 (local import)

            return ElementCount.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "FullyQualifiedIdentifier":
            from sila2.framework.constraints.fully_qualified_identifier import (  # noqa: PLC0415 (local import)
                FullyQualifiedIdentifier,
            )

            return FullyQualifiedIdentifier.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "Length":
            from sila2.framework.constraints.length import Length  # noqa: PLC0415 (local import)

            return Length.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "MaximalElementCount":
            from sila2.framework.constraints.maximal_element_count import (  # noqa: PLC0415 (local import)
                MaximalElementCount,
            )

            return MaximalElementCount.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "MaximalExclusive":
            from sila2.framework.constraints.maximal_exclusive import MaximalExclusive  # noqa: PLC0415 (local import)

            return MaximalExclusive.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "MaximalInclusive":
            from sila2.framework.constraints.maximal_inclusive import MaximalInclusive  # noqa: PLC0415 (local import)

            return MaximalInclusive.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "MaximalLength":
            from sila2.framework.constraints.maximal_length import MaximalLength  # noqa: PLC0415 (local import)

            return MaximalLength.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "MinimalElementCount":
            from sila2.framework.constraints.minimal_element_count import (  # noqa: PLC0415 (local import)
                MinimalElementCount,
            )

            return MinimalElementCount.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "MinimalExclusive":
            from sila2.framework.constraints.minimal_exclusive import MinimalExclusive  # noqa: PLC0415 (local import)

            return MinimalExclusive.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "MinimalInclusive":
            from sila2.framework.constraints.minimal_inclusive import MinimalInclusive  # noqa: PLC0415 (local import)

            return MinimalInclusive.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "MinimalLength":
            from sila2.framework.constraints.minimal_length import MinimalLength  # noqa: PLC0415 (local import)

            return MinimalLength.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "Pattern":
            from sila2.framework.constraints.pattern import Pattern  # noqa: PLC0415 (local import)

            return Pattern.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "Schema":
            from sila2.framework.constraints.schema import Schema  # noqa: PLC0415 (local import)

            return Schema.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "Set":
            from sila2.framework.constraints.set import Set  # noqa: PLC0415 (local import)

            return Set.from_fdl_node(fdl_node, parent_feature, base_type)
        if identifier == "Unit":
            from sila2.framework.constraints.unit import Unit  # noqa: PLC0415 (local import)

            return Unit.from_fdl_node(fdl_node, parent_feature, base_type)
        raise RuntimeError(f"Unknown constraint node: {identifier}")
