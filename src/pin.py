from micropython import const
from machine import Pin as _Pin

from log import debug

class Pin:
    PULL_DOWN = _Pin.PULL_DOWN
    PULL_UP = _Pin.PULL_UP
    
    IN = _Pin.IN
    OUT = _Pin.OUT
    
    def __init__(
        self,
        id: int,
        mode: int = _Pin.IN,
        pull: int | None = None,
        name: str | None = None,
    ):
        self.id = id
        self.pin = _Pin(id, mode, pull)
        self.name = name if name is not None else f"pin<{id}>"
        debug(f"Created pin {repr(self)}")

    def init(self, mode: int | None = None, pull: int | None = None):
        args = ()
        kwargs= {}
        if mode is not None:
            if pull is not None:
                args = (mode, pull)
            else:
                args = (mode,)
        elif pull is not None:
            kwargs["pull"] = pull
        self.pin.init(*args, **kwargs)

    def value(self, value: int = None):
        if value is None:
            return self.pin.value()
        return self.pin.value(*value)

    def toggle(self):
        self.pin.toggle()

    def low(self):
        self.pin.low()

    def high(self):
        self.pin.high()

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.name} {{ id: {self.id}, value: {self.value()} }}"

# Shift-registers control Pins
##Display data write
DDW = Pin(15, Pin.OUT, name="DDW")
##Display data clock
DCK = Pin(14, Pin.OUT, name="DCK") 
##Display data serial
DDS = Pin(13, Pin.OUT, name="DDS")

# 7-segment display control Pins
##Leftmost display enable
DEN0 = Pin(0, Pin.OUT, name="DEN0")
##Rightmost display enable
DEN1 = Pin(1, Pin.OUT, name="DEN1")

# LED Pins
##Green LED
LAL0 = Pin(19, Pin.OUT, name="LAL0")
##Red LED
LAL1 = Pin(18, Pin.OUT, name="LAL1")
##Green on-board LED
LSTA = Pin(25, Pin.OUT, name="LSTA")

# Ultrasonic distance probe Pins
##ECHO Pin
SECH = Pin(27, Pin.IN, name="SECH")
##TRIG Pin
STRG = Pin(28, Pin.OUT, name="STRG")
