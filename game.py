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
    def __init__(self, x, y, color, controls, radius=20):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.velocity = [0, 0]
        self.controls = controls
        self.health = 100
        self.frozen = 0
        self.score = 0
        self.bullets = []
        self.auto_aim = NO_AUTO_AIM

    def move(self):
        if self.frozen > 0:
            self.frozen -= 1
            return

        keys = pygame.key.get_pressed()
        self.velocity[0] *= FRICTION
        self.velocity[1] *= FRICTION

        if keys[self.controls["up"]]:
            self.velocity[1] -= PLAYER_SPEED
        if keys[self.controls["down"]]:
            self.velocity[1] += PLAYER_SPEED
        if keys[self.controls["left"]]:
            self.velocity[0] -= PLAYER_SPEED
        if keys[self.controls["right"]]:
            self.velocity[0] += PLAYER_SPEED

        self.x += self.velocity[0]
        self.y += self.velocity[1]

        self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

    def shoot(self, target_pos, ball_pos, players):
        if self.frozen > 0:
            return

        if self.auto_aim == AUTO_AIM_PLAYER:
            target_pos = target_pos
        elif self.auto_aim == AUTO_AIM_BALL:
            target_pos = ball_pos

        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        angle = math.atan2(dy, dx)
        velocity = [BULLET_SPEED * math.cos(angle), BULLET_SPEED * math.sin(angle)]
        self.bullets.append(Bullet(self.x, self.y, velocity, self.color))

    def player_collide(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance < self.radius + other.radius:
            angle = math.atan2(dy, dx)
            overlap = self.radius + other.radius - distance
            self.x += math.cos(angle) * overlap / 2
            self.y += math.sin(angle) * overlap / 2
            other.x -= math.cos(angle) * overlap / 2
            other.y -= math.sin(angle) * overlap / 2
            self.velocity[0] *= -1
            self.velocity[1] *= -1
            other.velocity[0] *= -1
            other.velocity[1] *= -1

class Bullet:
    def __init__(self, x, y, velocity, color, radius=5):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.color = color
        self.radius = radius
        self.damage = BULLET_DAMAGE

    def move(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.damage = max(0, self.damage - DAMAGE_DECAY)

    def get_damage(self):
        return self.damage

class Ball:
    def __init__(self, x, y, radius=15):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity = [0, 0]

    def move(self):
        self.velocity[0] *= BALL_FRICTION
        self.velocity[1] *= BALL_FRICTION

        self.x += self.velocity[0]
        self.y += self.velocity[1]

        if self.x < self.radius or self.x > WIDTH - self.radius:
            self.velocity[0] *= -BALL_BOUNCE
            self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        if self.y < self.radius or self.y > HEIGHT - self.radius:
            self.velocity[1] *= -BALL_BOUNCE
            self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

    def collide(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance < self.radius + other.radius:
            angle = math.atan2(dy, dx)
            overlap = self.radius + other.radius - distance
            self.x += math.cos(angle) * overlap
            self.y += math.sin(angle) * overlap
            self.velocity[0] += other.velocity[0] * BALL_IMPACT_MULTIPLIER
            self.velocity[1] += other.velocity[1] * BALL_IMPACT_MULTIPLIER

    def collide(self, bullet):
        dx = self.x - bullet.x
        dy = self.y - bullet.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance < self.radius + bullet.radius:
            angle = math.atan2(dy, dx)
            self.velocity[0] += bullet.velocity[0] * BALL_IMPACT_MULTIPLIER
            self.velocity[1] += bullet.velocity[1] * BALL_IMPACT_MULTIPLIER

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
                if event.key ==pygame.K_2:
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
                    return

        # Draw everything
        for player in players:
            pygame.draw.circle(screen, player.color, (int(player.x), int(player.y)), player.radius)
            for bullet in player.bullets:
                pygame.draw.circle(screen, bullet.color, (int(bullet.x), int(bullet.y)), bullet.radius)
            health_bar_width = player.health
            pygame.draw.rect(screen, GREEN, (player.x - player.radius, player.y - player.radius - 10, health_bar_width/100 * player.radius*2, 5))

        pygame.draw.circle(screen, YELLOW, (int(ball.x), int(ball.y)), ball.radius)

        for goal in goalposts:
            pygame.draw.rect(screen, WHITE, goal)

        # Draw scores
        score_text = font.render(f"Blue: {players[0].score}  Red: {players[1].score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball Game")

    player1 = Player(WIDTH // 4, HEIGHT // 2, BLUE, {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d})
    player2 = Player(3 * WIDTH // 4, HEIGHT // 2, RED, {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT})
    ball = Ball(WIDTH // 2, HEIGHT // 2)

    goalposts = [pygame.Rect(0, HEIGHT // 2 - 50, 10, 100), pygame.Rect(WIDTH - 10, HEIGHT // 2 - 50, 10, 100)]

    running_flag = [True]
    game_over_flag = [False]

    game_loop(screen, [player1, player2], ball, goalposts, running_flag, game_over_flag)

    pygame.quit()

if __name__ == "__main__":
    main()
