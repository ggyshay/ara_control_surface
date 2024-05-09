from .colors import Rgb


class Skin:
    class DefaultButton:
        On = Rgb.RED
        Off = Rgb.BLACK

    class StepButton:
        # StepButton.[Active][Step][Acc]
        ActiveStep = Rgb.WHITE_w
        ActiveStepAcc = Rgb.WHITE
        InactiveStep = Rgb.CYAN_w
        InactiveStepAcc = Rgb.CYAN
        Active = Rgb.RED_w
        ActiveAcc = Rgb.RED
        Inactive = Rgb.BLACK_w
        InactiveAcc = Rgb.BLACK

    class InstrumentButton:
        Active = Rgb.YELLOW
        Inactive = Rgb.BLACK
        Mutted = Rgb.BLUE
