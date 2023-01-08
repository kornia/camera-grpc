
import asyncio
import logging
import time
from typing import Iterable, Optional, List

import kornia_rs as K
import cv2

import grpc
import camera_pb2
import camera_pb2_grpc


class CameraServer(camera_pb2_grpc.CameraServiceServicer):
    """Provides methods that implement functionality of route guide server."""

    def __init__(self) -> None:
        self.grabber: Optional[cv2.VideoCapture] = None
        self.encoder = K.ImageEncoder()

        self._frame_counter: int = 0

    async def StreamFrames(
        self, request: camera_pb2.StreamFramesRequest, context: grpc.aio.ServicerContext
    ) -> Iterable[camera_pb2.CameraFrame]:

        def stop_grabber(context):
            self.grabber.release()
            self.grabber = None

        context.add_done_callback(stop_grabber)

        self.grabber = cv2.VideoCapture(request.camera_id)
        fps_sleep_time: float = 1 / request.fps

        while True:
            ret, frame = self.grabber.read()
            if not ret:
                continue
            frame_encoded: List[int] = self.encoder.encode(frame.tobytes(), frame.shape)
            yield camera_pb2.CameraFrame(
                image_data=bytes(frame_encoded),
                frame_number=self._frame_counter,
                encoding_type="jpeg",
                image_size=camera_pb2.ImageSize(
                    height=frame.shape[0],
                    width=frame.shape[1]
                ),
                stamp=time.monotonic()
            )
            self._frame_counter += 1
            time.sleep(fps_sleep_time)


async def serve(port: int) -> None:
    server = grpc.aio.server()
    camera_pb2_grpc.add_CameraServiceServicer_to_server(
        CameraServer(), server)
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    port: int = 50051

    asyncio.run(serve(port))