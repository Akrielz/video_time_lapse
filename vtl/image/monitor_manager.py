import screeninfo


class MonitorManager:
    def __init__(self):
        self.monitors = screeninfo.get_monitors()

    def primary_monitor(self):
        for monitor in self.monitors:
            if monitor.is_primary:
                return monitor

        return self.monitors[0]

    def prepare_args_for_screenshooter(self, i):
        monitor = self.monitors[i]
        x_min = monitor.x
        y_min = monitor.y
        x_max = monitor.width + x_min
        y_max = monitor.height + y_min

        return x_min, y_min, x_max, y_max

    def __getitem__(self, item):
        return self.monitors[item]

    def __len__(self):
        return len(self.monitors)