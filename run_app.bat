@echo off
echo Installing required packages...
pip install -r requirements.txt

echo Starting Soccer Shooter Game...
streamlit run game.py

pause
