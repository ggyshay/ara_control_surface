from ableton.v3.base import depends, listenable_property, listens
from ableton.v3.control_surface import Component
from ableton.v3.control_surface.controls import ButtonControl, control_matrix
from ableton.v3.live import liveobj_changed, liveobj_valid
from Live.Clip import MidiNoteSpecification  # type: ignore
import logging
from .sequencer import Sequencer
from typing import Optional, Any

logger = logging.getLogger("ara")


# def get_notes(clip, pitches, time, length, all_pitches=False):
#     if len(pitches) > 1 or all_pitches:
#         return clip.get_notes_extended(
#             from_time=time, from_pitch=0, time_span=length, pitch_span=128
#         )
#     return clip.get_notes_extended(
#         from_time=time, from_pitch=(pitches[0]), time_span=length, pitch_span=1
#     )


# def remove_notes(clip, pitches, time, length, all_pitches=False):
#     """
#     Remove notes for each pitch in pitches at the given time and length.
#     """
#     if len(pitches) > 1 or all_pitches:
#         clip.remove_notes_extended(
#             from_time=time, from_pitch=0, time_span=length, pitch_span=128
#         )
#     else:
#         clip.remove_notes_extended(
#             from_time=time, from_pitch=(pitches[0]), time_span=length, pitch_span=1
#         )


def assert_clip_valid(clip):

    def decorator(func):
        def wrapper(*args, **kwargs):
            assert clip is not None
            assert liveobj_valid(clip)
            return func(*args, **kwargs)

        return wrapper

    return decorator


class NoteEditorComponent(Component):
    """
    This is duplicated from the original ableton/v3

    """

    ## no fucking idea what this is
    # __events__ = ('clip_notes', )

    ## not sure how this works, but I think it only validates these dependencies when the component is enabled, nope
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

        ## this errors for some reason
        ## EventError: Object <Clip.Clip object at 0x138a99ce0> missing "add" method for event: clip
        # logger.info("Setting callbacks")
        # self._AraNoteEditorComponent__on_sequencer_clip_changed.subject = sequencer_clip
        # self._AraNoteEditorComponent__on_sequencer_clip_changed()

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

        ####################################################################################################

        # self._NoteEditorComponent__on_clip_notes_changed.subject = clip
        # self._NoteEditorComponent__on_clip_notes_changed()

    # @listens("notes")
    # def __on_clip_notes_changed(self):
    #     self._clip_notes = []
    #     if self._has_clip():
    #         if self._can_edit():
    #             start, length = self._get_clip_notes_time_range()
    #             self._clip_notes = get_notes(
    #                 self._clip,
    #                 self._pitches,
    #                 start,
    #                 length,
    #                 self._pitch_provider.is_polyphonic,
    #             )
    #     self._update_editor_matrix()
    #     self.notify_clip_notes()

    # @listens("clip")
    # def __on_sequencer_clip_changed(self):
    #     self.set_clip(self._sequencer_clip.clip)
