const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Constants
const WIDTH = 800;
const HEIGHT = 600;
const WHITE = "#FFFFFF";
const RED = "#FF0000";
const GREEN = "#00FF00";
const BLUE = "#0000FF";
const YELLOW = "#FFFF00";
const BLACK = "#000000";
const FRICTION = 0.90;
const BALL_FRICTION = 0.97;
const BULLET_SPEED = 8;
const PLAYER_SPEED = 3;
const BULLET_DAMAGE = 20;
const FREEZE_TIME = 180;
const GOAL_SCORE = 5;
const BALL_IMPACT_MULTIPLIER = 1.2;
const BALL_BOUNCE = 0.8;
const DAMAGE_DECAY = 0.01;
const AUTO_AIM_PLAYER = 1;
const AUTO_AIM_BALL = 2;
const NO_AUTO_AIM = 0;

// Player Class
class Player {
  constructor(x, y, color, keys, autoAim = NO_AUTO_AIM) {
    this.x = x;
    this.y = y;
    this.radius = 20;
    this.color = color;
    this.velocity = { x: 0, y: 0 };
    this.health = 100;
    this.maxHealth = 100;
    this.bullets = [];
    this.score = 0;
    this.frozen = 0;
    this.keys = keys;
    this.autoAim = autoAim;
  }

  move() {
    if (this.frozen > 0) {
      this.frozen--;
      if (this.frozen === 0) this.health = this.maxHealth;
      return;
    }

    if (keys[this.keys.left]) this.velocity.x -= PLAYER_SPEED;
    if (keys[this.keys.right]) this.velocity.x += PLAYER_SPEED;
    if (keys[this.keys.up]) this.velocity.y -= PLAYER_SPEED;
    if (keys[this.keys.down]) this.velocity.y += PLAYER_SPEED;

    this.velocity.x *= FRICTION;
    this.velocity.y *= FRICTION;
    this.x += this.velocity.x;
    this.y += this.velocity.y;

    // Boundary checks
    this.x = Math.max(this.radius, Math.min(this.x, WIDTH - this.radius));
    this.y = Math.max(this.radius, Math.min(this.y, HEIGHT - this.radius));
  }

  shoot(target, ballPos = null, players = []) {
    if (this.frozen > 0) return;

    if (this.autoAim === AUTO_AIM_PLAYER && players.length > 0) {
      let closestPlayer = null;
      let closestDist = Infinity;
      for (const otherPlayer of players) {
        if (otherPlayer !== this) {
          const dx = this.x - otherPlayer.x;
          const dy = this.y - otherPlayer.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < closestDist) {
            closestDist = dist;
            closestPlayer = otherPlayer;
          }
        }
      }
      if (closestPlayer) target = { x: closestPlayer.x, y: closestPlayer.y };
    } else if (this.autoAim === AUTO_AIM_BALL && ballPos) {
      target = ballPos;
    }

    const angle = Math.atan2(target.y - this.y, target.x - this.x);
    this.bullets.push(new Bullet(this.x, this.y, this.color, angle));
  }

  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = this.color;
    ctx.fill();
    ctx.closePath();

    // Health bar
    ctx.fillStyle = RED;
    ctx.fillRect(this.x - 20, this.y - 30, 40, 5);
    ctx.fillStyle = GREEN;
    ctx.fillRect(this.x - 20, this.y - 30, (40 * this.health) / this.maxHealth, 5);

    // Score
    ctx.fillStyle = WHITE;
    ctx.font = "16px Arial";
    ctx.fillText(`Score: ${this.score}`, this.x - 20, this.y - 45);
  }
}

// Bullet Class
class Bullet {
  constructor(x, y, color, angle) {
    this.x = x;
    this.y = y;
    this.radius = 4;
    this.color = color;
    this.velocity = {
      x: Math.cos(angle) * BULLET_SPEED,
      y: Math.sin(angle) * BULLET_SPEED,
    };
  }

  move() {
    this.x += this.velocity.x;
    this.y += this.velocity.y;
  }

  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = this.color;
    ctx.fill();
    ctx.closePath();
  }
}

// Ball Class
class Ball {
  constructor(x, y, color) {
    this.x = x;
    this.y = y;
    this.radius = 15;
    this.color = color;
    this.velocity = { x: 0, y: 0 };
  }

  move() {
    this.x += this.velocity.x;
    this.y += this.velocity.y;
    this.velocity.x *= BALL_FRICTION;
    this.velocity.y *= BALL_FRICTION;

    // Boundary checks
    if (this.x <= this.radius || this.x >= WIDTH - this.radius) this.velocity.x *= -BALL_BOUNCE;
    if (this.y <= this.radius || this.y >= HEIGHT - this.radius) this.velocity.y *= -BALL_BOUNCE;
  }

  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = this.color;
    ctx.fill();
    ctx.closePath();
  }
}

// Initialize Game Objects
const players = [
  new Player(100, HEIGHT / 2, BLUE, { left: "KeyA", right: "KeyD", up: "KeyW", down: "KeyS", shoot: "Space" }, AUTO_AIM_PLAYER),
  new Player(WIDTH - 100, HEIGHT / 2, RED, { left: "ArrowLeft", right: "ArrowRight", up: "ArrowUp", down: "ArrowDown", shoot: "Enter" }, AUTO_AIM_BALL),
];
const ball = new Ball(WIDTH / 2, HEIGHT / 2, YELLOW);
const goalposts = [
  { x: 0, y: HEIGHT / 3, width: 10, height: HEIGHT / 3 },
  { x: WIDTH - 10, y: HEIGHT / 3, width: 10, height: HEIGHT / 3 },
];

// Key State
const keys = {};

// Touch Controls
document
