from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('game.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🐉 3D DND Dungeon Crawler - Flask Server")
    print("="*60)
    print("\n🎮 Starting game server...")
    print("📍 Open your browser to: http://localhost:5000")
    print("\nControls:")
    print("  WASD - Move")
    print("  Mouse - Look around (click to lock)")
    print("  E - Open chests")
    print("  Space - Attack enemies")
    print("\n" + "="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
