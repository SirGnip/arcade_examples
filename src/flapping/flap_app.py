import os
import os.path

import arcade

from gnp.arcadelib.timers import Timers
from gnp.arcadelib.actor import ActorList
from gnp.arcadelib import scriptutl
from flapping import flapping_cfg as CFG
from flapping import event
from flapping import collision
from flapping.player import Player
from flapping.registration import Registration


CIRCLE_TEXTURE = arcade.make_soft_circle_texture(diameter=20, color=arcade.color.WHITE)


class Game(arcade.Window):
    # game states
    WELCOME = 'welcome'
    REGISTRATION = 'registration'
    PLAY = 'gameplay'
    SCOREBOARD = 'scoreboard'

    def on_resize(self, width: float, height: float):
        # prevent arcade.Window.on_resize from changing the viewport on startup
        pass

    def __init__(self, width, height, title, fullscreen):
        super().__init__(width, height, title, fullscreen)
        if self.fullscreen:
            self.set_viewport(0, width, 0, height)  # scale viewport to full screen (doesn't preserve aspect ratio)
        else:
            self.set_location(250, 35)

        self.script = self.game_script()
        self.reg = Registration(self, height)

        self.round_num = 0
        self.winners = []

        self.window_width = width
        self.window_height = height
        arcade.set_background_color((178, 198, 232))

        self.player_list = arcade.SpriteList()
        self.gameplay_input = {
            event.KeyPress(arcade.key.ESCAPE).get_id(): self.close,
        }

        self.fx_actors = ActorList()

        # gamepad setup
        self.joysticks = arcade.joysticks.get_game_controllers()
        if self.joysticks:
            for joy in self.joysticks:
                print('Found joystick: ', joy.device)
                joy.open()
                joy.on_joybutton_press = self.on_joybutton_press
                joy.on_joybutton_release = self.on_joybutton_release
                joy.on_joyhat_motion = self.on_joyhat

        self.timers: Timers = Timers()
        self.script_sched: scriptutl.Scheduler = scriptutl.Scheduler()
        next(self.script)  # step gameplay script when everything is initialized

    def setup(self, map_name):
        # map
        map_name = 'resources/map/' + map_name
        print('Loading map: {}'.format(map_name))
        self.map = arcade.tilemap.read_tmx(map_name)
        self.walls = arcade.tilemap.process_layer(self.map, 'walls', 1.0)
        self.killers = arcade.tilemap.process_layer(self.map, 'kill', 1.0)

        # players
        x = 100
        for p in self.player_list:
            p.setup()
            p.center_x = x
            p.center_y = 120
            p.change_x = 0.0
            p.change_y = 0.0
            p.score = 0
            x += 100

    def setup_new_round(self):
        for p in self.player_list:
            p.round_wins = 0

    def on_round_end(self):
        # find max score, reward
        max_score = max([p.score for p in self.player_list])
        for p in self.player_list:
            if p.score == max_score:
                p.round_wins += 1
                print(f'{p.name} wins round with {p.score} points. Has now won {p.round_wins} rounds.')

        max_round_wins = max([p.round_wins for p in self.player_list])
        self.winners = [p for p in self.player_list if p.round_wins == max_round_wins]

    def game_script(self):
        """Generator-based game "script" that drives the game through its main states"""
        if CFG.Game.debug:
            # quick start game w/ no welcome or registration
            self.reg.load_players()
            self.reg.finalize()
            CFG.Game.goal_score = 1
        else:
            self.state = Game.WELCOME
            yield from scriptutl.sleep(1.0)

            self.state = Game.REGISTRATION
            yield from scriptutl.wait_until(lambda: self.reg.done)

        while True:
            self.setup_new_round()
            for round_idx in range(CFG.Game.rounds):
                self.round_num = round_idx + 1
                self.setup(CFG.Game.maps[round_idx % len(CFG.Game.maps)])
                self.state = Game.PLAY
                yield from scriptutl.wait_until(self.is_game_over)
                self.on_round_end()
                yield from scriptutl.sleep(1.0)  # give player a chance to see the effects of their action (and let FX play)
                self.fx_actors.clear()

                self.state = Game.SCOREBOARD
                # blackout input briefly so that any final, furious button mashing doesn't unintentionally skip the scoreboard
                self.scoreboard_sub_state = 'blackout'
                yield from scriptutl.sleep(1.0)
                self.scoreboard_sub_state = 'ready'
                yield from scriptutl.wait_until(lambda: self.scoreboard_sub_state == 'done')

    def on_draw(self):
        arcade.start_render()
        if self.state == Game.WELCOME:
            arcade.draw_text('Flapping Game', 100, 400, arcade.color.GRAY, 100)
            arcade.draw_text('Flapping Game', 105, 405, arcade.color.GREEN, 100)
        elif self.state == Game.REGISTRATION:
            self.reg.on_draw()
        elif self.state == Game.PLAY:
            self.walls.draw()
            self.killers.draw()
            self.player_list.draw()
            self.draw_scores()
        elif self.state == Game.SCOREBOARD:
            sorted_player_list = sorted(self.player_list, key=lambda p: p.score, reverse=True)
            if self.round_num == CFG.Game.rounds:
                header = f'FINAL Scoreboard (round {self.round_num} of {CFG.Game.rounds})'
                footer = 'Winners: ' + ','.join([p.name for p in self.winners])
            else:
                header = f'Scoreboard (round {self.round_num} of {CFG.Game.rounds})'
                footer = None
            arcade.draw_text(header, 100, self.window_height - 100, CFG.UI.HEADER_COLOR, 60)
            if footer:
                arcade.draw_text(footer, 100, self.window_height - 150, CFG.UI.HEADER_COLOR, 36)

            lines = [f'{p.name}: {p.score} points, {p.round_wins} rounds' for p in sorted_player_list]
            arcade.draw_text('\n'.join(lines), 100, 200, CFG.UI.BODY_COLOR, 38)
            if self.scoreboard_sub_state == 'ready':
                arcade.draw_text('Press any input to continue...', 100, 50, CFG.UI.HEADER_COLOR, 24)
        self.fx_actors.draw()

    def on_key_press(self, key, modifiers):
        evt = event.KeyPress(key, modifiers)
        if self.state == Game.REGISTRATION:
            self.reg.on_event(evt)
        elif self.state == Game.PLAY:
            if evt.get_id() in self.gameplay_input:
                self.gameplay_input[evt.get_id()]()
        elif self.state == Game.SCOREBOARD and self.scoreboard_sub_state == 'ready':
            if evt.get_id() in self.gameplay_input:
                self.scoreboard_sub_state = 'done'

    def on_key_release(self, key, modifiers):
        evt = event.KeyRelease(key, modifiers)
        if self.state == Game.PLAY:
            if evt.get_id() in self.gameplay_input:
                self.gameplay_input[evt.get_id()]()

    def on_joybutton_press(self, joy, button):
        evt = event.JoyButtonPress(joy, button)
        if self.state == Game.REGISTRATION:
            self.reg.on_event(evt)
        elif self.state == Game.PLAY:
            if evt.get_id() in self.gameplay_input:
                self.gameplay_input[evt.get_id()]()
        elif self.state == Game.SCOREBOARD and self.scoreboard_sub_state == 'ready':
            if evt.get_id() in self.gameplay_input:
                self.scoreboard_sub_state = 'done'

    def on_joybutton_release(self, joy, button):
        evt = event.JoyButtonRelease(joy, button)
        if self.state == Game.PLAY:
            if evt.get_id() in self.gameplay_input:
                self.gameplay_input[evt.get_id()]()

    def on_joyhat(self, joy, hatx, haty):
        # Many gamepads must be in "analog" mode for the "hat" to report values
        evt = event.JoyHatMotion(joy, hatx, haty)
        if self.state == Game.REGISTRATION:
            if hatx != 0:
                self.reg.on_event(evt)
        elif self.state == Game.PLAY:
            if evt.get_id() in self.gameplay_input:
                self.gameplay_input[evt.get_id()](hatx, haty)

    def update(self, delta_time):
        self.timers.update(delta_time)
        self.script_sched.update()
        self.fx_actors.update(delta_time)
        if self.state == Game.WELCOME:
            pass
        elif self.state == Game.REGISTRATION:
            try:
                next(self.reg.script)
            except StopIteration:
                pass
        elif self.state == Game.PLAY:
            self.player_list.update()

            # Prevent partial-pixel positioning, which can cause edge artifacts on player sprites.
            # This also makes it a bit easier for a player to completely stop the motion of their Player.
            for player in self.player_list:
                player.center_x = int(player.center_x)
                player.center_y = int(player.center_y)

            for p in self.player_list:
                self.check_killer_tiles_collision(p, self.killers)
                self.check_wall_tiles_collision(p, self.walls)
            for p in self.player_list:
                p.change_y -= 0.2  # gravity
                if p.center_x < 0:
                    p.center_x = self.window_width
                elif p.center_x > self.window_width:
                    p.center_x = 0
            self.check_player_collision()
        try:
            next(self.script)
        except StopIteration:
            self.close()

    def make_player_death_emitter(self, player):
        return arcade.make_burst_emitter(
            (player.center_x, player.center_y),
            [CIRCLE_TEXTURE],
            particle_count=15,
            particle_speed=5.0,
            particle_lifetime_min=0.1,
            particle_lifetime_max=0.2,
            fade_particles=True
        )

    def check_killer_tiles_collision(self, player: Player, killers):
        hit_list = arcade.check_for_collision_with_list(player, killers)
        if len(hit_list) > 0:
            player.score += CFG.Player.death_score
            self.fx_actors.append(self.make_player_death_emitter(player))
            self.script_sched.add(player.death_script())

    def check_wall_tiles_collision(self, player: Player, walls):
        hit_wall_list = arcade.check_for_collision_with_list(player, walls)
        if len(hit_wall_list) > 0:
            for wall in hit_wall_list:
                hit = collision.intersect_AABB(player, wall)
                if hit is None:
                    continue
                if hit.normal[0] > 0 or hit.normal[0] < 0:  # from right or left
                    player.center_x += hit.delta[0]
                    player.change_x = 0
                if hit.normal[1] > 0:  # hit top of wall
                    player.bottom = wall.top - 1
                    player.change_y = 0
                    player.set_landed()
                if hit.normal[1] < 0:  # hit bottom of wall
                    player.center_y += hit.delta[1]
                    player.change_y = -3.0
        else:
            player.set_flying()

    def check_player_collision(self) -> None:
        p1: Player
        for idx1, p1 in enumerate(self.player_list):
            for idx2 in range(idx1 + 1, len(self.player_list)):
                p2: Player = self.player_list[idx2]
                if p1.is_alive and p2.is_alive:
                    if arcade.check_for_collision(p1, p2):
                        if int(p1.center_y) == int(p2.center_y):
                            # equal collision
                            if p1.center_x < p2.center_x:
                                p1.center_x += -1
                                p1.change_x = -0.5
                                p1.change_y = 0.0
                                p2.center_x += 1
                                p2.change_x = 0.5
                                p2.change_y = 0.0
                            else:
                                p1.center_x += 1
                                p1.change_x = 0.5
                                p1.change_y = 0.0
                                p2.center_x += -1
                                p2.change_x = -0.5
                                p2.change_y = 0.0
                        elif p1.center_y > p2.center_y:
                            p1.score += CFG.Player.kill_score
                            self.fx_actors.append(self.make_player_death_emitter(p2))
                            self.script_sched.add(p2.death_script())
                        elif p2.center_y > p1.center_y:
                            p2.score += CFG.Player.kill_score
                            self.fx_actors.append(self.make_player_death_emitter(p1))
                            self.script_sched.add(p1.death_script())

    def print_scores(self):
        for p in self.player_list:
            print('{}: {}'.format(p.name, p.score))

    def is_game_over(self):
        scores = [p.score for p in self.player_list]
        return max(scores) >= CFG.Game.goal_score

    def draw_scores(self):
        labels = ['{}: {}'.format(p.name, p.score) for p in self.player_list]
        arcade.draw_text('    '.join(labels), 50, 5, arcade.color.WHITE, 20)


def main() -> None:
    print(f'Location of script entry point: {__file__}')
    new_path = os.path.dirname(os.path.abspath(__file__))
    print(f'Setting working directory to: {new_path}')
    os.chdir(new_path)  # set working dir relative to location of script entry point
    app = Game(1280, 720, 'Flapping', CFG.Window.fullscreen)
    # app.set_location(1500, 200)
    arcade.run()


if __name__ == "__main__":
    main()
