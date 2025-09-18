from __future__ import annotations

import platform
import ssl
import warnings
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Dict, Optional, Set, Type, TypeVar, Union
from uuid import UUID

import grpc

from sila2.client.client_feature import ClientFeature
from sila2.framework import DefinedExecutionError
from sila2.framework.defined_execution_error_node import DefinedExecutionErrorNode
from sila2.framework.fully_qualified_identifier import (
    FullyQualifiedDefinedExecutionErrorIdentifier,
    FullyQualifiedFeatureIdentifier,
    FullyQualifiedIdentifier,
)

if TYPE_CHECKING:
    from sila2.features.silaservice import SiLAServiceClient
    from sila2.framework.utils import HasFullyQualifiedIdentifier

ClientCls = TypeVar("ClientCls", bound="SilaClient")


class SilaClient:
    SiLAService: SiLAServiceClient
    """
    This Feature MUST be implemented by each SiLA Server.

    It specifies Commands and Properties to discover the Features a SiLA Server implements as well as details
    about the SiLA Server, like name, type, description, vendor and UUID.

    Any interaction described in this feature MUST not affect the behaviour of any other Feature.
    """

    _channel: grpc.Channel
    _features: Dict[str, ClientFeature]
    _children_by_fully_qualified_identifier: Dict[FullyQualifiedIdentifier, HasFullyQualifiedIdentifier]
    _registered_defined_execution_error_classes: Dict[
        FullyQualifiedDefinedExecutionErrorIdentifier, Type[DefinedExecutionError]
    ]
    _task_executor: ThreadPoolExecutor

    _expected_features: Set[FullyQualifiedFeatureIdentifier] = {
        FullyQualifiedFeatureIdentifier("org.silastandard/core/SiLAService/v1"),
    }

    __address: str
    __port: int

    def __init__(
        self,
        address: str,
        port: int,
        *,
        root_certs: Optional[bytes] = None,
        private_key: Optional[bytes] = None,
        cert_chain: Optional[bytes] = None,
        insecure: bool = False,
    ):
        """
        SiLA Client, which is connected to a SiLA Server

        Parameters
        ----------
        address
            IP address or hostname of the SiLA Server
        port
            Port of the SiLA Server
        root_certs
            PEM-encoded root certificates
        private_key
            PEM-encoded private key
        cert_chain
            PEM-encoded certificate chain
        insecure
            If ``True``, no encryption will be used

        Raises
        ------
        RuntimeError
            If the server does not implement required features
        """
        self.__address = address
        self.__port = port

        target = f"{self.__address}:{self.__port}"

        expected_server_uuid: Optional[UUID] = None
        if root_certs is not None or private_key is not None or cert_chain is not None:
            if insecure:
                raise ValueError("Cannot use certificate information with insecure connections")

            credentials = grpc.ssl_channel_credentials(
                root_certificates=root_certs, private_key=private_key, certificate_chain=cert_chain
            )

            # verify UUID from certificate
            expected_server_uuid = try_extract_server_uuid_from_server_cert(address, port)

            self._channel = grpc.secure_channel(target, credentials=credentials)
        elif insecure:
            self._channel = grpc.insecure_channel(target)
        else:
            self._channel = grpc.secure_channel(target, credentials=self.__create_default_ssl_channel_credentials())

        self._features = {}
        self._children_by_fully_qualified_identifier = {}
        self._registered_defined_execution_error_classes = {}

        # import locally to prevent circular import
        from sila2.features.silaservice import SiLAServiceFeature, UnimplementedFeature  # noqa: PLC0415 (local import)
        from sila2.framework.binary_transfer.client_binary_transfer_handler import (  # noqa: PLC0415 (local import)
            ClientBinaryTransferHandler,
        )

        self._binary_transfer_handler = ClientBinaryTransferHandler(self)

        # add SiLAService feature
        self.__add_feature(SiLAServiceFeature._feature_definition)
        self._register_defined_execution_error_class(
            SiLAServiceFeature.defined_execution_errors["UnimplementedFeature"], UnimplementedFeature
        )

        if expected_server_uuid is not None and UUID(self.SiLAService.ServerUUID.get()) != expected_server_uuid:
            raise RuntimeError("Server UUID does not match the UUID specified in the server certificate")

        # add other features
        for feature_id in self.SiLAService.ImplementedFeatures.get():
            if feature_id == SiLAServiceFeature.fully_qualified_identifier:
                continue
            try:
                self.__add_feature(self.SiLAService.GetFeatureDefinition(feature_id).FeatureDefinition)
            except ValueError as err:
                warnings.warn(f"Found invalid feature {feature_id!r}, ignoring it: {err}")
            except NameError:
                if self.__class__ != SilaClient:
                    raise RuntimeError(
                        "Using generated client class, but the server uses an incompatible version of feature "
                        f"'{feature_id}'. Please either update your generated client code, "
                        f"or use the generic sila2.client.SilaClient class instead."
                    )
                raise

        found_features: Set[FullyQualifiedFeatureIdentifier] = {
            f.fully_qualified_identifier for f in self._features.values()
        }
        if not self._expected_features.issubset(found_features):
            raise RuntimeError(
                f"Server does not implement the following required features: {self._expected_features - found_features}"
            )

        self._task_executor = ThreadPoolExecutor(max_workers=100)

    @property
    def address(self) -> str:
        """SiLA Server IP address or hostname"""
        return self.__address

    @property
    def port(self) -> int:
        """SiLA Server port"""
        return self.__port

    def close(self) -> None:
        """Close the connection to the SiLA Server, releasing all resources."""
        self._channel.close()

    @classmethod
    def discover(
        cls: Type[ClientCls],
        *,
        server_name: Optional[str] = None,
        server_uuid: Optional[Union[UUID, str]] = None,
        timeout: float = 0,
        root_certs: Optional[bytes] = None,
        private_key: Optional[bytes] = None,
        cert_chain: Optional[bytes] = None,
        insecure: bool = False,
    ) -> ClientCls:
        """
        Use SiLA Server Discovery to connect to a SiLA Server.
        If multiple matching servers are found, the returned client is connected to one of them.

        Parameters
        ----------
        server_name
            Only connect to SiLA Servers with this server name
        server_uuid
            Only connect to SiLA Servers with this server UUID
        timeout
            Time in seconds. If no matching server was found in this time, a ``TimeoutError`` will be raised
        root_certs
            PEM-encoded root certificates
        private_key
            PEM-encoded private key
        cert_chain
            PEM-encoded certificate chain
        insecure
            If ``True``, no encryption will be used

        Returns
        -------
        client
            SiLA Client connected to a discovered matching SiLA Server (instance of the calling class)

        Raises
        ------
        TimeoutError
            If no server was found in the given time
        RuntimeError
            If a server was found but did not implement required features
        """
        from sila2.discovery.browser import SilaDiscoveryBrowser  # noqa: PLC0415 (local import)

        with SilaDiscoveryBrowser(
            insecure=insecure, root_certs=root_certs, private_key=private_key, cert_chain=cert_chain, client_cls=cls
        ) as browser:
            return browser.find_server(server_name=server_name, server_uuid=server_uuid, timeout=timeout)

    def __add_feature(self, feature_definition: str) -> None:
        feature = ClientFeature(feature_definition, self)
        self._children_by_fully_qualified_identifier[feature.fully_qualified_identifier] = feature
        self._children_by_fully_qualified_identifier.update(feature.children_by_fully_qualified_identifier)
        self._features[feature._identifier] = feature

        setattr(self, feature._identifier, feature)

    def __enter__(self):
        """Context manager entry point"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point"""
        self.close()

    def _register_defined_execution_error_class(
        self, error_node: DefinedExecutionErrorNode, error_class: Type[DefinedExecutionError]
    ):
        self._registered_defined_execution_error_classes[error_node.fully_qualified_identifier] = error_class

    def clear_binary_transfer_download_cache(self) -> None:
        """Delete all downloaded binary transfer data."""
        self._binary_transfer_handler.known_binaries.clear()

    @staticmethod
    def __create_default_ssl_channel_credentials():
        # use default trust store
        if platform.system() == "Windows":
            # Windows-specific workaround: https://github.com/grpc/grpc/issues/25533#issuecomment-1830823902
            certs = ssl.create_default_context().get_ca_certs(binary_form=True)
            cert_string = ""
            for cert in certs:
                cert_string += ssl.DER_cert_to_PEM_cert(cert)
            credentials = grpc.ssl_channel_credentials(root_certificates=cert_string.encode("utf-8"))
        else:
            credentials = grpc.ssl_channel_credentials()
        return credentials


def try_extract_server_uuid_from_server_cert(address: str, port: int) -> Optional[UUID]:
    try:
        import ssl  # noqa: PLC0415 (local import)

        from cryptography import x509  # noqa: PLC0415 (local import)
        from cryptography.hazmat._oid import ObjectIdentifier  # noqa: PLC0415 (local import)
        from cryptography.hazmat.backends import default_backend  # noqa: PLC0415 (local import)
        from cryptography.x509 import ExtensionNotFound  # noqa: PLC0415 (local import)

        cert = x509.load_pem_x509_certificate(
            ssl.get_server_certificate((address, port)).encode("ascii"), backend=default_backend()
        )
        try:
            server_uuid_extension = cert.extensions.get_extension_for_oid(ObjectIdentifier("1.3.6.1.4.1.58583"))
            return UUID(server_uuid_extension.value.public_bytes().decode("ascii"))
        except ExtensionNotFound:
            warnings.warn("Server certificate is missing the extension 1.3.6.1.4.1.58583 to specify its UUID")
    except ImportError:
        return None
