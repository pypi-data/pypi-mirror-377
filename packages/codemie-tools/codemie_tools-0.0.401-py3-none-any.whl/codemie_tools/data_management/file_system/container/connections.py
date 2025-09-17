from tenacity import retry, retry_if_exception_cause_type, stop_after_attempt, wait_fixed
import zmq
import zmq.asyncio
from zmq.asyncio import Context
from typing import Self
import functools
import asyncio


def timeout(timeout: int):
    def decorator(coroutine_func):
        @functools.wraps(coroutine_func)
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(coroutine_func(*args, **kwargs), timeout=timeout)

        return wrapper

    return decorator


class ARouter:
    def __init__(self, socket: zmq.asyncio.Socket, context: zmq.asyncio.Context, port: int) -> None:
        self.socket = socket
        self.context = context
        self.port = port

    @classmethod
    def create(cls) -> Self:
        context = Context()  # pyright: ignore
        router = context.socket(zmq.ROUTER)
        port = router.bind_to_random_port("tcp://0.0.0.0")
        return cls(router, context, port)

    async def arecv_msg(self) -> tuple[bytes, bytes]:
        """
        Receive a message using ZMQ.

        Returns:
            tuple[0] - identity
            tuple[-1] - payload
        """
        frames = await self.socket.recv_multipart()
        return frames[0], frames[-1]

    def __del__(self):
        self.socket.close()
        self.context.term()


class Router:
    def __init__(self, socket: zmq.Socket, context: zmq.Context, port: int) -> None:
        self.socket = socket
        self.context = context
        self.port = port

    @classmethod
    def create(cls) -> Self:
        context = zmq.Context()  # pyright: ignore
        router = context.socket(zmq.ROUTER)
        port = router.bind_to_random_port("tcp://0.0.0.0")
        return cls(router, context, port)

    def recv_msg(self) -> tuple[bytes, bytes]:
        """
        Receive a message using ZMQ.

        Returns:
            tuple[0] - identity
            tuple[-1] - payload
        """
        frames = self.socket.recv_multipart()
        return frames[0], frames[-1]

    def __del__(self):
        self.socket.close()
        self.context.term()


class ADealer:
    def __init__(self, port: int, identity: bytes):
        self.context: zmq.asyncio.Context = Context()  # pyright: ignore
        self.socket: zmq.asyncio.Socket = self.context.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, identity)
        self.port = port

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_cause_type(Exception),
    )
    def __enter__(self):
        self.socket.connect(f"tcp://0.0.0.0:{self.port}")
        return self

    def __exit__(self, exec_type, exec_value, traceback):
        self.socket.close()
        self.context.term()

    async def asend_msg(self, data_bytes: bytes):
        await self.socket.send(data_bytes)


class Dealer:
    def __init__(self, port: int, identity: bytes):
        self.context: zmq.Context = zmq.Context()  # pyright: ignore
        self.socket: zmq.Socket = self.context.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, identity)
        self.port = port

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_cause_type(Exception),
    )
    def __enter__(self):
        self.socket.connect(f"tcp://0.0.0.0:{self.port}")
        return self

    def __exit__(self, exec_type, exec_value, traceback):
        self.socket.close()
        self.context.term()

    def send_msg(self, data_bytes: bytes):
        self.socket.send(data_bytes)
