from concurrent.futures import ThreadPoolExecutor
import logging
import threading
from typing import Iterator
import asyncio

import grpc

import camera_pb2
import camera_pb2_grpc


async def stream_frames(address: str, port: int) -> None:
    async with grpc.aio.insecure_channel(f"{address}:{port}") as channel:
        stub = camera_pb2_grpc.CameraServiceStub(channel)
        request = camera_pb2.StreamFramesRequest()
        response_iterator = stub.StreamFrames(request)
        async for msg in response_iterator:
            print(f"Stamp: {msg.stamp}\nFrame num: {msg.frame_number}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    address: str = "localhost"
    port: int = 50051
    asyncio.run(stream_frames(address, port))