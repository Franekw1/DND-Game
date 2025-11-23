#!/usr/bin/env python3
"""
D&D 5e Style Interactive Web Game
==================================
Flask backend for the tabletop RPG experience.
"""

from flask import Flask, render_template, request, jsonify, session
import random
import uuid
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ============================================================================
# DICE ROLLING SYSTEM (5e Style)
# ============================================================================

class Dice:
    @staticmethod
    def roll(sides: int, count: int = 1) -> Dict:
        rolls = [random.randint(1, sides) for _ in range(count)]
        return {
            'rolls': rolls,
            'total': sum(rolls),
            'dice': f"{count}d{sides}"
        }

    @staticmethod
    def d20(modifier: int = 0, advantage: bool = False, disadvantage: bool = False) -> Dict:
        if advantage:
            rolls = [random.randint(1, 20), random.randint(1, 20)]
            result = max(rolls)
            roll_type = "Advantage"
        elif disadvantage:
            rolls = [random.randint(1, 20), random.randint(1, 20)]
            result = min(rolls)
            roll_type = "Disadvantage"
        else:
            rolls = [random.randint(1, 20)]
            result = rolls[0]
            roll_type = "Normal"

        is_crit = result == 20
        is_fumble = result == 1

        return {
            'rolls': rolls,
            'natural': result,
            'modifier': modifier,
            'total': result + modifier,
            'roll_type': roll_type,
            'is_crit': is_crit,
            'is_fumble': is_fumble
        }

    @staticmethod
    def stat_roll() -> Dict:
        """Roll 4d6, drop lowest"""
        rolls = [random.randint(1, 6) for _ in range(4)]
        sorted_rolls = sorted(rolls, reverse=True)
        kept = sorted_rolls[:3]
        dropped = sorted_rolls[3]
        return {
            'all_rolls': rolls,
            'kept': kept,
            'dropped': dropped,
            'total': sum(kept)
        }

# ============================================================================
# GAME DATA
# ============================================================================

RACES = {
    'human': {
        'name': 'Human',
        'bonuses': {'str': 1, 'dex': 1, 'con': 1, 'int': 1, 'wis': 1, 'cha': 1},
        'traits': ['Versatile', 'Extra Language'],
        'description': 'Adaptable and ambitious, humans are the most common race in the realms.'
    },
    'elf': {
        'name': 'Elf',
        'bonuses': {'dex': 2, 'int': 1},
        'traits': ['Darkvision', 'Fey Ancestry', 'Trance'],
        'description': 'Graceful and long-lived, elves are masters of magic and archery.'
    },
    'dwarf': {
        'name': 'Dwarf',
        'bonuses': {'con': 2, 'str': 1},
        'traits': ['Darkvision', 'Dwarven Resilience', 'Stonecunning'],
        'description': 'Stout and sturdy, dwarves are master craftsmen and fierce warriors.'
    },
    'halfling': {
        'name': 'Halfling',
        'bonuses': {'dex': 2, 'cha': 1},
        'traits': ['Lucky', 'Brave', 'Nimble'],
        'description': 'Small but resourceful, halflings are known for their luck and courage.'
    },
    'half_orc': {
        'name': 'Half-Orc',
        'bonuses': {'str': 2, 'con': 1},
        'traits': ['Darkvision', 'Relentless Endurance', 'Savage Attacks'],
        'description': 'Powerful and intimidating, half-orcs combine human cunning with orcish strength.'
    },
    'gnome': {
        'name': 'Gnome',
        'bonuses': {'int': 2, 'con': 1},
        'traits': ['Darkvision', 'Gnome Cunning', 'Artificer\'s Lore'],
        'description': 'Inventive and curious, gnomes delight in discovery and creation.'
    },
    'tiefling': {
        'name': 'Tiefling',
        'bonuses': {'cha': 2, 'int': 1},
        'traits': ['Darkvision', 'Hellish Resistance', 'Infernal Legacy'],
        'description': 'Bearing the mark of infernal heritage, tieflings face prejudice but wield dark powers.'
    },
    'dragonborn': {
        'name': 'Dragonborn',
        'bonuses': {'str': 2, 'cha': 1},
        'traits': ['Draconic Ancestry', 'Breath Weapon', 'Damage Resistance'],
        'description': 'Proud dragon-blooded warriors who can unleash devastating breath attacks.'
    }
}

CLASSES = {
    'fighter': {
        'name': 'Fighter',
        'hit_die': 10,
        'primary_stat': 'str',
        'saves': ['str', 'con'],
        'armor': ['light', 'medium', 'heavy', 'shields'],
        'weapons': ['simple', 'martial'],
        'description': 'Masters of martial combat, fighters excel with weapons and armor.',
        'abilities': ['Second Wind', 'Action Surge'],
        'starting_equipment': ['Longsword', 'Shield', 'Chain Mail', 'Handaxe x2']
    },
    'wizard': {
        'name': 'Wizard',
        'hit_die': 6,
        'primary_stat': 'int',
        'saves': ['int', 'wis'],
        'armor': [],
        'weapons': ['daggers', 'darts', 'slings', 'quarterstaffs', 'light crossbows'],
        'description': 'Scholarly magic-users who command arcane forces through study.',
        'abilities': ['Arcane Recovery', 'Spellcasting'],
        'starting_equipment': ['Quarterstaff', 'Spellbook', 'Component Pouch', 'Scholar\'s Pack'],
        'spells': ['Fire Bolt', 'Magic Missile', 'Shield', 'Sleep']
    },
    'rogue': {
        'name': 'Rogue',
        'hit_die': 8,
        'primary_stat': 'dex',
        'saves': ['dex', 'int'],
        'armor': ['light'],
        'weapons': ['simple', 'hand crossbows', 'longswords', 'rapiers', 'shortswords'],
        'description': 'Skilled in stealth and precision, rogues strike from the shadows.',
        'abilities': ['Sneak Attack', 'Cunning Action', 'Thieves\' Cant'],
        'starting_equipment': ['Rapier', 'Shortbow', 'Leather Armor', 'Thieves\' Tools', 'Burglar\'s Pack']
    },
    'cleric': {
        'name': 'Cleric',
        'hit_die': 8,
        'primary_stat': 'wis',
        'saves': ['wis', 'cha'],
        'armor': ['light', 'medium', 'shields'],
        'weapons': ['simple'],
        'description': 'Divine spellcasters who channel the power of their deity.',
        'abilities': ['Spellcasting', 'Channel Divinity', 'Turn Undead'],
        'starting_equipment': ['Mace', 'Scale Mail', 'Shield', 'Holy Symbol', 'Priest\'s Pack'],
        'spells': ['Sacred Flame', 'Cure Wounds', 'Bless', 'Guiding Bolt']
    },
    'ranger': {
        'name': 'Ranger',
        'hit_die': 10,
        'primary_stat': 'dex',
        'saves': ['str', 'dex'],
        'armor': ['light', 'medium', 'shields'],
        'weapons': ['simple', 'martial'],
        'description': 'Warriors of the wilderness, skilled in tracking and survival.',
        'abilities': ['Favored Enemy', 'Natural Explorer', 'Spellcasting'],
        'starting_equipment': ['Longbow', 'Quiver', 'Two Shortswords', 'Leather Armor', 'Explorer\'s Pack']
    },
    'barbarian': {
        'name': 'Barbarian',
        'hit_die': 12,
        'primary_stat': 'str',
        'saves': ['str', 'con'],
        'armor': ['light', 'medium', 'shields'],
        'weapons': ['simple', 'martial'],
        'description': 'Fierce warriors who channel primal rage in battle.',
        'abilities': ['Rage', 'Unarmored Defense', 'Reckless Attack'],
        'starting_equipment': ['Greataxe', 'Handaxe x2', 'Explorer\'s Pack', 'Javelins x4']
    },
    'paladin': {
        'name': 'Paladin',
        'hit_die': 10,
        'primary_stat': 'str',
        'saves': ['wis', 'cha'],
        'armor': ['light', 'medium', 'heavy', 'shields'],
        'weapons': ['simple', 'martial'],
        'description': 'Holy warriors bound by sacred oaths to fight evil.',
        'abilities': ['Divine Sense', 'Lay on Hands', 'Divine Smite'],
        'starting_equipment': ['Longsword', 'Shield', 'Chain Mail', 'Holy Symbol', 'Priest\'s Pack']
    },
    'bard': {
        'name': 'Bard',
        'hit_die': 8,
        'primary_stat': 'cha',
        'saves': ['dex', 'cha'],
        'armor': ['light'],
        'weapons': ['simple', 'hand crossbows', 'longswords', 'rapiers', 'shortswords'],
        'description': 'Magical performers who weave spells through music and words.',
        'abilities': ['Spellcasting', 'Bardic Inspiration', 'Jack of All Trades'],
        'starting_equipment': ['Rapier', 'Lute', 'Leather Armor', 'Diplomat\'s Pack'],
        'spells': ['Vicious Mockery', 'Healing Word', 'Thunderwave', 'Charm Person']
    }
}

STORY_TEMPLATES = {
    'intro': [
        "The ancient tavern known as The Dragon's Flagon buzzes with whispered rumors. A hooded figure approaches your table, sliding a worn map across the ale-stained wood. 'The Tomb of Forgotten Kings,' they rasp. 'Riches beyond measure... if you survive.'",
        "Thunder crashes as you shelter in a roadside shrine. Lightning illuminates a desperate messenger who collapses at your feet, clutching a blood-stained scroll. With their dying breath, they whisper: 'The dark ones... they've found the portal...'",
        "The king's herald reads the royal proclamation in the town square: 'Brave adventurers sought! The princess has been taken by the dragon Scorax. A kingdom's ransom awaits those who return her safely.'",
        "You awaken in a dungeon cell, your memories foggy. Strange runes glow on your arms, and distant screams echo through stone corridors. A spectral voice whispers: 'The ritual begins at midnight. You must escape... or become the sacrifice.'"
    ],
    'exploration': [
        "The corridor opens into a vast chamber. {description} What do you do?",
        "You carefully advance deeper into the {location}. {description} Your instincts tell you danger lurks nearby.",
        "After navigating treacherous terrain, you discover {description} The air feels charged with ancient magic.",
        "The path splits before you. {description} Each direction seems to hold different promises and perils."
    ],
    'combat_intro': [
        "From the shadows, {enemy} emerge! Roll for initiative!",
        "Your presence has been detected! {enemy} block your path, weapons drawn!",
        "An ambush! {enemy} spring from hiding, hungry for blood!",
        "The {enemy} regard you with hostile intent. Combat is inevitable!"
    ],
    'victory': [
        "The last enemy falls, and silence returns to the chamber. You catch your breath, victorious.",
        "Your foes lie defeated. The thrill of battle fades, replaced by the satisfaction of survival.",
        "With a final blow, the combat ends. You stand triumphant among your fallen enemies."
    ],
    'treasure': [
        "Among the remains, you discover a chest containing {gold} gold pieces and {item}!",
        "A hidden compartment reveals {gold} gold and a mysterious {item}.",
        "The defeated foe carried {gold} gold pieces. You also find {item} nearby."
    ]
}

LOCATIONS = [
    "crumbling crypt", "torch-lit corridor", "ancient library", "sacrificial chamber",
    "underground river", "crystal cavern", "abandoned mine", "haunted chapel",
    "dragon's lair", "wizard's sanctum", "thieves' guild hideout", "cursed tomb"
]

DESCRIPTIONS = [
    "Ancient pillars support a ceiling lost in darkness. Cobwebs thick as curtains hang between forgotten statues.",
    "Bioluminescent fungi cast an eerie blue glow across damp stone walls covered in strange writings.",
    "The skeletal remains of past adventurers serve as grim warnings. Their rusted equipment lies scattered about.",
    "A massive stone door bears symbols of a long-dead god. The mechanisms look intact but require solving.",
    "Underground pools of crystal-clear water reflect torchlight. Something large moves beneath the surface.",
    "Treasure chests line the walls, but your experience tells you such easy riches often come with deadly traps.",
    "An altar to dark powers dominates the room. Fresh blood stains suggest recent... activities.",
    "Massive chains hang from the ceiling, attached to a cage containing... something that watches you."
]

ENEMIES = {
    'goblin': {'name': 'Goblin', 'hp': 7, 'ac': 15, 'attack': 4, 'damage': '1d6+2', 'xp': 50},
    'skeleton': {'name': 'Skeleton', 'hp': 13, 'ac': 13, 'attack': 4, 'damage': '1d6+2', 'xp': 50},
    'orc': {'name': 'Orc', 'hp': 15, 'ac': 13, 'attack': 5, 'damage': '1d12+3', 'xp': 100},
    'zombie': {'name': 'Zombie', 'hp': 22, 'ac': 8, 'attack': 3, 'damage': '1d6+1', 'xp': 50},
    'wolf': {'name': 'Dire Wolf', 'hp': 37, 'ac': 14, 'attack': 5, 'damage': '2d6+3', 'xp': 200},
    'ogre': {'name': 'Ogre', 'hp': 59, 'ac': 11, 'attack': 6, 'damage': '2d8+4', 'xp': 450},
    'troll': {'name': 'Troll', 'hp': 84, 'ac': 15, 'attack': 7, 'damage': '2d6+4', 'xp': 1800},
    'wraith': {'name': 'Wraith', 'hp': 67, 'ac': 13, 'attack': 6, 'damage': '3d6', 'xp': 1800},
    'dragon_wyrmling': {'name': 'Young Dragon', 'hp': 75, 'ac': 17, 'attack': 7, 'damage': '2d10+4', 'xp': 2900}
}

TREASURES = [
    "a Potion of Healing", "a Scroll of Fireball", "a +1 Dagger", "an Amulet of Protection",
    "a Ring of Feather Falling", "Boots of Elvenkind", "a Cloak of Invisibility",
    "a Wand of Magic Missiles", "Gauntlets of Ogre Power", "a Bag of Holding"
]

# ============================================================================
# GAME STATE MANAGEMENT
# ============================================================================

def get_modifier(score: int) -> int:
    return (score - 10) // 2

def create_character(name: str, race: str, char_class: str, stats: Dict[str, int]) -> Dict:
    race_data = RACES[race]
    class_data = CLASSES[char_class]

    # Apply racial bonuses
    for stat, bonus in race_data['bonuses'].items():
        stats[stat] = stats.get(stat, 10) + bonus

    # Calculate HP
    con_mod = get_modifier(stats['con'])
    max_hp = class_data['hit_die'] + con_mod

    # Calculate AC (base 10 + dex modifier, simplified)
    dex_mod = get_modifier(stats['dex'])
    base_ac = 10 + dex_mod
    if 'heavy' in class_data['armor']:
        base_ac = 16  # Chain mail equivalent
    elif 'medium' in class_data['armor']:
        base_ac = 14 + min(dex_mod, 2)  # Scale mail equivalent
    elif 'light' in class_data['armor']:
        base_ac = 11 + dex_mod  # Leather armor

    return {
        'name': name,
        'race': race,
        'race_name': race_data['name'],
        'char_class': char_class,
        'class_name': class_data['name'],
        'level': 1,
        'xp': 0,
        'stats': stats,
        'max_hp': max_hp,
        'current_hp': max_hp,
        'ac': base_ac,
        'hit_die': class_data['hit_die'],
        'traits': race_data['traits'],
        'abilities': class_data['abilities'],
        'equipment': class_data['starting_equipment'].copy(),
        'spells': class_data.get('spells', []),
        'gold': random.randint(10, 50),
        'primary_stat': class_data['primary_stat']
    }

def generate_choices(game_state: Dict) -> List[Dict]:
    """Generate 4 contextual choices based on current game state"""
    choices = []
    scene_type = game_state.get('scene_type', 'exploration')

    if scene_type == 'combat':
        char = game_state['character']
        choices = [
            {'id': 1, 'text': f"Attack with your weapon", 'type': 'attack'},
            {'id': 2, 'text': "Attempt to dodge and defend", 'type': 'defend'},
            {'id': 3, 'text': "Try to flee from combat", 'type': 'flee'},
        ]
        if char['spells']:
            choices.append({'id': 4, 'text': f"Cast {random.choice(char['spells'])}", 'type': 'spell'})
        else:
            choices.append({'id': 4, 'text': "Use a special ability", 'type': 'ability'})

    elif scene_type == 'exploration':
        choices = [
            {'id': 1, 'text': "Search the area carefully for hidden secrets", 'type': 'search'},
            {'id': 2, 'text': "Proceed cautiously deeper into the dungeon", 'type': 'advance'},
            {'id': 3, 'text': "Check for traps before moving forward", 'type': 'trap_check'},
            {'id': 4, 'text': "Take a short rest to recover (spend Hit Die)", 'type': 'rest'},
        ]

    elif scene_type == 'encounter':
        choices = [
            {'id': 1, 'text': "Approach peacefully and attempt diplomacy", 'type': 'diplomacy'},
            {'id': 2, 'text': "Ready your weapon and prepare for combat", 'type': 'ready_combat'},
            {'id': 3, 'text': "Try to sneak past unnoticed", 'type': 'stealth'},
            {'id': 4, 'text': "Observe from a distance to learn more", 'type': 'observe'},
        ]

    elif scene_type == 'puzzle':
        choices = [
            {'id': 1, 'text': "Examine the puzzle mechanism closely", 'type': 'examine'},
            {'id': 2, 'text': "Try to solve it with brute force", 'type': 'force'},
            {'id': 3, 'text': "Look for clues in the surrounding area", 'type': 'search_clues'},
            {'id': 4, 'text': "Use your class abilities to bypass it", 'type': 'ability'},
        ]

    return choices

def generate_scene(game_state: Dict) -> Dict:
    """Generate a new scene based on game progress"""
    depth = game_state.get('dungeon_depth', 1)

    # Determine scene type based on probability and depth
    roll = random.randint(1, 100)
    if roll <= 40:
        scene_type = 'exploration'
    elif roll <= 70:
        scene_type = 'combat'
    elif roll <= 85:
        scene_type = 'encounter'
    else:
        scene_type = 'puzzle'

    location = random.choice(LOCATIONS)
    description = random.choice(DESCRIPTIONS)

    scene = {
        'type': scene_type,
        'location': location,
        'description': description,
        'depth': depth
    }

    if scene_type == 'combat':
        # Scale enemies based on depth
        if depth <= 2:
            enemy_pool = ['goblin', 'skeleton', 'zombie']
        elif depth <= 4:
            enemy_pool = ['orc', 'wolf', 'skeleton']
        elif depth <= 6:
            enemy_pool = ['ogre', 'troll', 'wraith']
        else:
            enemy_pool = ['troll', 'wraith', 'dragon_wyrmling']

        enemy_type = random.choice(enemy_pool)
        enemy_count = min(depth, random.randint(1, 3))

        enemies = []
        for i in range(enemy_count):
            enemy = ENEMIES[enemy_type].copy()
            enemy['id'] = i
            enemy['current_hp'] = enemy['hp']
            enemies.append(enemy)

        scene['enemies'] = enemies

    return scene

def process_action(game_state: Dict, action: Dict) -> Dict:
    """Process player action and return result"""
    action_type = action.get('type', 'custom')
    char = game_state['character']
    result = {'success': False, 'narrative': '', 'rolls': [], 'damage': 0, 'effects': []}

    if action_type == 'attack':
        # Attack roll
        primary_stat = char['primary_stat']
        modifier = get_modifier(char['stats'][primary_stat])
        prof_bonus = 2  # Level 1
        attack_roll = Dice.d20(modifier + prof_bonus)
        result['rolls'].append({'type': 'Attack', 'data': attack_roll})

        enemies = game_state.get('enemies', [])
        if enemies:
            target = enemies[0]  # Attack first enemy
            if attack_roll['is_crit']:
                # Critical hit - double dice
                damage_roll = Dice.roll(8, 2)  # Assuming d8 weapon
                damage_roll['total'] += modifier
                result['damage'] = damage_roll['total']
                result['narrative'] = f"CRITICAL HIT! You strike {target['name']} for {result['damage']} damage!"
                result['success'] = True
            elif attack_roll['total'] >= target['ac']:
                damage_roll = Dice.roll(8, 1)
                damage_roll['total'] += modifier
                result['damage'] = damage_roll['total']
                result['rolls'].append({'type': 'Damage', 'data': damage_roll})
                result['narrative'] = f"You hit {target['name']} for {result['damage']} damage!"
                result['success'] = True
            else:
                result['narrative'] = f"Your attack misses {target['name']}! (Rolled {attack_roll['total']} vs AC {target['ac']})"

    elif action_type == 'defend':
        result['narrative'] = "You take a defensive stance, preparing to dodge incoming attacks."
        result['effects'].append({'type': 'ac_bonus', 'value': 2, 'duration': 1})
        result['success'] = True

    elif action_type == 'flee':
        dex_mod = get_modifier(char['stats']['dex'])
        flee_roll = Dice.d20(dex_mod)
        result['rolls'].append({'type': 'Athletics/Acrobatics', 'data': flee_roll})
        if flee_roll['total'] >= 12:
            result['narrative'] = "You successfully disengage and escape from combat!"
            result['effects'].append({'type': 'flee', 'success': True})
            result['success'] = True
        else:
            result['narrative'] = "You fail to escape! The enemies block your retreat."

    elif action_type == 'spell':
        int_mod = get_modifier(char['stats']['int'])
        wis_mod = get_modifier(char['stats']['wis'])
        cha_mod = get_modifier(char['stats']['cha'])
        spell_mod = max(int_mod, wis_mod, cha_mod)

        spell_roll = Dice.d20(spell_mod + 2)
        result['rolls'].append({'type': 'Spell Attack', 'data': spell_roll})

        enemies = game_state.get('enemies', [])
        if enemies and spell_roll['total'] >= enemies[0]['ac']:
            damage_roll = Dice.roll(10, 1)  # Cantrip damage
            damage_roll['total'] += spell_mod
            result['damage'] = damage_roll['total']
            result['rolls'].append({'type': 'Spell Damage', 'data': damage_roll})
            result['narrative'] = f"Your spell strikes true, dealing {result['damage']} damage!"
            result['success'] = True
        else:
            result['narrative'] = "Your spell fizzles or misses its mark!"

    elif action_type == 'search':
        wis_mod = get_modifier(char['stats']['wis'])
        perception_roll = Dice.d20(wis_mod)
        result['rolls'].append({'type': 'Perception', 'data': perception_roll})

        if perception_roll['total'] >= 15:
            treasure = random.choice(TREASURES)
            gold = random.randint(10, 50)
            result['narrative'] = f"Your keen eyes spot something hidden! You find {gold} gold and {treasure}!"
            result['effects'].append({'type': 'loot', 'gold': gold, 'item': treasure})
            result['success'] = True
        elif perception_roll['total'] >= 10:
            gold = random.randint(5, 20)
            result['narrative'] = f"You find a small cache of {gold} gold coins."
            result['effects'].append({'type': 'loot', 'gold': gold})
            result['success'] = True
        else:
            result['narrative'] = "You search thoroughly but find nothing of interest."

    elif action_type == 'advance':
        result['narrative'] = "You press onward, venturing deeper into the unknown..."
        result['effects'].append({'type': 'advance'})
        result['success'] = True

    elif action_type == 'trap_check':
        int_mod = get_modifier(char['stats']['int'])
        investigation_roll = Dice.d20(int_mod)
        result['rolls'].append({'type': 'Investigation', 'data': investigation_roll})

        trap_present = random.random() < 0.3
        if trap_present:
            if investigation_roll['total'] >= 13:
                result['narrative'] = "You spot a cunningly hidden trap! You carefully disarm it."
                result['success'] = True
            else:
                damage = Dice.roll(6, 2)
                result['damage'] = -damage['total']  # Negative = damage to player
                result['narrative'] = f"You trigger a hidden trap! You take {damage['total']} damage!"
                result['rolls'].append({'type': 'Trap Damage', 'data': damage})
        else:
            result['narrative'] = "The area appears to be safe. No traps detected."
            result['success'] = True

    elif action_type == 'rest':
        hit_die = char['hit_die']
        con_mod = get_modifier(char['stats']['con'])
        heal_roll = Dice.roll(hit_die, 1)
        healing = heal_roll['total'] + con_mod
        result['rolls'].append({'type': 'Hit Die', 'data': heal_roll})
        result['narrative'] = f"You take a short rest, recovering {healing} hit points."
        result['effects'].append({'type': 'heal', 'amount': healing})
        result['success'] = True

    elif action_type == 'diplomacy':
        cha_mod = get_modifier(char['stats']['cha'])
        persuasion_roll = Dice.d20(cha_mod)
        result['rolls'].append({'type': 'Persuasion', 'data': persuasion_roll})

        if persuasion_roll['total'] >= 15:
            result['narrative'] = "Your words find their mark. The encounter ends peacefully!"
            result['effects'].append({'type': 'peaceful_resolution'})
            result['success'] = True
        else:
            result['narrative'] = "Your diplomatic efforts fail. They seem unimpressed..."
            result['effects'].append({'type': 'combat_start'})

    elif action_type == 'stealth':
        dex_mod = get_modifier(char['stats']['dex'])
        stealth_roll = Dice.d20(dex_mod)
        result['rolls'].append({'type': 'Stealth', 'data': stealth_roll})

        if stealth_roll['total'] >= 14:
            result['narrative'] = "Moving like a shadow, you slip past undetected!"
            result['effects'].append({'type': 'stealth_success'})
            result['success'] = True
        else:
            result['narrative'] = "You step on a loose stone! You've been spotted!"
            result['effects'].append({'type': 'combat_start'})

    else:  # Custom action
        # Generic skill check for custom actions
        relevant_stat = 'int' if 'think' in action.get('text', '').lower() else 'wis'
        modifier = get_modifier(char['stats'][relevant_stat])
        check_roll = Dice.d20(modifier)
        result['rolls'].append({'type': 'Ability Check', 'data': check_roll})

        if check_roll['total'] >= 12:
            result['narrative'] = "Your creative approach succeeds!"
            result['success'] = True
        else:
            result['narrative'] = "Your attempt doesn't quite work as planned..."

    return result

def enemy_turn(game_state: Dict) -> Dict:
    """Process enemy attacks"""
    enemies = game_state.get('enemies', [])
    char = game_state['character']
    result = {'attacks': [], 'total_damage': 0, 'narrative': ''}

    for enemy in enemies:
        if enemy['current_hp'] <= 0:
            continue

        attack_roll = Dice.d20(enemy['attack'])

        attack_result = {
            'enemy': enemy['name'],
            'roll': attack_roll,
            'hit': False,
            'damage': 0
        }

        if attack_roll['is_crit']:
            # Parse damage dice and double
            damage = Dice.roll(6, 2)  # Simplified
            attack_result['damage'] = damage['total']
            attack_result['hit'] = True
            attack_result['crit'] = True
        elif attack_roll['total'] >= char['ac']:
            damage = Dice.roll(6, 1)
            attack_result['damage'] = damage['total']
            attack_result['hit'] = True

        result['attacks'].append(attack_result)
        result['total_damage'] += attack_result['damage']

    if result['total_damage'] > 0:
        result['narrative'] = f"The enemies strike back, dealing {result['total_damage']} total damage!"
    else:
        result['narrative'] = "The enemies' attacks miss!"

    return result

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/races')
def get_races():
    return jsonify(RACES)

@app.route('/api/classes')
def get_classes():
    return jsonify(CLASSES)

@app.route('/api/roll_stats', methods=['POST'])
def roll_stats():
    stats = {}
    rolls_data = {}
    for stat in ['str', 'dex', 'con', 'int', 'wis', 'cha']:
        roll_result = Dice.stat_roll()
        stats[stat] = roll_result['total']
        rolls_data[stat] = roll_result
    return jsonify({'stats': stats, 'rolls': rolls_data})

@app.route('/api/create_character', methods=['POST'])
def api_create_character():
    data = request.json
    character = create_character(
        data['name'],
        data['race'],
        data['char_class'],
        data['stats']
    )

    # Initialize game state
    session['game_state'] = {
        'character': character,
        'scene_type': 'intro',
        'dungeon_depth': 1,
        'turn': 0,
        'combat_active': False,
        'enemies': [],
        'game_log': []
    }

    # Generate intro story
    intro = random.choice(STORY_TEMPLATES['intro'])
    session['game_state']['current_narrative'] = intro
    session['game_state']['game_log'].append({'type': 'story', 'text': intro})

    return jsonify({
        'character': character,
        'narrative': intro,
        'choices': generate_choices({'scene_type': 'exploration', 'character': character})
    })

@app.route('/api/action', methods=['POST'])
def handle_action():
    data = request.json
    game_state = session.get('game_state', {})

    if not game_state:
        return jsonify({'error': 'No active game session'}), 400

    action = data.get('action', {})

    # Process player action
    result = process_action(game_state, action)

    # Apply effects
    char = game_state['character']
    for effect in result.get('effects', []):
        if effect['type'] == 'heal':
            char['current_hp'] = min(char['max_hp'], char['current_hp'] + effect['amount'])
        elif effect['type'] == 'loot':
            char['gold'] += effect.get('gold', 0)
            if 'item' in effect:
                char['equipment'].append(effect['item'])
        elif effect['type'] == 'advance':
            game_state['dungeon_depth'] += 1

    # Handle damage to enemies
    if result['damage'] > 0 and game_state.get('enemies'):
        game_state['enemies'][0]['current_hp'] -= result['damage']
        if game_state['enemies'][0]['current_hp'] <= 0:
            defeated_enemy = game_state['enemies'].pop(0)
            char['xp'] += defeated_enemy['xp']
            result['narrative'] += f" {defeated_enemy['name']} is defeated! (+{defeated_enemy['xp']} XP)"

            # Check for level up (simplified)
            if char['xp'] >= char['level'] * 300:
                char['level'] += 1
                hp_increase = Dice.roll(char['hit_die'], 1)['total'] + get_modifier(char['stats']['con'])
                char['max_hp'] += hp_increase
                char['current_hp'] += hp_increase
                result['narrative'] += f" LEVEL UP! You are now level {char['level']}!"

    # Handle damage to player from traps
    if result['damage'] < 0:
        char['current_hp'] += result['damage']  # damage is negative

    # Enemy turn if in combat
    enemy_result = None
    if game_state.get('enemies') and game_state.get('scene_type') == 'combat':
        enemy_result = enemy_turn(game_state)
        char['current_hp'] -= enemy_result['total_damage']

    # Check for death
    if char['current_hp'] <= 0:
        return jsonify({
            'narrative': result['narrative'] + "\n\nYou have fallen in battle... GAME OVER",
            'rolls': result['rolls'],
            'character': char,
            'game_over': True,
            'enemy_result': enemy_result
        })

    # Generate next scene if needed
    next_narrative = ""
    if not game_state.get('enemies') and game_state.get('scene_type') == 'combat':
        # Combat ended - victory
        victory = random.choice(STORY_TEMPLATES['victory'])
        gold = random.randint(10, 30) * game_state['dungeon_depth']
        treasure = random.choice(TREASURES)
        loot_text = f" You find {gold} gold and {treasure}!"
        char['gold'] += gold
        char['equipment'].append(treasure)
        next_narrative = victory + loot_text
        game_state['scene_type'] = 'exploration'
        game_state['combat_active'] = False

    if 'advance' in [e['type'] for e in result.get('effects', [])]:
        # Generate new scene
        scene = generate_scene(game_state)
        game_state['scene_type'] = scene['type']

        if scene['type'] == 'combat':
            game_state['enemies'] = scene['enemies']
            game_state['combat_active'] = True
            enemy_names = ', '.join([e['name'] for e in scene['enemies']])
            combat_intro = random.choice(STORY_TEMPLATES['combat_intro']).format(enemy=enemy_names)
            next_narrative = f"\n\nYou enter a {scene['location']}. {scene['description']}\n\n{combat_intro}"
        else:
            template = random.choice(STORY_TEMPLATES['exploration'])
            next_narrative = f"\n\n{template.format(location=scene['location'], description=scene['description'])}"

    # Update session
    game_state['turn'] += 1
    session['game_state'] = game_state

    # Generate new choices
    choices = generate_choices(game_state)

    return jsonify({
        'narrative': result['narrative'] + next_narrative,
        'rolls': result['rolls'],
        'character': char,
        'choices': choices,
        'enemies': game_state.get('enemies', []),
        'enemy_result': enemy_result,
        'scene_type': game_state['scene_type']
    })

@app.route('/api/custom_action', methods=['POST'])
def handle_custom_action():
    data = request.json
    custom_text = data.get('text', '')

    # Treat custom action as a generic action
    return handle_action_internal({'type': 'custom', 'text': custom_text})

def handle_action_internal(action):
    game_state = session.get('game_state', {})
    if not game_state:
        return jsonify({'error': 'No active game session'}), 400

    result = process_action(game_state, action)
    # ... rest of processing (same as handle_action)
    return jsonify(result)

@app.route('/api/roll_dice', methods=['POST'])
def roll_dice():
    data = request.json
    sides = data.get('sides', 20)
    count = data.get('count', 1)
    modifier = data.get('modifier', 0)

    result = Dice.roll(sides, count)
    result['modifier'] = modifier
    result['final_total'] = result['total'] + modifier

    return jsonify(result)

@app.route('/api/game_state')
def get_game_state():
    return jsonify(session.get('game_state', {}))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
