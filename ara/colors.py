from ableton.v3.control_surface.elements import SimpleColor

LED_CHANNEL = 0


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
