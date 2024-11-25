from .colors import Rgb


class Skin:
    class DefaultButton:
        On = Rgb.purple
        Off = Rgb.purple

    class StepButton:
        # StepButton.[Active][Step][Acc]
        ActiveStep = Rgb.peach_w
        ActiveStepAcc = Rgb.peach
        InactiveStep = Rgb.cherry_w
        InactiveStepAcc = Rgb.cherry
        Active = Rgb.ambar_w
        ActiveAcc = Rgb.ambar
        Inactive = Rgb.black
        InactiveAcc = Rgb.black

    class InstrumentButton:
        Active = Rgb.peach
        Inactive = Rgb.black
        Mutted = Rgb.purple
        ActiveMutted = Rgb.pink

    class PageButton:
        OnLock = Rgb.pink
        OnNormal = Rgb.ambar
        Off = Rgb.black
