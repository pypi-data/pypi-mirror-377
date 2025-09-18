from __future__ import annotations

import math
import re
from datetime import timedelta, timezone
from typing import TYPE_CHECKING, Iterable, Optional

from sila2.framework.abc.message_mappable import MessageMappable
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import Timezone as SilaTimezone

if TYPE_CHECKING:
    from sila2.client import ClientMetadataInstance


_MIN_OFFSET = timedelta(hours=-14)
_MAX_OFFSET = timedelta(hours=14)


class Timezone(MessageMappable):
    def to_message(
        self,
        utc_offset: timedelta,
        *,
        toplevel_named_data_node: Optional[NamedDataNode] = None,
        metadata: Optional[Iterable[ClientMetadataInstance]] = None,
    ) -> SilaTimezone:
        offset_seconds = utc_offset.total_seconds()
        if not math.isclose(int(offset_seconds) % 60, 0):
            raise ValueError("SiLA2 does not support seconds in Timezone")
        if utc_offset < _MIN_OFFSET or utc_offset > _MAX_OFFSET:
            raise ValueError("Timezone UTC offset must be between -14:00 and +14:00 hours")

        offset_hours, offset_minutes = divmod(offset_seconds // 60, 60)

        return SiLAFramework_pb2.Timezone(hours=int(offset_hours), minutes=int(offset_minutes))

    def to_native_type(
        self, message: SilaTimezone, toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> timezone:
        if message.minutes >= 60:
            raise ValueError("Timezone minutes must be less than 60")

        utc_offset = timedelta(hours=message.hours, minutes=message.minutes)
        if utc_offset < _MIN_OFFSET or utc_offset > _MAX_OFFSET:
            raise ValueError("Timezone UTC offset must be between -14:00 and +14:00 hours")

        return timezone(timedelta(hours=message.hours, minutes=message.minutes))

    @staticmethod
    def from_string(value: str) -> timezone:
        if value == "Z":
            return timezone(timedelta(hours=0, minutes=0))
        if not re.fullmatch(r"[+-]\d{2}:\d{2}", value):
            raise ValueError(f"Invalid timezone format: '{value}'. Must be 'Z' or like '+HH:MM' or '-HH:MM'")

        sign = int(value[0] + "1")
        utc_offset = sign * timedelta(hours=int(value[1:3]), minutes=int(value[-2:]))

        if utc_offset < _MIN_OFFSET or utc_offset > _MAX_OFFSET:
            raise ValueError("Timezone UTC offset must be between -14:00 and +14:00 hours")

        return timezone(utc_offset)
