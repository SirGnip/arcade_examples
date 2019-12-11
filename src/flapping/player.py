import random

import arcade

from flapping import collision
from flapping import flapping_cfg as CFG


class Player(arcade.Sprite):
    # state
    LANDED = 0
    FLYING = 1
    # direction
    RIGHT = 0
    LEFT = 1
    NO_DIRECTION = 2

    def __init__(self, img: str, name: str):
        super().__init__()
        self.btn_left = False
        self.btn_right = False
        self.state: int = Player.FLYING
        self.dir: int = Player.NO_DIRECTION
        self.setup()
        self.score = 0
        self.name = name
        self.is_alive = True
        right_texture = arcade.load_texture(img)
        left_texture = arcade.load_texture(img, mirrored=True)
        self.textures.append(right_texture)
        self.textures.append(left_texture)
        self.set_texture(Player.RIGHT)

    def on_up(self) -> None:
        if self.state == Player.LANDED:
            self.center_y += 1
        elif self.state == Player.FLYING:
            if self.dir == Player.LEFT:
                self.change_x -= CFG.Player.flap_horiz_impulse
            elif self.dir == Player.RIGHT:
                self.change_x += CFG.Player.flap_horiz_impulse
        self.change_y += CFG.Player.jump_speed

    def on_left(self) -> None:
        self.btn_left = True
        self.dir = Player.LEFT
        self.set_texture(Player.LEFT)

    def on_left_release(self) -> None:
        self.btn_left = False
        if self.btn_right:
            self.dir = Player.RIGHT
            self.set_texture(Player.RIGHT)
        else:
            self.dir = Player.NO_DIRECTION

    def on_right(self) -> None:
        self.btn_right = True
        self.dir = Player.RIGHT
        self.set_texture(Player.RIGHT)

    def on_right_release(self) -> None:
        self.btn_right = False
        if self.btn_left:
            self.dir = Player.LEFT
            self.set_texture(Player.LEFT)
        else:
            self.dir = Player.NO_DIRECTION

    def on_joyhat(self, hatx, haty) -> None:
        if hatx < 0:
            self.dir = Player.LEFT
            self.set_texture(Player.LEFT)
        elif hatx > 0:
            self.dir = Player.RIGHT
            self.set_texture(Player.RIGHT)
        else:
            self.dir = Player.NO_DIRECTION

    def set_landed(self) -> None:
        if self.state == Player.FLYING:
            self.state = Player.LANDED

    def set_flying(self):
        if self.state == Player.LANDED:
            self.state = Player.FLYING

    def update(self):
        super().update()
        if not self.is_alive:
            return

        if self.state == Player.LANDED:
            if self.dir == Player.LEFT:
                self.change_x -= CFG.Player.movement_speed
            elif self.dir == Player.RIGHT:
                self.change_x += CFG.Player.movement_speed
        self.change_x = min(self.change_x, CFG.Player.max_horiz_speed)
        self.change_x = max(self.change_x, -CFG.Player.max_horiz_speed)
        self.change_y = min(self.change_y, CFG.Player.max_vert_speed)
        self.change_y = max(self.change_y, -CFG.Player.max_vert_speed)

    def killers_collision_check(self, game: 'Game', killers):
        hit_list = arcade.geometry.check_for_collision_with_list(self, killers)
        if len(hit_list) > 0:
            self.score += CFG.Player.death_score
            game.do_die(self)

    def wall_collision_check(self, walls):
        hit_wall_list = arcade.geometry.check_for_collision_with_list(self, walls)
        if len(hit_wall_list) > 0:
            for wall in hit_wall_list:
                hit = collision.intersect_AABB(self, wall)
                if hit is None:
                    continue
                if hit.normal[0] > 0 or hit.normal[0] < 0:  # from right or left
                    self.center_x += hit.delta[0]
                    self.change_x = 0
                if hit.normal[1] > 0:  # hit top of wall
                    self.bottom = wall.top - 1
                    self.change_y = 0
                    self.set_landed()
                if hit.normal[1] < 0:  # hit bottom of wall
                    self.center_y += hit.delta[1]
                    self.change_y = -3.0
        else:
            self.set_flying()

    def setup(self):
        self.btn_left = False
        self.btn_right = False
        self.state = Player.FLYING
        self.dir = Player.NO_DIRECTION
        self.change_x = 0.0
        self.change_y = 0.0

    def kill(self):
        self.is_alive = False
        self.setup()
        # Move offscreen so Player isn't seen. Probably better to remove from SpriteList.
        self.center_x = -100
        self.center_y = -100

    def respawn(self):
        self.is_alive = True
        self.setup()
        self.center_x = random.randint(200, 1000)
        self.center_y = 75
        self.change_x = 0.0
        self.change_y = 0.0