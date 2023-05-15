import micropython, time
# Allocate ASAP an emergency exception buffer (100 advised for general-purpose)
micropython.alloc_emergency_exception_buf(1000)

from machine import Timer

from blink import Blinker
from display import force_update, set_displayed, set_displayed_raw
from log import error, warn, info, LOG_TRACE
from pin import LAL0, LAL1, LSTA, SECH, STRG
from probe import Probe

def update_distance(args):
    global red_blinker
    
    (probe, *extra_args) = args
    distance = probe.last_measure()
    if distance is None:
        error(f"{probe} did not acknowledge ping")
        set_displayed_raw(0b11001110, 0b10001000)
        LAL0.low()
        red_blinker.start()
    elif distance < 0:
        warn(
            f"{probe} couldn't detect anything within " 
            + f"{probe.max_distance()/100:6.2f}m"
        )
        set_displayed_raw(0b00001000, 0b00001000)
        LAL0.low()
        red_blinker.stop()
        LAL1.high()
    else:
        info(f"{probe} measured distance {distance} [cm]")
        set_displayed(distance)
        LAL0.high()
        red_blinker.stop()
        LAL1.low()
        
        


def core1_main(setup = None, loop = None, *extra_args):
    info("Starting core1 main")

    if setup is not None:
        setup(*extra_args)
    if loop is None:
        return
    while True:
        loop(*extra_args)

machine.lightsleep(1)

info("Starting core0 main")

set_displayed_raw(0b00001000, 0b00001000)

probe = Probe(STRG, SECH, max_distance=40, on_update=update_distance)
status_blinker = Blinker(LSTA, 500, name="Startus", start=True)
red_blinker = Blinker(LAL1, 100, name="Alarm")

ping_timer = Timer(mode=Timer.PERIODIC, period=500, callback=probe.send_ping)

# _thread.start_new_thread(core1_main, ())

while True:
    force_update()
    time.sleep_ms(0)
