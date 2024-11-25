from ableton.v3.control_surface.elements import SimpleColor

LED_CHANNEL = 0


class Rgb:
    black = SimpleColor(0, channel=LED_CHANNEL)
    ambar = SimpleColor(1, channel=LED_CHANNEL)
    ambar_w = SimpleColor(2, channel=LED_CHANNEL)

    cherry = SimpleColor(3, channel=LED_CHANNEL)
    cherry_w = SimpleColor(4, channel=LED_CHANNEL)

    peach = SimpleColor(5, channel=LED_CHANNEL)
    peach_w = SimpleColor(6, channel=LED_CHANNEL)

    purple = SimpleColor(7, channel=LED_CHANNEL)
    purple_w = SimpleColor(8, channel=LED_CHANNEL)

    pink = SimpleColor(9, channel=LED_CHANNEL)
    pink_w = SimpleColor(10, channel=LED_CHANNEL)
