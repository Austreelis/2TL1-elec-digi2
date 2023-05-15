from micropython import schedule
from machine import Timer

from log import info, debug, trace
from pin import Pin

class Blinker:
    def __init__(
        self,
        pin: Pin,
        period: int,
        *,
        start: bool = False,
        name: str | None = None
    ):
        pin.init(mode=Pin.OUT, pull=None)
        self.pin = pin
        self.period = period
        self.timer = Timer()
        self.running = start
        self.name = name if name is not None else f"blinker<{pin}>"

        self.toggle_cb = self.toggle
        self.log_toggle_cb = self.log_toggle
        self.log_toggle_str = f"Blinker: toggled {pin}"

        debug(f"Created blinker {repr(self)}")

        if start:
            self.start()

    def start(self):
        if self.running:
            return
        self.timer.init(
            mode=Timer.PERIODIC,
            period=self.period,
            callback=self.toggle_cb
        )
        self.running = True
        info(f"Blinker: started {self.name}")

    def stop(self):
        if not self.running:
            return
        self.timer.deinit()
        self.running = False
        info(f"Blinker: stopped {self.name}")

    def toggle(self, _timer) -> int:
        self.pin.toggle()
        if __debug__:
            schedule(self.log_toggle_cb, ())

    def log_toggle(self, _arg):
        trace(self.log_toggle_str)

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return f"{self.name} {{ pin: {repr(self.pin)}, period: " \
            + f"{self.period}, running: {self.running}, toggle_cb: " \
            + f"{repr(self.toggle_cb)}, log_toggle_cb: " \
            + f"{repr(self.log_toggle_cb)}, log_toggle_str: " \
            + f"'{self.log_toggle_str}' }}"
