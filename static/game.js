// ============================================================================
// D&D 5e Web App - Game Logic
// ============================================================================

let gameState = {
    character: null,
    inCombat: false,
    currentEnemy: null
};

// ============================================================================
// Utility Functions
// ============================================================================

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

function addActionMessage(message) {
    const messagesDiv = document.getElementById('action-messages');
    const messageEl = document.createElement('div');
    messageEl.className = 'action-message';
    messageEl.textContent = message;
    messagesDiv.appendChild(messageEl);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function clearActionMessages() {
    document.getElementById('action-messages').innerHTML = '';
}

function updateCharacterDisplay() {
    const char = gameState.character;
    if (!char) return;

    // Basic info
    document.getElementById('char-display-name').textContent = char.name;
    document.getElementById('char-display-race-class').textContent = `${char.race} ${char.class}`;
    document.getElementById('char-display-level').textContent = `Level ${char.level}`;

    // HP
    const hpPercent = (char.current_hp / char.max_hp) * 100;
    document.getElementById('hp-bar').style.width = `${hpPercent}%`;
    document.getElementById('hp-text').textContent = `${char.current_hp}/${char.max_hp}`;

    // Stats
    Object.keys(char.stats).forEach(stat => {
        document.getElementById(`stat-${stat}`).textContent = char.stats[stat];
        const mod = char.modifiers[stat];
        document.getElementById(`mod-${stat}`).textContent = mod >= 0 ? `+${mod}` : `${mod}`;
    });

    // Combat stats
    document.getElementById('char-ac').textContent = char.ac;
    document.getElementById('char-xp').textContent = char.xp;
    document.getElementById('char-gold').textContent = char.gold;

    // Inventory
    const inventoryList = document.getElementById('inventory-list');
    inventoryList.innerHTML = '';
    char.inventory.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        inventoryList.appendChild(li);
    });
}

function updateEnemyDisplay(enemy) {
    if (!enemy) {
        document.getElementById('combat-area').classList.add('hidden');
        return;
    }

    document.getElementById('combat-area').classList.remove('hidden');
    document.getElementById('enemy-name').textContent = enemy.name;
    document.getElementById('enemy-ac').textContent = enemy.ac;

    const hpPercent = (enemy.current_hp / enemy.hp) * 100;
    document.getElementById('enemy-hp-bar').style.width = `${hpPercent}%`;
    document.getElementById('enemy-hp-text').textContent = `${enemy.current_hp}/${enemy.hp}`;
}

function showDiceRoll(text) {
    const diceDisplay = document.getElementById('dice-display');
    const diceResult = document.getElementById('dice-result');

    diceDisplay.classList.remove('hidden');
    diceResult.textContent = text;

    setTimeout(() => {
        diceDisplay.classList.add('hidden');
    }, 2000);
}

function displayStory(text) {
    const storyText = document.getElementById('story-text');
    storyText.innerHTML = `<p>${text}</p>`;
}

function displayChoices(choices) {
    const choicesList = document.getElementById('choices-list');
    choicesList.innerHTML = '';

    choices.forEach((choice, index) => {
        const btn = document.createElement('button');
        btn.className = 'choice-btn';
        btn.textContent = choice;
        btn.onclick = () => performAction(choice);
        choicesList.appendChild(btn);
    });
}

// ============================================================================
// API Calls
// ============================================================================

async function createCharacter(name, race, charClass) {
    showLoading();

    try {
        const response = await fetch('/api/create_character', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                race: race,
                class: charClass
            })
        });

        const data = await response.json();

        if (data.success) {
            gameState.character = data.character;
            updateCharacterDisplay();
            displayStory(data.intro);

            // Get initial choices
            performAction('begin');
        }
    } catch (error) {
        console.error('Error creating character:', error);
        alert('Failed to create character. Please try again.');
    } finally {
        hideLoading();
    }
}

async function performAction(choice) {
    showLoading();
    clearActionMessages();

    try {
        const response = await fetch('/api/action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                choice: choice
            })
        });

        const data = await response.json();

        handleActionResponse(data);
    } catch (error) {
        console.error('Error performing action:', error);
        alert('Failed to perform action. Please try again.');
    } finally {
        hideLoading();
    }
}

function handleActionResponse(data) {
    // Update character if present
    if (data.character) {
        gameState.character = data.character;
        updateCharacterDisplay();
    }

    // Handle different result types
    switch(data.result) {
        case 'combat_start':
            gameState.inCombat = true;
            gameState.currentEnemy = data.enemy;
            addActionMessage(data.message);
            updateEnemyDisplay(data.enemy);
            displayStory(`⚔️ COMBAT INITIATED ⚔️\n\n${data.message}`);
            displayChoices(data.choices);
            break;

        case 'combat_continue':
            // Display all combat messages
            data.messages.forEach(msg => addActionMessage(msg));
            updateEnemyDisplay(data.enemy);
            displayChoices(data.choices);
            break;

        case 'combat_victory':
            gameState.inCombat = false;
            gameState.currentEnemy = null;
            data.messages.forEach(msg => addActionMessage(msg));
            updateEnemyDisplay(null);
            displayStory("Victory! The enemy has been defeated.");
            displayChoices(data.choices);
            break;

        case 'defeat':
            gameState.inCombat = false;
            data.messages.forEach(msg => addActionMessage(msg));
            displayStory("💀 You have been defeated...\n\nYour adventure ends here. Refresh the page to start a new journey.");
            document.getElementById('choices-list').innerHTML = '';
            document.getElementById('custom-action').style.display = 'none';
            break;

        case 'exploration':
            displayStory(data.message);
            displayChoices(data.choices);
            break;

        default:
            if (data.message) {
                displayStory(data.message);
            }
            if (data.choices) {
                displayChoices(data.choices);
            }
    }
}

async function takeRest() {
    showLoading();

    try {
        const response = await fetch('/api/rest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            gameState.character = data.character;
            updateCharacterDisplay();
            addActionMessage(data.message);
            showDiceRoll('🏕️ Short Rest Complete');
        }
    } catch (error) {
        console.error('Error resting:', error);
        alert('Failed to rest. Please try again.');
    } finally {
        hideLoading();
    }
}

// ============================================================================
// Event Listeners
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Character creation form
    const charForm = document.getElementById('char-form');
    charForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const name = document.getElementById('char-name').value;
        const race = document.getElementById('char-race').value;
        const charClass = document.getElementById('char-class').value;

        if (!name || !race || !charClass) {
            alert('Please fill in all fields');
            return;
        }

        createCharacter(name, race, charClass);
        showScreen('game-screen');
    });

    // Custom action button
    const customActionBtn = document.getElementById('custom-action-btn');
    customActionBtn.addEventListener('click', () => {
        const customInput = document.getElementById('custom-input');
        const action = customInput.value.trim();

        if (!action) {
            alert('Please enter an action');
            return;
        }

        performAction(action);
        customInput.value = '';
    });

    // Custom action on Enter key
    const customInput = document.getElementById('custom-input');
    customInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            customActionBtn.click();
        }
    });

    // Rest button
    const restBtn = document.getElementById('rest-btn');
    restBtn.addEventListener('click', takeRest);
});

// ============================================================================
// Keyboard Shortcuts
// ============================================================================

document.addEventListener('keydown', (e) => {
    // Number keys 1-4 for quick choices
    if (e.key >= '1' && e.key <= '4') {
        const choiceButtons = document.querySelectorAll('.choice-btn');
        const index = parseInt(e.key) - 1;
        if (choiceButtons[index]) {
            choiceButtons[index].click();
        }
    }

    // 'C' for custom action focus
    if (e.key === 'c' || e.key === 'C') {
        if (document.activeElement !== document.getElementById('custom-input')) {
            document.getElementById('custom-input').focus();
        }
    }

    // 'R' for rest
    if (e.key === 'r' || e.key === 'R') {
        if (!gameState.inCombat && document.activeElement !== document.getElementById('custom-input')) {
            document.getElementById('rest-btn').click();
        }
    }
});

// ============================================================================
// Sound Effects (Optional)
// ============================================================================

function playSound(type) {
    // Can implement sound effects here
    // For now, just console log
    console.log(`Sound: ${type}`);
}
