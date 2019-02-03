"""
Dual-stick shooter example

Uses joystick if one is present. Otherwise it fails back to using keyboard controls.

Improvements:
- Decay movement after input is released
- reap bullets that go off screen
- simple enemy "follow" AI
- keep player on screen
- basic particle system
"""
import arcade
import random
import math

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Dual-stick shooter example"
MOVEMENT_SPEED = 4
BULLET_SPEED = 10
BULLET_COOLDOWN_TICKS = 10


def _get_joy_axis(x, y):
    """given joystick axis values, return (x, y, angle)"""
    deadzone = 0.2
    if x > deadzone or x < -deadzone or y > deadzone or y < -deadzone:
        y = -y
        rad = math.atan2(y, x)
        angle = math.degrees(rad)
        return x, y, angle
    return None, None, None


class Ship(arcade.sprite.Sprite):
    def __init__(self, filename):
        super().__init__(filename=filename, scale=0.5, center_x=200, center_y=200)
        self.shoot_up_pressed = False
        self.shoot_down_pressed = False
        self.shoot_left_pressed = False
        self.shoot_right_pressed = False


class Enemy(arcade.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(filename='../img/round.png', scale=1.0, center_x=x, center_y=y)


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.DARK_MIDNIGHT_BLUE)
        self.game_over = False
        self.score = 0
        self.bullet_cooldown = 0
        self.ship = Ship("../img/ship.png")
        self.ship.center_x = 200
        self.ship.center_y = 200
        self.sprites = arcade.SpriteList()
        self.sprites.append(self.ship)
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.enemy_list.append(Enemy(300, 300))
        self.joy = None
        joys = arcade.get_joysticks()
        if joys:
            self.joy = joys[0]
            self.joy.open()
            print("Using joystick controls: {}".format(self.joy.device))
        if not self.joy:
            print("No joystick present, using keyboard controls")
        arcade.window_commands.schedule(self.spawn_enemy, 2.0)

    def spawn_enemy(self, elapsed):
        if self.game_over:
            return
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        self.enemy_list.append(Enemy(x, y))

    def setup(self):
        pass

    def update(self, delta_time):
        if self.game_over:
            return

        self.bullet_cooldown += 1

        if self.joy:
            # handle movement
            move_x, move_y, move_angle = _get_joy_axis(self.joy.x, self.joy.y)
            if move_angle:
                self.ship.change_x = move_x * MOVEMENT_SPEED
                self.ship.change_y = move_y * MOVEMENT_SPEED
                self.ship.angle = move_angle
            else:
                self.ship.change_x = 0
                self.ship.change_y = 0
            # handle shooting
            shoot_x, shoot_y, shoot_angle = _get_joy_axis(self.joy.z, self.joy.rz)
            if shoot_x:
                self.spawn_bullet(shoot_angle)
        else:
            # handle shooting
            if self.ship.shoot_right_pressed and self.ship.shoot_up_pressed:
                self.spawn_bullet(0+45)
            elif self.ship.shoot_up_pressed and self.ship.shoot_left_pressed:
                self.spawn_bullet(90+45)
            elif self.ship.shoot_left_pressed and self.ship.shoot_down_pressed:
                self.spawn_bullet(180+45)
            elif self.ship.shoot_down_pressed and self.ship.shoot_right_pressed:
                self.spawn_bullet(270+45)
            elif self.ship.shoot_right_pressed:
                self.spawn_bullet(0)
            elif self.ship.shoot_up_pressed:
                self.spawn_bullet(90)
            elif self.ship.shoot_left_pressed:
                self.spawn_bullet(180)
            elif self.ship.shoot_down_pressed:
                self.spawn_bullet(270)

        self.enemy_list.update()
        self.sprites.update()
        self.bullet_list.update()
        ship_death_hit_list = arcade.check_for_collision_with_list(self.ship, self.enemy_list)
        if len(ship_death_hit_list) > 0:
            self.game_over = True
        for bullet in self.bullet_list:
            bullet_killed = False
            enemy_shot_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            # Loop through each colliding sprite, remove it, and add to the score.
            for enemy in enemy_shot_list:
                enemy.kill()
                bullet.kill()
                bullet_killed = True
                self.score += 1
            if bullet_killed:
                continue

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.ship.change_y = MOVEMENT_SPEED
            self.ship.angle = 90
        elif key == arcade.key.S:
            self.ship.change_y = -MOVEMENT_SPEED
            self.ship.angle = 270
        elif key == arcade.key.A:
            self.ship.change_x = -MOVEMENT_SPEED
            self.ship.angle = 180
        elif key == arcade.key.D:
            self.ship.change_x = MOVEMENT_SPEED
            self.ship.angle = 0
        elif key == arcade.key.RIGHT:
            self.ship.shoot_right_pressed = True
        elif key == arcade.key.UP:
            self.ship.shoot_up_pressed = True
        elif key == arcade.key.LEFT:
            self.ship.shoot_left_pressed = True
        elif key == arcade.key.DOWN:
            self.ship.shoot_down_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self.ship.change_y = 0
        elif key == arcade.key.S:
            self.ship.change_y = 0
        elif key == arcade.key.A:
            self.ship.change_x = 0
        elif key == arcade.key.D:
            self.ship.change_x = 0
        elif key == arcade.key.RIGHT:
            self.ship.shoot_right_pressed = False
        elif key == arcade.key.UP:
            self.ship.shoot_up_pressed = False
        elif key == arcade.key.LEFT:
            self.ship.shoot_left_pressed = False
        elif key == arcade.key.DOWN:
            self.ship.shoot_down_pressed = False

    def spawn_bullet(self, angle_in_deg):
        if self.bullet_cooldown < BULLET_COOLDOWN_TICKS:
            return
        self.bullet_cooldown = 0

        bullet = arcade.Sprite("../img/laser.png", 0.75)

        # Position the bullet at the player's current location
        start_x = self.ship.center_x
        start_y = self.ship.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        bullet.angle = angle_in_deg
        angle_in_rad = math.radians(angle_in_deg)
        bullet.change_x = math.cos(angle_in_rad) * BULLET_SPEED
        bullet.change_y = math.sin(angle_in_rad) * BULLET_SPEED

        # Add the bullet to the appropriate lists
        self.bullet_list.append(bullet)

    def on_draw(self):
        arcade.start_render() # clear screen and start render process
        # Put the text on the screen.
        output = f"GAME OVER Score: {self.score}" if self.game_over else f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)
        self.bullet_list.draw()
        self.enemy_list.draw()
        self.sprites.draw()


if __name__ == "__main__":
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()
