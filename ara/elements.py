from ableton.v3.control_surface import MIDI_NOTE_TYPE, ElementsBase, MapMode
from functools import partial


class Elements(ElementsBase):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        add_button_matrix = partial(
            (self.add_button_matrix),
            msg_type=MIDI_NOTE_TYPE,
            led_channel=0,
            is_rgb=True,
            is_momentary=True,
        )
        add_button_matrix([range(52, 68)], base_name="Steps_Buttons", channels=0)

        add_button_matrix(
            [list(range(36, 44))], base_name="Instruments_Buttons", channels=0
        )

        add_button_matrix([list(range(44, 48))], base_name="Page_Buttons", channels=0)

        self.add_button(48, "Shift_Button", channel=0, msg_type=MIDI_NOTE_TYPE)
        self.add_button(49, "Double_Button", channel=0, msg_type=MIDI_NOTE_TYPE)
        self.add_button(50, "Fill_Button", channel=0, msg_type=MIDI_NOTE_TYPE)
        self.add_button(51, "Mute_Button", channel=0, msg_type=MIDI_NOTE_TYPE)

        self.add_encoder_matrix(
            [range(36, 44)],
            base_name="Encoder_Matrix",
            channels=0,
            is_feedback_enabled=True,
            needs_takeover=True,
            map_mode=MapMode.LinearBinaryOffset,
            # msg_type=
        )

        # self.add_button(44, name='Shift_Button')

    # def add_button(self, *a, **k):
    #     (super().add_button)(a, **k, **{"is_momentary": False, "is_rgb": True})
