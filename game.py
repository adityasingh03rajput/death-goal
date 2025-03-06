import streamlit as st
import threading

def run_arcade_game():
    import arcade
    import math
    import random

    # Constants
    WIDTH, HEIGHT = 800, 500
    PLAYER_SIZE = 20
    BALL_SIZE = 15
    BULLET_SIZE = 5
    PLAYER_SPEED = 4
    BULLET_SPEED = 6
    MAX_BULLETS = 6
    GOAL_WIDTH = 100
    GOAL_HEIGHT = 120
    HEALTH = 100
    BALL_SPEED = 3
    FRICTION = 0.98
    AI_REACTION_TIME = 15
    MIN_BALL_SPEED = 0.5

    class SoccerShooter(arcade.Window):
        def __init__(self):
            super().__init__(WIDTH, HEIGHT, "Arcade Soccer Shooter")
            self.players = []
            self.ball = None
            self.score_p1 = 0
            self.score_p2 = 0
            self.paused = False
            self.ai_timer = 0
            arcade.set_background_color(arcade.color.GREEN)

        def setup(self):
            self.players = [
                {'x': 100, 'y': HEIGHT // 2, 'color': arcade.color.RED, 'health': HEALTH,
                 'bullets': [], 'angle': 0, 'is_ai': False},
                {'x': 700, 'y': HEIGHT // 2, 'color': arcade.color.BLUE, 'health': HEALTH,
                 'bullets': [], 'angle': 0, 'is_ai': True}
            ]
            self.ball = {'x': WIDTH // 2, 'y': HEIGHT // 2,
                         'vx': random.uniform(-BALL_SPEED, BALL_SPEED),
                         'vy': random.uniform(-BALL_SPEED, BALL_SPEED)}

        def on_draw(self):
            arcade.start_render()
            for player in self.players:
                arcade.draw_circle_filled(player['x'], player['y'], PLAYER_SIZE, player['color'])
                for bullet in player['bullets']:
                    arcade.draw_circle_filled(bullet[0], bullet[1], BULLET_SIZE, arcade.color.YELLOW)
            arcade.draw_circle_filled(self.ball['x'], self.ball['y'], BALL_SIZE, arcade.color.WHITE)

        def update(self, delta_time):
            if self.paused:
                return
            for player in self.players:
                self.update_bullets(player)
            self.update_ball()
            if self.players[1]['is_ai']:
                self.ai_control(self.players[1], self.ball)

        def update_ball(self):
            self.ball['x'] += self.ball['vx']
            self.ball['y'] += self.ball['vy']
            self.ball['vx'] *= FRICTION
            self.ball['vy'] *= FRICTION

            if abs(self.ball['vx']) < MIN_BALL_SPEED:
                self.ball['vx'] = MIN_BALL_SPEED if self.ball['vx'] > 0 else -MIN_BALL_SPEED
            if abs(self.ball['vy']) < MIN_BALL_SPEED:
                self.ball['vy'] = MIN_BALL_SPEED if self.ball['vy'] > 0 else -MIN_BALL_SPEED

            if self.ball['x'] - BALL_SIZE < 0 or self.ball['x'] + BALL_SIZE > WIDTH:
                self.ball['vx'] *= -1
            if self.ball['y'] - BALL_SIZE < 0 or self.ball['y'] + BALL_SIZE > HEIGHT:
                self.ball['vy'] *= -1

        def update_bullets(self, player):
            for bullet in player['bullets'][:]:
                bullet[0] += bullet[2]
                bullet[1] += bullet[3]

                if bullet[0] < 0 or bullet[0] > WIDTH or bullet[1] < 0 or bullet[1] > HEIGHT:
                    player['bullets'].remove(bullet)

        def ai_control(self, ai, ball):
            if self.ai_timer % AI_REACTION_TIME == 0:
                if ball['x'] > ai['x']:
                    ai['x'] += PLAYER_SPEED
                elif ball['x'] < ai['x']:
                    ai['x'] -= PLAYER_SPEED
                if ball['y'] > ai['y']:
                    ai['y'] += PLAYER_SPEED
                elif ball['y'] < ai['y']:
                    ai['y'] -= PLAYER_SPEED
                self.auto_aim(ai, ball)
                self.shoot(ai)
            self.ai_timer += 1

        def auto_aim(self, player, target):
            dx = target['x'] - player['x']
            dy = target['y'] - player['y']
            player['angle'] = math.degrees(math.atan2(dy, dx))

        def shoot(self, player):
            if len(player['bullets']) < MAX_BULLETS:
                rad = math.radians(player['angle'])
                vx = BULLET_SPEED * math.cos(rad)
                vy = BULLET_SPEED * math.sin(rad)
                player['bullets'].append([player['x'], player['y'], vx, vy])

        def on_key_press(self, key, modifiers):
            if key == arcade.key.P:
                self.paused = not self.paused
            if key == arcade.key.F:
                self.shoot(self.players[0])

    game = SoccerShooter()
    game.setup()
    arcade.run()

# Streamlit interface
st.title("Arcade Soccer Shooter via Streamlit")
st.write("Click the button below to launch the Arcade Soccer Shooter game.")

if st.button("Launch Game"):
    # Run the arcade game in a separate thread so it doesn't block Streamlit
    thread = threading.Thread(target=run_arcade_game, daemon=True)
    thread.start()
    st.write("Game launched! Check your desktop for the game window.")
