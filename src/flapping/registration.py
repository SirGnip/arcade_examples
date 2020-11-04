import itertools
import inspect
import pickle
import traceback
from typing import Iterator, List, Optional, TYPE_CHECKING

import arcade
import pyglet

from flapping import event
from gnp.arcadelib import scriptutl
from flapping.player import Player
from flapping import flapping_cfg as CFG


if TYPE_CHECKING:  # prevent circular import reference caused by type hinting
    from flapping.flap_app import Game


class Registration:
    """Hacky class to store state related to the Registration state. Prob should be a "state" class or something."""
    def __init__(self, game: "Game", win_height: int):
        self.msg = '...'
        self.last_input: Optional[event.Event] = None
        self.done = False
        self.entries: List["_RegistrationEntry"] = []
        self.win_height = win_height
        self.game = game
        self.script = self.registration_script()

    @staticmethod
    def _get_device_locked_event(evt: Optional[event.Event], cur_joy) -> Optional[event.Event]:
        """Used by scriptutil.wait_until_non_none() to block until a key locked to current input device has been pressed"""
        if evt is not None:
            if evt.get_id() == event.KeyPress(arcade.key.ESCAPE).get_id():
                return None

            if cur_joy is None:
                # keyboard input
                if isinstance(evt, event.KeyPress):
                    return evt
                else:
                    return None
            else:
                # joystick input
                if isinstance(evt, (event.JoyButtonPress, event.JoyHatMotion)):
                    if evt.joy == cur_joy:
                        return evt
                    return None
                else:
                    return None
        return None

    def registration_script(self) -> Iterator[None]:
        """Generator-script that creates players and registers their input"""
        self.load_players()
        player_num = len(self.entries)

        while True:
            player_num += 1
            self.msg = 'Press your desired FLAP to register Player {}...\nESC to start game. F5 to clear bottom player.'.format(player_num)
            evt = yield from scriptutl.wait_until_non_none(lambda: self.last_input if not isinstance(self.last_input, event.JoyHatMotion) else None)

            # clear player list
            if evt.get_id() == event.KeyPress(arcade.key.F5).get_id():
                if len(self.entries) > 0:
                    self.entries.pop()
                    self.last_input = None
                    player_num -= 1
                    continue

            # end registration
            if evt.get_id() == event.KeyPress(arcade.key.ESCAPE).get_id():
                self.last_input = None
                if len(self.entries) > 0:
                    break
                else:
                    print('WARNING: Game can not start with no players')
                    continue

            entry = _RegistrationEntry()
            self.entries.append(entry)
            entry.flap = evt
            flap_joy = None
            if isinstance(evt, event.JoyButtonPress):
                flap_joy = evt.joy
            self.last_input = None
            self.msg = 'Press LEFT for Player {}'.format(player_num)
            evt = yield from scriptutl.wait_until_non_none(lambda: self._get_device_locked_event(self.last_input, flap_joy))

            if isinstance(evt, event.JoyHatMotion):
                entry.left = evt
                entry.right = evt
                self.last_input = None
                continue

            entry.left = evt
            self.last_input = None
            self.msg = 'Press RIGHT for Player {}'.format(player_num)
            evt = yield from scriptutl.wait_until_non_none(lambda: self._get_device_locked_event(self.last_input, flap_joy))

            entry.right = evt
            self.last_input = None

        self.finalize()
        self.done = True

    def on_draw(self) -> None:
        arcade.draw_text('Player Registration', 25, self.win_height - 75, CFG.UI.HEADER_COLOR, 40)
        arcade.draw_text(self.msg, 25, self.win_height - 175, CFG.UI.HEADER_COLOR, 30)
        summary = self.get_summary()
        arcade.draw_text(summary, 25, self.win_height - 200, CFG.UI.BODY_COLOR, 25, anchor_y='top')
        arcade.draw_text('After registering, press FLAP to cycle through names.', 100, 40, CFG.UI.HEADER_COLOR, 20)

    def on_event(self, evt: event.Event) -> None:
        matched = False
        for entry in self.entries:
            if entry.is_event_used(evt):
                matched = True
                if evt.get_id() == entry.flap.get_id():
                    entry.make_name()
        if not matched:
            self.last_input = evt

    def get_summary(self) -> str:
        summaries = [e.get_summary() for e in self.entries]
        if len(summaries) == 0:
            return '<no players registered>'
        return '\n'.join(summaries)

    def finalize(self) -> None:
        self.save_players()
        for entry in self.entries:
            entry.finalize(self.game)

    def save_players(self) -> None:
        def get_persistent_id(obj) -> Optional[int]:
            """Pickle pyglet's Joystick object by simply saving index into list"""
            if isinstance(obj, pyglet.input.base.Joystick):
                joy_idx = self.game.joysticks.index(obj)
                print('  Pickling joystick idx #{} {}'.format(joy_idx, obj.device))
                return joy_idx
            return None

        with open(CFG.Player.filename, 'wb') as out_file:
            print('Saving player list to {}'.format(CFG.Player.filename))
            pickler = pickle.Pickler(out_file)
            pickler.persistent_id = get_persistent_id  # type: ignore[assignment]
            pickler.dump(self.entries)

    def load_players(self) -> None:
        def load_from_persistent_id(persist_id) -> pyglet.input.base.Joystick:
            """Unpickle pyglet's Joystick object by using index to lookup joystick in list"""
            print('  Unpickling object using persistent_id:', persist_id)
            joystick_idx = persist_id
            joy = self.game.joysticks[joystick_idx]
            print('  Unpickling joystick:', joy.device)
            return joy

        try:
            print('Attempting to load last players from {}'.format(CFG.Player.filename))
            with open(CFG.Player.filename, 'rb') as in_file:
                unpickler = pickle.Unpickler(in_file)
                unpickler.persistent_load = load_from_persistent_id  # type: ignore[assignment]
                self.entries = unpickler.load()
                print('Loaded {} players'.format(len(self.entries)))
        except Exception as exc:
            print('WARNING: Problem loading previous player list from file:"{}" so starting with an empty player list. Exception: {}'.format(CFG.Player.filename, type(exc)))
            traceback.print_exc()


class _RegistrationEntry:
    """Represents a player during the registration phase"""
    def __init__(self):
        self.name: str
        self.names = itertools.cycle(sorted(CFG.Registration.names.keys()))
        self.make_name()
        self.flap = None
        self.left = None
        self.right = None

    def is_event_used(self, evt: event.Event):
        used_ids = (
            self.flap.get_id() if self.flap else None,
            self.left.get_id() if self.left else None,
            self.right.get_id() if self.right else None,
        )
        return evt.get_id() in used_ids

    def make_name(self) -> None:
        self.name = next(self.names)

    def get_summary(self) -> str:
        """Return a string representing the player"""
        key_constants = [(name, value) for name, value in inspect.getmembers(arcade.key) if not name.startswith('__') and not name.startswith("MOTION")]
        key_name_lookup = {}
        for key_name, key_id in key_constants:
            key_name_lookup[key_id] = key_name

        if self.flap is None:
            flap = ""
        else:
            if not str(self.flap).isascii():
                flap = key_name_lookup[self.flap.key]
            else:
                flap = str(self.flap)

        if self.left is None:
            left = ""
        else:
            if not str(self.left).isascii():
                left = key_name_lookup[self.left.key]
            else:
                left = str(self.left)

        if self.right is None:
            right = ""
        else:
            if not str(self.right).isascii():
                right = key_name_lookup[self.right.key]
            else:
                right = str(self.right)

        summary = f'Player:{self.name} {flap} / {left} / {right}\n'
        return summary

    def finalize(self, game: 'Game') -> None:
        """Create Player objects and input handling dict when registration is complete"""
        img = 'img/' + CFG.Registration.names[self.name]
        player = Player(img, self.name, game)
        game.player_list.append(player)

        # flap
        game.gameplay_input[self.flap.get_id()] = player.on_up

        if isinstance(self.left, event.JoyHatMotion):
            # left & right with joyhat
            game.gameplay_input[self.left.get_id()] = player.on_joyhat
            game.gameplay_input[self.right.get_id()] = player.on_joyhat
        else:
            # left
            game.gameplay_input[self.left.get_id()] = player.on_left
            left_release_event_id = self.left.make_release().get_id()
            game.gameplay_input[left_release_event_id] = player.on_left_release
            # right
            game.gameplay_input[self.right.get_id()] = player.on_right
            right_release_event_id = self.right.make_release().get_id()
            game.gameplay_input[right_release_event_id] = player.on_right_release
