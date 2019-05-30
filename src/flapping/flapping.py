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

    def __init__(self, img):
        super().__init__(img)
        self.state = Player.FLYING
        self.dir = Player.NO_DIRECTION

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


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.map = arcade.read_tiled_map('map.tmx')
        self.walls = arcade.generate_sprites(self.map, 'walls', 1.0)
        for s in self.walls.sprite_list:
            s.center_x += 32

        self.player1 = Player("img/duck.png")
        self.player1.center_x = 200
        self.player1.center_y = 120
        self.player2 = Player("img/duck.png")
        self.player2.center_x = 400
        self.player2.center_y = 120

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player1)
        self.player_list.append(self.player2)

        self.controller_press = {
            arcade.key.UP:    self.player1.on_up,
            arcade.key.LEFT:  self.player1.on_left,
            arcade.key.RIGHT: self.player1.on_right,
            arcade.key.W: self.player2.on_up,
            arcade.key.A: self.player2.on_left,
            arcade.key.D: self.player2.on_right,
            arcade.key.ESCAPE: self.close,
        }
        self.controller_release = {
            arcade.key.LEFT:  self.player1.on_left_release,
            arcade.key.RIGHT: self.player1.on_right_release,
            arcade.key.A: self.player2.on_left_release,
            arcade.key.D: self.player2.on_right_release,
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
            self.controller_press[(id(joy), 0)] = self.player2.on_up
            self.controller_press[(id(joy), 3)] = self.player2.on_left
            self.controller_press[(id(joy), 2)] = self.player2.on_right
            self.controller_release[(id(joy), 3)] = self.player2.on_left_release
            self.controller_release[(id(joy), 2)] = self.player2.on_right_release

    def on_draw(self):
        arcade.start_render()
        self.walls.draw()
        self.player_list.draw()

    def on_key_press(self, key, modifiers):
        if key in self.controller_press:
            self.controller_press[key]()

    def on_key_release(self, key, modifiers):
        if key in self.controller_release:
            self.controller_release[key]()

    def on_joybutton_press(self, joy, button):
        key = (id(joy), button)
        if key in self.controller_press:
            self.controller_press[key]()

    def on_joybutton_release(self, joy, button):
        key = (id(joy), button)
        if key in self.controller_release:
            self.controller_release[key]()

    def on_joyhat(self, joy, hatx, haty):
        """Many gamepads must be in "analog" mode for the "hat" to report values"""
        print('hat', hatx, haty)

    def update(self, delta_time):
        self.player_list.update()
        self.player1.collision_check(self.walls)
        self.player2.collision_check(self.walls)
        for p in self.player_list:
            p.change_y -= 0.2  # gravity


def main():
    app = MyGame(1280, 720, 'Flapping')
    app.set_location(250, 35)
    arcade.run()


if __name__ == "__main__":
    main()
