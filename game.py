import streamlit as st
import pygame
import math
import random
import threading
import time

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
FRICTION = 0.90
BALL_FRICTION = 0.97
BULLET_SPEED = 8
PLAYER_SPEED = 3
BULLET_DAMAGE = 20
FREEZE_TIME = 180
GOAL_SCORE = 5
BALL_IMPACT_MULTIPLIER = 1.2
BALL_BOUNCE = 0.8
DAMAGE_DECAY = 0.01
AUTO_AIM_PLAYER = 1
AUTO_AIM_BALL = 2
NO_AUTO_AIM = 0

class Player:
    # ... (Player class code from previous response) ...

class Bullet:
    # ... (Bullet class code from previous response) ...

class Ball:
    # ... (Ball class code from previous response) ...

def game_loop(screen, players, ball, goalposts, running_flag, game_over_flag):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    while running_flag[0]:
        clock.tick(60)
        screen.fill(BLACK)

        # Help Caption (Auto-Aim Only)
        help_text = [
            "Auto-Aim Controls:",
            "Player 1 (Blue):",
            "  1: No Auto-Aim",
            "  2: Aim Player",
            "  3: Aim Ball",
            "Player 2 (Red):",
            "  4: No Auto-Aim",
            "  5: Aim Player",
            "  6: Aim Ball"
        ]

        y_offset = 10
        for line in help_text:
            text_surface = font.render(line, True, WHITE)
            screen.blit(text_surface, (10, y_offset))
            y_offset += 20

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running_flag[0] = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    players[0].shoot((players[1].x, players[1].y), ball_pos=(ball.x, ball.y), players=players)
                if event.key == pygame.K_RETURN:
                    players[1].shoot((players[0].x, players[0].y), ball_pos=(ball.x, ball.y), players=players)
                if event.key == pygame.K_1:
                    players[0].auto_aim = NO_AUTO_AIM
                if event.key == pygame.K_2:
                    players[0].auto_aim = AUTO_AIM_PLAYER
                if event.key == pygame.K_3:
                    players[0].auto_aim = AUTO_AIM_BALL
                if event.key == pygame.K_4:
                    players[1].auto_aim = NO_AUTO_AIM
                if event.key == pygame.K_5:
                    players[1].auto_aim = AUTO_AIM_PLAYER
                if event.key == pygame.K_6:
                    players[1].auto_aim = AUTO_AIM_BALL

        for i, player in enumerate(players):
            player.move()
            ball.collide(player)
            for j in range(i + 1, len(players)):
                player2 = players[j]
                if player.radius + player2.radius > math.sqrt((player.x - player2.x)**2 + (player.y - player2.y)**2):
                    player.player_collide(player2)

        all_bullets = players[0].bullets[:] + players[1].bullets[:]

        for i, bullet1 in enumerate(all_bullets):
            for j in range(i + 1, len(all_bullets)):
                bullet2 = all_bullets[j]
                if bullet1.radius + bullet2.radius > math.sqrt((bullet1.x - bullet2.x)**2 + (bullet1.y - bullet2.y)**2):
                    if bullet1.get_damage() < bullet2.get_damage():
                        for p in players:
                            if bullet1 in p.bullets:
                                p.bullets.remove(bullet1)
                    else:
                        for p in players:
                            if bullet2 in p.bullets:
                                p.bullets.remove(bullet2)

        for player in players:
            for bullet in player.bullets[:]:
                bullet.move()
                for other_player in players:
                    if other_player != player and bullet.radius + other_player.radius > math.sqrt((bullet.x - other_player.x)**2 + (bullet.y - other_player.y)**2):
                        damage = bullet.get_damage()
                        other_player.health -= damage
                        player.bullets.remove(bullet)
                        if other_player.health <= 0:
                            other_player.frozen = FREEZE_TIME
                ball.collide(bullet)

        ball.move()

        for idx, goal in enumerate(goalposts):
            if goal.colliderect(pygame.Rect(ball.x - ball.radius, ball.y - ball.radius, ball.radius * 2, ball.radius * 2)):
                players[idx ^ 1].score += 1
                ball.x, ball.y = WIDTH // 2, HEIGHT // 2
                ball.velocity = [0, 0]
                if players[idx ^ 1].score >= GOAL_SCORE:
                    winner_text = font.render(f"Player {idx ^ 1 + 1} wins!", True, WHITE)
                    winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    screen.blit(winner_text, winner_rect)
                    pygame.display.flip()
                    time.sleep(3)
                    game_over_flag[0] = True
                    running_flag[0] = False

        for player in players:
            pygame.draw.circle(screen, player.color, (int(player.x), int(player.y)), player.radius)
            pygame.draw.rect(screen, RED, (player.x - 20, player.y - 30, 40, 5))
            pygame.draw.rect(screen, GREEN, (player.x - 20, player.y - 30, int(40 * player.health / player.max_health), 5))
            score_text = font.render(f"Score: {player.score}", True, WHITE)
            screen.blit(score_text, (player.x - 20, player.y - 45))
        for player in players:
            for bullet in player.bullets:
                pygame.draw.circle(screen, bullet.color, (int(bullet.x), int(bullet.y)), bullet.radius)

        pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), ball.radius)
        for goal in goalposts:
            pygame.draw.rect(screen, WHITE, goal)

        pygame.display.flip()

def main():
    st.title("Soccer Shooter Game")

    canvas = st.empty()

    pygame.init()
    screen = pygame.Surface((WIDTH, HEIGHT))

    players = [
        Player(100, HEIGHT // 2, BLUE, {'left': pygame.K_a, 'right': pygame.K_d, 'up': pygame.K_w, 'down': pygame.K_s, 'shoot': pygame.K_SPACE}, AUTO_AIM_PLAYER),
        Player(WIDTH - 100, HEIGHT // 2, RED, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP, 'down': pygame.K_DOWN, 'shoot': pygame.K_RETURN}, AUTO_AIM_BALL)
    ]
    ball = Ball(WIDTH // 2, HEIGHT // 2, YELLOW)
    goalposts = [pygame.Rect(0, HEIGHT // 3, 10, HEIGHT // 3), pygame.Rect(WIDTH - 10, HEIGHT // 3, 10, HEIGHT // 3)]running_flag = [True]
    game_over_flag = [False]

    def run_game():
        game_loop(screen, players, ball, goalposts, running_flag, game_over_flag)

    game_thread = threading.Thread(target=run_game)
    game_thread.daemon = True  # Allow the thread to be killed when the main app exits
    game_thread.start()

    while running_flag[0]:
        img_bytes = pygame.image.tostring(screen, "RGB")
        img = pygame.image.fromstring(img_bytes, (WIDTH, HEIGHT), "RGB")
        canvas.image(img, use_column_width=True)
        time.sleep(1/60) #Limit redraws to 60fps

    if game_over_flag[0]:
        st.write("Game Over!")
        # Reset the game state if needed
        players[0] = Player(100, HEIGHT // 2, BLUE, {'left': pygame.K_a, 'right': pygame.K_d, 'up': pygame.K_w, 'down': pygame.K_s, 'shoot': pygame.K_SPACE}, AUTO_AIM_PLAYER)
        players[1] = Player(WIDTH - 100, HEIGHT // 2, RED, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP, 'down': pygame.K_DOWN, 'shoot': pygame.K_RETURN}, AUTO_AIM_BALL)
        ball = Ball(WIDTH // 2, HEIGHT // 2, YELLOW)
        game_over_flag[0] = False
        running_flag[0] = True
        game_thread = threading.Thread(target=run_game)
        game_thread.daemon = True
        game_thread.start()

if __name__ == "__main__":
    main()
