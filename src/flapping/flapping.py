import random
import scriptutl
import flapping_cfg as CFG
import arcade


class Player(arcade.Sprite):
    # state
    LANDED = 0
    FLYING = 1
    # direction
    RIGHT = 0
    LEFT = 1
    NO_DIRECTION = 2

    def __init__(self, img, name):
        super().__init__()
        self.state = Player.FLYING
        self.dir = Player.NO_DIRECTION
        self.score = 0
        self.name = name
        right_texture = arcade.load_texture(img)
        left_texture = arcade.load_texture(img, mirrored=True)
        self.textures.append(right_texture)
        self.textures.append(left_texture)
        self.set_texture(Player.LEFT)

    def on_up(self):
        if self.state == Player.LANDED:
            self.center_y += 1
        elif self.state == Player.FLYING:
            if self.dir == Player.LEFT:
                self.change_x -= CFG.Player.flap_horiz_impulse
            elif self.dir == Player.RIGHT:
                self.change_x += CFG.Player.flap_horiz_impulse
        self.change_y += CFG.Player.jump_speed

    def on_left(self):
        self.dir = Player.LEFT
        self.set_texture(Player.LEFT)

    def on_left_release(self):
        self.dir = Player.NO_DIRECTION

    def on_right(self):
        self.dir = Player.RIGHT
        self.set_texture(Player.RIGHT)

    def on_right_release(self):
        self.dir = Player.NO_DIRECTION

    def on_joyhat(self, hatx, haty):
        if hatx < 0:
            self.dir = Player.LEFT
            self.set_texture(Player.LEFT)
        elif hatx > 0:
            self.dir = Player.RIGHT
            self.set_texture(Player.RIGHT)
        else:
            self.dir = Player.NO_DIRECTION

    def set_landed(self):
        if self.state == Player.FLYING:
            self.state = Player.LANDED

    def set_flying(self):
        if self.state == Player.LANDED:
            self.state = Player.FLYING

    def update(self):
        super().update()
        if self.state == Player.LANDED:
            if self.dir == Player.LEFT:
                self.change_x -= CFG.Player.movement_speed
            elif self.dir == Player.RIGHT:
                self.change_x += CFG.Player.movement_speed
        self.change_x = min(self.change_x, CFG.Player.max_horiz_speed)
        self.change_x = max(self.change_x, -CFG.Player.max_horiz_speed)

    def collision_check(self, walls):
        hit_list = arcade.geometry.check_for_collision_with_list(self, walls)
        if len(hit_list) > 0:
            for item in hit_list:
                if self.center_y > item.center_y:
                    self.bottom = item.top - 1
                    self.change_y = 0.0
                    self.set_landed()
                elif self.center_y < item.center_y:
                    self.top = item.bottom
                    self.change_y = 0.0
        else:
            self.set_flying()

    def respawn(self):
        self.center_x = random.randint(200, 1000)
        self.center_y = 500
        self.change_x = 0.0
        self.change_y = 0.0


class Event:
    """Base abstract class that represents an input event, regardless of device

    This allows mapping from input framework-specific input routines (Arcade and Pyglet)
    to app-specific actions (ex: moving a player). The goal is to avoid framework-specific
    input code and logic leaking into app-specific code.

    Any Event can have `.get_id()` called on it to return a value that represents what type
    of event this is. The value returned is suitable to serve as the key in a dictionary.
    This mapping often looks something like this

        event_mapping[event.get_id()] = player.move_up  # where player.move_up is a method reference
    """
    def get_id(self):
        """Return value that identifies the type of event (usually a tuple)"""
        pass


class KeyPressEvent(Event):
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
        return KeyReleaseEvent(self.key, self.modifiers)


class KeyReleaseEvent(Event):
    def __init__(self, key, modifiers=None):
        assert isinstance(key, int)
        assert isinstance(modifiers, (int, type(None)))
        self.key = key
        self.modifiers = modifiers

    def get_id(self):
        return type(self), self.key


class JoyButtonPressEvent(Event):
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
        return JoyButtonReleaseEvent(self.joy, self.button)


class JoyButtonReleaseEvent(Event):
    def __init__(self, joy, button):
        assert isinstance(joy, arcade.joysticks.pyglet.input.base.Joystick)
        assert isinstance(button, int)
        self.joy = joy
        self.button = button

    def get_id(self):
        return type(self), self.joy, self.button


class JoyHatMotionEvent(Event):
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


class RegistrationEntry:
    """Represents a player during the registration phase"""
    def __init__(self):
        self.name = None
        self.make_name()
        self.flap = None
        self.left = None
        self.right = None

    def is_event_used(self, event):
        used_ids = (
            self.flap.get_id() if self.flap else None,
            self.left.get_id() if self.left else None,
            self.right.get_id() if self.right else None,
        )
        return event.get_id() in used_ids

    def make_name(self):
        self.name = random.choice(list(CFG.Registration.names.keys()))

    def get_summary(self):
        """Return a string representing the player"""
        summary = 'Player:{} FLAP:{} '.format(self.name, self.flap)
        if self.left:
            summary += 'LEFT:{} '.format(self.left)
        if self.right:
            summary += 'RIGHT:{}\n'.format(self.right)
        return summary

    def finalize(self, game):
        """Create Player objects and input handling dict when registration is complete"""
        img = 'img/' + CFG.Registration.names[self.name]
        player = Player(img, self.name)
        game.player_list.append(player)

        # flap
        game.gameplay_input[self.flap.get_id()] = player.on_up

        if isinstance(self.left, JoyHatMotionEvent):
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


class Registration:
    """Hacky class to store state related to the Registration state. Prob should be a "state" class or something."""
    def __init__(self, win_height):
        self.msg = '...'
        self.last_input = None
        self.done = False
        self.entries = []
        self.win_height = win_height

    def on_draw(self):
        arcade.draw_text('Player Registration', 100, self.win_height - 100, arcade.color.WHITE, 40)
        arcade.draw_text(self.msg, 100, self.win_height - 150, arcade.color.WHITE, 30)
        summary = self.get_summary()
        arcade.draw_text(summary, 100, self.win_height - 200, arcade.color.GRAY, 25, anchor_y='top')
        arcade.draw_text('After registering, press FLAP to randomly select a new name.', 100, 40, arcade.color.WHITE, 20)

    def on_event(self, event):
        matched = False
        for entry in self.entries:
            if entry.is_event_used(event):
                matched = True
                if event.get_id() == entry.flap.get_id():
                    entry.make_name()
        if not matched:
            self.last_input = event

    def get_summary(self):
        summaries = [e.get_summary() for e in self.entries]
        if len(summaries) == 0:
            return '<no players registered>'
        return '\n'.join(summaries)

    def finalize(self, game):
        for entry in self.entries:
            entry.finalize(game)


class MyGame(arcade.Window):
    # game states
    WELCOME = 'welcome'
    REGISTRATION = 'registration'
    PLAY = 'gameplay'
    SCOREBOARD = 'scoreboard'

    def __init__(self, width, height, title, fullscreen):
        super().__init__(width, height, title, fullscreen)
        if not fullscreen:
            self.set_location(250, 35)
        self.script = self.game_script()
        self.reg = Registration(height)
        self.reg_script = self.registration_script()
        next(self.script)
        self.window_width = width
        self.window_height = height
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        self.player_list = arcade.SpriteList()
        self.gameplay_input = {
            KeyPressEvent(arcade.key.ESCAPE).get_id(): self.close,
        }

        # gamepad setup
        joysticks = arcade.joysticks.get_game_controllers()
        self.joy = None
        if joysticks:
            for joy in joysticks:
                print('Found joystick: ', joy.device)
                joy.open()
                joy.on_joybutton_press = self.on_joybutton_press
                joy.on_joybutton_release = self.on_joybutton_release
                joy.on_joyhat_motion = self.on_joyhat

    def setup(self, map_name):
        # map
        self.map = arcade.read_tiled_map(map_name)
        self.walls = arcade.generate_sprites(self.map, 'walls', 1.0)
        for s in self.walls.sprite_list:
            s.center_x += 32

        # players
        x = 100
        for p in self.player_list:
            p.center_x = x
            p.center_y = 120
            p.change_x = 0.0
            p.change_y = 0.0
            p.score = 0
            x += 100

    def game_script(self):
        """Generator-based game "script" that drives the game through its main states"""
        self.state = MyGame.WELCOME
        yield from scriptutl.sleep(1.0)

        self.state = MyGame.REGISTRATION
        yield from scriptutl.wait_until(lambda: self.reg.done)

        for i in range(CFG.Game.rounds):
            self.setup(CFG.Game.maps[i % len(CFG.Game.maps)])
            self.state = MyGame.PLAY
            yield from scriptutl.wait_until(self.is_game_over)

            self.state = MyGame.SCOREBOARD
            yield from scriptutl.sleep(2.0)

        print('Game over')

    def registration_script(self):
        """Generator-script that creates players and registers their input"""
        # This is a WIP, experimenting with generator-based scripts to drive sequential logic
        # EDGE: what happens if there are multiple key presses in one frame? Prob need a queue, not a single value.
        # BUG: trying to start game with one player
        # BUG: can register same key multiple times (overwriting previous registration)
        player_num = 0
        while True:
            player_num += 1
            self.reg.msg = 'Press your desired FLAP to register Player {}... ESC to start game.'.format(player_num)
            event = yield from scriptutl.wait_until_non_none(lambda: self.reg.last_input)

            if event.get_id() == KeyPressEvent(arcade.key.ESCAPE).get_id():
                break

            entry = RegistrationEntry()
            self.reg.entries.append(entry)
            entry.flap = event
            self.reg.last_input = None
            self.reg.msg = 'Press LEFT for Player {}'.format(player_num)
            event = yield from scriptutl.wait_until_non_none(lambda: self.reg.last_input)

            if isinstance(event, JoyHatMotionEvent):
                entry.left = event
                entry.right = event
                self.reg.last_input = None
                continue

            entry.left = event
            self.reg.last_input = None
            self.reg.msg = 'Press RIGHT for Player {}'.format(player_num)
            event = yield from scriptutl.wait_until_non_none(lambda: self.reg.last_input)

            entry.right = event
            self.reg.last_input = None

        self.reg.finalize(self)
        self.reg.done = True

    def on_draw(self):
        arcade.start_render()
        if self.state == MyGame.WELCOME:
            arcade.draw_text('Flapping Game', 100, 400, arcade.color.GRAY, 100)
            arcade.draw_text('Flapping Game', 105, 405, arcade.color.GREEN, 100)
        elif self.state == MyGame.REGISTRATION:
            self.reg.on_draw()
        elif self.state == MyGame.PLAY:
            self.walls.draw()
            self.player_list.draw()
            self.draw_scores()
        elif self.state == MyGame.SCOREBOARD:
            arcade.draw_text('Scoreboard', 100, self.window_height - 100, arcade.color.GRAY, 60)
            lines = ['{} = {}'.format(p.name, p.score) for p in self.player_list]
            arcade.draw_text('\n'.join(lines), 100, 100, arcade.color.WHITE, 40)

    def on_key_press(self, key, modifiers):
        event = KeyPressEvent(key, modifiers)
        if self.state == MyGame.REGISTRATION:
            self.reg.on_event(event)
        elif self.state == MyGame.PLAY:
            if event.get_id() in self.gameplay_input:
                self.gameplay_input[event.get_id()]()

    def on_key_release(self, key, modifiers):
        event = KeyReleaseEvent(key, modifiers)
        if self.state == MyGame.PLAY:
            if event.get_id() in self.gameplay_input:
                self.gameplay_input[event.get_id()]()

    def on_joybutton_press(self, joy, button):
        event = JoyButtonPressEvent(joy, button)
        if self.state == MyGame.REGISTRATION:
            self.reg.on_event(event)
        elif self.state == MyGame.PLAY:
            if event.get_id() in self.gameplay_input:
                self.gameplay_input[event.get_id()]()

    def on_joybutton_release(self, joy, button):
        event = JoyButtonReleaseEvent(joy, button)
        if self.state == MyGame.PLAY:
            if event.get_id() in self.gameplay_input:
                self.gameplay_input[event.get_id()]()

    def on_joyhat(self, joy, hatx, haty):
        # Many gamepads must be in "analog" mode for the "hat" to report values
        event = JoyHatMotionEvent(joy, hatx, haty)
        if self.state == MyGame.REGISTRATION:
            if hatx != 0:
                self.reg.on_event(event)
        elif self.state == MyGame.PLAY:
            if event.get_id() in self.gameplay_input:
                self.gameplay_input[event.get_id()](hatx, haty)

    def update(self, delta_time):
        if self.state == MyGame.WELCOME:
            pass
        elif self.state == MyGame.REGISTRATION:
            try:
                next(self.reg_script)
            except StopIteration:
                pass
        elif self.state == MyGame.PLAY:
            self.player_list.update()

            # Prevent partial-pixel positioning, which can cause edge artifacts on player sprites.
            # This also makes it a bit easier to "stop" a player.
            for player in self.player_list:
                player.center_x = int(player.center_x)
                player.center_y = int(player.center_y)

            for p in self.player_list:
                p.collision_check(self.walls)
            for p in self.player_list:
                p.change_y -= 0.2  # gravity
                if p.center_x < 0:
                    p.center_x = self.window_width
                elif p.center_x > self.window_width:
                    p.center_x = 0
            self.check_player_collision()
        try:
            next(self.script)
        except StopIteration:
            self.close()

    def check_player_collision(self):
        for idx1, p1 in enumerate(self.player_list):
            for idx2 in range(idx1 + 1, len(self.player_list)):
                p2 = self.player_list[idx2]
                if arcade.check_for_collision(p1, p2):
                    if int(p1.center_y) == int(p2.center_y):
                        # equal collision
                        if p1.center_x < p2.center_x:
                            p1.center_x += -1
                            p1.change_x = -0.5
                            p1.change_y = 0.0
                            p2.center_x += 1
                            p2.change_x = 0.5
                            p2.change_y = 0.0
                        else:
                            p1.center_x += 1
                            p1.change_x = 0.5
                            p1.change_y = 0.0
                            p2.center_x += -1
                            p2.change_x = -0.5
                            p2.change_y = 0.0
                    elif p1.center_y > p2.center_y:
                        p1.score += 1
                        p2.respawn()
                    elif p2.center_y > p1.center_y:
                        p2.score += 1
                        p1.respawn()

    def print_scores(self):
        for p in self.player_list:
            print('{}: {}'.format(p.name, p.score))

    def is_game_over(self):
        scores = [p.score for p in self.player_list]
        return max(scores) >= CFG.Game.goal_score

    def draw_scores(self):
        labels = ['{}: {}'.format(p.name, p.score) for p in self.player_list]
        arcade.draw_text('    '.join(labels), 50, 5, arcade.color.WHITE, 20)


def main():
    app = MyGame(1280, 720, 'Flapping', CFG.Window.fullscreen)
    arcade.run()


if __name__ == "__main__":
    main()
