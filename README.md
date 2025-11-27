# 🐉 3D DND Dungeon Crawler

An immersive 3D Dungeons & Dragons dungeon crawler built with **Three.js**. Explore a dark dungeon, collect treasure, and battle enemies in this first-person adventure!

## ✨ Features

### 🎮 3D Components
- **Fully 3D Environment**: Explore a maze-like dungeon with walls, floors, and ceilings
- **Dynamic Lighting**: Atmospheric torch lighting with flickering flame effects
- **First-Person Controls**: WASD movement with mouse-look camera controls
- **3D Character System**: Player represented with collision detection and smooth movement
- **3D Enemies**: Hostile creatures that chase and attack the player with AI pathfinding
- **Interactive Objects**:
  - Treasure chests with randomized gold rewards
  - Animated chest opening mechanics
  - Lootable objects throughout the dungeon

### 🎯 Gameplay Features
- **Combat System**: Attack enemies in close quarters
- **Health Management**: Take damage from enemies and manage your survival
- **Score Tracking**: Earn points for defeating enemies and finding treasure
- **Gold Collection**: Gather wealth from treasure chests
- **Enemy AI**: Enemies patrol and chase the player when nearby
- **Collision Detection**: Realistic physics preventing movement through walls

### 🎨 Visual Effects
- **Fog System**: Atmospheric distance fog for immersion
- **Shadow Mapping**: Dynamic shadows from objects and characters
- **Animated Torches**: Flickering flames with pulsing light
- **Textured Environments**: Stone floor patterns
- **Particle Effects**: Visual feedback for damage and interactions

## 🚀 Installation & Setup

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn
- Modern web browser with WebGL support

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DND-Game
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the game**
   ```bash
   npm start
   ```

4. **Open in browser**
   - Navigate to `http://localhost:8080`
   - Click anywhere to start playing
   - Use mouse to look around

### Alternative: Direct HTML Loading

You can also open `index.html` directly in your browser, but you'll need to serve it via a local server due to ES6 module imports:

```bash
# Using Python 3
python -m http.server 8080

# Using PHP
php -S localhost:8080

# Using Node.js http-server
npx http-server -p 8080
```

## 🎮 Controls

| Key | Action |
|-----|--------|
| **W** | Move Forward |
| **A** | Strafe Left |
| **S** | Move Backward |
| **D** | Strafe Right |
| **Mouse** | Look Around (after clicking to lock pointer) |
| **E** | Interact with Chests |
| **Space** | Attack Enemies |

## 🎯 Gameplay Tips

1. **Explore Thoroughly**: Look for treasure chests in corners and alcoves
2. **Watch Your Health**: Enemies deal damage when close - keep moving!
3. **Attack Strategically**: Get close to enemies and press Space to attack
4. **Use the Environment**: Torches illuminate the dungeon - stay near light
5. **Score High**: Combine chest looting and enemy kills for maximum points

## 📊 Game Stats

- **Health**: Your life points (0-100)
- **Score**: Total points earned
- **Gold**: Currency collected from chests
- **Kills**: Number of enemies defeated

## 🛠️ Technical Details

### Built With
- **Three.js** (v0.160.0) - 3D graphics library
- **Vanilla JavaScript** - Game logic
- **ES6 Modules** - Code organization
- **WebGL** - Hardware-accelerated rendering

### Architecture
- `index.html` - Main HTML structure and HUD overlay
- `game.js` - Core game engine, 3D scene setup, and game logic
- `styles.css` - UI styling and HUD design
- `package.json` - Dependencies and scripts

### 3D Scene Structure
```
Scene
├── Lighting
│   ├── Ambient Light
│   └── Point Lights (Torches)
├── Environment
│   ├── Floor (Textured Plane)
│   ├── Ceiling
│   └── Walls (Collision-enabled)
├── Interactive Objects
│   ├── Treasure Chests
│   └── Enemies (AI-controlled)
└── Camera (First-Person)
```

## 🎨 Customization

### Modify Game Parameters

Edit `game.js` to customize:

```javascript
// Player speed
player.speed = 0.1; // Increase for faster movement

// Enemy behavior
enemy.userData.speed = 0.02; // Enemy chase speed
enemy.userData.health = 50; // Enemy health

// Chest rewards
goldValue: Math.floor(Math.random() * 50) + 10 // Random gold amount
```

### Add More Content

- **More Enemies**: Call `createEnemy(x, z)` with new positions
- **More Chests**: Call `createChest(x, z)` to add treasure
- **New Walls**: Use `createWall(x, y, z, width, height, depth)` for maze design
- **Additional Torches**: Use `createTorch(x, z)` for more lighting

## 🐛 Troubleshooting

### Black Screen
- Ensure you're serving the files via HTTP (not file://)
- Check browser console for errors
- Verify Three.js is loading correctly

### Controls Not Working
- Click on the game window to activate pointer lock
- Check if browser permissions allow pointer lock
- Ensure JavaScript is enabled

### Performance Issues
- Reduce number of enemies or torches
- Disable shadows: `renderer.shadowMap.enabled = false`
- Lower resolution in renderer settings

## 🔮 Future Enhancements

Potential features to add:
- [ ] More enemy types with different behaviors
- [ ] Weapon system with different attack types
- [ ] Power-ups and potions
- [ ] Multiple dungeon levels
- [ ] Save/load game system
- [ ] Sound effects and music
- [ ] Minimap display
- [ ] Inventory system
- [ ] Character progression/leveling
- [ ] Boss battles

## 📝 License

MIT License - Feel free to use and modify for your own projects!

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 🎮 Enjoy Your Adventure!

Dive into the dungeon, collect treasure, and become the ultimate adventurer! Good luck, brave hero! ⚔️✨

---

**Made with ❤️ using Three.js**
