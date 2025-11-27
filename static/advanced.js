// ============================================================================
// Advanced Features - Spells, Status Effects, Save/Load
// ============================================================================

function updateManaDisplay() {
    const char = gameState.character;
    if (!char) return;

    const manaBlock = document.getElementById('mana-block');
    const spellbookBtn = document.getElementById('spellbook-btn');

    if (char.max_mana && char.max_mana > 0) {
        manaBlock.style.display = 'block';
        spellbookBtn.style.display = 'block';

        const manaPercent = (char.current_mana / char.max_mana) * 100;
        document.getElementById('mana-bar').style.width = `${manaPercent}%`;
        document.getElementById('mana-text').textContent = `${char.current_mana}/${char.max_mana}`;
    } else {
        manaBlock.style.display = 'none';
        spellbookBtn.style.display = 'none';
    }
}

function updateStatusEffects() {
    const char = gameState.character;
    if (!char || !char.status_effects) return;

    const statusBlock = document.getElementById('status-effects-block');
    const statusList = document.getElementById('status-effects-list');

    const effects = Object.entries(char.status_effects);
    if (effects.length > 0) {
        statusBlock.style.display = 'block';
        statusList.innerHTML = '';

        effects.forEach(([effectName, turnsLeft]) => {
            const effectDiv = document.createElement('div');
            effectDiv.className = `status-effect ${effectName.toLowerCase()}`;
            effectDiv.textContent = `${effectName} (${turnsLeft})`;
            statusList.appendChild(effectDiv);
        });
    } else {
        statusBlock.style.display = 'none';
    }
}

async function openSpellbook() {
    showLoading();

    try {
        const char = gameState.character;
        if (!char || !char.known_spells || char.known_spells.length === 0) {
            alert('You do not know any spells!');
            hideLoading();
            return;
        }

        displaySpellbook(char);
        document.getElementById('spellbook-modal').classList.remove('hidden');
    } catch (error) {
        console.error('Error opening spellbook:', error);
        alert('Failed to open spellbook');
    } finally {
        hideLoading();
    }
}

function displaySpellbook(char) {
    document.getElementById('spell-mana').textContent = `${char.current_mana}/${char.max_mana}`;

    const spellList = document.getElementById('spell-list');
    spellList.innerHTML = '';

    // Spell data definitions
    const spellData = {
        'Wizard': {
            'Magic Missile': {level: 1, damage: '3d4+3', mana_cost: 2, description: 'Auto-hit arcane missiles', type: 'damage'},
            'Fireball': {level: 3, damage: '8d6', mana_cost: 5, description: 'Explosive fire damage', type: 'damage'},
            'Shield': {level: 1, ac_bonus: 5, duration: 1, mana_cost: 2, description: '+5 AC for 1 turn', type: 'buff'},
            'Lightning Bolt': {level: 3, damage: '8d6', mana_cost: 5, description: 'Chain lightning', type: 'damage'},
            'Haste': {level: 3, duration: 3, mana_cost: 4, description: 'Double attacks for 3 turns', type: 'buff'}
        },
        'Cleric': {
            'Cure Wounds': {level: 1, heal: '1d8+3', mana_cost: 2, description: 'Heal wounds', type: 'heal'},
            'Bless': {level: 1, attack_bonus: 1, duration: 3, mana_cost: 2, description: '+1 to attacks for 3 turns', type: 'buff'},
            'Sacred Flame': {level: 1, damage: '2d8', mana_cost: 1, description: 'Holy fire', type: 'damage'},
            'Mass Healing': {level: 3, heal: '3d8+5', mana_cost: 6, description: 'Heal entire party', type: 'heal'},
            'Divine Smite': {level: 2, damage: '4d8', mana_cost: 3, description: 'Holy damage', type: 'damage'}
        },
        'Paladin': {
            'Lay on Hands': {level: 1, heal: '2d8+2', mana_cost: 2, description: 'Heal yourself or ally', type: 'heal'},
            'Smite': {level: 1, damage: '2d8', mana_cost: 2, description: 'Holy weapon strike', type: 'damage'},
            'Protection': {level: 2, ac_bonus: 3, duration: 2, mana_cost: 3, description: '+3 AC for 2 turns', type: 'buff'}
        },
        'Bard': {
            'Vicious Mockery': {level: 1, damage: '1d4', mana_cost: 1, description: 'Damage and enemy disadvantage', type: 'damage'},
            'Healing Word': {level: 1, heal: '1d4+4', mana_cost: 2, description: 'Quick heal', type: 'heal'},
            'Inspiration': {level: 1, attack_bonus: 2, duration: 3, mana_cost: 2, description: '+2 to party attacks', type: 'buff'}
        },
        'Ranger': {
            'Hunters Mark': {level: 1, damage_bonus: '1d6', duration: 5, mana_cost: 2, description: 'Mark enemy for extra damage', type: 'buff'},
            'Cure Wounds': {level: 1, heal: '1d8+2', mana_cost: 2, description: 'Heal wounds', type: 'heal'}
        }
    };

    const classSpells = spellData[char.class] || {};

    char.known_spells.forEach(spellName => {
        const spell = classSpells[spellName];
        if (!spell) return;

        const spellDiv = document.createElement('div');
        spellDiv.className = 'spell-item';

        if (char.current_mana < spell.mana_cost) {
            spellDiv.classList.add('disabled');
        }

        spellDiv.innerHTML = `
            <div class="spell-name">
                ${spellName}
                <span class="spell-cost">${spell.mana_cost} Mana</span>
            </div>
            <div class="spell-description">${spell.description}</div>
            <div class="spell-stats">
                ${spell.damage ? `Damage: ${spell.damage}` : ''}
                ${spell.heal ? `Heal: ${spell.heal}` : ''}
                ${spell.ac_bonus ? `AC Bonus: +${spell.ac_bonus}` : ''}
                ${spell.duration ? ` for ${spell.duration} turns` : ''}
            </div>
        `;

        if (char.current_mana >= spell.mana_cost) {
            spellDiv.onclick = () => castSpell(spellName);
        }

        spellList.appendChild(spellDiv);
    });
}

async function castSpell(spellName) {
    showLoading();

    try {
        const response = await fetch('/api/cast_spell', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                spell_name: spellName,
                target: 'enemy'
            })
        });

        const data = await response.json();

        if (data.success) {
            gameState.character = data.character;
            updateCharacterDisplay();
            updateManaDisplay();
            updateStatusEffects();

            data.messages.forEach(msg => addActionMessage(msg));

            document.getElementById('spellbook-modal').classList.add('hidden');
            showDiceRoll(`Cast ${spellName}!`, 20);
        } else {
            alert(data.error || 'Failed to cast spell');
        }
    } catch (error) {
        console.error('Error casting spell:', error);
        alert('Failed to cast spell');
    } finally {
        hideLoading();
    }
}

async function saveGame() {
    showLoading();

    try {
        const response = await fetch('/api/save_game', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('save-data').value = JSON.stringify(data.save_data);
            document.getElementById('save-load-modal').classList.remove('hidden');
            addActionMessage('💾 Game saved! Copy the data from the text box.');
        }
    } catch (error) {
        console.error('Error saving game:', error);
        alert('Failed to save game');
    } finally {
        hideLoading();
    }
}

async function loadGame() {
    const saveDataText = document.getElementById('save-data').value;

    if (!saveDataText) {
        alert('Please paste save data first!');
        return;
    }

    showLoading();

    try {
        const saveData = JSON.parse(saveDataText);

        const response = await fetch('/api/load_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                save_data: saveData
            })
        });

        const data = await response.json();

        if (data.success) {
            gameState.character = data.character;
            updateCharacterDisplay();
            updateManaDisplay();
            updateStatusEffects();

            document.getElementById('save-load-modal').classList.add('hidden');
            addActionMessage('📂 Game loaded successfully!');

            // Switch to game screen
            showScreen('game-screen');
        }
    } catch (error) {
        console.error('Error loading game:', error);
        alert('Failed to load game. Make sure the save data is valid.');
    } finally {
        hideLoading();
    }
}

// Update character display to include new features
const originalUpdateCharacterDisplay = updateCharacterDisplay;
updateCharacterDisplay = function() {
    originalUpdateCharacterDisplay();
    updateManaDisplay();
    updateStatusEffects();
};

// Event listeners for new features
document.addEventListener('DOMContentLoaded', () => {
    // Spellbook button
    const spellbookBtn = document.getElementById('spellbook-btn');
    if (spellbookBtn) {
        spellbookBtn.addEventListener('click', openSpellbook);
    }

    // Close spellbook
    const closeSpellbook = document.getElementById('close-spellbook');
    if (closeSpellbook) {
        closeSpellbook.addEventListener('click', () => {
            document.getElementById('spellbook-modal').classList.add('hidden');
        });
    }

    // Save button
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveGame);
    }

    // Load button
    const loadBtn = document.getElementById('load-btn');
    if (loadBtn) {
        loadBtn.addEventListener('click', () => {
            document.getElementById('save-load-modal').classList.remove('hidden');
        });
    }

    // Close save/load modal
    const closeSaveLoad = document.getElementById('close-save-load');
    if (closeSaveLoad) {
        closeSaveLoad.addEventListener('click', () => {
            document.getElementById('save-load-modal').classList.add('hidden');
        });
    }

    // Copy save data
    const copySaveBtn = document.getElementById('copy-save-btn');
    if (copySaveBtn) {
        copySaveBtn.addEventListener('click', () => {
            const saveDataBox = document.getElementById('save-data');
            saveDataBox.select();
            document.execCommand('copy');
            addActionMessage('📋 Save data copied to clipboard!');
        });
    }

    // Load save data
    const loadSaveBtn = document.getElementById('load-save-btn');
    if (loadSaveBtn) {
        loadSaveBtn.addEventListener('click', loadGame);
    }
});
