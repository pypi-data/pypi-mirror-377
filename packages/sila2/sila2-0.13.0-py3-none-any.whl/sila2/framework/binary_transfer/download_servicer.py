from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Iterable
from uuid import UUID

from grpc import ServicerContext

from sila2.framework.abc.binary_transfer_handler import grpc_module as binary_transfer_grpc_module
from sila2.framework.abc.binary_transfer_handler import pb2_module as binary_transfer_pb2_module
from sila2.framework.binary_transfer.binary_transfer_error import BinaryDownloadFailed, InvalidBinaryTransferUUID
from sila2.framework.command.duration import Duration
from sila2.framework.utils import raise_as_rpc_error

if TYPE_CHECKING:
    from sila2.framework.binary_transfer.server_binary_transfer_handler import ServerBinaryTransferHandler


class BinaryDownloadServicer(binary_transfer_grpc_module.BinaryDownloadServicer):
    def __init__(self, parent_handler: ServerBinaryTransferHandler):
        self.parent_handler = parent_handler
        self._duration_field = Duration(binary_transfer_pb2_module.SiLAFramework__pb2)
        self.__logger = logging.getLogger(self.__class__.__name__)

    def GetBinaryInfo(self, request: binary_transfer_pb2_module.GetBinaryInfoRequest, context: ServicerContext):
        self.__logger.info(f"Received GetBinaryInfoRequest(binaryTransferUUID={request.binaryTransferUUID})")

        try:
            try:
                bin_id = UUID(request.binaryTransferUUID)
            except ValueError:
                raise InvalidBinaryTransferUUID(
                    f"Download of large binary failed: invalid UUID {request.binaryTransferUUID}"
                )

            if bin_id not in self.parent_handler.known_binaries:
                raise InvalidBinaryTransferUUID(f"Download of large binary failed: invalid UUID {bin_id}")

            bin_size = len(self.parent_handler.known_binaries[bin_id])
            response = binary_transfer_pb2_module.GetBinaryInfoResponse(
                binarySize=bin_size,
                lifetimeOfBinary=self._duration_field.to_message(self.parent_handler.get_default_lifetime()),
            )
            self.__logger.info(f"Found binary of {bin_size} bytes, sending response")
            return response
        except InvalidBinaryTransferUUID as ex:
            self.__logger.exception("Failed to get binary info")
            raise_as_rpc_error(ex, context)
        except Exception as ex:
            self.__logger.exception("Failed to get binary info")
            raise_as_rpc_error(BinaryDownloadFailed(f"Download of large binary failed: {ex}"), context)

    def GetChunk(
        self, request_iterator: Iterable[binary_transfer_pb2_module.GetChunkRequest], context: ServicerContext
    ):
        self.__logger.debug("Starting to send chunks")

        try:
            for chunk_request in request_iterator:
                self.__logger.debug(
                    f"Received GetChunkRequest(binaryTransferUUID={chunk_request.binaryTransferUUID}, "
                    f"offset={chunk_request.offset}, length={chunk_request.length})"
                )
                try:
                    bin_id = UUID(chunk_request.binaryTransferUUID)
                except ValueError:
                    raise InvalidBinaryTransferUUID(
                        f"Download of large binary failed: invalid UUID {chunk_request.binaryTransferUUID}"
                    )

                if bin_id not in self.parent_handler.known_binaries:
                    raise InvalidBinaryTransferUUID(f"Download of large binary failed: invalid UUID {bin_id}")

                offset = chunk_request.offset
                length = chunk_request.length

                if length > 1024 * 1024 * 2:
                    raise BinaryDownloadFailed("Request exceeded maximum chunk size (2 MiB)")

                binary = self.parent_handler.known_binaries[bin_id]
                if offset + length > len(binary):
                    raise BinaryDownloadFailed(
                        f"Requested byte range (offset {offset}, length {length}) is out of bounds "
                        f"for binary {bin_id} with length {len(binary)}"
                    )

                yield binary_transfer_pb2_module.GetChunkResponse(
                    binaryTransferUUID=str(bin_id),
                    offset=offset,
                    payload=binary[offset : offset + length],
                    lifetimeOfBinary=self._duration_field.to_message(self.parent_handler.get_default_lifetime()),
                )
                self.__logger.debug(f"Sent payload for uuid {bin_id} with offset={offset} and length={length}")
        except InvalidBinaryTransferUUID as ex:
            self.__logger.exception("Failed to send chunk")
            raise_as_rpc_error(ex, context)
        except Exception as ex:
            self.__logger.exception("Failed to send chunk")
            raise_as_rpc_error(BinaryDownloadFailed(f"Download of large binary failed: {ex}"), context)

    def DeleteBinary(self, request: binary_transfer_pb2_module.DeleteBinaryRequest, context: ServicerContext):
        try:
            try:
                bin_id = UUID(request.binaryTransferUUID)
            except ValueError:
                raise InvalidBinaryTransferUUID(
                    f"Download of large binary failed: invalid UUID {request.binaryTransferUUID}"
                )

            if bin_id not in self.parent_handler.known_binaries:
                raise InvalidBinaryTransferUUID(f"Download of large binary failed: invalid UUID {bin_id}")

            self.parent_handler.known_binaries.pop(UUID(request.binaryTransferUUID))
            return binary_transfer_pb2_module.DeleteBinaryResponse()
        except InvalidBinaryTransferUUID as ex:
            raise_as_rpc_error(ex, context)
        except Exception as ex:
            raise_as_rpc_error(BinaryDownloadFailed(f"Deletion of large binary failed: {ex}"), context)
