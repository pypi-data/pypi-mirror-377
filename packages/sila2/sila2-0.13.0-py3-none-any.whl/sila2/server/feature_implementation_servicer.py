from __future__ import annotations

import logging
import re
from collections import defaultdict
from contextlib import contextmanager
from datetime import timedelta
from queue import Queue
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, Iterator, List, NoReturn, Optional, Set, Tuple, Union
from uuid import UUID

import grpc
from google.protobuf.message import Message
from grpc import ServicerContext

from sila2.framework import (
    Command,
    DefinedExecutionError,
    InvalidMetadata,
    Metadata,
    NoMetadataAllowed,
    Property,
    UndefinedExecutionError,
    ValidationError,
)
from sila2.framework.abc.sila_error import SilaError
from sila2.framework.defined_execution_error_node import DefinedExecutionErrorNode
from sila2.framework.errors.invalid_command_execution_uuid import InvalidCommandExecutionUUID
from sila2.framework.feature import Feature
from sila2.framework.fully_qualified_identifier import FullyQualifiedIdentifier, FullyQualifiedMetadataIdentifier
from sila2.framework.pb2.custom_protocols import AffectedCallsMessage
from sila2.framework.property.observable_property import ObservableProperty
from sila2.framework.utils import FullyQualifiedIdentifierRegex, raise_as_rpc_error
from sila2.server.feature_implementation_base import FeatureImplementationBase
from sila2.server.metadata_dict import MetadataDict
from sila2.server.observables.observable_command_manager import ObservableCommandManager
from sila2.server.observables.subscription_manager_thread import SubscriptionManagerThread

if TYPE_CHECKING:
    from sila2.framework.pb2.SiLAFramework_pb2 import CommandExecutionUUID as SilaCommandExecutionUUID
    from sila2.server import ObservableCommandInstance
    from sila2.server.sila_server import SilaServer


class FeatureImplementationServicer:
    parent_server: SilaServer
    feature: Feature
    implementation: Optional[FeatureImplementationBase]
    observable_command_managers: Dict[str, Dict[UUID, ObservableCommandManager]]
    observable_property_subscription_managers: Dict[str, Dict[Optional[Queue], SubscriptionManagerThread]]

    def __init__(self, parent_server: SilaServer, feature: Feature):
        self.parent_server = parent_server
        self.feature = feature
        self.implementation = None
        self.observable_command_managers = defaultdict(dict)
        self.observable_property_subscription_managers = {}
        self.logger = logging.getLogger(feature._identifier)

    def start(self):
        self.__start_observable_property_listeners()
        self.implementation.start()

    def set_implementation(self, implementation: FeatureImplementationBase):
        self.logger.debug(f"Setting implementation to {implementation}")
        self.implementation = implementation

        for prop in self.feature._unobservable_properties.values():
            setattr(self, f"Get_{prop._identifier}", self.__get_unobservable_property_get_call(prop._identifier))
        for cmd in self.feature._unobservable_commands.values():
            setattr(self, cmd._identifier, self.__get_unobservable_command_init_call(cmd._identifier))
        for prop in self.feature._observable_properties.values():
            setattr(
                self, f"Subscribe_{prop._identifier}", self.__get_observable_property_subscribe_call(prop._identifier)
            )
        for cmd in self.feature._observable_commands.values():
            setattr(self, cmd._identifier, self.__get_observable_command_init_call(cmd._identifier))
            setattr(self, f"{cmd._identifier}_Info", self.__get_observable_command_info_subscribe_call(cmd._identifier))
            setattr(
                self,
                f"{cmd._identifier}_Intermediate",
                self.__get_observable_command_intermediate_subscribe_call(cmd._identifier),
            )
            setattr(self, f"{cmd._identifier}_Result", self.__get_observable_command_result_get_call(cmd._identifier))
        for metadata in self.feature.metadata_definitions.values():
            setattr(
                self,
                f"Get_FCPAffectedByMetadata_{metadata._identifier}",
                self.__get_fpc_affected_by_metadata_call(metadata._identifier),
            )

    def __start_observable_property_listeners(self):
        self.logger.debug("Starting subscription managers for observable properties")
        for prop in self.feature._observable_properties.values():
            manager = SubscriptionManagerThread(
                prop.fully_qualified_identifier,
                getattr(self.implementation, f"_{prop._identifier}_producer_queue"),
                prop.to_message,
            )
            self.observable_property_subscription_managers[prop._identifier] = {None: manager}
            manager.start()

    def __get_observable_command_manager(
        self, command_id: str, execution_uuid: UUID, context: ServicerContext
    ) -> ObservableCommandManager:
        manager = self.observable_command_managers[command_id].get(execution_uuid)
        if manager is None:
            self.__raise_as_rpc_error(
                InvalidCommandExecutionUUID(f"No running command instance with the execution uuid {execution_uuid}"),
                context,
            )
        return manager

    def __get_unobservable_command_init_call(self, command_id: str) -> Callable[[Message, ServicerContext], Message]:
        cmd = self.feature._unobservable_commands[command_id]
        impl_func: Callable = getattr(self.implementation, command_id)

        def wrapper(request: Message, context: ServicerContext) -> Message:
            self.logger.info(f"Request: unobservable command {command_id}")
            metadata = self.__extract_metadata(context, self.parent_server, cmd)
            allowed_errors = self.__find_allowed_defined_execution_errors(cmd, metadata)
            params = self.__unpack_parameters(cmd, request, context)

            with raises_rpc_errors(context, self.logger, allowed_errors):
                self.__apply_metadata_interceptors(None, metadata, cmd.fully_qualified_identifier)
                response = impl_func(*params, metadata=metadata)
                self.logger.info(f"Implementation returned {response!r}")
                return cmd.responses.to_message(response)

        return wrapper

    def __get_unobservable_property_get_call(self, property_id: str) -> Callable[[Message, ServicerContext], Message]:
        prop = self.feature._unobservable_properties[property_id]
        impl_func: Callable = getattr(self.implementation, f"get_{property_id}")

        def wrapper(request, context: ServicerContext):
            self.logger.info(f"Request: unobservable property {property_id}")
            metadata = self.__extract_metadata(context, self.parent_server, prop)
            allowed_errors = self.__find_allowed_defined_execution_errors(prop, metadata)

            with raises_rpc_errors(context, self.logger, allowed_errors):
                self.__apply_metadata_interceptors(None, metadata, prop.fully_qualified_identifier)
                response = impl_func(metadata=metadata)
                self.logger.info(f"Implementation returned {response!r}")
                return prop.to_message(response)

        return wrapper

    def __get_observable_command_init_call(self, command_id: str) -> Callable[[Message, ServicerContext], Message]:
        cmd = self.feature._observable_commands[command_id]
        impl_func: Callable = getattr(self.implementation, command_id)
        default_lifetime_of_execution: Optional[timedelta] = getattr(
            self.implementation, f"{command_id}_default_lifetime_of_execution", None
        )

        def wrapper(request: Message, context: ServicerContext) -> Message:
            self.logger.info(f"Request: observable command initiation for {command_id}")
            metadata = self.__extract_metadata(context, self.parent_server, cmd)

            params = self.__unpack_parameters(cmd, request, context)

            def _func_to_execute(instance: ObservableCommandInstance) -> Message:
                self.__apply_metadata_interceptors(None, metadata, cmd.fully_qualified_identifier)
                response = impl_func(
                    *params,
                    metadata=metadata,
                    instance=instance,
                )
                self.logger.info(f"Implementation returned {response!r}")
                return cmd.responses.to_message(response)

            command_manager = ObservableCommandManager(
                self.parent_server, cmd, _func_to_execute, metadata, default_lifetime_of_execution
            )
            self.observable_command_managers[command_id][command_manager.command_execution_uuid] = command_manager

            if default_lifetime_of_execution is None:
                lifetime_of_execution_message = None
            else:
                seconds, rest = divmod(default_lifetime_of_execution.total_seconds(), 1)
                lifetime_of_execution_message = self.feature._pb2_module.SiLAFramework__pb2.Duration(
                    seconds=round(seconds), nanos=round(rest * 1e9)
                )

            return self.feature._pb2_module.SiLAFramework__pb2.CommandConfirmation(
                commandExecutionUUID=self.feature._pb2_module.SiLAFramework__pb2.CommandExecutionUUID(
                    value=str(command_manager.command_execution_uuid)
                ),
                lifetimeOfExecution=lifetime_of_execution_message,
            )

        return wrapper

    def __get_observable_command_info_subscribe_call(
        self, command_id: str
    ) -> Callable[[SilaCommandExecutionUUID, ServicerContext], Iterator[Message]]:
        def wrapper(request: SilaCommandExecutionUUID, context: ServicerContext) -> Iterator[Message]:
            self.logger.info(f"Request: observable command info subscription for {command_id}")
            try:
                exec_uuid = UUID(request.value)
            except ValueError:
                raise_as_rpc_error(InvalidCommandExecutionUUID(f"Not a valid UUID string: {request.value!r}"), context)

            manager = self.__get_observable_command_manager(command_id, exec_uuid, context)

            with raises_rpc_errors(context, self.logger):
                for value in manager.subscribe_to_execution_infos(context):
                    yield value
                self.logger.info(f"Cancelled by client: execution info subscription for {command_id}")

        return wrapper

    def __get_observable_command_intermediate_subscribe_call(
        self, command_id: str
    ) -> Callable[[SilaCommandExecutionUUID, ServicerContext], Iterator[Message]]:
        def wrapper(request: SilaCommandExecutionUUID, context: ServicerContext) -> Iterator[Message]:
            self.logger.info(f"Request: observable command intermediate response subscription for {command_id}")
            try:
                exec_uuid = UUID(request.value)
            except ValueError:
                raise_as_rpc_error(InvalidCommandExecutionUUID(f"Not a valid UUID string: {request.value!r}"), context)

            manager = self.__get_observable_command_manager(command_id, exec_uuid, context)

            with raises_rpc_errors(context, self.logger):
                for value in manager.subscribe_to_intermediate_responses(context):
                    yield value
                self.logger.info(f"Cancelled by client: intermediate response subscription for {command_id}")

        return wrapper

    def __get_observable_command_result_get_call(
        self, command_id: str
    ) -> Callable[[SilaCommandExecutionUUID, ServicerContext], Message]:
        cmd = self.feature._observable_commands[command_id]

        def wrapper(request: SilaCommandExecutionUUID, context: ServicerContext) -> Message:
            self.logger.info(f"Request: observable command result for {command_id}")
            try:
                exec_uuid = UUID(request.value)
            except ValueError:
                raise_as_rpc_error(InvalidCommandExecutionUUID(f"Not a valid UUID string: {request.value!r}"), context)

            manager = self.__get_observable_command_manager(command_id, exec_uuid, context)
            allowed_errors = self.__find_allowed_defined_execution_errors(cmd, manager.metadata)

            with raises_rpc_errors(context, self.logger, allowed_errors):
                responses = manager.get_responses()
                self.logger.info(f"Returning {responses}")
                return responses

        return wrapper

    def __get_observable_property_subscribe_call(
        self, property_id: str
    ) -> Callable[[Message, ServicerContext], Iterator[Message]]:
        prop = self.feature._observable_properties[property_id]
        impl_func = getattr(self.implementation, f"{property_id}_on_subscription")

        def wrapper(request: Message, context: ServicerContext) -> Iterator[Message]:
            self.logger.info(f"Request: observable property subscription for {property_id}")
            metadata = self.__extract_metadata(context, self.parent_server, prop)
            allowed_errors = self.__find_allowed_defined_execution_errors(prop, metadata)

            with raises_rpc_errors(context, self.logger, allowed_errors):
                self.__apply_metadata_interceptors(None, metadata, prop.fully_qualified_identifier)

                producer_queue: Queue = impl_func(metadata=metadata)
                manager = self.__get_observable_property_subscription_thread_for_queue(prop, producer_queue)

                subscriber_stream = manager.add_subscription(context)
                for value in subscriber_stream:
                    if isinstance(value, BaseException):
                        raise value
                    else:
                        yield value
                self.logger.info(f"Cancelled by client: observable property subscription for {property_id}")

        return wrapper

    def __get_fpc_affected_by_metadata_call(
        self, metadata_id: str
    ) -> Callable[[Message, ServicerContext], AffectedCallsMessage]:
        metadata_node = self.feature.metadata_definitions[metadata_id]
        impl_func = getattr(self.implementation, f"get_calls_affected_by_{metadata_id}")

        def wrapper(request: Message, context: ServicerContext) -> AffectedCallsMessage:
            self.logger.info(f"Request: Calls affected by {metadata_id}")
            with raises_rpc_errors(context, self.logger):
                affected_calls = impl_func()
                self.logger.info(f"Returning {affected_calls}")
                return metadata_node.to_affected_calls_message(affected_calls)

        return wrapper

    def cancel_all_subscriptions(self):
        self.logger.info("Cancelling all subscriptions")
        for managers in self.observable_property_subscription_managers.values():
            for manager in managers.values():
                manager.cancel_producer()

    def __apply_metadata_interceptors(self, parameters: Any, metadata: MetadataDict, target: FullyQualifiedIdentifier):
        for interceptor in self.parent_server.metadata_interceptors:
            if any(m.fully_qualified_identifier in interceptor.affected_metadata for m in metadata):
                self.logger.info(f"Applying metadata interceptor {interceptor}")
                interceptor.intercept(parameters, metadata, target)

    def __unpack_parameters(self, command: Command, request, context: ServicerContext) -> Tuple[Any, ...]:
        try:
            parameters = command.parameters.to_native_type(request)
            self.logger.info(f"Unpacked parameters: {parameters}")
            return parameters
        except ValidationError as val_err:
            self.__raise_as_rpc_error(val_err, context)

    def __find_allowed_defined_execution_errors(
        self,
        origin: Union[Command, Property],
        metadata: Iterable[Metadata],
    ) -> List[DefinedExecutionErrorNode]:
        allowed_errors: List[DefinedExecutionErrorNode] = origin.defined_execution_errors.copy()
        for m in metadata:
            allowed_errors.extend(m.defined_execution_errors)
        self.logger.debug(f"Allowed defined execution errors: {[err._identifier for err in allowed_errors]}")
        return allowed_errors

    def __extract_metadata(
        self, context: grpc.ServicerContext, server: SilaServer, origin: Union[Property, Command]
    ) -> MetadataDict:
        self.logger.debug("Extracting metadata")

        # get expected metadata
        expected_metadata: Set[FullyQualifiedMetadataIdentifier] = set()
        for feature_servicer in server.feature_servicers.values():
            for meta_id, meta in feature_servicer.feature.metadata_definitions.items():
                raw_affected_calls: List[Union[Feature, Command, Property, FullyQualifiedIdentifier]] = getattr(
                    feature_servicer.implementation, f"get_calls_affected_by_{meta_id}"
                )()
                affected_fqis = [
                    obj if isinstance(obj, FullyQualifiedIdentifier) else obj.fully_qualified_identifier
                    for obj in raw_affected_calls
                ]

                if (
                    origin.fully_qualified_identifier in affected_fqis
                    or origin.parent_feature.fully_qualified_identifier in affected_fqis
                ):
                    expected_metadata.add(meta.fully_qualified_identifier)
        self.logger.debug(f"Expected metadata: {expected_metadata}")

        # ignore expected metadata if call targets SiLAService
        from sila2.features.silaservice import SiLAServiceFeature  # noqa: PLC0415 (local import)

        call_targets_silaservice = (
            origin.parent_feature.fully_qualified_identifier == SiLAServiceFeature.fully_qualified_identifier
        )
        if call_targets_silaservice and expected_metadata:
            self.logger.warning(
                f"Call to {origin.fully_qualified_identifier} expected metadata {expected_metadata}, "
                f"ignoring (SiLAService cannot be target of metadata)"
            )
            expected_metadata = set()

        # get received metadata
        received_metadata: Dict[FullyQualifiedMetadataIdentifier, Any] = {}
        for raw_key, value in context.invocation_metadata():
            if not re.fullmatch(
                f"sila/{FullyQualifiedIdentifierRegex.MetadataIdentifier}/bin",
                raw_key.replace("-", "/"),
                flags=re.IGNORECASE,
            ):
                continue

            key = raw_key[5:-4].replace("-", "/")

            # raise NoMetadataAllowed if metadata targeted SiLAService
            if call_targets_silaservice:
                self.__raise_as_rpc_error(
                    NoMetadataAllowed(
                        f"Calls to the SiLAService feature must not contain SiLA Client Metadata "
                        f"(call target: {origin.fully_qualified_identifier}, received metadata key: {key})"
                    ),
                    context,
                )

            # try to parse received metadata
            try:
                meta: Metadata = server.children_by_fully_qualified_identifier[FullyQualifiedIdentifier(key)]
                received_metadata[meta.fully_qualified_identifier] = meta.to_native_type(value)
            except KeyError:
                self.__raise_as_rpc_error(InvalidMetadata(f"Server has no metadata {key}"), context)
            except Exception as ex:
                if not isinstance(ex, InvalidMetadata):
                    ex = InvalidMetadata(f"Failed to deserialize metadata value for {key!r}: {ex}")
                self.__raise_as_rpc_error(ex, context)
        self.logger.debug(f"Received metadata: {received_metadata}")

        # check if all required metadata was received
        for expected_meta_fqi in expected_metadata:
            if expected_meta_fqi not in received_metadata:
                self.__raise_as_rpc_error(
                    InvalidMetadata(f"Did not receive required metadata '{expected_meta_fqi}'"), context
                )

        # ignore received but not expected metadata
        metadata_to_forward = {}
        for received_metadata_fqi, metadata_item in received_metadata.items():
            if received_metadata_fqi not in expected_metadata:
                self.logger.warning(f"Received unexpected metadata {received_metadata_fqi}, ignoring")
            else:
                metadata_to_forward[received_metadata_fqi] = metadata_item

        return MetadataDict(parent_server=self.parent_server, base_dict=metadata_to_forward)

    def __raise_as_rpc_error(self, error: SilaError, context: grpc.ServicerContext) -> NoReturn:
        self.logger.exception("Raising exception as RpcError")
        raise_as_rpc_error(error, context)

    def __get_observable_property_subscription_thread_for_queue(
        self, prop: ObservableProperty, queue: Optional[Queue]
    ) -> SubscriptionManagerThread:
        prop_managers = self.observable_property_subscription_managers[prop._identifier]

        # default queue
        if queue is None:
            return prop_managers[None]

        # subscribe to existing custom queue
        if queue in prop_managers:
            return prop_managers[queue]

        # new custom queue
        manager = SubscriptionManagerThread(prop.fully_qualified_identifier, queue, prop.to_message)
        prop_managers[queue] = manager
        manager.start()
        return manager


@contextmanager
def raises_rpc_errors(
    context: ServicerContext,
    logger: logging.Logger,
    allowed_defined_execution_errors: Optional[Iterable[DefinedExecutionErrorNode]] = None,
):
    try:
        yield
    except Exception as ex:
        logger.exception("Caught exception, raising as RpcError")
        if isinstance(ex, NotImplementedError):
            context.abort(grpc.StatusCode.UNIMPLEMENTED, "The requested functionality is not implemented")

        if not isinstance(ex, SilaError):
            raise_as_rpc_error(UndefinedExecutionError.from_exception(ex), context)

        if isinstance(ex, ValidationError) and ex.parameter_fully_qualified_identifier is None:
            raise_as_rpc_error(
                UndefinedExecutionError(
                    f"Server tried to respond with invalid value: Caught ValidationError {str(ex)!r}"
                ),
                context,
            )

        allowed_error_identifiers = [err.fully_qualified_identifier for err in allowed_defined_execution_errors]
        if isinstance(ex, DefinedExecutionError) and ex.fully_qualified_identifier not in allowed_error_identifiers:
            logger.warning(
                "Defined Execution Error '%s' is not allowed here, raising as Undefined Execution Error",
                ex.__class__.__name__,
            )
            raise_as_rpc_error(UndefinedExecutionError.from_exception(ex), context)

        raise_as_rpc_error(ex, context)
