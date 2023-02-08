from machine import Pin, Timer

led = Pin(0, Pin.OUT)


def timer_interrupt_handler(toggle):
    global led
    led.toggle()


Timer().init(freq=2.0, mode=Timer.PERIODIC, callback=timer_interrupt_handler)
