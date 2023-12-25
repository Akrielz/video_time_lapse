import asyncio
import os

import cv2
import streamlit as st

from vtl.image.monitor_manager import MonitorManager
from vtl.image.screenshot import ScreenshooterPIL, ScreenshooterMSS
from vtl.recorder.recorder import TimeLapseRecorder


class VideoTimeLapse:
    def __init__(self):
        self.monitor_manager = MonitorManager()
        self.monitor_indexes = [f"Monitor {i+1}" for i in range(len(self.monitor_manager))]

        self.num_monitors = len(self.monitor_manager)
        self.screen_shooters = [
            ScreenshooterMSS(*self.monitor_manager.prepare_args_for_screenshooter(i))
            for i in range(len(self.monitor_manager))
        ]

        self._init_session_state()

        self.time_lapse_recorder = st.session_state.time_lapse_recorder

    def _init_session_state(self):
        if "selected_monitor_index" not in st.session_state:
            st.session_state.selected_monitor_index = 0

        if "save_dir" not in st.session_state:
            st.session_state.save_dir = os.getcwd()

        if "diff_threshold" not in st.session_state:
            st.session_state.diff_threshold = 0.0

        if "fps" not in st.session_state:
            st.session_state.fps = 30

        self._select_monitor()

        if "time_lapse_recorder" not in st.session_state:
            st.session_state.time_lapse_recorder = TimeLapseRecorder(
                self.selected_screen_shooter,
                fps=st.session_state.fps,
                save_dir=st.session_state.save_dir,
                diff_threshold=st.session_state.diff_threshold,
            )

    @property
    def is_recording(self):
        return st.session_state.time_lapse_recorder.is_recording

    @staticmethod
    def _update_monitor_state(index: int):
        st.session_state.selected_monitor_index = index

    def _select_monitor(self):
        index = st.session_state.selected_monitor_index
        self.selected_monitor_index = index
        self.selected_monitor = self.monitor_manager[index]

    @property
    def selected_screen_shooter(self):
        return self.screen_shooters[self.selected_monitor_index]

    @staticmethod
    def check_if_dir_exists_or_possible(dir_path: str):
        # Check if the directory exists
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            return True

        if os.path.exists(dir_path) and not os.path.isdir(dir_path):
            st.error("The path you entered is not a directory.")
            return False

        st.error("The path you entered does not exist.")
        return False

    def _select_save_dir(self, dir_path: str):
        if not self.check_if_dir_exists_or_possible(dir_path):
            return

        st.session_state.save_dir = dir_path

    def display_interface(self):
        st.title("VTL Interface")
        st.write("First, select the monitor you want to record from the dropdown below:")

        # For each monitor, add a screenshot and a button
        columns = st.columns(self.num_monitors)

        for i, col in enumerate(columns):
            screenshot = self.screen_shooters[i]()
            if self.selected_monitor_index == i:
                screenshot = cv2.rectangle(screenshot, (0, 0), (screenshot.shape[1], screenshot.shape[0]), (0, 255, 0), 10)
            col.image(screenshot, use_column_width=True)

            col.button(f"Select Monitor {i + 1}", on_click=lambda x=i: self._update_monitor_state(x), disabled=self.is_recording)

        # Select the directory to save the video
        st.write("Select the directory to save the video to:")
        save_dir = st.text_input("Save Directory", value=f"{os.getcwd()}", disabled=self.is_recording)
        self._select_save_dir(save_dir)

        # Select the fps
        st.write("Select the fps you want the video to have:")
        st.number_input("FPS", value=30, min_value=1, max_value=60, step=1, disabled=self.is_recording)
        st.session_state.fps = 30

        # Select the diff threshold
        st.write("Select the threshold of the pixels that must change for the frame to be recorded:")
        max_pixels = self.selected_screen_shooter.output_size[0] * self.selected_screen_shooter.output_size[1]
        pixels_threshold = st.number_input(
            "Threshold", value=0, min_value=0, max_value=max_pixels, step=1, disabled=self.is_recording
        )
        st.session_state.diff_threshold = pixels_threshold / max_pixels

        st.write("Now, select the action you want to perform:")

        record_button, stop_button, cancel_button = st.columns(3)
        record_button.button("Record", disabled=self.is_recording, on_click=self.time_lapse_recorder._start_new)
        stop_button.button("Stop", disabled=not self.is_recording, on_click=self.time_lapse_recorder._stop)
        cancel_button.button("Cancel", disabled=not self.is_recording, on_click=self.time_lapse_recorder._cancel)

        st.write(st.session_state)

        if not self.is_recording:
            self.time_lapse_recorder.update_args(
                self.selected_screen_shooter,
                fps=st.session_state.fps,
                save_dir=st.session_state.save_dir,
                diff_threshold=st.session_state.diff_threshold,
            )
            st.session_state.time_lapse_recorder = self.time_lapse_recorder

    async def async_write_frames(self):
        while True:
            st.write(f"Frames recorded so far: {self.time_lapse_recorder.recorded_frames}")
            await asyncio.sleep(1)

    def record(self):
        self.display_interface()
        asyncio.run(self.time_lapse_recorder._record_frames_async())
