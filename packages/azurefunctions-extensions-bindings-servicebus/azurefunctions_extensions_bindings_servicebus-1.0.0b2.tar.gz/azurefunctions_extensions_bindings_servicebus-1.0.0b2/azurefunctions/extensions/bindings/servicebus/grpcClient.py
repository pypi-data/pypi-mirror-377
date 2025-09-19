# Copyright (c) .NET Foundation. All rights reserved.
# Licensed under the MIT License.

import grpc
from typing import Any, Optional, Type


class GrpcChannelError(Exception):
    """Exception raised when gRPC channel creation fails."""


class GrpcClientFactory:
    """
    Factory class for creating gRPC clients from generated Python stubs.

    Python requires `.proto` files to be compiled into
    `_pb2.py` and `_pb2_grpc.py` modules before use. This factory assumes
    those files are already generated and importable.

    Example:
        from my_service_pb2_grpc import MyServiceStub

        client = GrpcClientFactory.create_client(
            service_stub=MyServiceStub,
            address="localhost:50051",
            grpc_max_message_length=4 * 1024 * 1024,  # 4 MB
        )
    """

    @staticmethod
    def create_client(
        service_stub: Type[Any],
        address: str,
        grpc_max_message_length: int = 4 * 1024 * 1024,
        root_certificates: Optional[bytes] = None,
    ) -> Any:
        """
        Creates and returns a gRPC client for the given service stub.

        Args:
            service_stub: The generated service stub class (e.g. `MyServiceStub`).
            address: The server address (e.g., "localhost:50051").
            grpc_max_message_length: Max message size for send/receive.
            root_certificates: Optional root certificates for TLS.

        Returns:
            An instance of the gRPC client stub.
        """

        options = [
            ("grpc.max_send_message_length", grpc_max_message_length),
            ("grpc.max_receive_message_length", grpc_max_message_length),
        ]

        try:
            channel = grpc.insecure_channel(address, options=options)
        except Exception as e:
            raise GrpcChannelError(f"Failed to create gRPC channel. URL: {address},"
                                   f" Options: {options}, Error: {e}")

        return service_stub(channel)
