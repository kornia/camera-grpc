import logging
import asyncio

import cv2
import numpy as np
import kornia_rs as K

import grpc

import camera_pb2
import camera_pb2_grpc


def decode_frame(decoder: K.ImageDecoder, data: bytes) -> np.ndarray:
    return np.from_dlpack(decoder.decode(data))


async def main(address: str, port: int):
    decoder = K.ImageDecoder()
    async with grpc.aio.insecure_channel(f"{address}:{port}") as channel:
        stub = camera_pb2_grpc.CameraServiceStub(channel)
        request = camera_pb2.StreamFramesRequest(
            camera_id=0, fps=40)
        response_iterator = stub.StreamFrames(request)
        async for msg in response_iterator:
            print(f"Stamp: {msg.stamp}\nFrame num: {msg.frame_number}")

            # await for blocking decoder function
            img: np.ndarray = await asyncio.get_running_loop().run_in_executor(
                None, lambda: decode_frame(decoder, msg.image_data))

            # visualize with opencv
            cv2.namedWindow("image", cv2.WINDOW_NORMAL)
            cv2.imshow("image", img)
            cv2.waitKey(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    address: str = "localhost"
    port: int = 50051

    asyncio.run(main(address, port))