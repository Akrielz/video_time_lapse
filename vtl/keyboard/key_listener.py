from typing import Dict, Callable

from pynput import keyboard
from pynput.keyboard import Key


class KeyListener:
    def __init__(self, on_press_map: Dict[str, Callable]):
        """
        Arguments
        ---------
        on_press_map: Dict[str, Callable]
            A dictionary mapping keyboard akeys to callbacks.
        """
        self.on_press_key_map = on_press_map

        # Convert the on_press_map keys to virtual key codes
        self.on_press_vk_map = {
            get_virtual_key_code(keybind): callback
            for keybind, callback in self.on_press_key_map.items()
        }

    def on_press(self, key: keyboard.Key):
        for keybind, callback in self.on_press_vk_map.items():
            if key == keybind:
                callback()

    def listen(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()


def get_virtual_key_code(key: str):
    if len(key) == 1:
        return keyboard.KeyCode.from_char(key)

    # Convert key string to uppercase
    key = key.lower()
    return getattr(Key, key)
