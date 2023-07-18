from vtl.image.screenshot import ScreenshooterPIL
from vtl.recorder.time_lapse import TimeLapseRecorder

screen_shooter = ScreenshooterPIL(x_min=0, y_min=0, x_max=1920, y_max=1080)

diff_threshold = 100 / (1920 * 1080)
recoder = TimeLapseRecorder(screen_shooter, fps=1, diff_threshold=diff_threshold)
recoder.record()