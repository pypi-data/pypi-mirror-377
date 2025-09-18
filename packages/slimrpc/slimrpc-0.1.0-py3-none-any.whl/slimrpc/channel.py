# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0

import asyncio
import datetime
import logging
import sys
import time
from collections.abc import AsyncGenerator, AsyncIterable, Callable
from dataclasses import dataclass
from typing import Any

if sys.version_info >= (3, 11):
    from asyncio import timeout_at as asyncio_timeout_at
else:
    from async_timeout import timeout_at as asyncio_timeout_at

import slim_bindings
from google.rpc import code_pb2, status_pb2

from slimrpc.common import (
    DEADLINE_KEY,
    MAX_TIMEOUT,
    RequestType,
    ResponseType,
    create_local_app,
    service_and_method_to_pyname,
    split_id,
)
from slimrpc.rpc import SRPCResponseError

logger = logging.getLogger(__name__)


@dataclass
class SLIMAppConfig:
    identity: str
    slim_client_config: dict
    enable_opentelemetry: bool = False
    shared_secret: str = ""


class ChannelFactory:
    def __init__(
        self,
        slim_app_config: SLIMAppConfig | None = None,
        local_app: slim_bindings.Slim | None = None,
    ) -> None:
        if slim_app_config is None and local_app is None:
            raise ValueError("Either slim_app_config or local_app must be provided")
        if slim_app_config is not None and local_app is not None:
            raise ValueError("Only one of slim_app_config or local_app can be provided")
        self._slim_app_config = slim_app_config
        self._local_app_lock = asyncio.Lock()
        self._local_app: slim_bindings.Slim | None = local_app

    async def get_local_app(self) -> slim_bindings.Slim:
        """
        Get or create the local SLIM instance
        """
        async with self._local_app_lock:
            if self._local_app is None:
                # Create local SLIM instance
                assert self._slim_app_config is not None, (
                    "slim_app_config must be provided to create a local app"
                )
                self._local_app = await create_local_app(
                    split_id(self._slim_app_config.identity),
                    self._slim_app_config.slim_client_config,
                    enable_opentelemetry=self._slim_app_config.enable_opentelemetry,
                    shared_secret=self._slim_app_config.shared_secret,
                )
                # Start receiving messages
                await self._local_app.__aenter__()
            return self._local_app

    async def close(self) -> None:
        """
        Close the channel factory
        """
        async with self._local_app_lock:
            if self._local_app is not None:
                if self._slim_app_config is None:
                    logger.debug("not closing local app as it was provided externally")
                    return
                await self._local_app.__aexit__(None, None, None)
            self._local_app = None

    def new_channel(self, remote: str) -> "Channel":
        return Channel(remote=remote, channel_factory=self)


class Channel:
    def __init__(
        self,
        remote: str,
        channel_factory: ChannelFactory,
    ) -> None:
        self.remote = split_id(remote)
        self.channel_factory = channel_factory

    async def close(self) -> None:
        """
        Close the channel.
        """
        return None

    async def _common_setup(
        self, method: str, metadata: dict[str, str] | None = None
    ) -> tuple[slim_bindings.PyName, slim_bindings.PySessionInfo, dict[str, str]]:
        service_name = service_and_method_to_pyname(self.remote, method)

        local_app = await self.channel_factory.get_local_app()
        await local_app.set_route(
            service_name,
        )

        # Create a session
        session = await local_app.create_session(
            slim_bindings.PySessionConfiguration.FireAndForget(
                max_retries=10,
                timeout=datetime.timedelta(seconds=1),
                sticky=True,
            )
        )

        return service_name, session, metadata or {}

    async def _delete_session(self, session: slim_bindings.PySessionInfo) -> None:
        local_app = await self.channel_factory.get_local_app()
        await local_app.delete_session(session.id)

    async def _send_unary(
        self,
        request: RequestType,
        session: slim_bindings.PySessionInfo,
        service_name: slim_bindings.PyName,
        metadata: dict[str, str],
        request_serializer: Callable,
        deadline: float,
    ) -> None:
        # Add deadline to metadata
        metadata[DEADLINE_KEY] = str(deadline)

        # Send the request
        request_bytes = request_serializer(request)
        local_app = await self.channel_factory.get_local_app()
        await local_app.publish(
            session,
            request_bytes,
            dest=service_name,
            metadata=metadata,
        )

    async def _send_stream(
        self,
        request_stream: AsyncIterable,
        session: slim_bindings.PySessionInfo,
        service_name: slim_bindings.PyName,
        metadata: dict[str, str],
        request_serializer: Callable,
        deadline: float,
    ) -> None:
        # Send the request
        local_app = await self.channel_factory.get_local_app()

        # Add deadline to metadata
        metadata[DEADLINE_KEY] = str(deadline)

        # Send requests
        async for request in request_stream:
            request_bytes = request_serializer(request)
            await local_app.publish(
                session,
                request_bytes,
                dest=service_name,
                metadata=metadata,
            )

        # Send enf of streaming message
        await local_app.publish(
            session,
            b"",
            dest=service_name,
            metadata={**metadata, "code": str(code_pb2.OK)},
        )

    async def _receive_unary(
        self,
        session: slim_bindings.PySessionInfo,
        response_deserializer: Callable,
        deadline: float,
    ) -> tuple[slim_bindings.PySessionInfo, Any]:
        # Wait for the response
        local_app = await self.channel_factory.get_local_app()

        async with asyncio_timeout_at(deadline):
            session_recv, response_bytes = await local_app.receive(
                session=session.id,
            )

            code = session_recv.metadata.get("code")
            if code != str(code_pb2.OK):
                status = status_pb2.Status.FromString(response_bytes)
                raise SRPCResponseError(status.code, status.message, status.details)

            response = response_deserializer(response_bytes)
            return session_recv, response

    async def _receive_stream(
        self,
        session: slim_bindings.PySessionInfo,
        response_deserializer: Callable,
        deadline: float,
    ) -> AsyncIterable:
        # Wait for the responses
        async def generator() -> AsyncIterable:
            try:
                while True:
                    local_app = await self.channel_factory.get_local_app()
                    session_recv, response_bytes = await local_app.receive(
                        session=session.id,
                    )

                    code = session_recv.metadata.get("code")
                    if code != str(code_pb2.OK):
                        status = status_pb2.Status.FromString(response_bytes)
                        raise SRPCResponseError(
                            status.code, status.message, status.details
                        )

                    if not response_bytes:
                        logger.debug("end of stream received")
                        break

                    response = response_deserializer(response_bytes)
                    yield response
            except SRPCResponseError:
                raise
            except Exception as e:
                logger.error(f"error receiving messages: {e}")
                raise

        async with asyncio_timeout_at(deadline):
            async for response in generator():
                yield response

    def stream_stream(
        self,
        method: str,
        request_serializer: Callable = lambda x: x,
        response_deserializer: Callable = lambda x: x,
    ) -> Callable:
        async def call_stream_stream(
            request_stream: AsyncIterable,
            timeout: int = MAX_TIMEOUT,
            metadata: dict | None = None,
        ) -> AsyncIterable:
            try:
                service_name, session, metadata = await self._common_setup(
                    method, metadata
                )

                # Send the requests
                await self._send_stream(
                    request_stream,
                    session,
                    service_name,
                    metadata,
                    request_serializer,
                    _compute_deadline(timeout),
                )

                # Wait for the responses
                async for response in self._receive_stream(
                    session, response_deserializer, _compute_deadline(timeout)
                ):
                    yield response
            finally:
                await self._delete_session(session)

        return call_stream_stream

    def stream_unary(
        self,
        method: str,
        request_serializer: Callable = lambda x: x,
        response_deserializer: Callable = lambda x: x,
    ) -> Callable:
        async def call_stream_unary(
            request_stream: AsyncIterable,
            timeout: int = MAX_TIMEOUT,
            metadata: dict | None = None,
        ) -> ResponseType:
            try:
                service_name, session, metadata = await self._common_setup(
                    method, metadata
                )

                # Send the requests
                await self._send_stream(
                    request_stream,
                    session,
                    service_name,
                    metadata,
                    request_serializer,
                    _compute_deadline(timeout),
                )

                # Wait for response
                _, ret = await self._receive_unary(
                    session, response_deserializer, _compute_deadline(timeout)
                )

                return ret
            finally:
                await self._delete_session(session)

        return call_stream_unary

    def unary_stream(
        self,
        method: str,
        request_serializer: Callable = lambda x: x,
        response_deserializer: Callable = lambda x: x,
    ) -> Callable:
        async def call_unary_stream(
            request: RequestType,
            timeout: int = MAX_TIMEOUT,
            metadata: dict[str, str] | None = None,
        ) -> AsyncGenerator:
            try:
                service_name, session, metadata = await self._common_setup(
                    method, metadata
                )

                # Send the request
                await self._send_unary(
                    request,
                    session,
                    service_name,
                    metadata,
                    request_serializer,
                    _compute_deadline(timeout),
                )

                # Wait for the responses
                async for response in self._receive_stream(
                    session, response_deserializer, _compute_deadline(timeout)
                ):
                    yield response
            finally:
                await self._delete_session(session)

        return call_unary_stream

    def unary_unary(
        self,
        method: str,
        request_serializer: Callable = lambda x: x,
        response_deserializer: Callable = lambda x: x,
    ) -> Callable:
        async def call_unary_unary(
            request: RequestType,
            timeout: int = MAX_TIMEOUT,
            metadata: dict[str, str] | None = None,
        ) -> ResponseType:
            try:
                service_name, session, metadata = await self._common_setup(
                    method, metadata
                )

                # Send request
                await self._send_unary(
                    request,
                    session,
                    service_name,
                    metadata,
                    request_serializer,
                    _compute_deadline(timeout),
                )

                # Wait for the response
                _, ret = await self._receive_unary(
                    session, response_deserializer, _compute_deadline(timeout)
                )

                return ret
            finally:
                await self._delete_session(session)

        return call_unary_unary


def _compute_deadline(timeout: int) -> float:
    return time.time() + float(timeout)
