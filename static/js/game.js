/**
 * D&D 5e Interactive Adventure - Game Client
 * ==========================================
 */

// Game State
let gameState = {
    character: null,
    selectedRace: null,
    selectedClass: null,
    stats: null,
    inCombat: false,
    enemies: []
};

// Race icons mapping
const raceIcons = {
    human: '👤',
    elf: '🧝',
    dwarf: '⛏️',
    halfling: '🍀',
    half_orc: '👹',
    gnome: '🔧',
    tiefling: '😈',
    dragonborn: '🐲'
};

// Class icons mapping
const classIcons = {
    fighter: '⚔️',
    wizard: '🧙',
    rogue: '🗡️',
    cleric: '✝️',
    ranger: '🏹',
    barbarian: '🪓',
    paladin: '🛡️',
    bard: '🎵'
};

// Enemy icons mapping
const enemyIcons = {
    'Goblin': '👺',
    'Skeleton': '💀',
    'Orc': '👹',
    'Zombie': '🧟',
    'Dire Wolf': '🐺',
    'Ogre': '👾',
    'Troll': '🧌',
    'Wraith': '👻',
    'Young Dragon': '🐉'
};

// ============================================================================
// SCREEN MANAGEMENT
// ============================================================================

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

function startGame() {
    showScreen('character-screen');
    loadRacesAndClasses();
}

function restartGame() {
    gameState = {
        character: null,
        selectedRace: null,
        selectedClass: null,
        stats: null,
        inCombat: false,
        enemies: []
    };
    showScreen('title-screen');
}

// ============================================================================
// CHARACTER CREATION
// ============================================================================

async function loadRacesAndClasses() {
    try {
        const [racesRes, classesRes] = await Promise.all([
            fetch('/api/races'),
            fetch('/api/classes')
        ]);

        const races = await racesRes.json();
        const classes = await classesRes.json();

        renderRaceOptions(races);
        renderClassOptions(classes);
    } catch (error) {
        console.error('Error loading character options:', error);
    }
}

function renderRaceOptions(races) {
    const container = document.getElementById('race-selection');
    container.innerHTML = '';

    Object.entries(races).forEach(([key, race]) => {
        const option = document.createElement('div');
        option.className = 'selection-option';
        option.dataset.race = key;
        option.innerHTML = `
            <span class="option-icon">${raceIcons[key] || '👤'}</span>
            <span class="option-name">${race.name}</span>
        `;
        option.onclick = () => selectRace(key, race);
        container.appendChild(option);
    });
}

function renderClassOptions(classes) {
    const container = document.getElementById('class-selection');
    container.innerHTML = '';

    Object.entries(classes).forEach(([key, cls]) => {
        const option = document.createElement('div');
        option.className = 'selection-option';
        option.dataset.class = key;
        option.innerHTML = `
            <span class="option-icon">${classIcons[key] || '⚔️'}</span>
            <span class="option-name">${cls.name}</span>
        `;
        option.onclick = () => selectClass(key, cls);
        container.appendChild(option);
    });
}

function selectRace(key, race) {
    // Update selection
    document.querySelectorAll('#race-selection .selection-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    document.querySelector(`[data-race="${key}"]`).classList.add('selected');

    gameState.selectedRace = { key, ...race };
    updateSelectionInfo();
    checkCreateButton();
}

function selectClass(key, cls) {
    // Update selection
    document.querySelectorAll('#class-selection .selection-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    document.querySelector(`[data-class="${key}"]`).classList.add('selected');

    gameState.selectedClass = { key, ...cls };
    updateSelectionInfo();
    checkCreateButton();
}

function updateSelectionInfo() {
    const infoDiv = document.getElementById('selection-info');
    let html = '';

    if (gameState.selectedRace) {
        html += `
            <h4>${raceIcons[gameState.selectedRace.key]} ${gameState.selectedRace.name}</h4>
            <p>${gameState.selectedRace.description}</p>
            <div class="traits">
                ${gameState.selectedRace.traits.map(t => `<span class="trait">${t}</span>`).join('')}
            </div>
        `;
    }

    if (gameState.selectedClass) {
        html += `
            <h4>${classIcons[gameState.selectedClass.key]} ${gameState.selectedClass.name}</h4>
            <p>${gameState.selectedClass.description}</p>
            <p><strong>Hit Die:</strong> d${gameState.selectedClass.hit_die} | <strong>Primary:</strong> ${gameState.selectedClass.primary_stat.toUpperCase()}</p>
            <div class="traits">
                ${gameState.selectedClass.abilities.map(a => `<span class="trait">${a}</span>`).join('')}
            </div>
        `;
    }

    if (!html) {
        html = '<p>Select a race and class to see details...</p>';
    }

    infoDiv.innerHTML = html;
}

async function rollAllStats() {
    const statBoxes = document.querySelectorAll('.stat-box');

    // Add rolling animation
    statBoxes.forEach(box => {
        box.classList.add('rolling');
        box.querySelector('.stat-value').textContent = '?';
        box.querySelector('.stat-mod').textContent = '';
    });

    try {
        const response = await fetch('/api/roll_stats', { method: 'POST' });
        const data = await response.json();

        gameState.stats = data.stats;

        // Reveal stats one by one with animation
        const stats = ['str', 'dex', 'con', 'int', 'wis', 'cha'];
        for (let i = 0; i < stats.length; i++) {
            await delay(200);
            const stat = stats[i];
            const box = document.querySelector(`[data-stat="${stat}"]`);
            const value = data.stats[stat];
            const modifier = Math.floor((value - 10) / 2);
            const modStr = modifier >= 0 ? `+${modifier}` : `${modifier}`;

            box.classList.remove('rolling');
            box.classList.add('rolled');
            box.querySelector('.stat-value').textContent = value;
            box.querySelector('.stat-mod').textContent = modStr;
        }

        checkCreateButton();
    } catch (error) {
        console.error('Error rolling stats:', error);
        statBoxes.forEach(box => box.classList.remove('rolling'));
    }
}

function checkCreateButton() {
    const btn = document.getElementById('create-btn');
    const name = document.getElementById('char-name').value.trim();
    const hasRace = gameState.selectedRace !== null;
    const hasClass = gameState.selectedClass !== null;
    const hasStats = gameState.stats !== null;

    btn.disabled = !(name && hasRace && hasClass && hasStats);
}

// Add event listener for name input
document.addEventListener('DOMContentLoaded', () => {
    const nameInput = document.getElementById('char-name');
    if (nameInput) {
        nameInput.addEventListener('input', checkCreateButton);
    }
});

async function createCharacter() {
    const name = document.getElementById('char-name').value.trim();

    if (!name || !gameState.selectedRace || !gameState.selectedClass || !gameState.stats) {
        alert('Please complete all character creation steps!');
        return;
    }

    try {
        const response = await fetch('/api/create_character', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                race: gameState.selectedRace.key,
                char_class: gameState.selectedClass.key,
                stats: gameState.stats
            })
        });

        const data = await response.json();
        gameState.character = data.character;

        // Switch to game screen
        showScreen('game-screen');

        // Initialize game UI
        updateCharacterPanel();
        displayNarrative(data.narrative);
        displayChoices(data.choices);
        addLogEntry('story', `${name} the ${data.character.race_name} ${data.character.class_name} begins their adventure!`);

    } catch (error) {
        console.error('Error creating character:', error);
        alert('Error creating character. Please try again.');
    }
}

// ============================================================================
// GAME UI UPDATES
// ============================================================================

function updateCharacterPanel() {
    const char = gameState.character;
    if (!char) return;

    // Basic info
    document.getElementById('char-display-name').textContent = char.name;
    document.getElementById('char-display-info').textContent =
        `${char.race_name} ${char.class_name} (Level ${char.level})`;

    // Health bar
    const healthPercent = (char.current_hp / char.max_hp) * 100;
    document.getElementById('health-fill').style.width = `${healthPercent}%`;
    document.getElementById('health-text').textContent = `HP: ${char.current_hp}/${char.max_hp}`;

    // Stats
    document.getElementById('display-ac').textContent = char.ac;
    document.getElementById('display-level').textContent = char.level;
    document.getElementById('display-xp').textContent = char.xp;
    document.getElementById('display-gold').textContent = char.gold;

    // Ability scores mini display
    const abilityMini = document.getElementById('ability-scores-mini');
    abilityMini.innerHTML = '';
    const statNames = { str: 'STR', dex: 'DEX', con: 'CON', int: 'INT', wis: 'WIS', cha: 'CHA' };
    Object.entries(char.stats).forEach(([stat, value]) => {
        const mod = Math.floor((value - 10) / 2);
        const modStr = mod >= 0 ? `+${mod}` : `${mod}`;
        const div = document.createElement('div');
        div.className = 'ability-mini';
        div.innerHTML = `<span>${statNames[stat]}</span><span>${value} (${modStr})</span>`;
        abilityMini.appendChild(div);
    });

    // Equipment
    const equipList = document.getElementById('equipment-list');
    equipList.innerHTML = '';
    char.equipment.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        equipList.appendChild(li);
    });

    // Abilities
    const abilitiesList = document.getElementById('abilities-list');
    abilitiesList.innerHTML = '';
    char.abilities.forEach(ability => {
        const li = document.createElement('li');
        li.textContent = ability;
        abilitiesList.appendChild(li);
    });
    if (char.spells && char.spells.length > 0) {
        char.spells.forEach(spell => {
            const li = document.createElement('li');
            li.textContent = `✨ ${spell}`;
            abilitiesList.appendChild(li);
        });
    }
}

function displayNarrative(text) {
    const narrative = document.getElementById('narrative');
    const p = document.createElement('p');
    p.innerHTML = text.replace(/\n/g, '</p><p>');
    narrative.appendChild(p);

    // Scroll to bottom
    const storyArea = document.getElementById('story-area');
    storyArea.scrollTop = storyArea.scrollHeight;
}

function displayRollResult(rolls) {
    if (!rolls || rolls.length === 0) return;

    const diceResults = document.getElementById('dice-results');
    const rollDetails = document.getElementById('roll-details');

    diceResults.classList.remove('hidden');

    let html = '';
    rolls.forEach(roll => {
        const data = roll.data;
        let resultClass = '';
        if (data.is_crit) resultClass = 'crit';
        if (data.is_fumble) resultClass = 'fumble';

        html += `
            <div class="roll-item">
                <strong>${roll.type}:</strong>
                <span class="roll-value ${resultClass}">${data.total || data.natural}</span>
                ${data.natural ? `<span class="roll-detail">(d20: ${data.natural}${data.modifier ? ` + ${data.modifier}` : ''})</span>` : ''}
                ${data.rolls && data.rolls.length > 1 ? `<span class="roll-detail">[${data.rolls.join(', ')}]</span>` : ''}
                ${data.is_crit ? '<span class="crit-text"> CRITICAL!</span>' : ''}
                ${data.is_fumble ? '<span class="fumble-text"> FUMBLE!</span>' : ''}
            </div>
        `;
    });

    rollDetails.innerHTML = html;

    // Hide after delay
    setTimeout(() => {
        diceResults.classList.add('hidden');
    }, 3000);
}

function displayChoices(choices) {
    const container = document.getElementById('choices');
    container.innerHTML = '';

    choices.forEach((choice, index) => {
        const btn = document.createElement('button');
        btn.className = 'choice-btn';
        btn.innerHTML = `<span class="choice-number">${index + 1}</span> ${choice.text}`;
        btn.onclick = () => selectChoice(choice);
        container.appendChild(btn);
    });
}

function updateCombatArea(enemies) {
    const combatArea = document.getElementById('combat-area');
    const enemyList = document.getElementById('enemy-list');

    if (!enemies || enemies.length === 0) {
        combatArea.classList.add('hidden');
        gameState.inCombat = false;
        return;
    }

    gameState.inCombat = true;
    gameState.enemies = enemies;
    combatArea.classList.remove('hidden');

    enemyList.innerHTML = '';
    enemies.forEach(enemy => {
        const hpPercent = (enemy.current_hp / enemy.hp) * 100;
        const isDefeated = enemy.current_hp <= 0;

        const card = document.createElement('div');
        card.className = `enemy-card${isDefeated ? ' defeated' : ''}`;
        card.innerHTML = `
            <span class="enemy-icon">${enemyIcons[enemy.name] || '👾'}</span>
            <span class="enemy-name">${enemy.name}</span>
            <div class="enemy-hp">
                <span>HP: ${Math.max(0, enemy.current_hp)}/${enemy.hp}</span>
                <div class="enemy-hp-bar">
                    <div class="enemy-hp-fill" style="width: ${Math.max(0, hpPercent)}%"></div>
                </div>
            </div>
            <div class="enemy-stats">
                <small>AC: ${enemy.ac}</small>
            </div>
        `;
        enemyList.appendChild(card);
    });
}

function addLogEntry(type, text) {
    const log = document.getElementById('game-log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = text;
    log.insertBefore(entry, log.firstChild);

    // Keep log manageable
    while (log.children.length > 50) {
        log.removeChild(log.lastChild);
    }
}

// ============================================================================
// GAME ACTIONS
// ============================================================================

async function selectChoice(choice) {
    // Disable buttons during action
    document.querySelectorAll('.choice-btn').forEach(btn => btn.disabled = true);

    addLogEntry('action', `> ${choice.text}`);

    try {
        const response = await fetch('/api/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: choice })
        });

        const data = await response.json();
        processActionResult(data);

    } catch (error) {
        console.error('Error processing action:', error);
        addLogEntry('error', 'Something went wrong...');
        document.querySelectorAll('.choice-btn').forEach(btn => btn.disabled = false);
    }
}

async function submitCustomAction() {
    const input = document.getElementById('custom-action-input');
    const text = input.value.trim();

    if (!text) return;

    addLogEntry('action', `> ${text}`);
    input.value = '';

    try {
        const response = await fetch('/api/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: { type: 'custom', text: text }
            })
        });

        const data = await response.json();
        processActionResult(data);

    } catch (error) {
        console.error('Error processing custom action:', error);
        addLogEntry('error', 'Your action fails...');
    }
}

function processActionResult(data) {
    // Check for game over
    if (data.game_over) {
        displayNarrative(data.narrative);
        if (data.rolls) displayRollResult(data.rolls);

        setTimeout(() => {
            showGameOver();
        }, 2000);
        return;
    }

    // Display rolls
    if (data.rolls && data.rolls.length > 0) {
        displayRollResult(data.rolls);

        // Log rolls
        data.rolls.forEach(roll => {
            const rollData = roll.data;
            let logText = `🎲 ${roll.type}: ${rollData.total || rollData.natural}`;
            if (rollData.is_crit) logText += ' (CRITICAL!)';
            if (rollData.is_fumble) logText += ' (FUMBLE!)';
            addLogEntry('roll', logText);
        });
    }

    // Display narrative
    if (data.narrative) {
        displayNarrative(data.narrative);

        // Check for special text
        if (data.narrative.includes('damage')) {
            addLogEntry('combat', data.narrative.split('.')[0]);
        }
    }

    // Handle enemy attacks
    if (data.enemy_result && data.enemy_result.total_damage > 0) {
        addLogEntry('combat', `⚔️ ${data.enemy_result.narrative}`);
    }

    // Update character
    if (data.character) {
        gameState.character = data.character;
        updateCharacterPanel();
    }

    // Update combat area
    updateCombatArea(data.enemies);

    // Display new choices
    if (data.choices) {
        displayChoices(data.choices);
    }
}

function showGameOver() {
    const char = gameState.character;

    document.getElementById('final-level').textContent = char.level;
    document.getElementById('final-gold').textContent = char.gold;

    showScreen('gameover-screen');
}

// ============================================================================
// QUICK DICE ROLLER
// ============================================================================

async function quickRoll(sides) {
    const resultDiv = document.getElementById('quick-roll-result');

    // Animation
    resultDiv.textContent = '🎲';
    resultDiv.style.animation = 'roll 0.3s ease';

    try {
        const response = await fetch('/api/roll_dice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sides: sides, count: 1 })
        });

        const data = await response.json();

        await delay(300);
        resultDiv.style.animation = '';
        resultDiv.textContent = `d${sides}: ${data.total}`;

        addLogEntry('roll', `🎲 Quick roll d${sides}: ${data.total}`);

    } catch (error) {
        console.error('Error rolling dice:', error);
        resultDiv.textContent = 'Error!';
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Number keys for choices
    if (e.key >= '1' && e.key <= '4') {
        const buttons = document.querySelectorAll('.choice-btn');
        const index = parseInt(e.key) - 1;
        if (buttons[index] && !buttons[index].disabled) {
            buttons[index].click();
        }
    }

    // Enter for custom action
    if (e.key === 'Enter' && document.activeElement.id === 'custom-action-input') {
        submitCustomAction();
    }

    // Enter on title screen
    if (e.key === 'Enter' && document.getElementById('title-screen').classList.contains('active')) {
        startGame();
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Ensure title screen is visible
    showScreen('title-screen');
});
