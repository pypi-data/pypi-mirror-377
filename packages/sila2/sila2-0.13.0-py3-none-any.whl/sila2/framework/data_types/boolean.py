from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Optional

from sila2.framework.abc.data_type import DataType
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import Boolean as SilaBoolean

if TYPE_CHECKING:
    from sila2.client import ClientMetadataInstance


class Boolean(DataType[SilaBoolean, bool]):
    message_type = SiLAFramework_pb2.Boolean

    def to_native_type(self, message: SilaBoolean, toplevel_named_data_node: Optional[NamedDataNode] = None) -> bool:
        return message.value

    def to_message(
        self,
        value: bool,
        *,
        toplevel_named_data_node: Optional[NamedDataNode] = None,
        metadata: Optional[Iterable[ClientMetadataInstance]] = None,
    ) -> SilaBoolean:
        if not isinstance(value, bool):
            raise TypeError("Expected a bool value")
        return SiLAFramework_pb2.Boolean(value=value)
