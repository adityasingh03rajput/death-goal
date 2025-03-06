import streamlit as st
import os

st.title("⚽ Web Soccer Shooter Game")
st.write("Press the button below to launch the game!")

if st.button("Start Game"):
    os.system("python game.py")
