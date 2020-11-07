import arcade
from dataclasses import dataclass
from typing import Optional


@dataclass
class PlayerAvatar:
    """Data used to draw a player's avatar"""
    image: str
    color: Optional[arcade.arcade_types.Color]  # None == no color replacing


class Registration:
    avatars = {
        'Pepto': PlayerAvatar('player_blob.png', (255, 91, 173)),
        'Ruby': PlayerAvatar('player_blob.png', (228, 0, 19)),
        'Orange': PlayerAvatar('player_blob.png', (255, 127, 0)),
        'Sunny': PlayerAvatar('player_blob.png', (252, 246, 81)),
        'Greedo': PlayerAvatar('player_blob.png', (0, 188, 56)),
        'Cyan': PlayerAvatar('player_blob.png', (0, 255, 255)),
        'Azul': PlayerAvatar('player_blob.png', (0, 157, 248)),
        'Navy': PlayerAvatar('player_blob.png', (0, 0, 210)),
        'Plum': PlayerAvatar('player_blob.png', (148, 0, 211)),
        'Indigo': PlayerAvatar('player_blob.png', (75, 0, 130)),
        'Choco': PlayerAvatar('player_blob.png', (139, 69, 19)),
        'Shadow': PlayerAvatar('player_blob.png', (80, 80, 80)),
        'Grasion': PlayerAvatar('player_blob.png', (170, 170, 170)),
        'Snowy': PlayerAvatar('player_blob.png', (255, 255, 255)),
        # 'Quackers': PlayerData('player/duck.png', None),
    }


class Window:
    fullscreen = False


class Game:
    debug = False
    goal_score = 5
    maps = ('map1.tmx', 'map2.tmx', 'map3.tmx', 'map4.tmx', 'map5.tmx')
    rounds = len(maps)


class Player:
    movement_speed = 0.15  # pixels per frame
    flap_horiz_impulse = 1.5
    max_horiz_speed = 5.0
    max_vert_speed = 7.0
    jump_speed = 3
    filename = 'flapping.last_players'
    respawn_delay = 1.0
    kill_score = 2
    death_score = -1


class UI:
    HEADER_COLOR = arcade.color.FOREST_GREEN
    BODY_COLOR = arcade.color.DARK_BROWN
