from typing import Dict, Callable

from pynput import keyboard


class KeyListener:
    def __init__(self, on_press_map: Dict[str, Callable]):
        """
        Arguments
        ---------
        on_press_map: Dict[str, Callable]
            A dictionary mapping keybinds to callbacks.
        """
        self.on_press_map = on_press_map

    def on_press(self, key: keyboard.Key):
        if key == keyboard.Key.esc:
            # Stop listener if the 'Esc' key is pressed
            return False

        for keybind, callback in self.on_press_map.items():
            if key == keyboard.KeyCode.from_char(keybind):
                callback()

    def listen(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()
