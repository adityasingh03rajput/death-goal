import streamlit as st
import asyncio

# Streamlit app
st.title("Soccer Shooter Game")
st.write("Use the buttons to control the game!")

# Game state
if "player1_score" not in st.session_state:
    st.session_state.player1_score = 0
if "player2_score" not in st.session_state:
    st.session_state.player2_score = 0

# Player controls
col1, col2 = st.columns(2)
with col1:
    if st.button("Move Player 1 Left"):
        st.session_state.player1_action = "left"
    if st.button("Move Player 1 Right"):
        st.session_state.player1_action = "right"
    if st.button("Shoot Player 1"):
        st.session_state.player1_action = "shoot"

with col2:
    if st.button("Move Player 2 Left"):
        st.session_state.player2_action = "left"
    if st.button("Move Player 2 Right"):
        st.session_state.player2_action = "right"
    if st.button("Shoot Player 2"):
        st.session_state.player2_action = "shoot"

# Embed JavaScript game
st.components.v1.html(
    """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Soccer Shooter Game</title>
        <style>
            canvas {
                border: 1px solid black;
                background: black;
            }
        </style>
    </head>
    <body>
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");

            // Game state
            let player1 = { x: 100, y: 300, color: "blue", score: 0 };
            let player2 = { x: 700, y: 300, color: "red", score: 0 };
            let ball = { x: 400, y: 300, color: "yellow", radius: 15 };

            // Draw game objects
            function draw() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Draw players
                ctx.fillStyle = player1.color;
                ctx.beginPath();
                ctx.arc(player1.x, player1.y, 20, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = player2.color;
                ctx.beginPath();
                ctx.arc(player2.x, player2.y, 20, 0, Math.PI * 2);
                ctx.fill();

                // Draw ball
                ctx.fillStyle = ball.color;
                ctx.beginPath();
                ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
                ctx.fill();

                // Draw scores
                ctx.fillStyle = "white";
                ctx.font = "20px Arial";
                ctx.fillText("Player 1: " + player1.score, 20, 30);
                ctx.fillText("Player 2: " + player2.score, 620, 30);
            }

            // Update game state
            function update() {
                // Move players
                if (window.parent.player1_action === "left") {
                    player1.x -= 5;
                }
                if (window.parent.player1_action === "right") {
                    player1.x += 5;
                }
                if (window.parent.player2_action === "left") {
                    player2.x -= 5;
                }
                if (window.parent.player2_action === "right") {
                    player2.x += 5;
                }

                // Check for collisions
                if (Math.hypot(player1.x - ball.x, player1.y - ball.y) < 20 + ball.radius) {
                    ball.x = 400;
                    ball.y = 300;
                    player1.score += 1;
                    window.parent.player1_score = player1.score;
                }
                if (Math.hypot(player2.x - ball.x, player2.y - ball.y) < 20 + ball.radius) {
                    ball.x = 400;
                    ball.y = 300;
                    player2.score += 1;
                    window.parent.player2_score = player2.score;
                }

                // Reset actions
                window.parent.player1_action = "";
                window.parent.player2_action = "";
            }

            // Game loop
            function gameLoop() {
                update();
                draw();
                requestAnimationFrame(gameLoop);
            }

            // Start game loop
            gameLoop();
        </script>
    </body>
    </html>
    """,
    height=620,
)

# Display scores
st.write(f"Player 1 Score: {st.session_state.player1_score}")
st.write(f"Player 2 Score: {st.session_state.player2_score}")

# Game over logic
if st.session_state.player1_score >= 5:
    st.write("Player 1 wins!")
if st.session_state.player2_score >= 5:
    st.write("Player 2 wins!")
