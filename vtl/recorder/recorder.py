import os
from datetime import datetime
from typing import Optional

import cv2
import numpy as np

from vtl.image.screenshot import Screenshooter


class TimeLapseRecorder:

    def __init__(
            self,
            screen_shooter: Screenshooter,
            *,
            fps: int,
            save_dir: Optional[str] = None,
            diff_threshold: float = 0.0,
    ):
        """
        Arguments:
        ----------
        screenshotter: Screenshooter
            A Screenshooter object that will be used to take screenshots

        fps: int
            The number of frames per second

        key_binds: Optional[Dict[str, str]]
            A dictionary mapping key binds to their corresponding actions
            The actions can be:
                - 'start': Start the recording
                - 'stop': Stop the recording
                - 'cancel' Cancel the recording

        save_dir: Optional[str]
            The path to save the video to. If None, the video will be saved in the current directory
        """

        self.update_args(screen_shooter, fps=fps, save_dir=save_dir, diff_threshold=diff_threshold)

    def update_args(
            self,
            screen_shooter: Screenshooter,
            *,
            fps: int,
            save_dir: Optional[str] = None,
            diff_threshold: float = 0.0,
    ):
        self.screen_shooter = screen_shooter
        self.fps = fps

        self.save_dir = save_dir
        if self.save_dir is None:
            self.save_dir = self.default_save_dir

        self.diff_threshold = diff_threshold

        # Prepare state
        self.video_stream = None
        self.output_size = screen_shooter.output_size
        self.file_path = None
        self.is_recording = False
        self.last_frame = None
        self.area = self.output_size[0] * self.output_size[1]

        self.recorded_frames = 0

    @property
    def default_save_dir(self) -> str:
        return os.getcwd()

    def _start_new(self):
        """
        Start a new recording
        """
        if self.is_recording:
            return

        # Prepare the file
        current_date = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
        file_path = f'{self.save_dir}/{current_date}.mp4'
        self.file_path = file_path

        # Prepare the video stream
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        self.video_stream = cv2.VideoWriter(file_path, fourcc, self.fps, self.output_size, True)

        self.is_recording = True
        self.last_frame = None

    def _stop(self):
        """
        Stop the current recording
        """
        if not self.is_recording:
            return

        # Update state
        self.is_recording = False

        # Stop recording and save the video
        self.video_stream.release()
        self.video_stream = None

        self.recorded_frames = 0

    def _cancel(self):
        """
        Cancel the current recording
        """
        if not self.is_recording:
            return

        # Update state
        self.is_recording = False

        # Stop recording and delete the video
        self.video_stream.release()
        os.remove(self.file_path)
        self.video_stream = None

        self.recorded_frames = 0

    def _quit(self):
        """
        Quit the program
        """
        if self.is_recording:
            self._cancel()

        exit(0)

    def _record_frame(self):
        if not self.is_recording:
            return

        frame = self.screen_shooter()

        if not self.is_recording:
            return

        if self.last_frame is not None:
            difference = np.sum(np.any(self.last_frame != frame, axis=-1)) / self.area

            if difference < self.diff_threshold:
                return

        self.video_stream.write(frame)
        self.last_frame = frame

        self.recorded_frames += 1

    async def _record_frame_async(self):
        self._record_frame()

    def _record_frames(self):
        while True:
            self._record_frame()

    async def _record_frames_async(self):
        while True:
            try:
                await self._record_frame_async()
            except Exception:
                pass
