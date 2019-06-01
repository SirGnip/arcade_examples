import random
import scriptutl
import arcade


class Player(arcade.Sprite):
    MOVEMENT_SPEED = 0.15  # pixels per frame
    FLAP_HORIZ_IMPULSE = 1.3
    MAX_HORIZ_SPEED = 5.0
    JUMP_SPEED = 3
    # state
    LANDED = 0
    FLYING = 1
    # direction
    NO_DIRECTION = 0
    LEFT = 1
    RIGHT = 2

    def __init__(self, img, name):
        super().__init__(img)
        self.state = Player.FLYING
        self.dir = Player.NO_DIRECTION
        self.score = 0
        self.name = name

    def on_up(self):
        if self.state == Player.LANDED:
            self.center_y += 1
        elif self.state == Player.FLYING:
            if self.dir == Player.LEFT:
                self.change_x -= Player.FLAP_HORIZ_IMPULSE
            elif self.dir == Player.RIGHT:
                self.change_x += Player.FLAP_HORIZ_IMPULSE
        self.change_y += self.JUMP_SPEED

    def on_left(self):
        self.dir = Player.LEFT

    def on_left_release(self):
        self.dir = Player.NO_DIRECTION

    def on_right(self):
        self.dir = Player.RIGHT

    def on_right_release(self):
        self.dir = Player.NO_DIRECTION

    def on_joyhat(self, hatx, haty):
        if hatx < 0:
            self.dir = Player.LEFT
        elif hatx > 0:
            self.dir = Player.RIGHT
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
                self.change_x -= Player.MOVEMENT_SPEED
            elif self.dir == Player.RIGHT:
                self.change_x += Player.MOVEMENT_SPEED
        self.change_x = min(self.change_x, Player.MAX_HORIZ_SPEED)
        self.change_x = max(self.change_x, -Player.MAX_HORIZ_SPEED)

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


class Registration:
    """Hacky class to store state related to the Registration state. Prob should be a "state" class or something."""
    def __init__(self):
        self.msg = '...'
        self.last_input = None
        self.done = False
        self.summary = ''

    def on_draw(self):
        arcade.draw_text('Player Registration', 100, 600, arcade.color.WHITE, 40)
        arcade.draw_text(self.msg, 100, 500, arcade.color.GRAY, 30)
        if len(self.summary) > 0:
            arcade.draw_text(self.summary, 100, 350, arcade.color.GRAY, 25, anchor_y='top')

    def on_key(self, key):
        self.last_input = key

    def on_joybutton(self, joy, button):
        self.last_input = (id(joy), button)

    def get_input_label(self):
        if self.last_input is None:
            return ''
        elif isinstance(self.last_input, int):
            return chr(self.last_input)  # keyboard input
        else:
            return '{}/{}'.format(self.last_input[0], self.last_input[1]) # joystick input


class MyGame(arcade.Window):
    # Constants
    GOAL_SCORE = 3
    # game states
    WELCOME = 'welcome'
    REGISTRATION = 'registration'
    PLAY = 'gameplay'
    SCOREBOARD = 'scoreboard'

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.script = self.game_script()
        self.reg = Registration()
        self.reg_script = self.registration_script()
        next(self.script)
        self.window_width = width
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.map = arcade.read_tiled_map('map.tmx')
        self.walls = arcade.generate_sprites(self.map, 'walls', 1.0)
        for s in self.walls.sprite_list:
            s.center_x += 32

        self.player_list = arcade.SpriteList()
        self.controller_press = {
            arcade.key.ESCAPE: self.close,
        }
        self.controller_release = {
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

    def setup(self):
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

        for i in range(3):
            self.setup()
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
        CONFIRM_DELAY = 0.7
        names = ('TheOne', 'Two-fer', 'Threesies', 'Four', 'Fiver', 'PickUpSix', 'Lucky7')
        player_num = 0
        while True:
            player_num += 1
            self.reg.msg = 'Press FLAP to register Player {}... ESC to start game.'.format(player_num)
            key = yield from scriptutl.wait_until_non_none(lambda: self.reg.last_input)

            if key == arcade.key.ESCAPE:
                break
            player = Player('img/duck.png', names[player_num - 1])
            self.player_list.append(player)
            self.controller_press[key] = player.on_up
            name = names[player_num - 1]
            input_label = self.reg.get_input_label() # HACKY!
            self.reg.msg = 'Created player {} with FLAP: {}'.format(name, input_label)
            self.reg.summary += 'Player:{} FLAP:{} '.format(name, input_label)
            self.reg.last_input = None
            yield from scriptutl.sleep(CONFIRM_DELAY)

            self.reg.msg = 'Press LEFT for Player {}'.format(player_num)
            key = yield from scriptutl.wait_until_non_none(lambda: self.reg.last_input)

            self.controller_press[key] = player.on_left
            self.controller_release[key] = player.on_left_release
            input_label = self.reg.get_input_label()  # HACKY!
            self.reg.msg = 'Got LEFT: {}'.format(input_label)
            self.reg.summary += 'LEFT:{} '.format(input_label)
            self.reg.last_input = None
            yield from scriptutl.sleep(CONFIRM_DELAY)

            self.reg.msg = 'Press RIGHT for Player {}'.format(player_num)
            key = yield from scriptutl.wait_until_non_none(lambda: self.reg.last_input)

            self.controller_press[key] = player.on_right
            self.controller_release[key] = player.on_right_release
            input_label = self.reg.get_input_label()  # HACKY!
            self.reg.msg = 'Got RIGHT: {}'.format(input_label)
            self.reg.summary += 'RIGHT:{}\n'.format(input_label)
            self.reg.last_input = None
            yield from scriptutl.sleep(CONFIRM_DELAY)

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
        elif self.state == MyGame.SCOREBOARD:
            arcade.draw_text('Scoreboard', 100, 500, arcade.color.GRAY, 60)
            lines = ['{} = {}'.format(p.name, p.score) for p in self.player_list]
            arcade.draw_text('\n'.join(lines), 100, 300, arcade.color.WHITE, 50)

    def on_key_press(self, key, modifiers):
        if self.state == MyGame.REGISTRATION:
            self.reg.on_key(key)
        elif self.state == MyGame.PLAY:
            if key in self.controller_press:
                self.controller_press[key]()

    def on_key_release(self, key, modifiers):
        if self.state == MyGame.PLAY:
            if key in self.controller_release:
                self.controller_release[key]()

    def on_joybutton_press(self, joy, button):
        key = (id(joy), button)
        if self.state == MyGame.REGISTRATION:
            self.reg.on_joybutton(joy, button)
        elif self.state == MyGame.PLAY:
            if key in self.controller_press:
                self.controller_press[key]()

    def on_joybutton_release(self, joy, button):
        key = (id(joy), button)
        if key in self.controller_release:
            self.controller_release[key]()

    def on_joyhat(self, joy, hatx, haty):
        """Many gamepads must be in "analog" mode for the "hat" to report values"""
        key = id(joy)
        if key in self.controller_press:
            self.controller_press[key](hatx, haty)

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
                    if p1.center_y > p2.center_y:
                        p1.score += 1
                        p2.respawn()
                    elif p2.center_y > p1.center_y:
                        p2.score += 1
                        p1.respawn()
                    self.print_scores()

    def print_scores(self):
        for p in self.player_list:
            print('{}: {}'.format(p.name, p.score))

    def is_game_over(self):
        scores = [p.score for p in self.player_list]
        return max(scores) >= MyGame.GOAL_SCORE


def main():
    app = MyGame(1280, 720, 'Flapping')
    app.set_location(250, 35)
    arcade.run()


if __name__ == "__main__":
    main()
