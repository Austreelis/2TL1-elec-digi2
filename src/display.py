from micropython import const
import time

from log import error, debug, trace
from pins import DEN0, DEN1, DDS, DCK, DDW

# Bit offsets for each segment:
#  1
# 2 0
#  3
# 7 5
#  6 4
#
# Note: Dot segment is unconnected on the rightmost display.
SEGMENTS_MAP = const((
    # xxx
    # x x
    # x.x
    # x x
    # xxx.
    0b11100111, # 0
    # ..x
    # . x
    # ..x
    # . x
    # ..x. 
    0b00100001, # 1
    # xxx
    # . x
    # xxx
    # x .
    # xxx.
    0b11001011, # 2
    # xxx
    # . x
    # xxx
    # . x
    # xxx.
    0b01101011, # 3
    # x.x
    # x x
    # xxx
    # . x
    # ..x.
    0b00101101, # 4
    # xxx
    # x .
    # xxx
    # . x
    # xxx.
    0b01101110, # 5
    # xxx
    # x .
    # xxx
    # x x
    # xxx.
    0b11101110, # 6
    # xxx
    # . x
    # ..x
    # . x
    # ..x.
    0b00100011, # 7
    # xxx
    # x x
    # xxx
    # x x
    # xxx.
    0b11101111, # 8
    # xxx
    # x x
    # xxx
    # . x
    # xxx.
    0b01101111, # 9
))

SM_DISPLAY_WRITE = const(None)

left_display_bits = 0
right_display_bits = 0

def set_displayed_raw(lhs: int, rhs: int) -> bool:
    """
    Update the segments displayed on the 7-segments displays.

    # Arguments

    - `lhs`: An `int` where each bit represents whether a segment of the
      leftmost display is on or off.
    - `rhs`: An `int` where each bit represents whether a segment of the
      rightmost display is on or off.

    # Returns

    `True` if the cpu will still need to regularly update displays through
    `force_update` for these values to be displayed. `False` if a PIO state
    machine is handling display updates.
    """
    global left_display_bits
    global right_display_bits
    global SM_DISPLAY_WRITE

    left_display_bits = lhs
    right_display_bits = rhs

    if SM_DISPLAY_WRITE is not None:
        trace(
            f"Pushing ({left_display_bits}, {right_display_bits}) to 7seg "
            + "display state machine"
        )
        SM_DISPLAY_WRITE.put(left_display_bits)
        SM_DISPLAY_WRITE.put(right_display_bits)
        return False
    trace(
        "Setting 7seg displays to "
        + f"({left_display_bits:b}, {right_display_bits:b})"
    )
    return True


def set_displayed_raw_int(lhs: int, rhs: int, *, dot: bool = False) -> bool:
    """
    Update the integer value displayed on the 7-segments displays.

    # Arguments

    - `lhs`: The `int` from `0` to `9` (inclusive) displayed on the leftmost
        display.
    - `rhs`: The `int` from `0` to `9` (inclusive) displayed on the rightmost
        display.
    - `dot`: Whether the middle dot is displayed (Default: `False`).

    # Returns

    `True` if the cpu will still need to regularly update displays through
    `force_update` for these values to be displayed. `False` if a PIO state
    machine is handling display updates.
    """
    global SEGMENTS_MAP

    return set_displayed_raw(
        SEGMENTS_MAP[lhs] | (int(dot) << 4)
        ,SEGMENTS_MAP[rhs]
    )


def set_displayed(value: int) -> bool:
    """
    Update the value displayed on the 7-segments displays.

    # Arguments

    - `value`: The distance to display in cm.

    # Returns

    `True` if the cpu will still need to regularly update displays through
    `force_update` for these values to be displayed. `False` if a PIO state
    machine is handling display updates.
    """
    if value > 99:
        lhs = value // 100
        rhs = (value - lhs * 100) // 10
        dot = True
        debug(f"Displaying a distance of {lhs}.|{rhs} m on 7seg displays")
    else:
        lhs = value // 10
        rhs = value - (lhs * 10)
        dot = False
        debug(f"Displaying a distance of {lhs}|{rhs} cm on 7seg displays")
    return set_displayed_raw_int(lhs, rhs, dot=dot)


def force_update():
    """
    Sends data to displays using CPU-controlled GPIOs. 
    """
    global left_display_bits
    global right_display_bits
    
    DEN0.low()
    DEN1.low()
    DDW.high()

    for bit in range(8):
        DCK.low()
        DDS.value((left_display_bits >> bit) & 1)
        DCK.high()

    DEN0.high()
    DDW.low()

    time.sleep_ms(10)

    DEN0.low()
    DEN1.high()
    DDW.high()

    for bit in range(8):
        DCK.low()
        DDS.value((right_display_bits >> bit) & 1)
        DCK.high()

    DDW.low()

    time.sleep_ms(9)

