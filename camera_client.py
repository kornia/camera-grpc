import logging
import asyncio

import cv2
import numpy as np

import grpc

import camera_pb2
import camera_pb2_grpc


def decode_frame(data: bytes) -> np.ndarray:
    return cv2.imdecode(
        np.frombuffer(data, dtype="uint8"), cv2.IMREAD_UNCHANGED)


async def main(address: str, port: int, window_name: str):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    async with grpc.aio.insecure_channel(f"{address}:{port}") as channel:
        stub = camera_pb2_grpc.CameraServiceStub(channel)
        request = camera_pb2.StreamFramesRequest()
        response_iterator = stub.StreamFrames(request)
        async for msg in response_iterator:
            print(f"Stamp: {msg.stamp}\nFrame num: {msg.frame_number}")
            img: np.ndarray = decode_frame(msg.image_data)
            cv2.imshow(window_name, img)
            cv2.waitKey(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    address: str = "localhost"
    port: int = 50051
    window_name: str = "image"

    asyncio.run(main(address, port, window_name))