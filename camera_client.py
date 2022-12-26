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


async def main(address: str, port: int):
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    async with grpc.aio.insecure_channel(f"{address}:{port}") as channel:
        stub = camera_pb2_grpc.CameraServiceStub(channel)
        request = camera_pb2.StreamFramesRequest(
            camera_id=0, fps=40)
        response_iterator = stub.StreamFrames(request)
        async for msg in response_iterator:
            print(f"Stamp: {msg.stamp}\nFrame num: {msg.frame_number}")
            img: np.ndarray = decode_frame(msg.image_data)
            cv2.imshow("image", img)
            cv2.waitKey(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    address: str = "localhost"
    port: int = 50051

    asyncio.run(main(address, port))