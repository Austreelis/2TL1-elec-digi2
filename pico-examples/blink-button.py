from machine import Pin
import utime

led = Pin(0, Pin.OUT)
led = Pin(15, Pin.IN, PIN.PULL_UP)

while True:
    if button.value():
        led.toggle()
        utime.sleep_ms(500)
