import os
import webbrowser

# Path to the index.html file
index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

# Open index.html in the default web browser
webbrowser.open(f"file://{index_path}")
