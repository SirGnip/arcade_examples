# arcade_examples
Example games created with the [Python Arcade library](https://github.com/pvcraven/arcade), a 2D game engine for Python.

# Code included in this repo

- "[flapping](src/flapping)": A local multiplyer game that supports 2-10 players. See details below.
- "[dual_stick_shooter](src/dual_stick_shooter.py)": tech demo for single player dual-analog stick shooter
- "[gnp.arcadelib](src/gnp/arcadelib)": Basic utilities for use with the Arcade library. 
- Minimal examples of arcade library:
    - "[minimal_using_functions](src/minimal_using_functions.py)": demonstrate a minimal `arcade` app, using `arcade`'s functional style interface.
    - "[minimal_using_class](src/minimal_using_class.py)": demonstrate a minimal `arcade` game, using `arcade`'s class-based interface.
    - "[minimal_one_of_everything](src/minimal_one_of_everything.py)": demonstrate a minimal `arcade` game, using several key features of `arcade`. 

# "Flapping" Game

This is a work in progress. Gameplay is simple, but playable. This is a local multiplayer
game that supports 2-10 players on one computer. Players flap their wings to make sure they have a higher 
position when they collide with opponents. Similar to the classic game "Joust." 

Features

- Local multiplayer: 2-10 local players on one computer
- Input:
    - One keyboard can support Multiple players 
    - Game can use almost any USB gamepad/joystick

### Installation

    pip install git+https://github.com/SirGnip/arcade_examples.git
    python -m flapping.flap_app

### Playing with a large number of players

Screen:

- With lots of players, it helps to have a larger screen. Run the game from a laptop and use an HDMI cable to plug it into a large-screen TV!

Input:

- crowd people around one keyboard (game supports multiple people using one keyboard)
    - When more than 2 or 3 players are sharing the keyboard for their input (which is completely possible and a lot of fun!), you need to be aware of the "[multi-key rollover](https://en.wikipedia.org/wiki/Rollover_(key)#Multi-key_rollover)" limitations of your specific keyboard.
- plug a second keyboard into your computer
- plug multiple USB gamepads into a USB hub

![Hits](https://hitcounter.pythonanywhere.com/count/tag.svg?url=https%3A%2F%2Fgithub.com%2FSirGnip%2Farcade_examples)
