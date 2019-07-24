"""
Minimal app that makes minimal use of several key features of arcade
"""
import arcade

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.YELLOW)
        self.x = 0
        self.y = 0
        self.xvel = 0
        self.yvel = 0

    def setup(self):
        self.x = 100
        self.y = 100
        self.xvel = 0
        self.yvel = 0

    def update(self, delta_time):
        self.x += self.xvel
        self.y += self.yvel

    def on_key_press(self, key, key_modifiers):
        SPEED = 1
        if key == arcade.key.S:
            self.setup()
        elif key == arcade.key.UP:
            self.yvel += SPEED
        elif key == arcade.key.DOWN:
            self.yvel -= SPEED
        elif key == arcade.key.RIGHT:
            self.xvel += SPEED
        elif key == arcade.key.LEFT:
            self.xvel -= SPEED
        elif key == arcade.key.SPACE:
            self.xvel = 0
            self.yvel = 0

    def on_mouse_press(self, x, y, button, modifiers):
        self.x = x
        self.y = y

    def on_draw(self):
        arcade.start_render() # clear screen and start render process
        arcade.draw_circle_filled(self.x, self.y, 25, arcade.color.PURPLE)

if __name__ == "__main__":
    game = MyGame(600, 400, 'One of everything')
    game.setup()
    arcade.run()
