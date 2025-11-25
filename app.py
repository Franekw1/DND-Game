#!/usr/bin/env python3
"""
D&D 5e Web Application
Flask backend for interactive D&D game
"""

from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import secrets
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# ============================================================================
# DICE ROLLING SYSTEM
# ============================================================================
class Dice:
    @staticmethod
    def roll(sides: int, count: int = 1, modifier: int = 0) -> Dict:
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls) + modifier
        return {
            'rolls': rolls,
            'modifier': modifier,
            'total': total,
            'notation': f"{count}d{sides}" + (f"+{modifier}" if modifier > 0 else f"{modifier}" if modifier < 0 else "")
        }

    @staticmethod
    def d20(modifier: int = 0, advantage: bool = False, disadvantage: bool = False) -> Dict:
        if advantage:
            roll1, roll2 = random.randint(1, 20), random.randint(1, 20)
            chosen = max(roll1, roll2)
            return {
                'rolls': [roll1, roll2],
                'chosen': chosen,
                'modifier': modifier,
                'total': chosen + modifier,
                'type': 'advantage'
            }
        elif disadvantage:
            roll1, roll2 = random.randint(1, 20), random.randint(1, 20)
            chosen = min(roll1, roll2)
            return {
                'rolls': [roll1, roll2],
                'chosen': chosen,
                'modifier': modifier,
                'total': chosen + modifier,
                'type': 'disadvantage'
            }
        else:
            roll = random.randint(1, 20)
            return {
                'rolls': [roll],
                'chosen': roll,
                'modifier': modifier,
                'total': roll + modifier,
                'type': 'normal'
            }

# ============================================================================
# GAME DATA
# ============================================================================
RACES = {
    'Human': {'str': 1, 'dex': 1, 'con': 1, 'int': 1, 'wis': 1, 'cha': 1},
    'Elf': {'dex': 2, 'int': 1},
    'Dwarf': {'con': 2, 'wis': 1},
    'Halfling': {'dex': 2, 'cha': 1},
    'Half-Orc': {'str': 2, 'con': 1},
    'Gnome': {'int': 2, 'dex': 1},
    'Tiefling': {'cha': 2, 'int': 1},
    'Dragonborn': {'str': 2, 'cha': 1}
}

CLASSES = {
    'Fighter': {'hit_die': 10, 'primary': 'str'},
    'Wizard': {'hit_die': 6, 'primary': 'int'},
    'Rogue': {'hit_die': 8, 'primary': 'dex'},
    'Cleric': {'hit_die': 8, 'primary': 'wis'},
    'Ranger': {'hit_die': 10, 'primary': 'dex'},
    'Barbarian': {'hit_die': 12, 'primary': 'str'},
    'Paladin': {'hit_die': 10, 'primary': 'str'},
    'Bard': {'hit_die': 8, 'primary': 'cha'}
}

# ============================================================================
# STORY GENERATION
# ============================================================================
class StoryGenerator:
    INTRO_TEMPLATES = [
        "You find yourself at the entrance of {location}, a place whispered about in tavern tales. The air is thick with {atmosphere}.",
        "The road has led you to {location}. Before you stands {obstacle}, and you sense {atmosphere}.",
        "As dawn breaks, you arrive at {location}. {atmosphere} fills the air, and danger lurks nearby.",
    ]

    LOCATIONS = [
        "the Forgotten Crypt", "Shadowfang Cavern", "the Ruins of Thornkeep",
        "Blackwood Forest", "the Tower of Eternal Night", "Dragon's Maw Canyon",
        "the Sunken Temple", "Frostpeak Mountain", "the Cursed Marshlands"
    ]

    ATMOSPHERES = [
        "an ancient evil", "the smell of sulfur and decay", "a sense of being watched",
        "whispers of the damned", "an unnatural silence", "a foreboding darkness"
    ]

    OBSTACLES = [
        "a massive iron gate, slightly ajar", "the corpses of previous adventurers",
        "mysterious glowing runes", "a deep chasm with a rope bridge"
    ]

    EXPLORATION_SCENES = [
        "You enter a dimly lit chamber. {detail}. What do you do?",
        "The passage narrows. {detail}. How do you proceed?",
        "You hear strange sounds ahead. {detail}. What's your move?",
        "A fork in the path appears. {detail}. Which way?",
    ]

    EXPLORATION_DETAILS = [
        "Strange markings cover the walls",
        "You notice fresh blood on the ground",
        "A faint glow emanates from deeper within",
        "The bones of fallen warriors litter the floor",
        "You smell smoke and hear distant chanting"
    ]

    @staticmethod
    def generate_intro():
        template = random.choice(StoryGenerator.INTRO_TEMPLATES)
        return template.format(
            location=random.choice(StoryGenerator.LOCATIONS),
            atmosphere=random.choice(StoryGenerator.ATMOSPHERES),
            obstacle=random.choice(StoryGenerator.OBSTACLES)
        )

    @staticmethod
    def generate_exploration():
        template = random.choice(StoryGenerator.EXPLORATION_SCENES)
        return template.format(
            detail=random.choice(StoryGenerator.EXPLORATION_DETAILS)
        )

    @staticmethod
    def generate_choices(scene_type='exploration'):
        if scene_type == 'exploration':
            return [
                "Search the area carefully for traps and treasure",
                "Proceed cautiously, weapons ready",
                "Light a torch and investigate the sounds",
                "Cast a detection spell to sense magic or danger"
            ]
        elif scene_type == 'combat':
            return [
                "Attack with your weapon",
                "Cast a spell or use a special ability",
                "Take defensive position and dodge",
                "Attempt to intimidate or negotiate"
            ]
        else:
            return [
                "Investigate further",
                "Proceed with caution",
                "Prepare for combat",
                "Look for another path"
            ]

# ============================================================================
# EQUIPMENT SYSTEM
# ============================================================================
EQUIPMENT = {
    'weapons': {
        'Rusty Dagger': {'rarity': 'Common', 'damage': '1d4', 'attack_bonus': 0, 'price': 10, 'level': 1},
        'Iron Sword': {'rarity': 'Common', 'damage': '1d6', 'attack_bonus': 1, 'price': 50, 'level': 1},
        'Steel Longsword': {'rarity': 'Uncommon', 'damage': '1d8', 'attack_bonus': 1, 'price': 150, 'level': 2},
        'Enchanted Blade': {'rarity': 'Rare', 'damage': '1d8', 'attack_bonus': 2, 'price': 500, 'level': 3},
        'Flaming Sword': {'rarity': 'Rare', 'damage': '1d10', 'attack_bonus': 2, 'price': 800, 'level': 4},
        'Dragonslayer Greatsword': {'rarity': 'Epic', 'damage': '2d6', 'attack_bonus': 3, 'price': 2000, 'level': 5},
        'Legendary Blade of Heroes': {'rarity': 'Legendary', 'damage': '2d8', 'attack_bonus': 4, 'price': 5000, 'level': 7},
    },
    'armor': {
        'Tattered Robes': {'rarity': 'Common', 'ac_bonus': 0, 'hp_bonus': 0, 'price': 5, 'level': 1},
        'Leather Armor': {'rarity': 'Common', 'ac_bonus': 1, 'hp_bonus': 5, 'price': 45, 'level': 1},
        'Chain Mail': {'rarity': 'Uncommon', 'ac_bonus': 2, 'hp_bonus': 10, 'price': 150, 'level': 2},
        'Reinforced Plate': {'rarity': 'Rare', 'ac_bonus': 3, 'hp_bonus': 15, 'price': 500, 'level': 3},
        'Enchanted Armor': {'rarity': 'Rare', 'ac_bonus': 4, 'hp_bonus': 20, 'price': 800, 'level': 4},
        'Dragon Scale Mail': {'rarity': 'Epic', 'ac_bonus': 5, 'hp_bonus': 30, 'price': 2000, 'level': 5},
        'Legendary Armor of the Gods': {'rarity': 'Legendary', 'ac_bonus': 6, 'hp_bonus': 50, 'price': 5000, 'level': 7},
    },
    'accessories': {
        'Copper Ring': {'rarity': 'Common', 'stat_bonus': {'str': 1}, 'price': 30, 'level': 1},
        'Silver Amulet': {'rarity': 'Uncommon', 'stat_bonus': {'dex': 1, 'str': 1}, 'price': 100, 'level': 2},
        'Ring of Protection': {'rarity': 'Uncommon', 'stat_bonus': {'con': 2}, 'price': 200, 'level': 2},
        'Amulet of Wisdom': {'rarity': 'Rare', 'stat_bonus': {'wis': 2, 'int': 1}, 'price': 400, 'level': 3},
        'Belt of Giant Strength': {'rarity': 'Rare', 'stat_bonus': {'str': 3}, 'price': 600, 'level': 4},
        'Cloak of Charisma': {'rarity': 'Epic', 'stat_bonus': {'cha': 3, 'wis': 1}, 'price': 1500, 'level': 5},
        'Crown of the Archmage': {'rarity': 'Legendary', 'stat_bonus': {'int': 4, 'wis': 2}, 'price': 4000, 'level': 7},
    }
}

RARITY_COLORS = {
    'Common': '⚪',
    'Uncommon': '🟢',
    'Rare': '🔵',
    'Epic': '🟣',
    'Legendary': '🟠'
}

def calculate_total_stats(character):
    """Calculate total stats including equipment bonuses"""
    total_stats = character['stats'].copy()

    # Add accessory bonuses
    if 'equipped' in character and 'accessory' in character['equipped']:
        accessory_name = character['equipped']['accessory']
        if accessory_name and accessory_name in EQUIPMENT['accessories']:
            accessory = EQUIPMENT['accessories'][accessory_name]
            if 'stat_bonus' in accessory:
                for stat, bonus in accessory['stat_bonus'].items():
                    total_stats[stat] = total_stats.get(stat, 10) + bonus

    return total_stats

def calculate_ac(character):
    """Calculate AC including equipment bonuses"""
    base_ac = 10 + character['modifiers']['dex']

    # Add armor bonus
    if 'equipped' in character and 'armor' in character['equipped']:
        armor_name = character['equipped']['armor']
        if armor_name and armor_name in EQUIPMENT['armor']:
            armor = EQUIPMENT['armor'][armor_name]
            base_ac += armor.get('ac_bonus', 0)

    return base_ac

def calculate_attack_damage(character):
    """Calculate attack bonus and damage from equipped weapon"""
    attack_bonus = 0
    damage = '1d4'  # Default unarmed

    if 'equipped' in character and 'weapon' in character['equipped']:
        weapon_name = character['equipped']['weapon']
        if weapon_name and weapon_name in EQUIPMENT['weapons']:
            weapon = EQUIPMENT['weapons'][weapon_name]
            attack_bonus = weapon.get('attack_bonus', 0)
            damage = weapon.get('damage', '1d6')

    return attack_bonus, damage

# ============================================================================
# ENEMY SYSTEM
# ============================================================================
ENEMIES = {
    'Goblin': {'hp': 15, 'ac': 13, 'attack': 4, 'damage': '1d6+2', 'xp': 50, 'loot_tier': 'common'},
    'Orc Warrior': {'hp': 30, 'ac': 14, 'attack': 5, 'damage': '1d8+3', 'xp': 100, 'loot_tier': 'common'},
    'Skeleton': {'hp': 13, 'ac': 13, 'attack': 4, 'damage': '1d6+2', 'xp': 50, 'loot_tier': 'common'},
    'Giant Spider': {'hp': 26, 'ac': 14, 'attack': 5, 'damage': '1d8+3', 'xp': 100, 'loot_tier': 'uncommon'},
    'Zombie': {'hp': 22, 'ac': 8, 'attack': 3, 'damage': '1d6+1', 'xp': 50, 'loot_tier': 'common'},
    'Bandit': {'hp': 18, 'ac': 12, 'attack': 3, 'damage': '1d6+1', 'xp': 75, 'loot_tier': 'common'},
    'Ogre': {'hp': 59, 'ac': 11, 'attack': 6, 'damage': '2d8+4', 'xp': 450, 'loot_tier': 'rare'},
    'Troll': {'hp': 84, 'ac': 15, 'attack': 7, 'damage': '2d6+4', 'xp': 1800, 'loot_tier': 'rare'},
    'Dragon Wyrmling': {'hp': 75, 'ac': 17, 'attack': 7, 'damage': '2d10+4', 'xp': 2300, 'loot_tier': 'epic'}
}

def generate_loot(loot_tier, character_level):
    """Generate random equipment loot based on tier"""
    loot_chances = {
        'common': {'weapons': 0.3, 'armor': 0.3, 'accessories': 0.2},
        'uncommon': {'weapons': 0.4, 'armor': 0.4, 'accessories': 0.3},
        'rare': {'weapons': 0.5, 'armor': 0.5, 'accessories': 0.4},
        'epic': {'weapons': 0.7, 'armor': 0.7, 'accessories': 0.6}
    }

    chances = loot_chances.get(loot_tier, loot_chances['common'])
    loot = []

    for equip_type, chance in chances.items():
        if random.random() < chance:
            # Get equipment of appropriate level
            available = [name for name, stats in EQUIPMENT[equip_type].items()
                        if stats['level'] <= character_level + 1]
            if available:
                item = random.choice(available)
                loot.append({'type': equip_type, 'name': item, 'stats': EQUIPMENT[equip_type][item]})

    return loot

# ============================================================================
# FLASK ROUTES
# ============================================================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create_character', methods=['POST'])
def create_character():
    data = request.json

    # Roll ability scores (4d6 drop lowest)
    def roll_stat():
        rolls = sorted([random.randint(1, 6) for _ in range(4)])
        return sum(rolls[1:])  # Drop lowest

    base_stats = {
        'str': roll_stat(),
        'dex': roll_stat(),
        'con': roll_stat(),
        'int': roll_stat(),
        'wis': roll_stat(),
        'cha': roll_stat()
    }

    # Apply racial bonuses
    race = data['race']
    racial_bonuses = RACES[race]
    for stat, bonus in racial_bonuses.items():
        base_stats[stat] = base_stats.get(stat, 10) + bonus

    # Calculate modifiers
    def calc_modifier(score):
        return (score - 10) // 2

    modifiers = {stat: calc_modifier(score) for stat, score in base_stats.items()}

    # Get class info
    char_class = data['class']
    class_info = CLASSES[char_class]

    # Calculate HP
    con_mod = modifiers['con']
    max_hp = class_info['hit_die'] + con_mod

    # Starting equipment based on class
    if char_class in ['Fighter', 'Paladin']:
        starting_weapon = 'Iron Sword'
        starting_armor = 'Chain Mail'
    elif char_class in ['Ranger', 'Barbarian']:
        starting_weapon = 'Iron Sword'
        starting_armor = 'Leather Armor'
    elif char_class in ['Rogue', 'Bard']:
        starting_weapon = 'Rusty Dagger'
        starting_armor = 'Leather Armor'
    else:  # Wizard, Cleric
        starting_weapon = 'Rusty Dagger'
        starting_armor = 'Tattered Robes'

    character = {
        'name': data['name'],
        'race': race,
        'class': char_class,
        'level': 1,
        'xp': 0,
        'stats': base_stats,
        'modifiers': modifiers,
        'max_hp': max_hp,
        'current_hp': max_hp,
        'gold': 100,
        'inventory': ['Adventurer\'s Pack', 'Waterskin', 'Rations (5 days)'],
        'equipped': {
            'weapon': starting_weapon,
            'armor': starting_armor,
            'accessory': None
        },
        'equipment_inventory': []
    }

    # Calculate AC with starting armor
    character['ac'] = calculate_ac(character)

    # Initialize game state
    session['character'] = character
    session['game_state'] = {
        'current_scene': 'intro',
        'story_text': '',
        'combat_active': False,
        'turn_count': 0
    }

    return jsonify({
        'success': True,
        'character': character,
        'intro': StoryGenerator.generate_intro()
    })

@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    character = session.get('character', {})
    game_state = session.get('game_state', {})
    return jsonify({
        'character': character,
        'game_state': game_state
    })

@app.route('/api/action', methods=['POST'])
def perform_action():
    data = request.json
    choice = data['choice']
    character = session.get('character')
    game_state = session.get('game_state', {})

    if not character:
        return jsonify({'error': 'No character found'}), 400

    # Determine if combat occurs (40% chance in exploration)
    combat_chance = random.random()

    if combat_chance < 0.4 and not game_state.get('combat_active'):
        # Start combat
        enemy_name = random.choice(list(ENEMIES.keys()))
        enemy = ENEMIES[enemy_name].copy()

        game_state['combat_active'] = True
        game_state['enemy'] = enemy
        game_state['enemy_name'] = enemy_name
        game_state['enemy_current_hp'] = enemy['hp']

        session['game_state'] = game_state

        return jsonify({
            'result': 'combat_start',
            'message': f"A wild {enemy_name} appears!",
            'enemy': {
                'name': enemy_name,
                'hp': enemy['hp'],
                'current_hp': enemy['hp'],
                'ac': enemy['ac']
            },
            'choices': StoryGenerator.generate_choices('combat')
        })
    elif game_state.get('combat_active'):
        # Handle combat action
        result = handle_combat(choice, character, game_state)
        session['character'] = character
        session['game_state'] = game_state
        return jsonify(result)
    else:
        # Continue exploration
        story = StoryGenerator.generate_exploration()
        choices = StoryGenerator.generate_choices('exploration')

        # Random loot
        if random.random() < 0.3:
            gold_found = random.randint(5, 25)
            character['gold'] += gold_found
            story += f"\n\n💰 You found {gold_found} gold pieces!"
            session['character'] = character

        return jsonify({
            'result': 'exploration',
            'message': story,
            'choices': choices
        })

def handle_combat(choice, character, game_state):
    enemy_name = game_state['enemy_name']
    enemy = game_state['enemy']
    enemy_hp = game_state['enemy_current_hp']

    messages = []

    # Player attack with equipment bonuses
    char_class = character['class']
    primary_stat = CLASSES[char_class]['primary']
    attack_mod = character['modifiers'][primary_stat]

    # Add weapon attack bonus
    weapon_attack_bonus, weapon_damage = calculate_attack_damage(character)
    total_attack_mod = attack_mod + weapon_attack_bonus

    attack_roll = Dice.d20(total_attack_mod)
    messages.append(f"🎲 You rolled {attack_roll['chosen']} + {total_attack_mod} = {attack_roll['total']} to attack")

    if attack_roll['chosen'] == 20:
        # Critical hit - use weapon damage
        damage_dice = weapon_damage.split('d')
        dice_count = int(damage_dice[0]) * 2
        dice_sides = int(damage_dice[1].split('+')[0]) if '+' not in damage_dice[1] else int(damage_dice[1].split('+')[0])
        damage_roll = Dice.roll(dice_sides, dice_count, attack_mod)
        enemy_hp -= damage_roll['total']
        messages.append(f"⚔️ CRITICAL HIT! You deal {damage_roll['total']} damage!")
    elif attack_roll['total'] >= enemy['ac']:
        # Hit - use weapon damage
        damage_dice = weapon_damage.split('d')
        dice_count = int(damage_dice[0])
        dice_sides = int(damage_dice[1].split('+')[0]) if '+' not in damage_dice[1] else int(damage_dice[1])
        damage_roll = Dice.roll(dice_sides, dice_count, attack_mod)
        enemy_hp -= damage_roll['total']
        messages.append(f"⚔️ Hit! You deal {damage_roll['total']} damage!")
    else:
        messages.append(f"❌ Miss! Your attack fails to connect.")

    # Check if enemy defeated
    if enemy_hp <= 0:
        xp_gained = enemy['xp']
        gold_gained = random.randint(10, 50)
        character['xp'] += xp_gained
        character['gold'] += gold_gained

        messages.append(f"🏆 Victory! The {enemy_name} is defeated!")
        messages.append(f"📈 You gained {xp_gained} XP and {gold_gained} gold!")

        # Generate loot
        loot_tier = enemy.get('loot_tier', 'common')
        loot = generate_loot(loot_tier, character['level'])

        if loot:
            for item in loot:
                character['equipment_inventory'].append({
                    'type': item['type'],
                    'name': item['name']
                })
                rarity_icon = RARITY_COLORS.get(item['stats']['rarity'], '⚪')
                messages.append(f"✨ Found: {rarity_icon} {item['name']} ({item['stats']['rarity']} {item['type']})")

        # Check for level up
        xp_needed = character['level'] * 1000
        if character['xp'] >= xp_needed:
            character['level'] += 1
            hp_gain = random.randint(1, CLASSES[character['class']]['hit_die']) + character['modifiers']['con']
            character['max_hp'] += hp_gain
            character['current_hp'] = character['max_hp']
            messages.append(f"🎉 LEVEL UP! You are now level {character['level']}! Max HP increased by {hp_gain}!")

        game_state['combat_active'] = False
        game_state['enemy'] = None

        return {
            'result': 'combat_victory',
            'messages': messages,
            'character': character,
            'loot': loot if loot else [],
            'choices': StoryGenerator.generate_choices('exploration')
        }

    # Enemy attack
    enemy_attack_roll = Dice.d20(enemy['attack'])
    messages.append(f"🎲 {enemy_name} rolled {enemy_attack_roll['chosen']} + {enemy['attack']} = {enemy_attack_roll['total']} to attack")

    if enemy_attack_roll['total'] >= character['ac']:
        damage_dice = enemy['damage'].split('d')
        dice_count = int(damage_dice[0])
        dice_sides = int(damage_dice[1].split('+')[0])
        damage_bonus = int(damage_dice[1].split('+')[1]) if '+' in damage_dice[1] else 0
        damage_roll = Dice.roll(dice_sides, dice_count, damage_bonus)
        character['current_hp'] -= damage_roll['total']
        messages.append(f"💥 {enemy_name} hits you for {damage_roll['total']} damage!")

        if character['current_hp'] <= 0:
            character['current_hp'] = 0
            return {
                'result': 'defeat',
                'messages': messages + ["💀 You have been defeated..."],
                'character': character
            }
    else:
        messages.append(f"🛡️ {enemy_name}'s attack misses!")

    game_state['enemy_current_hp'] = enemy_hp

    return {
        'result': 'combat_continue',
        'messages': messages,
        'character': character,
        'enemy': {
            'name': enemy_name,
            'hp': enemy['hp'],
            'current_hp': enemy_hp,
            'ac': enemy['ac']
        },
        'choices': StoryGenerator.generate_choices('combat')
    }

@app.route('/api/rest', methods=['POST'])
def short_rest():
    character = session.get('character')
    if not character:
        return jsonify({'error': 'No character found'}), 400

    # Heal some HP
    hit_die = CLASSES[character['class']]['hit_die']
    heal_roll = Dice.roll(hit_die, 1, character['modifiers']['con'])
    heal_amount = min(heal_roll['total'], character['max_hp'] - character['current_hp'])
    character['current_hp'] += heal_amount

    session['character'] = character

    return jsonify({
        'success': True,
        'message': f"You rest and recover {heal_amount} HP",
        'character': character
    })

@app.route('/api/shop', methods=['GET'])
def get_shop():
    """Get shop inventory based on character level"""
    character = session.get('character')
    if not character:
        return jsonify({'error': 'No character found'}), 400

    level = character['level']

    # Filter equipment by character level
    shop_inventory = {
        'weapons': [],
        'armor': [],
        'accessories': []
    }

    for equip_type in ['weapons', 'armor', 'accessories']:
        for name, stats in EQUIPMENT[equip_type].items():
            if stats['level'] <= level + 2:  # Show items slightly above level
                item_data = stats.copy()
                item_data['name'] = name
                item_data['rarity_icon'] = RARITY_COLORS.get(stats['rarity'], '⚪')
                shop_inventory[equip_type].append(item_data)

    return jsonify({
        'shop': shop_inventory,
        'gold': character['gold']
    })

@app.route('/api/buy', methods=['POST'])
def buy_item():
    """Purchase an item from the shop"""
    character = session.get('character')
    if not character:
        return jsonify({'error': 'No character found'}), 400

    data = request.json
    item_type = data['type']
    item_name = data['name']

    if item_type not in EQUIPMENT or item_name not in EQUIPMENT[item_type]:
        return jsonify({'error': 'Item not found'}), 404

    item = EQUIPMENT[item_type][item_name]
    price = item['price']

    if character['gold'] < price:
        return jsonify({'error': 'Not enough gold'}), 400

    # Deduct gold and add item to inventory
    character['gold'] -= price
    character['equipment_inventory'].append({
        'type': item_type,
        'name': item_name
    })

    session['character'] = character

    return jsonify({
        'success': True,
        'message': f"Purchased {item_name} for {price} gold",
        'character': character
    })

@app.route('/api/equip', methods=['POST'])
def equip_item():
    """Equip an item from inventory"""
    character = session.get('character')
    if not character:
        return jsonify({'error': 'No character found'}), 400

    data = request.json
    item_type = data['type']
    item_name = data['name']

    # Check if item is in inventory
    item_in_inventory = any(
        item['name'] == item_name and item['type'] == item_type
        for item in character['equipment_inventory']
    )

    if not item_in_inventory:
        return jsonify({'error': 'Item not in inventory'}), 404

    # Unequip current item (put back in inventory)
    if character['equipped'].get(item_type):
        old_item = character['equipped'][item_type]
        if old_item:
            character['equipment_inventory'].append({
                'type': item_type,
                'name': old_item
            })

    # Equip new item (remove from inventory)
    character['equipped'][item_type] = item_name
    character['equipment_inventory'] = [
        item for item in character['equipment_inventory']
        if not (item['name'] == item_name and item['type'] == item_type)
    ]

    # Recalculate stats
    character['ac'] = calculate_ac(character)

    # Recalculate modifiers with accessory bonuses
    total_stats = calculate_total_stats(character)
    def calc_modifier(score):
        return (score - 10) // 2
    character['modifiers'] = {stat: calc_modifier(score) for stat, score in total_stats.items()}

    session['character'] = character

    return jsonify({
        'success': True,
        'message': f"Equipped {item_name}",
        'character': character
    })

@app.route('/api/sell', methods=['POST'])
def sell_item():
    """Sell an item from inventory"""
    character = session.get('character')
    if not character:
        return jsonify({'error': 'No character found'}), 400

    data = request.json
    item_type = data['type']
    item_name = data['name']

    # Check if item is in inventory
    item_in_inventory = any(
        item['name'] == item_name and item['type'] == item_type
        for item in character['equipment_inventory']
    )

    if not item_in_inventory:
        return jsonify({'error': 'Item not in inventory'}), 404

    # Remove item and add gold (sell for 50% of price)
    if item_type in EQUIPMENT and item_name in EQUIPMENT[item_type]:
        sell_price = EQUIPMENT[item_type][item_name]['price'] // 2
        character['gold'] += sell_price

        character['equipment_inventory'] = [
            item for item in character['equipment_inventory']
            if not (item['name'] == item_name and item['type'] == item_type)
        ]

        session['character'] = character

        return jsonify({
            'success': True,
            'message': f"Sold {item_name} for {sell_price} gold",
            'character': character
        })

    return jsonify({'error': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
