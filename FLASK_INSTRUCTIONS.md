# 🐉 3D DND Dungeon Crawler - Flask Version

## Quick Start (No Node.js Required!)

This version uses Flask to serve the 3D game, so you only need Python!

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask server:**
   ```bash
   python app.py
   ```

3. **Open your browser:**
   - Go to: `http://localhost:5000`
   - Click to start playing
   - Use mouse to look around

## 🎮 Controls

| Key | Action |
|-----|--------|
| **W** | Move Forward |
| **A** | Strafe Left |
| **S** | Move Backward |
| **D** | Strafe Right |
| **Mouse** | Look Around (click to lock pointer) |
| **E** | Interact with Chests |
| **Space** | Attack Enemies |

## 📁 Project Structure

```
DND-Game/
├── app.py              # Flask server
├── requirements.txt    # Python dependencies
├── templates/
│   └── game.html      # Main game HTML
└── static/
    ├── css/
    │   └── styles.css # Game styling
    └── js/
        └── game.js    # 3D game logic (Three.js)
```

## 🎯 Features

- ✅ Fully 3D dungeon environment
- ✅ First-person controls (WASD + Mouse)
- ✅ Enemy AI that chases you
- ✅ Treasure chests to loot
- ✅ Combat system
- ✅ Health, score, and gold tracking
- ✅ Dynamic lighting with animated torches
- ✅ Collision detection
- ✅ No Node.js/npm required!

## 🔧 Troubleshooting

### Port Already in Use
If port 5000 is busy, edit `app.py` and change the port:
```python
app.run(debug=True, port=8080)  # Use any available port
```

### Three.js Not Loading
The game uses Three.js from CDN. Make sure you have internet connection.

## 🎮 Enjoy Your Adventure!

Explore the dungeon, defeat enemies, and collect treasure! ⚔️✨
