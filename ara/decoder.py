from ableton.v3.control_surface import Component
from ableton.v3.control_surface.controls import (
    ButtonControl,
    control_matrix,
    EncoderControl,
)
from ableton.v3.live import liveobj_changed, liveobj_valid
from Live.Clip import MidiNoteSpecification  # type: ignore
import logging
from .sequencer import Sequencer
from typing import Optional, Any

logger = logging.getLogger("ara")


class StepButtonControl(ButtonControl):

    class State(ButtonControl.State):
        x = property(lambda self: self.coordinate[1])
        y = property(lambda self: self.coordinate[0])
        is_active = False


class StepDecoder(Component):
    """ """

    shift_button = ButtonControl(color=None)
    double_button = ButtonControl(color=None)
    mute_button = ButtonControl(color=None)
    fill_button = ButtonControl(color=None)

    matrix = control_matrix(StepButtonControl)
    instrument_matrix = control_matrix(StepButtonControl)
    page_matrix = control_matrix(StepButtonControl)
    encoder_matrix = control_matrix(EncoderControl)

    ## not sure how this works, but I think it only validates these dependencies when the component is enabled, nope
    def __init__(
        self,
        name="Step_Decoder",
        sequencer: Optional[Sequencer] = None,
        *a,
        **k,
    ):
        logger.info(f"args=[{a}], kwargs=[{k}]")
        super().__init__(name=name, *a, **k)

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
        if self._sequencer is not None:
            self._sequencer.update_leds_callback = self.update_leds
            self._sequencer.update_inst_leds_callback = self.update_instrument_leds

    def set_device(self, device):
        self._device = device
        # for encoder, pad in zip(self.encoder_matrix, self._device.drum_pads[36:44]):
        #     encoder.mapped_parameter =

    def _pot_to_vol(self, pot):
        return (pot + 1) / 2

    @encoder_matrix.value
    def encoder_turn(self, value, encoder):
        if self._device is None:
            return

        self._device.drum_pads[36 + encoder.index].chains[
            0
        ].mixer_device.volume.value = self._pot_to_vol(value)
        # logger.info(f"value={value}")
        # # for k, v in vars(value).items():
        # #     logger.info(f"{k}={v}")

        # logger.info("")
        # for k, v in vars(encoder).items():
        #     logger.info(f"{k}={v}")
        # logger.info("")

    def set_matrix(self, matrix):
        self.matrix.set_control_element(matrix)

    @matrix.value
    def matrix_click(self, _, state):
        idx = state.x
        if self._sequencer is None:
            return
        if self.mute_button.is_pressed:
            self._sequencer.toggle_acc_for_step(idx)
        elif self.shift_button.is_pressed:
            self._sequencer.set_length(idx + 1)
        else:
            self._sequencer.toggle_step(idx)

    @instrument_matrix.value
    def instruments_click(self, _, state):
        idx = state.x
        if self._sequencer is None:
            return

        if self.mute_button.is_pressed:
            self._sequencer.mute_instrument(idx)
            self.update_instrument_leds()

        elif self.shift_button.is_pressed:
            self._sequencer.erase_instrument(idx)
            self.update_leds()
        else:
            self._sequencer.selected_instrument = idx
            self.update_instrument_leds()

    @page_matrix.value
    def page_clic(self, _, state):
        idx = state.x

        if self._sequencer is None:
            return

        self._sequencer.set_page(idx)
        self.update_page_leds()

    @shift_button.pressed
    def on_shift_pressed(self, *a, **k):
        self.update_leds()

    @shift_button.released
    def on_shift_released(self, *a):
        self.update_leds()

    @double_button.pressed
    def on_double(self, *a):
        assert self._sequencer
        if self.shift_button.is_pressed:
            self.try_lock_callback()
        else:
            self._sequencer.double_loop()

    @shift_button.value
    def on_shift_pressed2(self, *a, **k):
        logger.info(f"shift pressed: {self.shift_button.is_pressed}")

    @fill_button.pressed
    def on_fill(self, *a):
        if self.shift_button.is_pressed:
            self._sequencer.fill_current_instrument()

        #     self.try_lock_callback()

    @mute_button.pressed
    def on_mute(self, *a):
        if self.shift_button.is_pressed and self._sequencer is not None:
            self._sequencer.clear_all()

    def refresh_all_leds(self):
        self.update_leds()
        self.update_instrument_leds()
        self.update_page_leds()

    def update_leds(self):
        if not self._sequencer:
            return

        steps, accs = self._sequencer.get_current_page()

        # StepButton.[Active][Step][Acc]
        for idx, (state, value, acc) in enumerate(zip(self.matrix, steps, accs)):
            seq_idx = self._sequencer._get_step_idx(idx)
            if self.shift_button.is_pressed:
                if seq_idx < self._sequencer._current_length:
                    state.color = "StepButton.ActiveStepAcc"
                else:
                    state.color = "StepButton.Inactive"

            else:
                if seq_idx == self._sequencer._current_step:
                    is_step = "Step"
                else:
                    is_step = ""

                if value:
                    is_active = "Active"
                else:
                    is_active = "Inactive"

                if acc:
                    is_acc = "Acc"
                else:
                    is_acc = ""

                state.color = "StepButton." + is_active + is_step + is_acc

    def update_instrument_leds(self):
        if not self._sequencer:
            return

        instruments, mutted = self._sequencer.get_instruments()

        for state, value, is_mutted in zip(self.instrument_matrix, instruments, mutted):
            if is_mutted:
                state.color = "InstrumentButton.Mutted"
            elif value:
                state.color = "InstrumentButton.Active"
            else:
                state.color = "InstrumentButton.Inactive"

            # state.color = "DefaultButton.On" if value else "DefaultButton.Off"

    def update_page_leds(self):
        if self._sequencer is None:
            return
        pages = [False] * 4
        pages[self._sequencer._selected_page] = True

        for state, value in zip(self.page_matrix, pages):
            state.color = "DefaultButton.On" if value else "DefaultButton.Off"
