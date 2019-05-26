import arcade


class Player(arcade.Sprite):
    PLAYER_MOVEMENT_SPEED = 5  # pixels per frame

    def __init__(self, img):
        super().__init__(img)

    def on_up(self):
        self.change_y = self.PLAYER_MOVEMENT_SPEED

    def on_down(self):
        self.change_y = -self.PLAYER_MOVEMENT_SPEED

    def on_left(self):
        self.change_x = -self.PLAYER_MOVEMENT_SPEED

    def on_right(self):
        self.change_x = self.PLAYER_MOVEMENT_SPEED

    def on_key_x_release(self):
        self.change_x = 0

    def on_key_y_release(self):
        self.change_y = 0


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.map = arcade.read_tiled_map('map.tmx')
        self.wall_list = arcade.generate_sprites(self.map, 'walls', 1.0)
        for s in self.wall_list.sprite_list:
            s.center_x += 32

        self.player1 = Player("img/duck.png")
        self.player1.center_x = 64
        self.player1.center_y = 120
        self.player2 = Player("img/duck.png")
        self.player2.center_x = 200
        self.player2.center_y = 120

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player1)
        self.player_list.append(self.player2)

        self.physics_engine1 = arcade.PhysicsEngineSimple(self.player1, self.wall_list)
        self.physics_engine2 = arcade.PhysicsEngineSimple(self.player2, self.wall_list)

        self.controller_press = {
            arcade.key.UP:    self.player1.on_up,
            arcade.key.DOWN:  self.player1.on_down,
            arcade.key.LEFT:  self.player1.on_left,
            arcade.key.RIGHT: self.player1.on_right,
            arcade.key.W: self.player2.on_up,
            arcade.key.S: self.player2.on_down,
            arcade.key.A: self.player2.on_left,
            arcade.key.D: self.player2.on_right,
            arcade.key.ESCAPE: self.close,
        }
        self.controller_release = {
            arcade.key.UP:    self.player1.on_key_y_release,
            arcade.key.DOWN:  self.player1.on_key_y_release,
            arcade.key.LEFT:  self.player1.on_key_x_release,
            arcade.key.RIGHT: self.player1.on_key_x_release,
            arcade.key.W: self.player2.on_key_y_release,
            arcade.key.S: self.player2.on_key_y_release,
            arcade.key.A: self.player2.on_key_x_release,
            arcade.key.D: self.player2.on_key_x_release,
        }

    def setup(self):
        pass

    def on_draw(self):
        arcade.start_render()
        self.wall_list.draw()
        self.player_list.draw()

    def on_key_press(self, key, modifiers):
        if key in self.controller_press:
            self.controller_press[key]()

    def on_key_release(self, key, modifiers):
        if key in self.controller_release:
            self.controller_release[key]()

    def update(self, delta_time):
        self.physics_engine1.update()
        self.physics_engine2.update()


def main():
    app = MyGame(1280, 720, 'Flapping')
    app.setup()
    app.set_location(250, 35)
    arcade.run()


if __name__ == "__main__":
    main()
