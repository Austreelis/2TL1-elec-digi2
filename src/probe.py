from micropython import const, schedule
import machine, time
from machine import Timer

from log import debug, trace
from pin import Pin

class Probe:
    def __init__(
        self,
        trigger: Pin,
        echo: Pin,
        *,
        max_distance: int = 2370,
        on_update = None,
        name: str | None = None,
    ):
        trigger.init(mode=Pin.OUT, pull=None)
        self.trigger = trigger
        echo.init(mode=Pin.IN, pull=Pin.PULL_DOWN)
        self.echo = echo
        self.max_pulse = 58 * max_distance
        self.name = name if name is not None else f"probe<{trigger}, {echo}>"

        self.measurement = None
        self.on_update_cb = on_update
        self.send_trigger_cb = self.send_trigger
        self.receive_echo_cb = self.receive_echo
        self.log_ping_received_cb = self.log_ping_received
        self.log_ping_str = f"Probe: {self.name} received ping"

        debug(f"Created probe {repr(self)}")

    def last_measure(self):
        return self.measurement

    def max_distance(self):
        return self.max_pulse // 58

    def send_ping(self, _arg):
        schedule(self.send_trigger_cb, ())

    def send_trigger(self, _arg):
        self.trigger.high()
        time.sleep_ms(10)
        self.trigger.low()
        schedule(self.receive_echo_cb, ())

    def receive_echo(self, _arg):
        measurement = machine.time_pulse_us(self.echo.pin, 1, self.max_pulse)
        if measurement > 0:
            self.measurement = (measurement + 29) // 58
        elif measurement == -1:
            self.measurement = -1
        else:
            self.measurement = None

        if self.on_update_cb is not None:
            schedule(self.on_update_cb, (self,))
        if __debug__:
            schedule(self.log_ping_received_cb, ())

    def log_ping_received(self, _arg):
        trace(self.log_ping_str)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.name} {{ trigger: {self.trigger}, echo: " \
            + f"{self.echo}, max_distance: {self.max_pulse // 58}, "\
            + f"on_update_cb: {repr(self.on_update_cb)}, send_trigger_cb: " \
            + f"{repr(self.send_trigger_cb)}, receive_echo_cb: " \
            + f"{repr(self.receive_echo_cb)}, log_ping_received_cb: " \
            + f"{repr(self.log_ping_received_cb)}, log_ping_str: " \
            + f"'{self.log_ping_str}' }}"
