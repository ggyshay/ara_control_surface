from ableton.v3.control_surface import BasicColors
from ableton.v3.control_surface.elements import (
    ColorPart,
    ComplexColor,
    FallbackColor,
    SimpleColor,
)
from ableton.v3.live import liveobj_valid

LED_CHANNEL = 0


def create_color(red, green, blue):
    return ComplexColor(
        (
            ColorPart(red, channel=LED_CHANNEL),
            ColorPart(green, channel=LED_CHANNEL),
            ColorPart(blue, channel=LED_CHANNEL),
        )
    )


class Rgb:
    BLACK = SimpleColor(0, channel=LED_CHANNEL)
    WHITE = SimpleColor(7, channel=LED_CHANNEL)
    RED = SimpleColor(0b100, channel=LED_CHANNEL)
    GREEN = SimpleColor(0b010, channel=LED_CHANNEL)
    BLUE = SimpleColor(0b001, channel=LED_CHANNEL)

    CYAN = SimpleColor(0b011, channel=LED_CHANNEL)
    YELLOW = SimpleColor(0b110, channel=LED_CHANNEL)
    PURPLE = SimpleColor(0b101, channel=LED_CHANNEL)

    BLACK_w = SimpleColor(0b1000, channel=LED_CHANNEL)
    WHITE_w = SimpleColor(0b1111, channel=LED_CHANNEL)
    RED_w = SimpleColor(0b1100, channel=LED_CHANNEL)
    GREEN_w = SimpleColor(0b1010, channel=LED_CHANNEL)
    BLUE_w = SimpleColor(0b1001, channel=LED_CHANNEL)

    CYAN_w = SimpleColor(0b1011, channel=LED_CHANNEL)
    YELLOW_w = SimpleColor(0b1110, channel=LED_CHANNEL)
    PURPLE_w = SimpleColor(0b1101, channel=LED_CHANNEL)

    # BLACK = FallbackColor(create_color(0, 0, 0), BasicColors.OFF)
    # WHITE = create_color(109, 80, 27)
    # RED = create_color(127, 0, 0)
    # RED_HALF = create_color(32, 0, 0)
    # GREEN = create_color(0, 127, 0)
    # GREEN_HALF = create_color(0, 32, 0)
    # BLUE = create_color(0, 16, 127)
    # BLUE_HALF = create_color(0, 0, 32)
    # YELLOW = create_color(127, 83, 3)
    # YELLOW_HALF = create_color(52, 34, 1)
    # PURPLE = create_color(65, 0, 65)
    # PURPLE_HALF = create_color(17, 0, 17)
    # LIGHT_BLUE = create_color(0, 91, 91)
    # ORANGE = create_color(127, 18, 0)
    # PEACH = create_color(127, 51, 6)
    # PINK = create_color(127, 17, 30)
