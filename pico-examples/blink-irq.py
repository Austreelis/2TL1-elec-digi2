from machine import Pin
import utime

led = Pin(0, Pin.OUT)


def irq_handler(pin):
    global led
    utime.sleep_ms(10)
    print("button pressed")
    for _ in range(5):
        led.toggle()
        utime.sleep_ms(100)


Pin(15, Pin.IN, PIN.PULL_UP).irq(trigger=Pin.IRQ_RISING, handler=irq_handler)

while True:
    led.toggle()
    utime.sleep_ms(1000)
