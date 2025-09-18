from __future__ import annotations

import collections.abc
from base64 import standard_b64decode
from typing import TYPE_CHECKING, Dict, Iterable, Optional
from uuid import UUID

import grpc

from sila2.client.utils import pack_metadata_for_grpc
from sila2.framework import SilaError
from sila2.framework.abc.binary_transfer_handler import BinaryTransferHandler
from sila2.framework.abc.binary_transfer_handler import grpc_module as binary_transfer_grpc_module
from sila2.framework.abc.binary_transfer_handler import pb2_module as binary_transfer_pb2_module
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.binary_transfer.binary_transfer_error import (
    BinaryDownloadFailed,
    BinaryTransferError,
    BinaryUploadFailed,
)
from sila2.framework.command.duration import Duration
from sila2.framework.command.parameter import Parameter
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.utils import consume_generator

from .binary_chunk import BinaryChunk
from .binary_info import BinaryInfo

if TYPE_CHECKING:
    from sila2.client import ClientMetadataInstance, SilaClient
    from sila2.framework.pb2.SiLAFramework_pb2 import Binary as SilaBinary


class ClientBinaryTransferHandler(BinaryTransferHandler):
    _upload_stub: binary_transfer_grpc_module.BinaryUploadStub
    _download_stub: binary_transfer_grpc_module.BinaryDownloadStub
    _max_chunk_size = 1024**2  # 1 MB
    known_binaries: Dict[UUID, bytes]
    _parent_client: SilaClient

    def __init__(self, client: SilaClient):
        self._upload_stub = binary_transfer_grpc_module.BinaryUploadStub(client._channel)
        self._download_stub = binary_transfer_grpc_module.BinaryDownloadStub(client._channel)
        self.known_binaries = {}
        self._parent_client = client

    def to_native_type(
        self,
        binary_uuid: UUID,
        toplevel_named_data_node: Optional[NamedDataNode] = None,
    ) -> bytes:
        """
        Get the payload of a binary either from the server or the cache.

        Parameters
        ----------
        binary_transfer_uuid : str
            The binary transfer uuid for which to get the payload.

        Returns
        -------
        bytes
            The complete binary payload.

        Raises
        ------
        InvalidBinaryTransferUUID
            If the provided binary transfer uuid is invalid or not known by the server.
        BinaryDownloadFailed
            If an error occured during the download of the binary.
        """

        if binary_uuid in self.known_binaries:
            return self.known_binaries[binary_uuid]

        try:
            binary_info = self.get_binary_info(str(binary_uuid))
            binary_chunks = self.get_chunks(str(binary_uuid), binary_info.binary_size, self._max_chunk_size)
            payload = b"".join(chunk.payload for chunk in binary_chunks)

            self.known_binaries[binary_uuid] = payload

            # request deletion to free up server resources
            self.delete_binary(str(binary_uuid))

            return payload
        except BinaryTransferError:
            raise
        except Exception as exception:
            raise BinaryDownloadFailed(f"Binary download failed with exception: {exception}") from exception

    def to_message(
        self,
        binary: bytes,
        *,
        toplevel_named_data_node: Parameter,
        metadata: Optional[Iterable[ClientMetadataInstance]] = None,
    ) -> SilaBinary:
        """Upload binary data to server"""
        n_chunks = self.__compute_chunk_count(len(binary))

        try:
            create_binary_response = self._upload_stub.CreateBinary(
                binary_transfer_pb2_module.CreateBinaryRequest(
                    binarySize=len(binary),
                    chunkCount=n_chunks,
                    parameterIdentifier=toplevel_named_data_node.fully_qualified_identifier,
                ),
                metadata=pack_metadata_for_grpc(metadata),
            )
        except Exception as ex:
            if isinstance(ex, grpc.RpcError) and ex.code() == grpc.StatusCode.ABORTED:
                details: bytes = standard_b64decode(ex.details())
                if details[0] == 0x08 or (details[0] == 0x12 and details[-2:] == b"\x08\x01"):
                    raise BinaryTransferError.from_rpc_error(ex)
                if details[0] in (0x1A, 0x22, 0x12):
                    raise SilaError.from_rpc_error(ex, self._parent_client)
            raise BinaryUploadFailed(f"Exception during binary upload: {ex}")

        try:
            binary_uuid = UUID(create_binary_response.binaryTransferUUID)

            chunk_requests = (
                binary_transfer_pb2_module.UploadChunkRequest(
                    binaryTransferUUID=str(binary_uuid),
                    chunkIndex=i,
                    payload=binary[i * self._max_chunk_size : (i + 1) * self._max_chunk_size],
                )
                for i in range(n_chunks)
            )

            chunk_responses = self._upload_stub.UploadChunk(chunk_requests)
            # UploadChunk can be implemented lazily so that a request is only processed once its response is requested
            consume_generator(chunk_responses)

            return SiLAFramework_pb2.Binary(binaryTransferUUID=str(binary_uuid))
        except Exception as ex:
            try:
                raise BinaryTransferError.from_rpc_error(ex)
            except:
                raise BinaryUploadFailed(f"Exception during binary upload: {ex}")

    def get_binary_info(self, binary_transfer_uuid: str) -> BinaryInfo:
        """
        Inspect the binary on the SiLA server with the provided binary transfer uuid.

        Parameters
        ----------
        binary_transfer_uuid : str
            The binary transfer uuid for which to request information.

        Returns
        -------
        BinaryInfo
            Additional information about the binary transfer.
        """

        try:
            binary_info_response = self._download_stub.GetBinaryInfo(
                binary_transfer_pb2_module.GetBinaryInfoRequest(binaryTransferUUID=binary_transfer_uuid)
            )
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.ABORTED:
                raise BinaryTransferError.from_rpc_error(rpc_error) from None

            raise BinaryDownloadFailed(rpc_error.details()) from rpc_error
        else:
            return BinaryInfo(
                binary_size=binary_info_response.binarySize,
                lifetime_of_binary=Duration(SiLAFramework_pb2).to_native_type(binary_info_response.lifetimeOfBinary),
            )

    def get_chunks(self, binary_transfer_uuid: str, binary_size: int, max_chunk_size: int) -> list[BinaryChunk]:
        """
        Download all chunks of the binary transfer.

        Parameters
        ----------
        binary_transfer_uuid : str
            The binary transfer uuid for which to download the chunks.
        binary_size : int
            The total size of the complete binary in bytes.
        max_chunk_size : int
            The maximum size for each chunk in bytes.

        Returns
        -------
        list[BinaryChunk]
            A list of all individual chunks, ordered by their occurrence in the final binary
            payload.
        """

        chunk_requests = (
            binary_transfer_pb2_module.GetChunkRequest(
                binaryTransferUUID=binary_transfer_uuid,
                offset=offset,
                length=size,
            )
            for offset, size in self.compute_chunks(binary_size, max_chunk_size)
        )

        binary_chunks = []
        try:
            for chunk_response in self._download_stub.GetChunk(chunk_requests):
                binary_chunk = BinaryChunk(
                    binary_transfer_uuid=chunk_response.binaryTransferUUID,
                    offset=chunk_response.offset,
                    payload=chunk_response.payload,
                    lifetime_of_binary=Duration(SiLAFramework_pb2).to_native_type(chunk_response.lifetimeOfBinary),
                )
                binary_chunks.append(binary_chunk)

        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.ABORTED:
                raise BinaryTransferError.from_rpc_error(rpc_error) from None

            raise BinaryDownloadFailed(rpc_error.details()) from rpc_error
        else:
            return sorted(binary_chunks, key=lambda chunk: chunk.offset)

    def delete_binary(self, binary_transfer_uuid: str) -> None:
        """
        Delete an binary from the server to free up its resources.

        Parameters
        ----------
        binary_transfer_uuid : str
            The binary transfer uuid for which to remove the data.
        """

        try:
            self._download_stub.DeleteBinary(
                binary_transfer_pb2_module.DeleteBinaryRequest(binaryTransferUUID=binary_transfer_uuid)
            )
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.ABORTED:
                raise BinaryTransferError.from_rpc_error(rpc_error) from None

            raise BinaryDownloadFailed(rpc_error.details()) from rpc_error

    def compute_chunks(self, binary_size: int, max_chunk_size: int) -> collections.abc.Iterable[tuple[int, int]]:
        """
        Compute an iterable of chunk indices for a given size.

        Parameters
        ----------
        binary_size : int
            The total size of the complete binary in bytes.
        max_chunk_size : int
            The maximum size for each chunk in bytes.

        Returns
        -------
        collections.abc.Iterable[tuple[int, int, int]]
            An iterable of chunk indices. Each tuple consists of the chunk's offset and its size in bytes.
        """

        return ((i, min(max_chunk_size, binary_size - i)) for i in range(0, binary_size, max_chunk_size))

    def __compute_chunk_count(self, binary_size: int) -> int:
        return binary_size // self._max_chunk_size + (1 if binary_size % self._max_chunk_size != 0 else 0)
