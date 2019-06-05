import arcade
"""
These classes make it easier to map input from framework-specific input routines (Arcade and Pyglet)
to app-specific actions (ex: moving a player). The goal is to avoid framework-specific
input code leaking into app-specific code.

Any Event can have `.get_id()` called on it to return a value that represents what type
of event this is. The value returned is suitable to serve as the key in a dictionary.
This mapping often looks something like this

    event_mapping[event.get_id()] = player.move_up  # where player.move_up is a method reference
"""


class Event:
    """Base abstract class that represents an input event, regardless of device"""
    def get_id(self):
        """Return a value that identifies the type of event (usually a tuple)"""
        pass


class KeyPress(Event):
    def __init__(self, key, modifiers=None):
        assert isinstance(key, int)
        assert isinstance(modifiers, (int, type(None)))
        self.key = key
        self.modifiers = modifiers

    def get_id(self):
        return type(self), self.key

    def __str__(self):
        return chr(self.key)

    def make_release(self):
        return KeyRelease(self.key, self.modifiers)


class KeyRelease(Event):
    def __init__(self, key, modifiers=None):
        assert isinstance(key, int)
        assert isinstance(modifiers, (int, type(None)))
        self.key = key
        self.modifiers = modifiers

    def get_id(self):
        return type(self), self.key


class JoyButtonPress(Event):
    def __init__(self, joy, button):
        assert isinstance(joy, arcade.joysticks.pyglet.input.base.Joystick)
        assert isinstance(button, int)
        self.joy = joy
        self.button = button

    def get_id(self):
        return type(self), self.joy, self.button

    def __str__(self):
        return 'JoyBtn{}'.format(self.button)

    def make_release(self):
        return JoyButtonRelease(self.joy, self.button)


class JoyButtonRelease(Event):
    def __init__(self, joy, button):
        assert isinstance(joy, arcade.joysticks.pyglet.input.base.Joystick)
        assert isinstance(button, int)
        self.joy = joy
        self.button = button

    def get_id(self):
        return type(self), self.joy, self.button


class JoyHatMotion(Event):
    def __init__(self, joy, hatx, haty):
        assert isinstance(joy, arcade.joysticks.pyglet.input.base.Joystick)
        assert isinstance(hatx, int)
        assert isinstance(haty, int)
        self.joy = joy
        self.hatx = hatx
        self.haty = haty

    def get_id(self):
        return type(self), self.joy

    def __str__(self):
        return 'JoyHat'
