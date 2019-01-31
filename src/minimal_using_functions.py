"""
Minimal app using functions
"""
import arcade

arcade.open_window(600, 400, "Minimal Game using functions")
arcade.set_background_color(arcade.color.YELLOW)
arcade.start_render() # clear screen and start render process
arcade.draw_circle_filled(300, 200, 25, arcade.color.PURPLE)
arcade.finish_render() # finish drawing and display result
arcade.run() # window stays open until user hits 'close' button
