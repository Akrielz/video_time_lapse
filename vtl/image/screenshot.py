from abc import ABC
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import ImageGrab
from PIL.Image import Image
from mss import mss


class Screenshooter(ABC):
    def __init__(
            self,
            x_min: int,
            y_min: int,
            x_max: int,
            y_max: int,
            resize_res: Optional[Tuple[int, int]] = None,
    ):
        """
        Arguments:
        ----------
        x_min: int
            The minimum x coordinate of the screenshot

        y_min: int
            The minimum y coordinate of the screenshot

        x_max: int
            The maximum x coordinate of the screenshot

        y_max: int
            The maximum y coordinate of the screenshot

        resize_res: Optional[Tuple[int, int]]
            The resolution to resize the screenshot to. If None, the screenshot will not be resized
            The format is (width, height)
        """

        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

        self.resize_res = resize_res

        self.original_width = x_max - x_min
        self.original_height = y_max - y_min

        if resize_res == (self.original_width, self.original_height):
            self.resize_res = None

    @property
    def output_size(self) -> Tuple[int, int]:
        if self.resize_res is None:
            return self.original_width, self.original_height

        return self.resize_res

    def __call__(self) -> np.ndarray:
        return self.get_screenshot()

    def get_screenshot(self) -> np.ndarray:
        raise NotImplementedError


class ScreenshooterMSS(Screenshooter):
    def __init__(
            self,
            x_min: int,
            y_min: int,
            x_max: int,
            y_max: int,
            resize_res: Optional[Tuple[int, int]] = None,
    ):
        super().__init__(x_min, y_min, x_max, y_max, resize_res)
        self.mss = mss()

    def get_screenshot(self) -> np.ndarray:

        bounding_box = {'top': self.y_min, 'left': self.x_min, 'width': self.original_width, 'height': self.original_height}

        img_sct = self.mss.grab(bounding_box)
        img_np = np.array(img_sct)
        img_np = img_np[:, :, :3]

        if self.resize_res is None:
            return img_np

        img_np = cv2.resize(img_np, dsize=self.resize_res, interpolation=cv2.INTER_CUBIC)
        return img_np


class ScreenshooterPIL(Screenshooter):
    def __init__(
            self,
            x_min: int,
            y_min: int,
            x_max: int,
            y_max: int,
            resize_res: Optional[Tuple[int, int]] = None,
    ):
        super().__init__(x_min, y_min, x_max, y_max, resize_res)

    def get_screenshot(self) -> np.ndarray:
        img_pil: Image = ImageGrab.grab(bbox=(self.x_min, self.y_min, self.x_max, self.y_max))

        if self.resize_res:
            img_pil = img_pil.resize(self.resize_res)

        return image_bgr_to_rgb(np.array(img_pil))


def image_bgr_to_rgb(img: np.array) -> np.array:
    return np.concatenate([img[:, :, 2:3], img[:, :, 1:2], img[:, :, 0:1]], -1)  # RGB


if __name__ == '__main__':
    screenshooter = ScreenshooterPIL(0, 0, 1920, 1080)
    img = screenshooter()
    cv2.imshow('img', img)
    cv2.waitKey(0)