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

    // Equipped items
    if (char.equipped) {
        document.getElementById('equipped-weapon').textContent = char.equipped.weapon || 'None';
        document.getElementById('equipped-armor').textContent = char.equipped.armor || 'None';
        document.getElementById('equipped-accessory').textContent = char.equipped.accessory || 'None';
    }

    // Equipment inventory
    const equipmentDiv = document.getElementById('equipment-inventory');
    if (char.equipment_inventory && char.equipment_inventory.length > 0) {
        equipmentDiv.innerHTML = '';
        char.equipment_inventory.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'equipment-item';
            itemDiv.innerHTML = `
                <span class="item-name">${item.name}</span>
                <span class="item-stats">${item.type}</span>
            `;
            itemDiv.onclick = () => equipItem(item.type, item.name);
            equipmentDiv.appendChild(itemDiv);
        });
    } else {
        equipmentDiv.innerHTML = '<p class="empty-inventory">No equipment</p>';
    }

    // Regular inventory
    const inventoryList = document.getElementById('inventory-list');
    inventoryList.innerHTML = '';
    char.inventory.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        inventoryList.appendChild(li);
    });

    // Party members display
    const partyDiv = document.getElementById('party-members');
    if (char.party && char.party.length > 0) {
        partyDiv.innerHTML = '';
        char.party.forEach(companion => {
            const memberDiv = document.createElement('div');
            memberDiv.className = 'party-member';

            const hpPercent = (companion.current_hp / companion.max_hp) * 100;

            memberDiv.innerHTML = `
                <div class="party-member-header">
                    <span class="party-member-name">${companion.name}</span>
                </div>
                <div class="party-member-class">${companion.race} ${companion.class} (Lvl ${companion.level})</div>
                <div class="party-member-hp">HP: ${companion.current_hp}/${companion.max_hp}</div>
                <div class="party-hp-bar">
                    <div class="party-hp-fill" style="width: ${hpPercent}%"></div>
                </div>
            `;
            partyDiv.appendChild(memberDiv);
        });
    } else {
        partyDiv.innerHTML = '<p class="empty-party">Adventuring alone</p>';
    }

    // Chapter and story progress display
    if (char.chapter) {
        const chapterTitles = {
            1: 'The Call to Adventure',
            2: 'Into the Darkness',
            3: 'Gathering Allies',
            4: 'The Rising Storm',
            5: 'The Final Confrontation'
        };
        document.getElementById('chapter-display').textContent =
            `Chapter ${char.chapter}: ${chapterTitles[char.chapter] || 'Unknown'}`;
    }

    if (char.story_progress !== undefined) {
        document.getElementById('story-progress').textContent =
            `Progress: ${char.story_progress}`;
    }
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

function showDiceRoll(text, rollValue = 20) {
    const diceDisplay = document.getElementById('dice-display');
    const diceResult = document.getElementById('dice-result');
    const dice3d = document.getElementById('dice-3d');

    // Update dice faces to show the roll
    const faces = dice3d.querySelectorAll('.dice-face');
    faces[0].textContent = rollValue; // Front face shows the result

    diceDisplay.classList.remove('hidden');
    diceResult.textContent = text;

    // Restart animation
    dice3d.style.animation = 'none';
    setTimeout(() => {
        dice3d.style.animation = 'dice-spin 1s ease-out';
    }, 10);

    setTimeout(() => {
        diceDisplay.classList.add('hidden');
    }, 3000);
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
            // Display all combat messages with dice animation for rolls
            data.messages.forEach((msg, index) => {
                setTimeout(() => {
                    if (msg.includes('rolled') && msg.includes('🎲')) {
                        // Extract roll value if possible
                        const rollMatch = msg.match(/rolled (\d+)/);
                        if (rollMatch) {
                            showDiceRoll(msg, parseInt(rollMatch[1]));
                        }
                    }
                    addActionMessage(msg);
                }, index * 300);
            });
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
// Shop and Equipment Functions
// ============================================================================

async function openShop() {
    showLoading();

    try {
        const response = await fetch('/api/shop');
        const data = await response.json();

        displayShop(data.shop, data.gold);
        document.getElementById('shop-modal').classList.remove('hidden');
    } catch (error) {
        console.error('Error loading shop:', error);
        alert('Failed to load shop');
    } finally {
        hideLoading();
    }
}

function displayShop(shop, gold) {
    document.getElementById('shop-gold').textContent = gold;

    // Display weapons
    const weaponsDiv = document.getElementById('shop-weapons');
    weaponsDiv.innerHTML = '';
    shop.weapons.forEach(item => {
        weaponsDiv.appendChild(createShopItem(item, 'weapons', gold));
    });

    // Display armor
    const armorDiv = document.getElementById('shop-armor');
    armorDiv.innerHTML = '';
    shop.armor.forEach(item => {
        armorDiv.appendChild(createShopItem(item, 'armor', gold));
    });

    // Display accessories
    const accessoriesDiv = document.getElementById('shop-accessories');
    accessoriesDiv.innerHTML = '';
    shop.accessories.forEach(item => {
        accessoriesDiv.appendChild(createShopItem(item, 'accessories', gold));
    });
}

function createShopItem(item, type, playerGold) {
    const itemDiv = document.createElement('div');
    itemDiv.className = 'shop-item';

    const infoDiv = document.createElement('div');
    infoDiv.className = 'shop-item-info';

    const nameDiv = document.createElement('div');
    nameDiv.className = `shop-item-name rarity-${item.rarity.toLowerCase()}`;
    nameDiv.textContent = `${item.rarity_icon} ${item.name}`;

    const statsDiv = document.createElement('div');
    statsDiv.className = 'shop-item-stats';

    if (type === 'weapons') {
        statsDiv.innerHTML = `Damage: ${item.damage} | Attack Bonus: +${item.attack_bonus}`;
    } else if (type === 'armor') {
        statsDiv.innerHTML = `AC Bonus: +${item.ac_bonus} | HP Bonus: +${item.hp_bonus}`;
    } else if (type === 'accessories') {
        const bonuses = Object.entries(item.stat_bonus).map(([stat, bonus]) =>
            `${stat.toUpperCase()} +${bonus}`
        ).join(', ');
        statsDiv.innerHTML = `Stats: ${bonuses}`;
    }

    const levelDiv = document.createElement('div');
    levelDiv.className = 'shop-item-stats';
    levelDiv.textContent = `Required Level: ${item.level}`;

    infoDiv.appendChild(nameDiv);
    infoDiv.appendChild(statsDiv);
    infoDiv.appendChild(levelDiv);

    const priceSpan = document.createElement('span');
    priceSpan.className = 'shop-item-price';
    priceSpan.textContent = `${item.price} 💰`;

    const buyBtn = document.createElement('button');
    buyBtn.className = 'buy-btn';
    buyBtn.textContent = 'Buy';
    buyBtn.onclick = () => buyItem(type, item.name, item.price);

    if (playerGold < item.price) {
        buyBtn.disabled = true;
    }

    itemDiv.appendChild(infoDiv);
    itemDiv.appendChild(priceSpan);
    itemDiv.appendChild(buyBtn);

    return itemDiv;
}

async function buyItem(type, name, price) {
    showLoading();

    try {
        const response = await fetch('/api/buy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: type,
                name: name
            })
        });

        const data = await response.json();

        if (data.success) {
            gameState.character = data.character;
            updateCharacterDisplay();
            addActionMessage(data.message);

            // Refresh shop with new gold amount
            openShop();
        } else {
            alert(data.error || 'Failed to purchase item');
        }
    } catch (error) {
        console.error('Error buying item:', error);
        alert('Failed to purchase item');
    } finally {
        hideLoading();
    }
}

async function equipItem(type, name) {
    showLoading();

    try {
        const response = await fetch('/api/equip', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: type,
                name: name
            })
        });

        const data = await response.json();

        if (data.success) {
            gameState.character = data.character;
            updateCharacterDisplay();
            addActionMessage(data.message);
        } else {
            alert(data.error || 'Failed to equip item');
        }
    } catch (error) {
        console.error('Error equipping item:', error);
        alert('Failed to equip item');
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

    // Shop button
    const shopBtn = document.getElementById('shop-btn');
    shopBtn.addEventListener('click', openShop);

    // Close shop modal
    const closeShop = document.getElementById('close-shop');
    closeShop.addEventListener('click', () => {
        document.getElementById('shop-modal').classList.add('hidden');
    });

    // Shop tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all tabs
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.shop-tab-content').forEach(c => c.classList.remove('active'));

            // Add active class to clicked tab
            btn.classList.add('active');
            const tab = btn.dataset.tab;
            document.getElementById(`shop-${tab}`).classList.add('active');
        });
    });

    // Close modal when clicking outside
    const shopModal = document.getElementById('shop-modal');
    shopModal.addEventListener('click', (e) => {
        if (e.target === shopModal) {
            shopModal.classList.add('hidden');
        }
    });
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
