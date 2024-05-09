from ableton.v3.live import liveobj_changed, liveobj_valid

from ableton.v3.base import (
    clamp,
    depends,
    first,
    listenable_property,
    listens,
    listens_group,
)
from ableton.v3.control_surface import Component
from ableton.v3.control_surface.controls import ButtonControl, control_matrix
from .sequencer import Sequencer
from typing import Optional, cast
import logging


BASE_DRUM_GROUP_NOTE = 36

logger = logging.getLogger("ara")


class DrumGroupComponent(Component):
    mute_button = ButtonControl(color=None)
    delete_button = ButtonControl(color=None)
    matrix = control_matrix(ButtonControl)
    shift_button = ButtonControl(color=None)

    def __init__(
        self,
        name="Drum_Group",
        target_track=None,
        sequencer: Optional[Sequencer] = None,
        *a,
        **k,
    ):
        super().__init__(name=name, *a, **k)
        self._target_track = target_track

        self._drum_group_device = None
        self._selected_drum_pad = None
        self._all_drum_pads = []
        self._assigned_drum_pads = []
        # assert sequencer is not None
        self._sequencer = sequencer

    @property
    def sequencer(
        self,
    ):
        return self._sequencer

    @sequencer.setter
    def sequencer(self, _sequencer):
        self._sequencer = _sequencer
        self.update_leds()

    @property
    def has_assigned_drum_pads(self):
        return self._assigned_drum_pads and liveobj_valid(
            first(self._assigned_drum_pads)
        )

    @property
    def assigned_drum_pads(self):
        return self._assigned_drum_pads

    def set_matrix(self, matrix):
        self.matrix.set_control_element(matrix)

    @matrix.value
    def matrix_click(self, _, button):
        for k, v in vars(button).items():
            logger.info(f"button.{k} = {v}")

        idx = button.coordinate[1]
        if self._sequencer is not None:
            if self.shift_button.is_pressed:
                self._sequencer.erase_instrument(idx)
            else:
                self._sequencer.selected_instrument = idx

        self.update_leds()

    def update_leds(self):
        if not self._sequencer:
            return

        instruments = self._sequencer.get_instruments()

        for state, value in zip(self.matrix, instruments):
            state.color = "DefaultButton.On" if value else "DefaultButton.Off"

    # @listens_group("mute")
    # def __on_mute_changed(self, _):
    #     self._update_led_feedback()

    # @listens("visible_drum_pads")
    # def __on_visible_drum_pads_changed(self):
    #     self._update_drum_pad_listeners()
    #     self._update_led_feedback()

    # @listens("selected_drum_pad")
    # def __on_selected_drum_pad_changed(self):
    #     self._update_selected_drum_pad()
    #     self._update_provided_pitches()
