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
    'Fighter': {'hit_die': 10, 'primary': 'str', 'spellcaster': False},
    'Wizard': {'hit_die': 6, 'primary': 'int', 'spellcaster': True, 'spell_stat': 'int'},
    'Rogue': {'hit_die': 8, 'primary': 'dex', 'spellcaster': False},
    'Cleric': {'hit_die': 8, 'primary': 'wis', 'spellcaster': True, 'spell_stat': 'wis'},
    'Ranger': {'hit_die': 10, 'primary': 'dex', 'spellcaster': True, 'spell_stat': 'wis'},
    'Barbarian': {'hit_die': 12, 'primary': 'str', 'spellcaster': False},
    'Paladin': {'hit_die': 10, 'primary': 'str', 'spellcaster': True, 'spell_stat': 'cha'},
    'Bard': {'hit_die': 8, 'primary': 'cha', 'spellcaster': True, 'spell_stat': 'cha'}
}

# ============================================================================
# SPELL SYSTEM
# ============================================================================
SPELLS = {
    'Wizard': {
        'Magic Missile': {'level': 1, 'damage': '3d4+3', 'mana_cost': 2, 'description': 'Auto-hit arcane missiles', 'type': 'damage'},
        'Fireball': {'level': 3, 'damage': '8d6', 'mana_cost': 5, 'description': 'Explosive fire damage', 'type': 'damage'},
        'Shield': {'level': 1, 'ac_bonus': 5, 'duration': 1, 'mana_cost': 2, 'description': '+5 AC for 1 turn', 'type': 'buff'},
        'Lightning Bolt': {'level': 3, 'damage': '8d6', 'mana_cost': 5, 'description': 'Chain lightning', 'type': 'damage'},
        'Haste': {'level': 3, 'duration': 3, 'mana_cost': 4, 'description': 'Double attacks for 3 turns', 'type': 'buff'}
    },
    'Cleric': {
        'Cure Wounds': {'level': 1, 'heal': '1d8+3', 'mana_cost': 2, 'description': 'Heal wounds', 'type': 'heal'},
        'Bless': {'level': 1, 'attack_bonus': 1, 'duration': 3, 'mana_cost': 2, 'description': '+1 to attacks for 3 turns', 'type': 'buff'},
        'Sacred Flame': {'level': 1, 'damage': '2d8', 'mana_cost': 1, 'description': 'Holy fire', 'type': 'damage'},
        'Mass Healing': {'level': 3, 'heal': '3d8+5', 'mana_cost': 6, 'description': 'Heal entire party', 'type': 'heal'},
        'Divine Smite': {'level': 2, 'damage': '4d8', 'mana_cost': 3, 'description': 'Holy damage', 'type': 'damage'}
    },
    'Paladin': {
        'Lay on Hands': {'level': 1, 'heal': '2d8+2', 'mana_cost': 2, 'description': 'Heal yourself or ally', 'type': 'heal'},
        'Smite': {'level': 1, 'damage': '2d8', 'mana_cost': 2, 'description': 'Holy weapon strike', 'type': 'damage'},
        'Protection': {'level': 2, 'ac_bonus': 3, 'duration': 2, 'mana_cost': 3, 'description': '+3 AC for 2 turns', 'type': 'buff'}
    },
    'Bard': {
        'Vicious Mockery': {'level': 1, 'damage': '1d4', 'debuff': 'disadvantage', 'mana_cost': 1, 'description': 'Damage and enemy disadvantage', 'type': 'damage'},
        'Healing Word': {'level': 1, 'heal': '1d4+4', 'mana_cost': 2, 'description': 'Quick heal', 'type': 'heal'},
        'Inspiration': {'level': 1, 'attack_bonus': 2, 'duration': 3, 'mana_cost': 2, 'description': '+2 to party attacks', 'type': 'buff'}
    },
    'Ranger': {
        'Hunters Mark': {'level': 1, 'damage_bonus': '1d6', 'duration': 5, 'mana_cost': 2, 'description': 'Mark enemy for extra damage', 'type': 'buff'},
        'Cure Wounds': {'level': 1, 'heal': '1d8+2', 'mana_cost': 2, 'description': 'Heal wounds', 'type': 'heal'}
    }
}

# ============================================================================
# STATUS EFFECTS
# ============================================================================
STATUS_EFFECTS = {
    'Poisoned': {'attack_penalty': -2, 'damage_per_turn': 5, 'description': 'Taking poison damage'},
    'Blessed': {'attack_bonus': 1, 'save_bonus': 1, 'description': 'Divine blessing'},
    'Stunned': {'cannot_act': True, 'description': 'Unable to act'},
    'Burning': {'damage_per_turn': 8, 'description': 'On fire!'},
    'Hasted': {'extra_attack': True, 'description': 'Moving with supernatural speed'},
    'Shielded': {'ac_bonus': 5, 'description': 'Protected by magical shield'},
    'Inspired': {'attack_bonus': 2, 'description': 'Inspired by bardic performance'}
}

# ============================================================================
# SKILLS SYSTEM
# ============================================================================
SKILLS = {
    'Persuasion': 'cha',
    'Intimidation': 'cha',
    'Deception': 'cha',
    'Stealth': 'dex',
    'Acrobatics': 'dex',
    'Sleight of Hand': 'dex',
    'Investigation': 'int',
    'Arcana': 'int',
    'History': 'int',
    'Perception': 'wis',
    'Insight': 'wis',
    'Survival': 'wis',
    'Athletics': 'str',
    'Medicine': 'wis'
}

# ============================================================================
# BOSS BATTLES
# ============================================================================
BOSSES = {
    'Shadow Lord': {
        'hp': 150,
        'ac': 18,
        'attack': 8,
        'damage': '3d8+5',
        'xp': 5000,
        'abilities': ['Shadow Strike', 'Dark Regeneration'],
        'loot_tier': 'legendary',
        'description': 'An ancient evil shrouded in darkness',
        'phase_2_hp': 75  # Triggers special phase
    },
    'Dragon Tyrant': {
        'hp': 200,
        'ac': 20,
        'attack': 10,
        'damage': '4d10+6',
        'xp': 8000,
        'abilities': ['Fire Breath', 'Wing Attack'],
        'loot_tier': 'legendary',
        'description': 'A massive red dragon of terrible power',
        'phase_2_hp': 100
    },
    'Lich King': {
        'hp': 180,
        'ac': 19,
        'attack': 9,
        'damage': '3d10+4',
        'xp': 7000,
        'abilities': ['Drain Life', 'Summon Undead'],
        'loot_tier': 'legendary',
        'description': 'An undead sorcerer of immense magical power',
        'phase_2_hp': 90
    }
}

# ============================================================================
# STORY GENERATION - ENHANCED
# ============================================================================
class StoryGenerator:
    # Chapter-based story progression
    CHAPTERS = {
        1: {
            'title': 'The Call to Adventure',
            'locations': ['the Village of Millhaven', 'the Old Tavern', 'the Market Square'],
            'quest': 'Investigate the disappearances in the northern woods'
        },
        2: {
            'title': 'Into the Darkness',
            'locations': ['the Forgotten Crypt', 'Shadowfang Cavern', 'the Ruins of Thornkeep'],
            'quest': 'Uncover the source of the evil'
        },
        3: {
            'title': 'Gathering Allies',
            'locations': ['Blackwood Forest', 'the Elven Outpost', 'the Dwarven Stronghold'],
            'quest': 'Recruit companions for the final battle'
        },
        4: {
            'title': 'The Rising Storm',
            'locations': ['the Tower of Eternal Night', 'Dragon\'s Maw Canyon', 'the Sunken Temple'],
            'quest': 'Confront the dark lord\'s lieutenants'
        },
        5: {
            'title': 'The Final Confrontation',
            'locations': ['Frostpeak Mountain', 'the Cursed Marshlands', 'the Dark Citadel'],
            'quest': 'Defeat the ancient evil threatening the realm'
        }
    }

    INTRO_TEMPLATES = [
        "You find yourself at the entrance of {location}, a place whispered about in tavern tales. The air is thick with {atmosphere}. {quest_hint}",
        "The road has led you to {location}. Before you stands {obstacle}, and you sense {atmosphere}. {quest_hint}",
        "As dawn breaks, you arrive at {location}. {atmosphere} fills the air, and danger lurks nearby. {quest_hint}",
    ]

    QUEST_HINTS = [
        "The locals speak of a great evil awakening",
        "An ancient prophecy speaks of a hero like you",
        "Dark forces gather, and only you can stop them",
        "The fate of the realm rests on your shoulders"
    ]

    ATMOSPHERES = [
        "an ancient evil", "the smell of sulfur and decay", "a sense of being watched",
        "whispers of the damned", "an unnatural silence", "a foreboding darkness",
        "the weight of destiny", "an otherworldly presence"
    ]

    OBSTACLES = [
        "a massive iron gate, slightly ajar", "the corpses of previous adventurers",
        "mysterious glowing runes", "a deep chasm with a rope bridge",
        "a warning sign written in blood", "the remnants of a fierce battle"
    ]

    DETAILED_EXPLORATION = {
        'mystery': [
            "You discover a hidden chamber filled with ancient scrolls. As you read them, you learn of a prophecy foretelling your arrival. The texts speak of trials ahead.",
            "A mysterious figure watches from the shadows. As you approach, they vanish, leaving behind a cryptic message carved in stone.",
            "You find a journal belonging to a previous adventurer. Their final entry warns of a terrible creature guarding the path ahead."
        ],
        'treasure': [
            "Glinting in the torchlight, you spot a locked chest. The craftsmanship suggests it contains something valuable.",
            "An ornate pedestal holds a mysterious artifact. Ancient runes glow faintly around its base.",
            "Among the rubble, you notice the shimmer of gold and the glint of steel. Treasure awaits the brave."
        ],
        'danger': [
            "Fresh claw marks rake across the stone walls. Whatever made them is massive... and nearby.",
            "You hear the click of a pressure plate beneath your boot. Time seems to slow as you realize you've triggered a trap.",
            "The temperature drops suddenly. Your breath mists in the air. Something unnatural is close."
        ],
        'npc': [
            "A wounded warrior leans against the wall. 'Turn back,' they gasp. 'This place... it's cursed.' But their eyes show determination.",
            "You encounter a mysterious mage studying the walls. They look up with interest. 'Seeking glory or redemption, adventurer?'",
            "A seasoned ranger emerges from the shadows. 'Dangerous to go alone. Perhaps we could aid each other?'"
        ]
    }

    @staticmethod
    def generate_intro(chapter=1):
        chapter_data = StoryGenerator.CHAPTERS.get(chapter, StoryGenerator.CHAPTERS[1])
        template = random.choice(StoryGenerator.INTRO_TEMPLATES)
        return template.format(
            location=random.choice(chapter_data['locations']),
            atmosphere=random.choice(StoryGenerator.ATMOSPHERES),
            obstacle=random.choice(StoryGenerator.OBSTACLES),
            quest_hint=random.choice(StoryGenerator.QUEST_HINTS)
        )

    @staticmethod
    def generate_exploration(story_progress=0):
        # Choose category based on story progress
        if story_progress < 3:
            category = random.choice(['mystery', 'danger', 'treasure'])
        else:
            category = random.choice(['mystery', 'danger', 'treasure', 'npc'])

        return random.choice(StoryGenerator.DETAILED_EXPLORATION[category])

    @staticmethod
    def generate_choices(scene_type='exploration', has_party=False):
        if scene_type == 'exploration':
            choices = [
                "Search the area carefully for traps and treasure",
                "Proceed cautiously, weapons ready",
                "Light a torch and investigate the sounds",
                "Cast a detection spell to sense magic or danger"
            ]
            if has_party:
                choices.append("Send a party member to scout ahead")
            return choices
        elif scene_type == 'combat':
            choices = [
                "Attack with your weapon",
                "Cast a spell or use a special ability",
                "Take defensive position and dodge",
                "Attempt to intimidate or negotiate"
            ]
            if has_party:
                choices.append("Coordinate an attack with your party")
            return choices
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

# ============================================================================
# PARTY MEMBERS / COMPANIONS SYSTEM
# ============================================================================
COMPANIONS = {
    'Theron the Brave': {
        'race': 'Human',
        'class': 'Fighter',
        'level': 2,
        'hp': 20,
        'ac': 16,
        'attack_bonus': 5,
        'damage': '1d8+3',
        'description': 'A seasoned warrior with a noble heart and unwavering courage.',
        'backstory': 'Once a knight of the realm, now seeking redemption for past failures.',
        'recruitment_chance': 0.15,
        'story_progress_required': 2
    },
    'Lyra Moonwhisper': {
        'race': 'Elf',
        'class': 'Wizard',
        'level': 3,
        'hp': 15,
        'ac': 13,
        'attack_bonus': 6,
        'damage': '2d6+3',
        'description': 'A mysterious elven mage with mastery over arcane forces.',
        'backstory': 'Seeks ancient knowledge hidden in these cursed lands.',
        'recruitment_chance': 0.12,
        'story_progress_required': 3
    },
    'Grimjaw Ironfoot': {
        'race': 'Dwarf',
        'class': 'Cleric',
        'level': 2,
        'hp': 18,
        'ac': 15,
        'attack_bonus': 4,
        'damage': '1d6+2',
        'description': 'A gruff dwarven cleric who heals wounds and smites evil.',
        'backstory': 'His temple was destroyed. He vows vengeance on the dark forces.',
        'recruitment_chance': 0.15,
        'story_progress_required': 2
    },
    'Shadow': {
        'race': 'Halfling',
        'class': 'Rogue',
        'level': 2,
        'hp': 14,
        'ac': 14,
        'attack_bonus': 5,
        'damage': '1d6+3',
        'description': 'A nimble rogue with a mysterious past and quick daggers.',
        'backstory': 'Speaks little of their past, but their skills speak volumes.',
        'recruitment_chance': 0.18,
        'story_progress_required': 1
    },
    'Zara Stormcaller': {
        'race': 'Dragonborn',
        'class': 'Paladin',
        'level': 3,
        'hp': 25,
        'ac': 17,
        'attack_bonus': 6,
        'damage': '1d10+4',
        'description': 'A noble dragonborn paladin sworn to protect the innocent.',
        'backstory': 'Answered a divine calling to vanquish the darkness.',
        'recruitment_chance': 0.10,
        'story_progress_required': 4
    }
}

def create_companion_instance(companion_name):
    """Create a companion instance from the template"""
    template = COMPANIONS[companion_name].copy()
    return {
        'name': companion_name,
        'race': template['race'],
        'class': template['class'],
        'level': template['level'],
        'max_hp': template['hp'],
        'current_hp': template['hp'],
        'ac': template['ac'],
        'attack_bonus': template['attack_bonus'],
        'damage': template['damage'],
        'description': template['description'],
        'backstory': template['backstory']
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

    # Calculate mana for spellcasters
    is_spellcaster = class_info.get('spellcaster', False)
    max_mana = 0
    current_mana = 0
    if is_spellcaster:
        spell_stat = class_info['spell_stat']
        max_mana = 10 + (1 * 5) + modifiers[spell_stat]  # Level 1 starts with base mana
        current_mana = max_mana

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
        'max_mana': max_mana,
        'current_mana': current_mana,
        'gold': 100,
        'inventory': ['Adventurer\'s Pack', 'Waterskin', 'Rations (5 days)'],
        'equipped': {
            'weapon': starting_weapon,
            'armor': starting_armor,
            'accessory': None
        },
        'equipment_inventory': [],
        'party': [],  # List of companion instances
        'story_progress': 0,  # Track story advancement
        'chapter': 1,  # Current chapter
        'status_effects': {},  # Active status effects {effect_name: turns_remaining}
        'known_spells': list(SPELLS.get(char_class, {}).keys()) if is_spellcaster else [],
        'boss_kills': 0  # Track boss defeats
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
        'intro': StoryGenerator.generate_intro(chapter=1)
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
        story_progress = character.get('story_progress', 0)
        character['story_progress'] = story_progress + 1

        story = StoryGenerator.generate_exploration(story_progress)
        has_party = len(character.get('party', [])) > 0
        choices = StoryGenerator.generate_choices('exploration', has_party)

        # Companion recruitment chance
        companion_recruited = None
        if story_progress >= 2 and len(character.get('party', [])) < 4:
            for comp_name, comp_data in COMPANIONS.items():
                # Check if already recruited
                if any(p['name'] == comp_name for p in character.get('party', [])):
                    continue

                # Check story progress requirement
                if story_progress >= comp_data['story_progress_required']:
                    if random.random() < comp_data['recruitment_chance']:
                        companion = create_companion_instance(comp_name)
                        character['party'].append(companion)
                        companion_recruited = companion
                        story += f"\n\n🤝 {comp_name} joins your party!\n\"{comp_data['backstory']}\""
                        break

        # Random loot
        if random.random() < 0.3:
            gold_found = random.randint(5, 25)
            character['gold'] += gold_found
            story += f"\n\n💰 You found {gold_found} gold pieces!"

        # Chapter progression
        if character['story_progress'] % 10 == 0 and character['chapter'] < 5:
            character['chapter'] += 1
            chapter_data = StoryGenerator.CHAPTERS[character['chapter']]
            story += f"\n\n📖 CHAPTER {character['chapter']}: {chapter_data['title']}\n{chapter_data['quest']}"

        session['character'] = character

        return jsonify({
            'result': 'exploration',
            'message': story,
            'choices': choices,
            'companion_recruited': companion_recruited
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

    # Party members attack
    party = character.get('party', [])
    for companion in party:
        if companion['current_hp'] > 0 and enemy_hp > 0:
            comp_attack_roll = Dice.d20(companion['attack_bonus'])
            messages.append(f"🎲 {companion['name']} rolled {comp_attack_roll['chosen']} + {companion['attack_bonus']} = {comp_attack_roll['total']} to attack")

            if comp_attack_roll['chosen'] == 20:
                # Critical hit
                damage_dice = companion['damage'].split('d')
                dice_count = int(damage_dice[0]) * 2
                dice_sides = int(damage_dice[1].split('+')[0]) if '+' in damage_dice[1] else int(damage_dice[1])
                damage_bonus = int(damage_dice[1].split('+')[1]) if '+' in damage_dice[1] else 0
                damage_roll = Dice.roll(dice_sides, dice_count, damage_bonus)
                enemy_hp -= damage_roll['total']
                messages.append(f"⚔️ CRITICAL HIT! {companion['name']} deals {damage_roll['total']} damage!")
            elif comp_attack_roll['total'] >= enemy['ac']:
                damage_dice = companion['damage'].split('d')
                dice_count = int(damage_dice[0])
                dice_sides = int(damage_dice[1].split('+')[0]) if '+' in damage_dice[1] else int(damage_dice[1])
                damage_bonus = int(damage_dice[1].split('+')[1]) if '+' in damage_dice[1] else 0
                damage_roll = Dice.roll(dice_sides, dice_count, damage_bonus)
                enemy_hp -= damage_roll['total']
                messages.append(f"⚔️ {companion['name']} hits for {damage_roll['total']} damage!")
            else:
                messages.append(f"❌ {companion['name']}'s attack misses!")

    # Check if enemy defeated after party attacks
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

        has_party = len(character.get('party', [])) > 0
        return {
            'result': 'combat_victory',
            'messages': messages,
            'character': character,
            'loot': loot if loot else [],
            'choices': StoryGenerator.generate_choices('exploration', has_party)
        }

    # Enemy attack (targets random party member or player)
    party_alive = [character] + [c for c in party if c['current_hp'] > 0]
    target = random.choice(party_alive)
    is_player = target == character

    enemy_attack_roll = Dice.d20(enemy['attack'])
    target_name = "you" if is_player else target['name']
    messages.append(f"🎲 {enemy_name} attacks {target_name}, rolled {enemy_attack_roll['chosen']} + {enemy['attack']} = {enemy_attack_roll['total']}")

    target_ac = target['ac'] if not is_player else character['ac']
    if enemy_attack_roll['total'] >= target_ac:
        damage_dice = enemy['damage'].split('d')
        dice_count = int(damage_dice[0])
        dice_sides = int(damage_dice[1].split('+')[0])
        damage_bonus = int(damage_dice[1].split('+')[1]) if '+' in damage_dice[1] else 0
        damage_roll = Dice.roll(dice_sides, dice_count, damage_bonus)
        target['current_hp'] -= damage_roll['total']
        messages.append(f"💥 {enemy_name} hits {target_name} for {damage_roll['total']} damage!")

        if is_player and character['current_hp'] <= 0:
            character['current_hp'] = 0
            return {
                'result': 'defeat',
                'messages': messages + ["💀 You have been defeated..."],
                'character': character
            }
        elif not is_player and target['current_hp'] <= 0:
            target['current_hp'] = 0
            messages.append(f"💀 {target['name']} has fallen in battle!")
    else:
        messages.append(f"🛡️ {enemy_name}'s attack on {target_name} misses!")

    game_state['enemy_current_hp'] = enemy_hp

    has_party = len(character.get('party', [])) > 0
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
        'choices': StoryGenerator.generate_choices('combat', has_party)
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

@app.route('/api/cast_spell', methods=['POST'])
def cast_spell():
    """Cast a spell"""
    character = session.get('character')
    if not character:
        return jsonify({'error': 'No character found'}), 400

    data = request.json
    spell_name = data['spell_name']
    target = data.get('target', 'enemy')  # 'enemy', 'self', or 'party'

    char_class = character['class']
    if char_class not in SPELLS or spell_name not in SPELLS[char_class]:
        return jsonify({'error': 'Spell not known'}), 400

    spell = SPELLS[char_class][spell_name]

    if character['current_mana'] < spell['mana_cost']:
        return jsonify({'error': 'Not enough mana'}), 400

    # Cast spell
    character['current_mana'] -= spell['mana_cost']
    messages = [f"✨ You cast {spell_name}!"]

    result = {}

    if spell['type'] == 'damage':
        damage_dice = spell['damage'].split('d')
        dice_count = int(damage_dice[0])
        dice_sides = int(damage_dice[1].split('+')[0]) if '+' in damage_dice[1] else int(damage_dice[1])
        damage_bonus = int(damage_dice[1].split('+')[1]) if '+' in damage_dice[1] else 0
        damage_roll = Dice.roll(dice_sides, dice_count, damage_bonus)
        messages.append(f"💥 Dealt {damage_roll['total']} magical damage!")
        result['damage'] = damage_roll['total']

    elif spell['type'] == 'heal':
        heal_dice = spell['heal'].split('d')
        dice_count = int(heal_dice[0])
        dice_sides = int(heal_dice[1].split('+')[0]) if '+' in heal_dice[1] else int(heal_dice[1])
        heal_bonus = int(heal_dice[1].split('+')[1]) if '+' in heal_dice[1] else 0
        heal_roll = Dice.roll(dice_sides, dice_count, heal_bonus)

        if target == 'party' and 'Mass' in spell_name:
            for companion in character.get('party', []):
                companion['current_hp'] = min(companion['current_hp'] + heal_roll['total'], companion['max_hp'])
            character['current_hp'] = min(character['current_hp'] + heal_roll['total'], character['max_hp'])
            messages.append(f"💚 Healed party for {heal_roll['total']} HP!")
        else:
            character['current_hp'] = min(character['current_hp'] + heal_roll['total'], character['max_hp'])
            messages.append(f"💚 Healed {heal_roll['total']} HP!")
        result['heal'] = heal_roll['total']

    elif spell['type'] == 'buff':
        duration = spell.get('duration', 1)
        if 'ac_bonus' in spell:
            character['status_effects']['Shielded'] = duration
            messages.append(f"🛡️ AC increased by {spell['ac_bonus']} for {duration} turns!")
        if 'attack_bonus' in spell:
            effect_name = 'Blessed' if 'Bless' in spell_name else 'Inspired'
            character['status_effects'][effect_name] = duration
            messages.append(f"⚔️ Attack bonus for {duration} turns!")
        if 'Haste' in spell_name:
            character['status_effects']['Hasted'] = duration
            messages.append(f"⚡ Hasted for {duration} turns!")

    session['character'] = character

    return jsonify({
        'success': True,
        'messages': messages,
        'character': character,
        **result
    })

@app.route('/api/skill_check', methods=['POST'])
def skill_check():
    """Perform a skill check"""
    character = session.get('character')
    if not character:
        return jsonify({'error': 'No character found'}), 400

    data = request.json
    skill = data['skill']
    dc = data.get('dc', 15)  # Difficulty Class

    if skill not in SKILLS:
        return jsonify({'error': 'Invalid skill'}), 400

    ability = SKILLS[skill]
    modifier = character['modifiers'][ability]

    roll = Dice.d20(modifier)

    success = roll['total'] >= dc
    result_text = 'Success!' if success else 'Failure!'

    return jsonify({
        'success': success,
        'roll': roll,
        'dc': dc,
        'message': f"🎲 {skill} check: {roll['chosen']} + {modifier} = {roll['total']} vs DC {dc} - {result_text}"
    })

@app.route('/api/save_game', methods=['POST'])
def save_game():
    """Save game state"""
    character = session.get('character')
    game_state = session.get('game_state', {})

    if not character:
        return jsonify({'error': 'No character found'}), 400

    save_data = {
        'character': character,
        'game_state': game_state,
        'timestamp': datetime.now().isoformat()
    }

    # Return save data to user (they can copy it)
    return jsonify({
        'success': True,
        'save_data': save_data,
        'message': 'Game saved! Copy this data to load later.'
    })

@app.route('/api/load_game', methods=['POST'])
def load_game():
    """Load game state"""
    data = request.json
    save_data = data.get('save_data')

    if not save_data:
        return jsonify({'error': 'No save data provided'}), 400

    session['character'] = save_data['character']
    session['game_state'] = save_data.get('game_state', {})

    return jsonify({
        'success': True,
        'character': save_data['character'],
        'message': 'Game loaded successfully!'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
