from machine import Pin
import utime

led = Pin(0, Pin.OUT)

while True:
    led.toggle()
    utime.sleep_ms(500)
