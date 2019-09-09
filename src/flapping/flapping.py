import random
import itertools
import traceback
import pickle
import scriptutl
import flapping_cfg as CFG
import event
import collision
import arcade
import pyglet

HEADER_COLOR = arcade.color.PEACH_ORANGE
BODY_COLOR = arcade.color.WHITE

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
        self.btn_left = None
        self.btn_right = None
        self.state = None
        self.dir = None
        self.setup()
        self.score = 0
        self.name = name
        right_texture = arcade.load_texture(img)
        left_texture = arcade.load_texture(img, mirrored=True)
        self.textures.append(right_texture)
        self.textures.append(left_texture)
        self.set_texture(Player.RIGHT)

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
        self.btn_left = True
        self.dir = Player.LEFT
        self.set_texture(Player.LEFT)

    def on_left_release(self):
        self.btn_left = False
        if self.btn_right:
            self.dir = Player.RIGHT
            self.set_texture(Player.RIGHT)
        else:
            self.dir = Player.NO_DIRECTION

    def on_right(self):
        self.btn_right = True
        self.dir = Player.RIGHT
        self.set_texture(Player.RIGHT)

    def on_right_release(self):
        self.btn_right = False
        if self.btn_left:
            self.dir = Player.LEFT
            self.set_texture(Player.LEFT)
        else:
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
        hit_wall_list = arcade.geometry.check_for_collision_with_list(self, walls)
        if len(hit_wall_list) > 0:
            for wall in hit_wall_list:
                hit = collision.intersect_AABB(self, wall)
                if hit is None:
                    continue
                if hit.normal[0] > 0 or hit.normal[0] < 0:  # from right or left
                    self.center_x += hit.delta[0]
                    self.change_x = 0
                if hit.normal[1] > 0:  # from top
                    self.bottom = wall.top - 1
                    self.change_y = 0
                    self.set_landed()
                if hit.normal[1] < 0:  # from bottom
                    self.center_y += hit.delta[1]
                    self.change_y = 0
        else:
            self.set_flying()

    def setup(self):
        self.btn_left = False
        self.btn_right = False
        self.state = Player.FLYING
        self.dir = Player.NO_DIRECTION
        self.change_x = 0.0
        self.change_y = 0.0

    def respawn(self):
        self.setup()
        self.center_x = random.randint(200, 1000)
        self.center_y = 75
        self.change_x = 0.0
        self.change_y = 0.0


class RegistrationEntry:
    """Represents a player during the registration phase"""
    def __init__(self):
        self.name = None
        self.names = itertools.cycle(sorted(CFG.Registration.names.keys()))
        self.make_name()
        self.flap = None
        self.left = None
        self.right = None

    def is_event_used(self, evt):
        used_ids = (
            self.flap.get_id() if self.flap else None,
            self.left.get_id() if self.left else None,
            self.right.get_id() if self.right else None,
        )
        return evt.get_id() in used_ids

    def make_name(self):
        self.name = next(self.names)

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


class Registration:
    """Hacky class to store state related to the Registration state. Prob should be a "state" class or something."""
    def __init__(self, game, win_height):
        self.msg = '...'
        self.last_input = None
        self.done = False
        self.entries = []
        self.win_height = win_height
        self.game = game
        self.script = self.registration_script()

    @staticmethod
    def _get_event_skip_escape_key(evt):
        """Used by scriptutil.wait_until_non_none() to block until a non-ESC key has been pressed"""
        if evt is not None:
            if evt.get_id() == event.KeyPress(arcade.key.ESCAPE).get_id():
                return None
        return evt

    def registration_script(self):
        """Generator-script that creates players and registers their input"""
        self.load_players()
        player_num = len(self.entries)

        while True:
            player_num += 1
            self.msg = 'Press your desired FLAP to register Player {}...\nESC to start game. F5 to clear player list.'.format(player_num)
            evt = yield from scriptutl.wait_until_non_none(lambda: self.last_input)

            # clear player list
            if evt.get_id() == event.KeyPress(arcade.key.F5).get_id():
                self.entries = []
                self.last_input = None
                player_num = 0
                continue

            # end registration
            if evt.get_id() == event.KeyPress(arcade.key.ESCAPE).get_id():
                break

            entry = RegistrationEntry()
            self.entries.append(entry)
            entry.flap = evt
            self.last_input = None
            self.msg = 'Press LEFT for Player {}'.format(player_num)
            evt = yield from scriptutl.wait_until_non_none(lambda: self._get_event_skip_escape_key(self.last_input))

            if isinstance(evt, event.JoyHatMotion):
                entry.left = evt
                entry.right = evt
                self.last_input = None
                continue

            entry.left = evt
            self.last_input = None
            self.msg = 'Press RIGHT for Player {}'.format(player_num)
            evt = yield from scriptutl.wait_until_non_none(lambda: self._get_event_skip_escape_key(self.last_input))

            entry.right = evt
            self.last_input = None

        self.finalize()
        self.done = True

    def on_draw(self):
        arcade.draw_text('Player Registration', 25, self.win_height - 75, HEADER_COLOR, 40)
        arcade.draw_text(self.msg, 25, self.win_height - 175, HEADER_COLOR, 30)
        summary = self.get_summary()
        arcade.draw_text(summary, 25, self.win_height - 200, BODY_COLOR, 25, anchor_y='top')
        arcade.draw_text('After registering, press FLAP to cycle through names.', 100, 40, HEADER_COLOR, 20)

    def on_event(self, evt):
        matched = False
        for entry in self.entries:
            if entry.is_event_used(evt):
                matched = True
                if evt.get_id() == entry.flap.get_id():
                    entry.make_name()
        if not matched:
            self.last_input = evt

    def get_summary(self):
        summaries = [e.get_summary() for e in self.entries]
        if len(summaries) == 0:
            return '<no players registered>'
        return '\n'.join(summaries)

    def finalize(self):
        self.save_players()
        for entry in self.entries:
            entry.finalize(self.game)

    def save_players(self):
        def get_persistent_id(obj):
            """Pickle pyglet's Joystick object by simply saving index into list"""
            if isinstance(obj, pyglet.input.base.Joystick):
                joy_idx = self.game.joysticks.index(obj)
                print('  Pickling joystick idx #{} {}'.format(joy_idx, obj.device))
                return joy_idx
            return None

        with open(CFG.Player.filename, 'wb') as out_file:
            print('Saving player list to {}'.format(CFG.Player.filename))
            pickler = pickle.Pickler(out_file)
            pickler.persistent_id = get_persistent_id
            pickler.dump(self.entries)

    def load_players(self):
        def load_from_persistent_id(persist_id):
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
                unpickler.persistent_load = load_from_persistent_id
                self.entries = unpickler.load()
                print('Loaded {} players'.format(len(self.entries)))
        except Exception as exc:
            print('WARNING: Problem loading previous player list from file:"{}" so starting with an empty player list. Exception: {}'.format(CFG.Player.filename, type(exc)))
            traceback.print_exc()


class Game(arcade.Window):
    # game states
    WELCOME = 'welcome'
    REGISTRATION = 'registration'
    PLAY = 'gameplay'
    SCOREBOARD = 'scoreboard'

    def on_resize(self, width: float, height: float):
        # prevent arcade.Window.on_resize from changing the viewport on startup
        pass

    def __init__(self, width, height, title, fullscreen):
        super().__init__(width, height, title, fullscreen)
        if self.fullscreen:
            self.set_viewport(0, width, 0, height)  # scale viewport to full screen (doesn't preserve aspect ratio)
        else:
            self.set_location(250, 35)

        self.script = self.game_script()
        self.reg = Registration(self, height)
        next(self.script)
        self.window_width = width
        self.window_height = height
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        self.player_list = arcade.SpriteList()
        self.gameplay_input = {
            event.KeyPress(arcade.key.ESCAPE).get_id(): self.close,
        }

        # gamepad setup
        self.joysticks = arcade.joysticks.get_game_controllers()
        if self.joysticks:
            for joy in self.joysticks:
                print('Found joystick: ', joy.device)
                joy.open()
                joy.on_joybutton_press = self.on_joybutton_press
                joy.on_joybutton_release = self.on_joybutton_release
                joy.on_joyhat_motion = self.on_joyhat

    def setup(self, map_name):
        # map
        print('Loading map: {}'.format(map_name))
        self.map = arcade.read_tiled_map(map_name)
        self.walls = arcade.generate_sprites(self.map, 'walls', 1.0)
        for s in self.walls.sprite_list:
            s.center_x += 32

        # players
        x = 100
        for p in self.player_list:
            p.setup()
            p.center_x = x
            p.center_y = 120
            p.change_x = 0.0
            p.change_y = 0.0
            p.score = 0
            x += 100

    def game_script(self):
        """Generator-based game "script" that drives the game through its main states"""
        self.state = Game.WELCOME
        yield from scriptutl.sleep(1.0)

        self.state = Game.REGISTRATION
        yield from scriptutl.wait_until(lambda: self.reg.done)

        for i in range(CFG.Game.rounds):
            self.setup(CFG.Game.maps[i % len(CFG.Game.maps)])
            self.state = Game.PLAY
            yield from scriptutl.wait_until(self.is_game_over)

            self.state = Game.SCOREBOARD
            # blackout input briefly so thtat any final, furious button mashing doesn't unintentionally skip the scoreboard
            self.scoreboard_sub_state = 'blackout'
            yield from scriptutl.sleep(3.0)
            self.scoreboard_sub_state = 'ready'
            yield from scriptutl.wait_until(lambda: self.scoreboard_sub_state == 'done')

        print('Game over')

    def on_draw(self):
        arcade.start_render()
        if self.state == Game.WELCOME:
            arcade.draw_text('Flapping Game', 100, 400, arcade.color.GRAY, 100)
            arcade.draw_text('Flapping Game', 105, 405, arcade.color.GREEN, 100)
        elif self.state == Game.REGISTRATION:
            self.reg.on_draw()
        elif self.state == Game.PLAY:
            self.walls.draw()
            self.player_list.draw()
            self.draw_scores()
        elif self.state == Game.SCOREBOARD:
            sorted_player_list = sorted(self.player_list, key=lambda p: p.score, reverse=True)
            arcade.draw_text('Scoreboard', 100, self.window_height - 100, HEADER_COLOR, 60)
            lines = ['{} = {}'.format(p.name, p.score) for p in sorted_player_list]
            arcade.draw_text('\n'.join(lines), 100, 200, BODY_COLOR, 38)
            if self.scoreboard_sub_state == 'ready':
                arcade.draw_text('Press any input to continue...', 100, 50, HEADER_COLOR, 24)

    def on_key_press(self, key, modifiers):
        evt = event.KeyPress(key, modifiers)
        if self.state == Game.REGISTRATION:
            self.reg.on_event(evt)
        elif self.state == Game.PLAY:
            if evt.get_id() in self.gameplay_input:
                self.gameplay_input[evt.get_id()]()
        elif self.state == Game.SCOREBOARD and self.scoreboard_sub_state == 'ready':
            if evt.get_id() in self.gameplay_input:
                self.scoreboard_sub_state = 'done'

    def on_key_release(self, key, modifiers):
        evt = event.KeyRelease(key, modifiers)
        if self.state == Game.PLAY:
            if evt.get_id() in self.gameplay_input:
                self.gameplay_input[evt.get_id()]()

    def on_joybutton_press(self, joy, button):
        evt = event.JoyButtonPress(joy, button)
        if self.state == Game.REGISTRATION:
            self.reg.on_event(evt)
        elif self.state == Game.PLAY:
            if evt.get_id() in self.gameplay_input:
                self.gameplay_input[evt.get_id()]()
        elif self.state == Game.SCOREBOARD and self.scoreboard_sub_state == 'ready':
            if evt.get_id() in self.gameplay_input:
                self.scoreboard_sub_state = 'done'

    def on_joybutton_release(self, joy, button):
        evt = event.JoyButtonRelease(joy, button)
        if self.state == Game.PLAY:
            if evt.get_id() in self.gameplay_input:
                self.gameplay_input[evt.get_id()]()

    def on_joyhat(self, joy, hatx, haty):
        # Many gamepads must be in "analog" mode for the "hat" to report values
        evt = event.JoyHatMotion(joy, hatx, haty)
        if self.state == Game.REGISTRATION:
            if hatx != 0:
                self.reg.on_event(evt)
        elif self.state == Game.PLAY:
            if evt.get_id() in self.gameplay_input:
                self.gameplay_input[evt.get_id()](hatx, haty)

    def update(self, delta_time):
        if self.state == Game.WELCOME:
            pass
        elif self.state == Game.REGISTRATION:
            try:
                next(self.reg.script)
            except StopIteration:
                pass
        elif self.state == Game.PLAY:
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
    app = Game(1280, 720, 'Flapping', CFG.Window.fullscreen)
    arcade.run()


if __name__ == "__main__":
    main()
