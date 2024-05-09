from ableton.v3.base import depends, listenable_property, listens
from ableton.v3.control_surface import Component
from ableton.v3.control_surface.controls import ButtonControl, control_matrix
from ableton.v3.live import liveobj_changed, liveobj_valid
from Live.Clip import MidiNoteSpecification  # type: ignore
import logging
from .sequencer import Sequencer
from typing import Optional, Any

logger = logging.getLogger("ara")


def get_notes(clip, pitches, time, length, all_pitches=False):
    if len(pitches) > 1 or all_pitches:
        return clip.get_notes_extended(
            from_time=time, from_pitch=0, time_span=length, pitch_span=128
        )
    return clip.get_notes_extended(
        from_time=time, from_pitch=(pitches[0]), time_span=length, pitch_span=1
    )


def remove_notes(clip, pitches, time, length, all_pitches=False):
    """
    Remove notes for each pitch in pitches at the given time and length.
    """
    if len(pitches) > 1 or all_pitches:
        clip.remove_notes_extended(
            from_time=time, from_pitch=0, time_span=length, pitch_span=128
        )
    else:
        clip.remove_notes_extended(
            from_time=time, from_pitch=(pitches[0]), time_span=length, pitch_span=1
        )


class StepButtonControl(ButtonControl):

    class State(ButtonControl.State):
        x = property(lambda self: self.coordinate[1])
        y = property(lambda self: self.coordinate[0])
        is_active = False


class NoteEditorComponent(Component):
    """
    This is duplicated from the original ableton/v3

    """

    ## no fucking idea what this is
    # __events__ = ('clip_notes', )
    matrix = control_matrix(StepButtonControl)

    ## not sure how this works, but I think it only validates these dependencies when the component is enabled, nope
    @depends(target_track=None, sequencer_clip=None)
    def __init__(
        self,
        name="Note_Editor",
        target_track: Any = None,
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

        self._target_track = target_track

        assert sequencer is not None
        self._sequencer = sequencer
        self._sequencer.set_note_creator_destructor(
            self.create_note_step, self.delete_note_step
        )

        ## this errors for some reason
        ## EventError: Object <Clip.Clip object at 0x138a99ce0> missing "add" method for event: clip
        # logger.info("Setting callbacks")
        # self._AraNoteEditorComponent__on_sequencer_clip_changed.subject = sequencer_clip
        # self._AraNoteEditorComponent__on_sequencer_clip_changed()

    def create_note_step(self, pitch, time):
        assert self._has_clip()
        assert self._clip is not None
        velocity = 127
        note = MidiNoteSpecification(
            pitch=pitch,
            start_time=time,
            duration=0.25,
            velocity=velocity,
            mute=False,
        )
        self._clip.add_new_notes((note,))
        self._clip.deselect_all_notes()

        # self._add_new_note_in_step(pitch, time)

    def delete_note_step(self, pitch, time):
        assert self._has_clip()
        assert self._clip is not None

        self._clip.remove_notes_extended(
            from_time=time, from_pitch=pitch, time_span=0.25, pitch_span=1
        )
        # self._delete_notes_in_step(pitch, time)

    def set_clip(self, clip):
        if liveobj_changed(clip, self._clip):
            self._clip = clip

            # self._NoteEditorComponent__on_clip_notes_changed.subject = clip
            # self._NoteEditorComponent__on_clip_notes_changed()

    def set_matrix(self, matrix):
        self.matrix.set_control_element(matrix)
        # for button in self.matrix:
        #     button.channel = self._translation_channel

        # self._update_editor_matrix()

    def _can_edit(self):
        return True
        1 / 0  # this should assert that there is a pitch selected
        pass
        # return len(self._pitches) != 0

    def _has_clip(self):
        return self._clip is not None and liveobj_valid(self._clip)

    @matrix.pressed
    def matrix(self, pad):
        self._on_pad_pressed(pad)

    def _on_pad_pressed(self, pad):
        logger.info(f"pad={pad} x={pad.x} y={pad.y} is_enabled={self.is_enabled()}")
        if self.is_enabled():

            if not self._has_clip():
                self.set_clip(self._sequencer_clip)

            pad.is_active = True

    @matrix.released_immediately
    def matrix(self, pad):
        self._on_release_step(pad, can_add_or_remove=True)

    @matrix.released_delayed
    def matrix(self, pad):
        self._on_release_step(pad)

    def _on_release_step(self, step, can_add_or_remove=False):
        if step.is_active:
            if can_add_or_remove:
                self._sequencer.toggle_step(step.coordinate[1])

        step.is_active = False

    def _release_active_steps(self):
        for step in self.matrix:
            self._on_release_step(step)

    # def update(self):
    #     super().update()

    @listens("notes")
    def __on_clip_notes_changed(self):
        self._clip_notes = []
        if self._has_clip():
            if self._can_edit():
                start, length = self._get_clip_notes_time_range()
                self._clip_notes = get_notes(
                    self._clip,
                    self._pitches,
                    start,
                    length,
                    self._pitch_provider.is_polyphonic,
                )
        self._update_editor_matrix()
        self.notify_clip_notes()

    @listens("clip")
    def __on_sequencer_clip_changed(self):
        self.set_clip(self._sequencer_clip.clip)

    @listens("target_track.color")
    def __on_target_track_color_changed(self):
        self._update_editor_matrix()

    @listens("is_polyphonic")
    def __on_provider_polyphony_changed(self, _):
        self._NoteEditorComponent__on_clip_notes_changed()

    @listens("index")
    def __on_resolution_changed(self, *_):
        self._release_active_steps()
        self._update_from_grid()
        self.notify_page_length()
        self._NoteEditorComponent__on_clip_notes_changed()
