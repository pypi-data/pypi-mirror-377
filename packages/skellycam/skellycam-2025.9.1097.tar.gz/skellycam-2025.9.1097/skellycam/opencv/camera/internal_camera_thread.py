import logging
import multiprocessing
import threading
import time
import traceback

import cv2

from skellycam.detection.models.frame_payload import FramePayload
from skellycam.opencv.camera.models.camera_config import CameraConfig
from skellycam.opencv.config.apply_config import apply_configuration
from skellycam.opencv.config.determine_backend import determine_backend

logger = logging.getLogger(__name__)


class VideoCaptureThread(threading.Thread):
    def __init__(
            self,
            config: CameraConfig,
            ready_event: multiprocessing.Event = None,
    ):
        super().__init__()
        self._previous_frame_timestamp_ns = None
        self._new_frame_ready = False
        self.daemon = False

        if ready_event is None:
            self._ready_event = multiprocessing.Event()
            self._ready_event.set()
        else:
            self._ready_event = ready_event

        self._config = config
        self._is_capturing_frames = False
        self._is_recording_frames = False

        self._number_of_frames_received: int = 0

        # self._elapsed_during_frame_grab = [] #TODO
        self._capture_timestamps = []
        self._mean_frames_per_second = None
        self._frame: FramePayload = FramePayload()
        self._cv2_video_capture = self._create_cv2_capture()

    @property
    def first_frame_timestamp(self):
        if len(self._capture_timestamps) > 0:
            return self._capture_timestamps[0]
        return None

    #
    # @property
    # def mean_frames_per_second(self):
    #     return self._mean_frames_per_second
    #
    # def update_mean_frames_per_second(self, latest_frame_timestamp_ns: float):
    #
    #     if self._previous_frame_timestamp_ns is None:
    #         self._previous_frame_timestamp_ns = latest_frame_timestamp_ns
    #         return 0
    #
    #     frame_duration_in_seconds = ((latest_frame_timestamp_ns - self._previous_frame_timestamp_ns) / 1e9) ** -1
    #
    #     if self._mean_frames_per_second is None:
    #         self._mean_frames_per_second = frame_duration_in_seconds
    #         return self._mean_frames_per_second
    #
    #     self._mean_frames_per_second = (self._mean_frames_per_second + frame_duration_in_seconds) / 2
    #
    #     return self._mean_frames_per_second

    @property
    def latest_frame(self) -> FramePayload:
        self._new_frame_ready = False
        self._frame.number_of_frames_recorded = self._frame.number_of_frames_recorded
        return self._frame

    @property
    def new_frame_ready(self):
        return self._new_frame_ready

    @property
    def is_capturing_frames(self) -> bool:
        """Is the thread capturing frames from the cameras (but not necessarily recording them, that's handled by `is_recording_frames`)"""
        return self._is_capturing_frames

    def run(self):
        self._start_frame_loop()

    def _start_frame_loop(self):
        self._is_capturing_frames = True
        logger.info(
            f"Camera ID: [{self._config.camera_id}] Frame capture loop has started"
        )
        try:
            while self._is_capturing_frames:
                try:
                    self._frame = self._get_next_frame()
                except Exception as e:
                    logger.error(e)


        except:
            logger.error(
                f"Camera ID: [{self._config.camera_id}] Frame loop thread exited due to error"
            )
            traceback.print_exc()
        else:
            logger.info(
                f"Camera ID: [{self._config.camera_id}] Frame capture has stopped."
            )

    def _get_next_frame(self):
        try:
            self._cv2_video_capture.grab()
            success, image = self._cv2_video_capture.retrieve()
            retrieval_timestamp = time.perf_counter_ns()
            if self._config.rotate_video_cv2_code != -1:
                image = cv2.rotate(image, self._config.rotate_video_cv2_code)

        except:
            logger.error(f"Failed to read frame from Camera: {self._config.camera_id}")
            raise Exception
        else:
            self._new_frame_ready = success

        if success:
            self._number_of_frames_received += 1

        return FramePayload(
            success=success,
            image=image,
            timestamp_ns=retrieval_timestamp,
            number_of_frames_received=self._number_of_frames_received,
            camera_id=str(self._config.camera_id),
        )

    def _create_cv2_capture(self):
        logger.info(f"Connecting to Camera: {self._config.camera_id}...")
        cap_backend = determine_backend()

        try:
            self._cv2_video_capture.release()
        except:
            pass

        capture = cv2.VideoCapture(int(self._config.camera_id), cap_backend)

        try:
            success, image = capture.read()
        except Exception as e:
            logger.error(
                f"Problem when trying to read frame from Camera: {self._config.camera_id}"
            )
            traceback.print_exc()
            raise e

        if not success or image is None:
            logger.error(
                f"Failed to read frame from camera at port# {self._config.camera_id}: "
                f"returned value: {success}, "
                f"returned image: {image} - releasing, closing, and deleting capture object and re-running self._create_cv2_capture()"
            )
            capture.release()
            del capture
            return self._create_cv2_capture()

        apply_configuration(capture, self._config)

        logger.info(f"Successfully connected to Camera: {self._config.camera_id}!")
        if not self._ready_event.is_set():
            self._ready_event.set()

        return capture

    def stop(self):
        self._is_capturing_frames = False
        if self._cv2_video_capture is not None:
            logger.debug(
                f"Releasing `opencv_video_capture_object` for Camera: {self._config.camera_id}"
            )
            self._cv2_video_capture.release()

    def update_camera_config(self, new_config: CameraConfig):
        self._config = new_config
        logger.info(f"Updating Camera: {self._config.camera_id} config to {new_config}")
        apply_configuration(self._cv2_video_capture, new_config)
