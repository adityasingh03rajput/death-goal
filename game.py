import pygame
import math

# Initialize pygame
pygame.init()

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
BULLET_LIFETIME = 50
WINNING_SCORE = 5

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Soccer Shooter")
clock = pygame.time.Clock()

# Player Class
class Player:
    def __init__(self, x, y, color, controls):
        self.x, self.y = x, y
        self.color = color
        self.bullets = []
        self.controls = controls
        self.health = HEALTH
        self.angle = 0
        self.reload = 0
        self.score = 0
        self.vx, self.vy = 0, 0

    def move(self, keys):
        ax, ay = 0, 0  # Acceleration components
        if keys[self.controls['up']]: ay -= 1
        if keys[self.controls['down']]: ay += 1
        if keys[self.controls['left']]: ax -= 1
        if keys[self.controls['right']]: ax += 1
        
        # Apply movement smoothly
        self.vx += ax * 0.5
        self.vy += ay * 0.5
        self.vx *= 0.9  # Friction
        self.vy *= 0.9  

        self.x += self.vx
        self.y += self.vy

        # Boundary restrictions
        self.x = max(PLAYER_SIZE, min(WIDTH - PLAYER_SIZE, self.x))
        self.y = max(PLAYER_SIZE, min(HEIGHT - PLAYER_SIZE, self.y))

    def auto_aim(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))

    def shoot(self):
        if len(self.bullets) < MAX_BULLETS and self.reload == 0:
            rad = math.radians(self.angle)
            vx = BULLET_SPEED * math.cos(rad)
            vy = BULLET_SPEED * math.sin(rad)
            self.bullets.append([self.x, self.y, vx, vy, BULLET_LIFETIME])
            self.reload = 20

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]
            bullet[4] -= 1
            if bullet[0] < 0 or bullet[0] > WIDTH or bullet[1] < 0 or bullet[1] > HEIGHT or bullet[4] <= 0:
                self.bullets.remove(bullet)

    def update_reload(self):
        if self.reload > 0:
            self.reload -= 1

# Ball Class
class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.vx, self.vy = 0, 0

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.98
        self.vy *= 0.98
        if self.x - BALL_SIZE < 0 or self.x + BALL_SIZE > WIDTH:
            self.vx *= -1
        if self.y - BALL_SIZE < 0 or self.y + BALL_SIZE > HEIGHT:
            self.vy *= -1

    def check_collision(self, player):
        distance = math.hypot(self.x - player.x, self.y - player.y)
        if distance < PLAYER_SIZE + BALL_SIZE and distance != 0:
            self.vx = (self.x - player.x) / distance * BALL_SPEED
            self.vy = (self.y - player.y) / distance * BALL_SPEED

# Initialize objects
player1 = Player(100, HEIGHT // 2, RED, {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d, 'shoot': pygame.K_f})
player2 = Player(700, HEIGHT // 2, BLUE, {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'shoot': pygame.K_RSHIFT})
ball = Ball()

# Game loop control
running = False

# Start screen
screen.fill(BLACK)
font = pygame.font.Font(None, 50)
text = font.render("Press ENTER to Start", True, WHITE)
screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2))
pygame.display.flip()

while not running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            running = True

# Main Game Loop
while running:
    screen.fill(GREEN)
    keys = pygame.key.get_pressed()
    player1.move(keys)
    player2.move(keys)
    player1.auto_aim(player2)
    player2.auto_aim(player1)
    player1.update_reload()
    player2.update_reload()
    player1.update_bullets()
    player2.update_bullets()
    if keys[player1.controls['shoot']]: player1.shoot()
    if keys[player2.controls['shoot']]: player2.shoot()
    ball.move()
    ball.check_collision(player1)
    ball.check_collision(player2)

    # Draw players and bullets
    pygame.draw.circle(screen, RED, (int(player1.x), int(player1.y)), PLAYER_SIZE)
    pygame.draw.circle(screen, BLUE, (int(player2.x), int(player2.y)), PLAYER_SIZE)
    pygame.draw.circle(screen, WHITE, (int(ball.x), int(ball.y)), BALL_SIZE)
    for bullet in player1.bullets:
        pygame.draw.circle(screen, RED, (int(bullet[0]), int(bullet[1])), BULLET_SIZE)
    for bullet in player2.bullets:
        pygame.draw.circle(screen, BLUE, (int(bullet[0]), int(bullet[1])), BULLET_SIZE)

    # Goal Detection
    if ball.x - BALL_SIZE <= 10 and HEIGHT // 2 - GOAL_HEIGHT // 2 <= ball.y <= HEIGHT // 2 + GOAL_HEIGHT // 2:
        player2.score += 1
        ball.reset()
    if ball.x + BALL_SIZE >= WIDTH - 10 and HEIGHT // 2 - GOAL_HEIGHT // 2 <= ball.y <= HEIGHT // 2 + GOAL_HEIGHT // 2:
        player1.score += 1
        ball.reset()
    
    if player1.score >= WINNING_SCORE or player2.score >= WINNING_SCORE:
        running = False
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
