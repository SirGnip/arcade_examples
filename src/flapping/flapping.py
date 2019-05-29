import arcade


class Player(arcade.Sprite):
    MOVEMENT_SPEED = 3  # pixels per frame
    JUMP_SPEED = 3

    def __init__(self, img):
        super().__init__(img)

    def on_up(self):
        self.change_y += self.JUMP_SPEED

    def on_down(self):
        self.change_y = -self.MOVEMENT_SPEED

    def on_left(self):
        self.change_x = -self.MOVEMENT_SPEED

    def on_right(self):
        self.change_x = self.MOVEMENT_SPEED


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.map = arcade.read_tiled_map('map.tmx')
        self.walls = arcade.generate_sprites(self.map, 'walls', 1.0)
        for s in self.walls.sprite_list:
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

    def setup(self):
        pass

    def on_draw(self):
        arcade.start_render()
        self.walls.draw()
        self.player_list.draw()

    def on_key_press(self, key, modifiers):
        if key in self.controller_press:
            self.controller_press[key]()

    def update(self, delta_time):
        self.player_list.update()
        for p in self.player_list:
            p.change_y -= 0.2 # gravity
        self.physics(self.player1, self.walls)
        self.physics(self.player2, self.walls)

    def physics(self, player, walls):
        hit_list = arcade.geometry.check_for_collision_with_list(player, walls)
        # If we hit a wall, move so the edges are at the same point
        if len(hit_list) > 0:
            for item in hit_list:
                if player.center_y > item.center_y:
                    player.bottom = item.top
                    player.change_y = 0
                elif player.center_y < item.center_y:
                    player.top = item.bottom
                    player.change_y = 0


def main():
    app = MyGame(1280, 720, 'Flapping')
    app.setup()
    app.set_location(250, 35)
    arcade.run()


if __name__ == "__main__":
    main()
