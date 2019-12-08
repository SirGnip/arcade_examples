class Registration:
    names = {
        'Wayne': 'bat.png',
        'Quad':  'box.png',
        'Quackers': 'duck.png',
        'Glorb': 'spaceship.png',
        'Clark': 'super.png',
        'Wright': 'biplane.png',
        'Luna': 'moon.png',
        'Crystal': 'snowflake.png',
        'Plumb': 'plunger.png',
        'Scooter': 'doghouse.png',
        'Melon': 'watermellon.png',
        'Centauri': 'star.png'
    }


class Window:
    fullscreen = False


class Game:
    debug = False
    goal_score = 3
    rounds = 8
    maps = ('map1.tmx', 'map2.tmx', 'map3.tmx', 'map4.tmx', 'map5.tmx')


class Player:
    movement_speed = 0.15  # pixels per frame
    flap_horiz_impulse = 1.5
    max_horiz_speed = 7.0
    jump_speed = 3
    filename = 'flapping.last_players'
