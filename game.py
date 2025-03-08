import streamlit as st
import asyncio
import random

# Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 20
BALL_SIZE = 15
BULLET_SIZE = 5
PLAYER_SPEED = 5
BULLET_SPEED = 10
GOAL_SCORE = 5

# Initialize game state
if "players" not in st.session_state:
    st.session_state.players = [
        {"x": 100, "y": HEIGHT // 2, "color": "blue", "score": 0, "bullets": []},
        {"x": WIDTH - 100, "y": HEIGHT // 2, "color": "red", "score": 0, "bullets": []},
    ]
if "ball" not in st.session_state:
    st.session_state.ball = {"x": WIDTH // 2, "y": HEIGHT // 2, "color": "yellow"}
if "game_over" not in st.session_state:
    st.session_state.game_over = False

# Helper functions
def move_player(player, dx, dy):
    player["x"] = max(PLAYER_SIZE, min(player["x"] + dx, WIDTH - PLAYER_SIZE))
    player["y"] = max(PLAYER_SIZE, min(player["y"] + dy, HEIGHT - PLAYER_SIZE))

def shoot_bullet(player):
    target_x = random.randint(0, WIDTH)
    target_y = random.randint(0, HEIGHT)
    bullet = {
        "x": player["x"],
        "y": player["y"],
        "target_x": target_x,
        "target_y": target_y,
        "color": player["color"],
    }
    player["bullets"].append(bullet)

def move_bullets():
    for player in st.session_state.players:
        for bullet in player["bullets"]:
            dx = bullet["target_x"] - bullet["x"]
            dy = bullet["target_y"] - bullet["y"]
            dist = (dx**2 + dy**2) ** 0.5
            if dist == 0:
                dist = 1
            bullet["x"] += (dx / dist) * BULLET_SPEED
            bullet["y"] += (dy / dist) * BULLET_SPEED

def check_collisions():
    ball = st.session_state.ball
    for player in st.session_state.players:
        # Check if ball collides with player
        dist = ((ball["x"] - player["x"]) ** 2 + (ball["y"] - player["y"]) ** 2) ** 0.5
        if dist < BALL_SIZE + PLAYER_SIZE:
            ball["x"] = WIDTH // 2
            ball["y"] = HEIGHT // 2
            player["score"] += 1
            if player["score"] >= GOAL_SCORE:
                st.session_state.game_over = True

# Streamlit UI
st.title("Soccer Shooter Game")
st.write("Use the buttons to move and shoot!")

# Player controls
col1, col2 = st.columns(2)
with col1:
    if st.button("Move Player 1 Left"):
        move_player(st.session_state.players[0], -PLAYER_SPEED, 0)
    if st.button("Move Player 1 Right"):
        move_player(st.session_state.players[0], PLAYER_SPEED, 0)
    if st.button("Move Player 1 Up"):
        move_player(st.session_state.players[0], 0, -PLAYER_SPEED)
    if st.button("Move Player 1 Down"):
        move_player(st.session_state.players[0], 0, PLAYER_SPEED)
    if st.button("Shoot Player 1"):
        shoot_bullet(st.session_state.players[0])

with col2:
    if st.button("Move Player 2 Left"):
        move_player(st.session_state.players[1], -PLAYER_SPEED, 0)
    if st.button("Move Player 2 Right"):
        move_player(st.session_state.players[1], PLAYER_SPEED, 0)
    if st.button("Move Player 2 Up"):
        move_player(st.session_state.players[1], 0, -PLAYER_SPEED)
    if st.button("Move Player 2 Down"):
        move_player(st.session_state.players[1], 0, PLAYER_SPEED)
    if st.button("Shoot Player 2"):
        shoot_bullet(st.session_state.players[1])

# Game canvas
canvas = st.empty()

# Game loop
async def game_loop():
    while not st.session_state.game_over:
        move_bullets()
        check_collisions()

        # Draw game state
        canvas.markdown(
            f"""
            <div style="position: relative; width: {WIDTH}px; height: {HEIGHT}px; background: black;">
                <div style="position: absolute; left: {st.session_state.ball['x']}px; top: {st.session_state.ball['y']}px; width: {BALL_SIZE}px; height: {BALL_SIZE}px; background: {st.session_state.ball['color']}; border-radius: 50%;"></div>
                {''.join(
                    f'<div style="position: absolute; left: {player["x"]}px; top: {player["y"]}px; width: {PLAYER_SIZE}px; height: {PLAYER_SIZE}px; background: {player["color"]}; border-radius: 50%;"></div>'
                    for player in st.session_state.players
                )}
                {''.join(
                    f'<div style="position: absolute; left: {bullet["x"]}px; top: {bullet["y"]}px; width: {BULLET_SIZE}px; height: {BULLET_SIZE}px; background: {bullet["color"]}; border-radius: 50%;"></div>'
                    for player in st.session_state.players for bullet in player["bullets"]
                )}
            </div>
            <p>Player 1 Score: {st.session_state.players[0]["score"]}</p>
            <p>Player 2 Score: {st.session_state.players[1]["score"]}</p>
            """,
            unsafe_allow_html=True,
        )

        await asyncio.sleep(0.1)

    st.write(f"Game Over! Player {1 if st.session_state.players[0]['score'] >= GOAL_SCORE else 2} wins!")

# Run the game loop
asyncio.run(game_loop())
