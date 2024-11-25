import importlib
import logging
import os
import traceback

from ableton.v2.base import listens
from ableton.v3.control_surface import (
    ControlSurface,
    ControlSurfaceSpecification,
    create_skin,
)

from ableton.v3.control_surface.capabilities import (
    CONTROLLER_ID_KEY,
    NOTES_CC,
    PORTS_KEY,
    REMOTE,
    SCRIPT,
    controller_id,
    inport,
    outport,
)

from . import ara


logger = logging.getLogger("ara")


def get_capabilities():
    return {
        CONTROLLER_ID_KEY: controller_id(
            vendor_id=5824,
            product_ids=[1161],
            model_name=["ARAv2"],
        ),
        PORTS_KEY: [inport(props=[NOTES_CC, SCRIPT, REMOTE]), outport(props=[SCRIPT])],
    }


def create_mappings(control_surface):
    mappings = {}

    mappings["StepDecoder"] = dict(
        matrix="steps_buttons",
        instrument_matrix="instruments_buttons",
        shift_button="shift_button",
        mute_button="mute_button",
        double_button="double_button",
        page_matrix="page_buttons",
        fill_button="fill_button",
        encoder_matrix="encoder_matrix",
    )

    return mappings


class Specification(ControlSurfaceSpecification):
    elements_type = ara.Elements
    control_surface_skin = create_skin(skin=ara.Skin)
    create_mappings_function = create_mappings
    component_map = {
        "Note_Editor": ara.NoteEditorComponent,
        "StepDecoder": ara.StepDecoder,
    }


def create_instance(c_instance):
    return ARA(Specification, c_instance=c_instance)


class ARA(ControlSurface):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)

        self.log_level = "info"

        self.start_logging()

        self.show_message("ARA: init mate")
        logger.info("ARA: init started ...")
        self.schedule_message(3, self.reflect_device)

    def setup(self):
        super().setup()
        self.init()

    def reload_imports(self):
        try:
            importlib.reload(ara.sequencer)
            importlib.reload(ara.note_editor)
            importlib.reload(ara.decoder)

        except Exception as e:
            exc = traceback.format_exc()
            logging.warning(exc)

    def init(self):
        self.reload_imports()
        self.target_clip = None
        self.target_clip_slot_index = None
        self.target_track = None
        self.target_device = None
        logger.info("init started:")
        with self.component_guard():
            logger.info("   adding sking")
            self._skin = create_skin(skin=ara.Skin, colors=ara.Rgb)

            logger.info("   adding listeners")

            self._ARA__on_selected_track_changed.subject = self.song.view

            logger.info("   adding listeners done")

            logger.info("creating components")
            logger.info("   creating sequencer")
            self.create_sequencer()

            logger.info("   creating note editor")
            self.create_note_editor()

            self._sequencer.set_editor(self._note_editor)

            self.component_map["StepDecoder"].sequencer = self._sequencer

            logger.info(f" ara is enabled= {self._enabled}")
            self.component_map["StepDecoder"].refresh_all_leds()
            self.component_map["StepDecoder"].try_lock_callback = (
                lambda: self.try_lock_track()
            )
            self.component_map["StepDecoder"].send_midi = self._send_midi

            self.get_target_track()
            self.create_clip()
            self.reflect_device()

    def get_target_track(self) -> None:

        self.target_track = None
        tracks = self.song.tracks
        for track in tracks:
            if track.name.lower() == "ara":
                self.target_track = track
                self._ARA__on_playing_clip_changed.subject = self.target_track
                break

        self.create_clip()
        self.reflect_device()

    def try_lock_track(self):
        logger.info(f"try lock track {self.song.view.selected_track.name}")
        self.target_track = self.song.view.selected_track
        self._ARA__on_playing_clip_changed.subject = self.target_track

        self.create_clip()
        self.reflect_device()

    def assign_target_clip(self):
        self._note_editor.set_clip(self.target_clip)
        self._ARA__on_playhead_move.subject = self.target_clip
        self.try_grab_device()
        self._sequencer.clear_all()
        self._sequencer.syncState()

    def create_clip(self):
        if self.target_track is None:
            return

        logger.info(f"Target track: {self.target_track.name}")
        self._ARA__on_devices_changed.subject = self.target_track

        slot = self.target_track.clip_slots[0]
        if slot.has_clip:
            self.target_clip = slot.clip
            self.target_clip.fire()
        else:
            self.target_clip = slot.create_clip(4)
            slot.fire()

        self.assign_target_clip()

        logger.info("creating clip done")

    def try_grab_device(self):
        if self.target_track is None:
            self.target_device = None
            return

        logger.info(f"devices={self.target_track.devices}")
        device = self.target_track.devices[0]

        logger.info(f"pad={device.drum_pads[36]}")
        logger.info(f"pad={device.drum_pads[36].chains}")
        logger.info(f"pad={device.drum_pads[36].chains[0]}")
        logger.info(f"pad={device.drum_pads[36].chains[0].mixer_device}")
        logger.info(f"pad={device.drum_pads[36].chains[0].mixer_device.volume}")

        if device.can_have_drum_pads:
            self.target_device = device
            self._sequencer.set_device(device)
            self.component_map["StepDecoder"].set_device(device)

    def reflect_device(self):
        logger.info("reflecting device")
        if getattr(self._sequencer, "_device", None) is None:
            return
        self._sequencer.syncState()
        self._send_midi((0x90, 0, 127))
        self.schedule_message(1, self.component_map["StepDecoder"].refresh_all_leds)

    def create_note_editor(self):
        self._note_editor = ara.NoteEditorComponent(
            is_enabled=False,
            sequencer_clip=self.target_clip,
            sequencer=self._sequencer,
        )

    def create_sequencer(self):
        self._sequencer = ara.Sequencer()

    def start_logging(self):
        """
        Start logging to a local logfile (logs/abletonosc.log),
        and relay error messages via OSC.
        """
        module_path = os.path.dirname(os.path.realpath(__file__))
        log_dir = os.path.join(module_path, "logs")
        if not os.path.exists(log_dir):
            os.mkdir(log_dir, 0o755)
        log_path = os.path.join(log_dir, "ara.log")
        self.log_file_handler = logging.FileHandler(log_path)
        self.log_file_handler.setLevel(self.log_level.upper())
        formatter = logging.Formatter("(%(asctime)s) [%(levelname)s] %(message)s")
        self.log_file_handler.setFormatter(formatter)
        logger.addHandler(self.log_file_handler)

    def stop_logging(self):
        logger.removeHandler(self.log_file_handler)

    def disconnect(self):
        self.show_message("Disconnecting...")
        logger.info("Disconnecting...")
        self.stop_logging()
        super().disconnect()

    @listens("selected_track")
    def __on_selected_track_changed(self):
        logger.info(f"selected track changed: {self.song.view.selected_track.name}")

    @listens("playing_position")
    def __on_playhead_move(self):

        if self.target_clip is not None:
            self._sequencer.set_position(self.target_clip.playing_position)

    @listens("devices")
    def __on_devices_changed(self):
        self.try_grab_device()

    @listens("playing_slot_index")
    def __on_playing_clip_changed(self):
        if self.target_track is None:
            return
        if self.target_track.playing_slot_index < 0:
            self.target_clip = None
            return

        if self.target_track.playing_slot_index == self.target_clip_slot_index:
            return

        self.target_clip_slot_index = self.target_track.playing_slot_index
        logger.info(f"playing clip changed: {self.target_clip_slot_index}")

        self.target_clip = self.target_track.clip_slots[
            self.target_clip_slot_index
        ].clip
        self.assign_target_clip()
