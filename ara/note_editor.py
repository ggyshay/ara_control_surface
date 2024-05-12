import logging
from typing import Any, Optional

from ableton.v3.control_surface import Component
from ableton.v3.live import liveobj_changed, liveobj_valid
from Live.Clip import MidiNoteSpecification  # type: ignore

from .sequencer import Sequencer

logger = logging.getLogger("ara")


def assert_clip_valid(clip):

    def decorator(func):
        def wrapper(*args, **kwargs):
            assert clip is not None
            assert liveobj_valid(clip)
            return func(*args, **kwargs)

        return wrapper

    return decorator


class NoteEditorComponent(Component):
    def __init__(
        self,
        name="Note_Editor",
        sequencer_clip: Any = None,
        sequencer: Optional[Sequencer] = None,
        *a,
        **k,
    ):
        logger.info(f"args=[{a}], kwargs=[{k}]")
        super().__init__(name=name, *a, **k)
        # (super().__init__)(a, name=name, **k)

        self._clip_notes = []
        self._clip = None
        self._sequencer_clip = sequencer_clip
        self.set_clip(self._sequencer_clip)

        assert sequencer is not None
        self._sequencer = sequencer

    def create_note(self, pitch, time, acc):
        assert self._has_clip()
        assert self._clip is not None
        velocity = 127 if acc else 90
        note = MidiNoteSpecification(
            pitch=pitch,
            start_time=time,
            duration=0.25,
            velocity=velocity,
            mute=False,
        )
        self._clip.add_new_notes((note,))
        self._clip.deselect_all_notes()

    def delete_note(self, pitch: int, time: float):
        assert self._has_clip()
        assert self._clip is not None

        self._clip.remove_notes_extended(
            from_time=time, from_pitch=pitch, time_span=0.25, pitch_span=1
        )

    def set_length(self, length: float):
        assert self._has_clip()
        assert self._clip is not None

        self._clip.loop_end = length

    def double_loop(self):
        assert self._clip is not None

        self._clip.duplicate_loop()

    def delete_all_note_steps_for_pitch(self, pitch):
        assert self._clip is not None

        self._clip.remove_notes_extended(
            from_time=0, from_pitch=pitch, time_span=100, pitch_span=1
        )

    def get_clip_notes(self):
        assert self._has_clip()
        assert self._clip is not None

        return self._clip.get_notes_extended(
            from_time=0, from_pitch=0, time_span=16, pitch_span=128
        )

    def set_clip(self, clip):
        if liveobj_changed(clip, self._clip):
            self._clip = clip

    def _has_clip(self):
        return self._clip is not None and liveobj_valid(self._clip)

    def clear_clip(self):
        assert self._has_clip()
        assert self._clip is not None

        self._clip.remove_notes_extended(0, 0, 100, 128)
