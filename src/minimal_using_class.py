"""
Minimal app using a class
"""
import arcade

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.YELLOW)

    def setup(self):
        pass  # initialize state

    def update(self, delta_time):
        pass  # called every frame

    def on_draw(self):
        arcade.start_render() # clear screen and start render process
        arcade.draw_circle_filled(300, 200, 25, arcade.color.PURPLE)

game = MyGame(600, 400, 'Minimal Game using Classes')
game.setup()
arcade.run() # window stays open until user hits 'close' button
