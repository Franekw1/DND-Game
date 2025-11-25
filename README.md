# D&D 5e Interactive Web Adventure

An immersive web-based Dungeons & Dragons 5th Edition text adventure game with real-time AI-generated stories, tactical combat, and character progression.

## Features

### 🎲 Authentic D&D 5e Mechanics
- Full dice rolling system (d4, d6, d8, d10, d12, d20, d100)
- Advantage/Disadvantage mechanics
- Ability score rolling (4d6 drop lowest)
- Attack rolls, armor class, and critical hits
- Initiative-based combat

### ⚔️ Character Creation
- **8 Playable Races**: Human, Elf, Dwarf, Halfling, Half-Orc, Gnome, Tiefling, Dragonborn
- **8 Classes**: Fighter, Wizard, Rogue, Cleric, Ranger, Barbarian, Paladin, Bard
- Racial ability bonuses following 5e rules
- Class-specific hit dice and abilities
- Dynamic stat rolling with racial modifiers

### 🗡️ Combat System
- Turn-based combat with initiative
- Attack rolls vs AC
- Critical hits (natural 20) and fumbles
- Class-specific combat abilities
- Enemy variety with different stats and rewards
- Boss encounters

### 📖 Dynamic Storytelling
- AI-generated story scenes
- **4 AI-generated choices** per action scene
- **1 custom input option** for creative freedom
- Your choices shape the adventure
- Random encounters and treasure

### 🎨 Beautiful Fantasy UI
- Parchment-themed interface
- Animated dice rolls
- Real-time character sheet
- HP bars with smooth animations
- Combat log and action history
- Responsive design for all devices

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd DND-Game
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## How to Play

### Character Creation
1. Enter your character name
2. Select a race (each has unique ability bonuses)
3. Choose a class (determines hit dice and abilities)
4. Click "Begin Adventure"

### Gameplay
- Read the story text describing your current situation
- Choose from 4 AI-generated actions, or
- Enter your own custom action in the text field
- Use keyboard shortcuts:
  - **1-4**: Quick select choices
  - **C**: Focus custom action input
  - **R**: Take a short rest (outside combat)

### Combat
- Combat triggers randomly during exploration
- Attack rolls are made automatically
- Choose your combat action each turn
- Monitor enemy HP and your character's HP
- Defeat enemies to gain XP and gold

### Progression
- Gain XP from defeating enemies
- Level up to increase HP
- Find treasure and gold
- Take short rests to recover HP
- Manage your inventory

## Game Mechanics

### Ability Scores
- **STR** (Strength): Melee attacks, carrying capacity
- **DEX** (Dexterity): Ranged attacks, AC, stealth
- **CON** (Constitution): Hit points, fortitude
- **INT** (Intelligence): Arcane knowledge, investigation
- **WIS** (Wisdom): Perception, insight, willpower
- **CHA** (Charisma): Persuasion, deception, performance

### Combat Flow
1. Enemy appears (40% chance during exploration)
2. You choose an action (attack, spell, defend, etc.)
3. Roll to hit vs enemy AC
4. Deal damage on hit
5. Enemy attacks back
6. Repeat until victory or defeat

### Rest System
- Short rests restore HP based on hit die + CON modifier
- Cannot rest during combat
- Strategic rest management is key to survival

## Development

### Project Structure
```
DND-Game/
├── app.py                 # Flask backend and game logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── style.css         # Parchment-themed styling
│   └── game.js           # Frontend game logic
└── README.md             # This file
```

### Technologies
- **Backend**: Flask (Python)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Session Management**: Flask-Session
- **Game Logic**: Python dataclasses and OOP

## Future Enhancements

Potential features for future versions:
- [ ] Spell system with spell slots
- [ ] Equipment and weapon upgrades
- [ ] Party system (multiple characters)
- [ ] Save/load game state
- [ ] More enemy types and bosses
- [ ] Dungeon levels and progression
- [ ] Character backgrounds and traits
- [ ] Sound effects and music
- [ ] Multiplayer support

## License

This project is open source and available under the MIT License.

## Credits

Created as an interactive D&D 5e experience. Based on the D&D 5th Edition ruleset by Wizards of the Coast.

---

**Roll for initiative and begin your adventure!** ⚔️🎲🐉
