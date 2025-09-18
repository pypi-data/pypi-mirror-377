from __future__ import annotations

import re
import warnings
from typing import TYPE_CHECKING, Optional

from sila2.framework.abc.sila_error import SilaError
from sila2.framework.fully_qualified_identifier import FullyQualifiedCommandParameterIdentifier
from sila2.framework.utils import FullyQualifiedIdentifierRegex

if TYPE_CHECKING:
    from sila2.client.sila_client import SilaClient
    from sila2.framework.pb2.SiLAFramework_pb2 import SiLAError
    from sila2.framework.pb2.SiLAFramework_pb2 import ValidationError as SilaValidationError


class ValidationError(SilaError):
    """
    Issued by a SiLA Server if a SiLA Client sent invalid command parameters

    Notes
    -----
    This error is raised automatically by the SDK if a received parameter violates a constraint defined in the
    feature definition, or if the SDK could not interpret the parameter message sent by the SiLA Client
    """

    parameter_fully_qualified_identifier: Optional[FullyQualifiedCommandParameterIdentifier]
    """Fully qualified identifier of the invalid parameter"""
    message: str
    """Error message"""

    def __init__(self, message: str):
        self.message = message
        self.parameter_fully_qualified_identifier = None
        super().__init__(f"Parameter value rejected: {message}")

    def to_message(self) -> SiLAError:
        if self.parameter_fully_qualified_identifier is None:
            raise RuntimeError(
                "Cannot convert ValidationError to SiLAError protobuf message without a parameter identifier"
            )
        return self._pb2_module.SiLAError(
            validationError=self._pb2_module.ValidationError(
                parameter=self.parameter_fully_qualified_identifier, message=self.message
            )
        )

    @classmethod
    def from_message(cls, message: SilaValidationError, client: SilaClient) -> ValidationError:
        raw_parameter = message.parameter

        parameter_fully_qualified_identifier = cls.parse_parameter_identifier(raw_parameter, client)

        err = cls(message.message)
        err.parameter_fully_qualified_identifier = parameter_fully_qualified_identifier
        return err

    @staticmethod
    def parse_parameter_identifier(
        parameter_identifier: str, client: SilaClient
    ) -> Optional[FullyQualifiedCommandParameterIdentifier]:
        if not re.fullmatch(FullyQualifiedIdentifierRegex.CommandParameterIdentifier, parameter_identifier):
            warnings.warn(
                f"Not a fully qualified parameter identifier: {parameter_identifier!r} "
                f"(Invalid server response, please contact the vendor)"
            )
            return None

        parameter_fully_qualified_identifier = client._children_by_fully_qualified_identifier.get(
            FullyQualifiedCommandParameterIdentifier(parameter_identifier)
        )
        if parameter_fully_qualified_identifier is None:
            warnings.warn(
                f"Not a valid parameter identifier: {parameter_identifier!r} "
                f"(Invalid server response, please contact the vendor)"
            )
        return parameter_fully_qualified_identifier
