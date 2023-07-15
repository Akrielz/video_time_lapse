import os
from datetime import datetime
from threading import Thread
from typing import Dict, Optional

import cv2
import numpy as np

from vtl.image.screenshot import Screenshooter
from vtl.keyboard.key_listener import KeyListener


class TimeLapseRecorder:

    def __init__(
            self,
            screen_shooter: Screenshooter,
            *,
            fps: int,
            key_binds: Optional[Dict[str, str]] = None,
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
                - 'quit': Quit the program

            If None, the following key binds will be used:
                - '1': Start the recording
                - '2': Stop the recording
                - '3': Cancel the recording
                - '0': Quit the program

        save_dir: Optional[str]
            The path to save the video to. If None, the video will be saved in the current directory
        """

        # Save the arguments
        self.screen_shooter = screen_shooter
        self.fps = fps

        self.key_binds = key_binds
        if self.key_binds is None:
            self.key_binds = self.default_key_binds

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
        
        # Prepare the key listener
        self.on_press_map = {
            keybind: getattr(self, f"_{action}")
            for keybind, action in self.key_binds.items()
        }
        
        self.key_listener = KeyListener(self.on_press_map)

    @property
    def default_key_binds(self) -> Dict[str, str]:
        return {
            '1': 'start_new',
            '2': 'stop',
            '3': 'cancel',
            '0': 'quit',
        }

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
        file_path = f'{self.save_dir}/{current_date}.avi'
        self.file_path = file_path

        # Prepare the video stream
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_stream = cv2.VideoWriter(file_path, fourcc, self.fps, self.output_size, True)

        # Update state
        print(f'Started recording to {file_path}')
        self.is_recording = True
        self.last_frame = None

    def _stop(self):
        """
        Stop the current recording
        """
        if not self.is_recording:
            return

        # Update state
        print(f'Stopped recording to {self.file_path}')
        self.is_recording = False

        # Stop recording and save the video
        self.video_stream.release()
        self.video_stream = None

    def _cancel(self):
        """
        Cancel the current recording
        """
        if not self.is_recording:
            return

        # Update state
        print(f'Cancelled recording to {self.file_path}')
        self.is_recording = False

        # Stop recording and delete the video
        self.video_stream.release()
        os.remove(self.file_path)
        self.video_stream = None

    def _quit(self):
        """
        Quit the program
        """
        if self.is_recording:
            self.cancel()

        print('Quitting the program')
        exit(0)

    def _record_frame(self):
        if not self.is_recording:
            return

        frame = self.screen_shooter()

        if not self.is_recording:
            return

        if self.last_frame is not None:
            # A pixel is considered different if it has at least one different channel
            # Let's compute difference using this

            difference = np.sum(np.any(self.last_frame != frame, axis=-1)) / self.area

            # similarity = np.sum(self.last_frame == frame) / self.area
            # difference = 1.0 - similarity
            if difference < self.diff_threshold:
                return

        self.video_stream.write(frame)
        self.last_frame = frame
        print("Added frame")

    def _record_frames(self):
        while True:
            self._record_frame()
        
    def record(self):
        """
        Start recording
        """

        thread_listener = Thread(target=self.key_listener.listen)
        thread_recoder = Thread(target=self._record_frames)

        # Start both of them
        thread_recoder.start()
        thread_listener.start()

        
