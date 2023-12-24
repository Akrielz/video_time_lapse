# Video Time Lapse

## Table of Contents

- [Description](#description)
- [Install](#install)
- [Usage](#usage)

## Description

This is a simple script that creates a video time-lapse, by recording only
the frames that have changed an 'X' amount of pixels. This is useful for
recording a video of a 3D printer, or a speed-up video of a drawing.

The main advantage of this script is that it optimizes the video size on the
hard drive.

## Install

In order to install this script, just download the script and run

```bash
pip install -r requirements.txt
```


## Usage

Here is a simple example that records the main screen of a full HD monitor
(1920x1080) at 10 frames per second.

```py
from vtl.image.screenshot import ScreenshooterPIL
from vtl.recorder.recorder import TimeLapseRecorder

screen_shooter = ScreenshooterPIL(x_min=0, y_min=0, x_max=1920, y_max=1080)

diff_threshold = 100 / (1920 * 1080)  # 100 pixels changed
recoder = TimeLapseRecorder(screen_shooter, fps=10, diff_threshold=diff_threshold)
recoder.record()
```

The default keys to control the recorder are:

- `F5`: To start new recording
- `F6`: To stop recording
- `F7`: To cancel recording
- `F8`: To exit the program

But they can be changed by passing a keybind dictionary like follows:

```py
key_binds = {
    '1': 'start_new',
    '2': 'stop',
    '3': 'cancel',
    '0': 'quit',
}
```