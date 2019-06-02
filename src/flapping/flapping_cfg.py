class Registration:
    names = {
        'Wayne': 'bat.png',
        'Quad':  'box.png',
        'Quackers': 'duck.png',
        'Glorb': 'spaceship.png',
        'Clark': 'super.png',
    }


class Window:
    fullscreen = False


class Game:
    goal_score = 3
    rounds = 3
    maps = ('map1.tmx', 'map2.tmx')


class Player:
    movement_speed = 0.15  # pixels per frame
    flap_horiz_impulse = 1.3
    max_horiz_speed = 5.0
    jump_speed = 3
