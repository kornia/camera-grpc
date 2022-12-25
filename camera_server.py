
import asyncio
import logging
import time
from typing import Iterable
import cv2

import grpc
import camera_pb2
import camera_pb2_grpc


class CamerServer(camera_pb2_grpc.CameraServiceServicer):
    """Provides methods that implement functionality of route guide server."""

    def __init__(self) -> None:
        self.grabber = cv2.VideoCapture(0)
        self._frame_counter: int = 0

    def StreamFrames(
        self, request: camera_pb2.StreamFramesRequest, context: grpc.ServicerContext
    ) -> Iterable[camera_pb2.CameraFrame]:
        while True:
            ret, frame = self.grabber.read()
            if not ret:
                continue
            succeded, frame_encoded = cv2.imencode(".jpg", frame)
            if not succeded:
                continue
            yield camera_pb2.CameraFrame(
                data=frame_encoded.tobytes(),
                frame_number=self._frame_counter,
                encoding_type="jpg",
                image_size=camera_pb2.ImageSize(
                    height=frame.shape[0],
                    width=frame.shape[1]
                ),
                stamp=time.monotonic()
            )
            self._frame_counter += 1


async def serve(port: int) -> None:
    server = grpc.aio.server()
    camera_pb2_grpc.add_CameraServiceServicer_to_server(
        CamerServer(), server)
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    port: int = 50051
    asyncio.get_event_loop().run_until_complete(serve(port))