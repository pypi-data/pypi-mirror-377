from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from lxml import etree

from sila2.framework.abc.message_mappable import MessageMappable, ProtobufType, PythonType
from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.feature import Feature


class DataType(MessageMappable[ProtobufType, PythonType], ABC):
    @staticmethod
    def from_fdl_node(fdl_node, parent_feature: Feature, parent_namespace) -> DataType:
        if xpath_sila(fdl_node, "sila:Basic"):
            identifier = xpath_sila(fdl_node, "sila:Basic/text()")[0]
            if identifier == "Boolean":
                from sila2.framework.data_types.boolean import Boolean  # noqa: PLC0415 (local import)

                return Boolean()
            if identifier == "Integer":
                from sila2.framework.data_types.integer import Integer  # noqa: PLC0415 (local import)

                return Integer()
            if identifier == "Real":
                from sila2.framework.data_types.real import Real  # noqa: PLC0415 (local import)

                return Real()
            if identifier == "String":
                from sila2.framework.data_types.string import String  # noqa: PLC0415 (local import)

                return String()
            if identifier == "Binary":
                from sila2.framework.data_types.binary import Binary  # noqa: PLC0415 (local import)

                return Binary(parent_feature)  # TODO: find a more elegant way than via feature
            if identifier == "Date":
                from sila2.framework.data_types.date import Date  # noqa: PLC0415 (local import)

                return Date()
            if identifier == "Time":
                from sila2.framework.data_types.time import Time  # noqa: PLC0415 (local import)

                return Time()
            if identifier == "Timestamp":
                from sila2.framework.data_types.timestamp import Timestamp  # noqa: PLC0415 (local import)

                return Timestamp()
            if identifier == "Any":
                from sila2.framework.data_types.any import Any  # noqa: PLC0415 (local import)

                return Any()
            raise RuntimeError(f"Unknown basic data type: {identifier}")
        if xpath_sila(fdl_node, "sila:Constrained"):
            from sila2.framework.data_types.constrained import Constrained  # noqa: PLC0415 (local import)

            return Constrained.from_fdl_node(
                xpath_sila(fdl_node, "sila:Constrained")[0],
                parent_feature,
                parent_namespace,
            )
        if xpath_sila(fdl_node, "sila:DataTypeIdentifier"):
            identifier = xpath_sila(fdl_node, "sila:DataTypeIdentifier/text()")[0]
            return parent_feature._data_type_definitions[identifier]
        if xpath_sila(fdl_node, "sila:List"):
            from sila2.framework.data_types.list import List  # noqa: PLC0415 (local import)

            return List(xpath_sila(fdl_node, "sila:List")[0], parent_feature, parent_namespace)
        if xpath_sila(fdl_node, "sila:Structure"):
            from sila2.framework.data_types.structure import Structure  # noqa: PLC0415 (local import)

            return Structure(
                xpath_sila(fdl_node, "sila:Structure")[0],
                parent_feature,
                parent_namespace,
            )
        raise RuntimeError(f"Unknown data type node: {etree.tostring(fdl_node).decode('utf-8')}")  # pragma: no cover
