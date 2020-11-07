import random
from typing import TYPE_CHECKING

import PIL.Image
import arcade

from gnp.arcadelib import scriptutl
from flapping import flapping_cfg as CFG
if TYPE_CHECKING:
    from flapping.flap_app import Game


DUST_TEXTURE = arcade.make_soft_circle_texture(diameter=20, color=arcade.color.GRAY)


class ControllableEmitInterval(arcade.EmitController):
    """Emit particles on an interval and can manually stop emitting"""
    def __init__(self, emit_interval: float):
        self._emit_interval = emit_interval
        self._carryover_time = 0.0
        self.active = False

    def how_many(self, delta_time: float, current_particle_count: int) -> int:
        if not self.active:
            return 0
        self._carryover_time += delta_time
        emit_count = 0
        while self._carryover_time >= self._emit_interval:
            self._carryover_time -= self._emit_interval
            emit_count += 1
        return emit_count

    def start(self) -> None:
        self.active = True

    def stop(self) -> None:
        self.active = False

    def is_complete(self) -> bool:
        return False


class Player(arcade.Sprite):
    # state
    LANDED = 0
    FLYING = 1
    # direction
    RIGHT = 0
    LEFT = 1
    NO_DIRECTION = 2

    def __init__(self, img_path: str, name: str, clr: arcade.arcade_types.Color, game: "Game"):
        super().__init__()
        self.game = game
        # self.change_x: float  # should be coming from arcade package
        # self.change_y: float  # should be coming from arcade package
        self.btn_left = False
        self.btn_right = False
        self.state: int = Player.FLYING
        self.dir: int = Player.NO_DIRECTION
        self.skid_fx = self.make_dust_emitter()  # re-initialized in .setup()
        self.setup()
        self.score = 0
        self.name = name
        self.is_alive = True
        if img_path.endswith('player_blob.png') and clr is not None:
            # replace colors
            img = PIL.Image.open(img_path)
            width, height = img.size

            darker_clr = (
                    int(clr[0] * 0.7),
                    int(clr[1] * 0.7),
                    int(clr[2] * 0.7)
            )
            for i, px in enumerate(img.getdata()):
                if px == (65, 216, 0, 255):
                    img.putpixel((i % width, i // width), clr + (255,))
                elif px == (53, 178, 0, 255):
                    img.putpixel((i % width, i // width), darker_clr + (255,))

            # facing-right texture
            cache_id = f'{img_path}-{clr}-right'
            right_texture = arcade.Texture(cache_id, img)

            # facing-left texture
            img = img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
            cache_id = f'{img}-{clr}-left'
            left_texture = arcade.Texture(cache_id, img)
        else:
            # no color replacing
            right_texture = arcade.load_texture(img)
            left_texture = arcade.load_texture(img, mirrored=True)
        self.textures.append(right_texture)
        self.textures.append(left_texture)
        self.set_texture(Player.RIGHT)

    def setup(self) -> None:
        self.btn_left = False
        self.btn_right = False
        self.state = Player.FLYING
        self.dir = Player.NO_DIRECTION
        self.change_x = 0.0
        self.change_y = 0.0
        self.skid_fx = self.make_dust_emitter()
        self.game.fx_actors.append(self.skid_fx)

    def death_script(self) -> scriptutl.GenScript:
        """Generator "script" that runs to manage the timing of a player's death"""
        self.kill()
        yield from scriptutl.sleep(CFG.Player.respawn_delay)
        self.respawn()

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

    def on_joyhat(self, hatx: float, haty: float) -> None:
        if hatx < 0:
            self.dir = Player.LEFT
            self.set_texture(Player.LEFT)
        elif hatx > 0:
            self.dir = Player.RIGHT
            self.set_texture(Player.RIGHT)
        else:
            self.dir = Player.NO_DIRECTION

    def make_dust_emitter(self):
        particle_factory = arcade.FadeParticle
        return arcade.Emitter(
            center_xy=(self.center_x, self.center_y),
            emit_controller=ControllableEmitInterval(0.07),
            particle_factory=lambda emitter: particle_factory(
                filename_or_texture=random.choice([DUST_TEXTURE]),
                change_xy=arcade.rand_vec_spread_deg(90, 20, 0.3),
                lifetime=random.uniform(0.5, 0.7),
            )
        )

    def set_landed(self) -> None:
        if self.state == Player.FLYING:
            self.state = Player.LANDED

    def set_flying(self) -> None:
        if self.state == Player.LANDED:
            self.state = Player.FLYING
            self.skid_fx.rate_factory.stop()

    def update(self) -> None:
        super().update()
        if not self.is_alive:
            return

        if self.skid_fx:
            self.skid_fx.center_x = self.center_x
            self.skid_fx.center_y = self.bottom

        if self.state == Player.LANDED:
            movement_pressed = self.btn_right or self.btn_left
            if movement_pressed or abs(self.change_x) > 2.5:
                self.skid_fx.rate_factory.start()
            else:
                self.skid_fx.rate_factory.stop()
            if self.dir == Player.LEFT:
                self.change_x -= CFG.Player.movement_speed
            elif self.dir == Player.RIGHT:
                self.change_x += CFG.Player.movement_speed
        self.change_x = min(self.change_x, CFG.Player.max_horiz_speed)
        self.change_x = max(self.change_x, -CFG.Player.max_horiz_speed)
        self.change_y = min(self.change_y, CFG.Player.max_vert_speed)
        self.change_y = max(self.change_y, -CFG.Player.max_vert_speed)

    def kill(self) -> None:
        self.is_alive = False
        # Move offscreen so Player isn't seen. Probably better to remove from SpriteList.
        self.center_x = -100
        self.center_y = -100

    def respawn(self) -> None:
        self.is_alive = True
        self.setup()
        self.center_x = random.randint(200, 1000)
        self.center_y = 75
        self.change_x = 0.0
        self.change_y = 0.0
