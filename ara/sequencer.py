from typing import Optional, Tuple, Any, Callable, List
from ableton.v2.control_surface import Component  # type: ignore
import logging
from ableton.v2.base import listens  # type: ignore

logger = logging.getLogger("ara")

START_DRUM_NOTE = 36


class Sequencer:
    update_leds_callback: Callable[[], None]
    update_inst_leds_callback: Callable[[], None]

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.logger = logging.getLogger("ara")
        self.logger.info("sequencer init called")
        self.reset()

    def reset(self):
        self.state = [[False for _ in range(16 * 4)] for _ in range(8)]
        self.acc = [[False for _ in range(16 * 4)] for _ in range(8)]
        self.instrument_mute = [False for _ in range(8)]
        self._selected_instrument = 0
        self._selected_page = 0
        self._current_step = 0
        self._current_length = 16

    def set_editor(self, editor):
        self._editor = editor

    def set_device(self, device):
        self._device = device

    @property
    def selected_instrument(self):
        return self._selected_instrument

    def _get_step_idx(self, idx):
        return idx + self._selected_page * 16

    @selected_instrument.setter
    def selected_instrument(self, value):
        assert 0 <= value < 8
        self._selected_instrument = value
        if self.update_leds_callback:
            self.update_leds_callback()

        if self.update_inst_leds_callback:
            self.update_inst_leds_callback()

    def toggle_step(self, idx):
        self.state[self._selected_instrument][self._get_step_idx(idx)] = not self.state[
            self._selected_instrument
        ][self._get_step_idx(idx)]
        logger.info(f"toggled step {idx} for instrument {self._selected_instrument}")

        if self.state[self._selected_instrument][self._get_step_idx(idx)]:
            self._editor.create_note(
                self._selected_instrument + START_DRUM_NOTE,
                (self._get_step_idx(idx)) / 4,
                self.acc[self._selected_instrument][self._get_step_idx(idx)],
            )
        else:
            self._editor.delete_note(
                self._selected_instrument + START_DRUM_NOTE,
                (self._get_step_idx(idx)) / 4,
            )

        if self.update_leds_callback:
            self.update_leds_callback()

    def get_current_page(self) -> Tuple[List[bool], List[bool]]:
        return (
            self.state[self._selected_instrument][
                self._selected_page * 16 : (self._selected_page + 1) * 16
            ],
            self.acc[self._selected_instrument][
                self._selected_page * 16 : (self._selected_page + 1) * 16
            ],
        )

    def get_instruments(self) -> Tuple[List[bool], List[bool]]:
        return [i == self._selected_instrument for i in range(8)], self.instrument_mute

    def set_position(self, position: float):
        step = int(4 * position)
        if step != self._current_step:
            self._current_step = step
            if self.update_leds_callback:
                self.update_leds_callback()

    def set_length(self, length):
        self._editor.set_length(self._get_step_idx(length) / 4)
        self._current_length = self._get_step_idx(length)
        self.update_leds_callback()

    def erase_instrument(self, instrument):
        self._editor.delete_all_note_steps_for_pitch(instrument + START_DRUM_NOTE)
        for i in range(4 * 16):
            self.state[instrument][i] = False
            self.acc[instrument][i] = False
        self.update_leds_callback()

    def double_loop(self):
        for instrument in range(8):
            for i in range(self._current_length):
                self.state[instrument][i + self._current_length] = self.state[
                    instrument
                ][i]
                self.acc[instrument][i + self._current_length] = self.acc[instrument][i]

        self._current_length *= 2

        self._editor.double_loop()
        self.update_leds_callback()

    def toggle_acc_for_step(self, idx):
        self.acc[self._selected_instrument][self._get_step_idx(idx)] = not self.acc[
            self._selected_instrument
        ][self._get_step_idx(idx)]
        if self.state[self._selected_instrument][self._get_step_idx(idx)]:
            self.toggle_step(
                idx
            )  # toggle will do the translating so no need to do it here
            self.toggle_step(idx)

    def set_page(self, page):
        self._selected_page = page

    def mute_instrument(self, instrument):
        self._device.drum_pads[instrument + START_DRUM_NOTE].mute = (
            not self._device.drum_pads[instrument + START_DRUM_NOTE].mute
        )
        self.instrument_mute[instrument] = self._device.drum_pads[
            instrument + START_DRUM_NOTE
        ].mute
        self.update_inst_leds_callback()

    def clear_all(self):
        self.reset()
        self.update_leds_callback()

    def fill_current_instrument(self):
        for i in range(self._current_length):
            self.state[self._selected_instrument][i] = True
            self.acc[self._selected_instrument][i] = False
            self._editor.create_note(
                self._selected_instrument + START_DRUM_NOTE,
                (i) / 4,
                False,
            )

        self.update_leds_callback()
        self.update_inst_leds_callback()
