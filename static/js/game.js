// Enhanced Game State
const gameState = {
    score: 0,
    health: 100,
    maxHealth: 100,
    gold: 0,
    kills: 0,
    level: 1,
    exp: 0,
    mana: 100,
    maxMana: 100,
    weapon: 'sword',
    shieldActive: false
};

// Initialize Three.js scene
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x1a1a1a, 10, 60);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Player setup
const player = {
    height: 1.8,
    speed: 0.15,
    turnSpeed: 0.05,
    position: new THREE.Vector3(0, 1, 0),
    velocity: new THREE.Vector3(0, 0, 0),
    rotation: 0
};

camera.position.copy(player.position);
camera.position.y = player.height;

// Particle system
const particles = [];

function createParticle(x, y, z, color, size = 0.2, velocity = null) {
    const geometry = new THREE.SphereGeometry(size, 8, 8);
    const material = new THREE.MeshBasicMaterial({ color: color });
    const particle = new THREE.Mesh(geometry, material);
    particle.position.set(x, y, z);

    if (!velocity) {
        velocity = new THREE.Vector3(
            (Math.random() - 0.5) * 0.2,
            Math.random() * 0.3,
            (Math.random() - 0.5) * 0.2
        );
    }

    particle.userData = {
        velocity: velocity,
        lifetime: 60,
        age: 0
    };

    scene.add(particle);
    particles.push(particle);
    return particle;
}

function updateParticles() {
    for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.userData.age++;

        p.position.add(p.userData.velocity);
        p.userData.velocity.y -= 0.01; // Gravity

        // Fade out
        p.material.opacity = 1 - (p.userData.age / p.userData.lifetime);
        p.material.transparent = true;

        if (p.userData.age >= p.userData.lifetime) {
            scene.remove(p);
            particles.splice(i, 1);
        }
    }
}

// Lighting - Much Brighter!
const ambientLight = new THREE.AmbientLight(0x666666, 1.2);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
directionalLight.position.set(5, 10, 5);
directionalLight.castShadow = true;
scene.add(directionalLight);

// Create torch lights in dungeon
function createTorch(x, z) {
    const torchLight = new THREE.PointLight(0xff8833, 3.5, 30);
    torchLight.position.set(x, 2, z);
    torchLight.castShadow = true;
    scene.add(torchLight);

    const torchGeometry = new THREE.CylinderGeometry(0.1, 0.1, 2, 8);
    const torchMaterial = new THREE.MeshStandardMaterial({ color: 0x4a2511 });
    const torchHolder = new THREE.Mesh(torchGeometry, torchMaterial);
    torchHolder.position.set(x, 1, z);
    torchHolder.castShadow = true;
    scene.add(torchHolder);

    const flameGeometry = new THREE.SphereGeometry(0.3, 8, 8);
    const flameMaterial = new THREE.MeshBasicMaterial({ color: 0xff6600 });
    const flame = new THREE.Mesh(flameGeometry, flameMaterial);
    flame.position.set(x, 2.5, z);
    scene.add(flame);

    return { light: torchLight, flame };
}

// Create dungeon floor
const floorGeometry = new THREE.PlaneGeometry(50, 50);
const floorTexture = new THREE.TextureLoader().load('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iIzMzMyIvPjxyZWN0IHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgZmlsbD0iIzI4MiIvPjxyZWN0IHg9IjUyIiB5PSI1MiIgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiBmaWxsPSIjMjgyIi8+PC9zdmc+');
floorTexture.wrapS = floorTexture.wrapT = THREE.RepeatWrapping;
floorTexture.repeat.set(10, 10);
const floorMaterial = new THREE.MeshStandardMaterial({ map: floorTexture });
const floor = new THREE.Mesh(floorGeometry, floorMaterial);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

const ceilingGeometry = new THREE.PlaneGeometry(50, 50);
const ceilingMaterial = new THREE.MeshStandardMaterial({ color: 0x3a3a3a });
const ceiling = new THREE.Mesh(ceilingGeometry, ceilingMaterial);
ceiling.rotation.x = Math.PI / 2;
ceiling.position.y = 5;
ceiling.receiveShadow = true;
scene.add(ceiling);

function createWall(x, y, z, width, height, depth, rotation = 0) {
    const geometry = new THREE.BoxGeometry(width, height, depth);
    const material = new THREE.MeshStandardMaterial({ color: 0x6a6a6a });
    const wall = new THREE.Mesh(geometry, material);
    wall.position.set(x, y, z);
    wall.rotation.y = rotation;
    wall.castShadow = true;
    wall.receiveShadow = true;
    scene.add(wall);
    return wall;
}

const walls = [];
walls.push(createWall(0, 2.5, -25, 50, 5, 1));
walls.push(createWall(0, 2.5, 25, 50, 5, 1));
walls.push(createWall(-25, 2.5, 0, 1, 5, 50));
walls.push(createWall(25, 2.5, 0, 1, 5, 50));
walls.push(createWall(-10, 2.5, -10, 20, 5, 1));
walls.push(createWall(10, 2.5, 10, 20, 5, 1));
walls.push(createWall(-10, 2.5, 10, 1, 5, 20));
walls.push(createWall(10, 2.5, -10, 1, 5, 15));

const torches = [
    createTorch(-20, -20), createTorch(20, -20),
    createTorch(-20, 20), createTorch(20, 20),
    createTorch(0, 0), createTorch(-10, 0), createTorch(10, 0)
];

// Health Potions
const potions = [];
function createPotion(x, z) {
    const group = new THREE.Group();

    const bottleGeom = new THREE.CylinderGeometry(0.2, 0.25, 0.6, 8);
    const bottleMat = new THREE.MeshStandardMaterial({
        color: 0xff0000,
        transparent: true,
        opacity: 0.7,
        emissive: 0xff0000,
        emissiveIntensity: 0.3
    });
    const bottle = new THREE.Mesh(bottleGeom, bottleMat);
    group.add(bottle);

    const capGeom = new THREE.CylinderGeometry(0.15, 0.15, 0.1, 8);
    const capMat = new THREE.MeshStandardMaterial({ color: 0x8B4513 });
    const cap = new THREE.Mesh(capGeom, capMat);
    cap.position.y = 0.35;
    group.add(cap);

    group.position.set(x, 0.3, z);
    group.userData = { type: 'potion', collected: false };
    scene.add(group);
    potions.push(group);
    return group;
}

createPotion(-18, -5);
createPotion(18, 5);
createPotion(-5, 18);
createPotion(5, -18);

// Enhanced treasure chests
const chests = [];
function createChest(x, z) {
    const chestGroup = new THREE.Group();

    const baseGeometry = new THREE.BoxGeometry(1, 0.7, 0.7);
    const baseMaterial = new THREE.MeshStandardMaterial({ color: 0x8B4513 });
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    base.castShadow = true;
    chestGroup.add(base);

    const lidGeometry = new THREE.BoxGeometry(1, 0.3, 0.7);
    const lid = new THREE.Mesh(lidGeometry, baseMaterial);
    lid.position.y = 0.5;
    lid.castShadow = true;
    chestGroup.add(lid);

    const trimGeometry = new THREE.BoxGeometry(1.1, 0.1, 0.75);
    const trimMaterial = new THREE.MeshStandardMaterial({
        color: 0xFFD700,
        emissive: 0xFFD700,
        emissiveIntensity: 0.3
    });
    const trim = new THREE.Mesh(trimGeometry, trimMaterial);
    chestGroup.add(trim);

    chestGroup.position.set(x, 0.5, z);
    chestGroup.userData = { type: 'chest', opened: false, goldValue: Math.floor(Math.random() * 50) + 10 };
    scene.add(chestGroup);
    chests.push(chestGroup);
    return chestGroup;
}

createChest(-15, -15);
createChest(15, 15);
createChest(-15, 15);
createChest(12, -12);

// Enhanced enemies with better models
const enemies = [];
function createEnemy(x, z, type = 'normal') {
    const enemyGroup = new THREE.Group();

    if (type === 'boss') {
        // Boss enemy - larger and more detailed
        const bodyGeometry = new THREE.BoxGeometry(1.5, 2.5, 1.5);
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: 0x8B0000,
            emissive: 0x330000,
            emissiveIntensity: 0.5
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.castShadow = true;
        enemyGroup.add(body);

        // Shoulder spikes
        for (let i = 0; i < 4; i++) {
            const spikeGeom = new THREE.ConeGeometry(0.15, 0.5, 8);
            const spike = new THREE.Mesh(spikeGeom, bodyMaterial);
            const angle = (i / 4) * Math.PI * 2;
            spike.position.set(Math.cos(angle) * 0.75, 1, Math.sin(angle) * 0.75);
            spike.rotation.z = Math.PI / 2;
            enemyGroup.add(spike);
        }

        enemyGroup.userData = {
            type: 'boss',
            health: 150,
            speed: 0.015,
            damage: 0.2,
            originalPos: new THREE.Vector3(x, 1, z)
        };
    } else {
        // Normal enemy
        const bodyGeometry = new THREE.BoxGeometry(1, 2, 1);
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: 0x8B0000,
            emissive: 0x220000,
            emissiveIntensity: 0.3
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.castShadow = true;
        enemyGroup.add(body);

        // Arms
        const armGeom = new THREE.BoxGeometry(0.3, 1, 0.3);
        const leftArm = new THREE.Mesh(armGeom, bodyMaterial);
        leftArm.position.set(-0.65, -0.3, 0);
        enemyGroup.add(leftArm);

        const rightArm = new THREE.Mesh(armGeom, bodyMaterial);
        rightArm.position.set(0.65, -0.3, 0);
        enemyGroup.add(rightArm);

        enemyGroup.userData = {
            type: 'normal',
            health: 50,
            speed: 0.02,
            damage: 0.1,
            originalPos: new THREE.Vector3(x, 1, z)
        };
    }

    // Eyes (for all enemy types)
    const eyeGeometry = new THREE.SphereGeometry(0.1, 8, 8);
    const eyeMaterial = new THREE.MeshBasicMaterial({ color: 0xFFFF00 });

    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.2, 0.5, 0.5);
    enemyGroup.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.2, 0.5, 0.5);
    enemyGroup.add(rightEye);

    enemyGroup.position.set(x, 1, z);
    scene.add(enemyGroup);
    enemies.push(enemyGroup);
    return enemyGroup;
}

createEnemy(-8, -8);
createEnemy(8, 8);
createEnemy(-8, 8);
createEnemy(5, -15);
createEnemy(15, -8, 'boss'); // Boss enemy!

// Fireballs
const fireballs = [];
function createFireball(startPos, direction) {
    const group = new THREE.Group();

    const core = new THREE.Mesh(
        new THREE.SphereGeometry(0.3, 16, 16),
        new THREE.MeshBasicMaterial({ color: 0xff4400 })
    );
    group.add(core);

    const glow = new THREE.Mesh(
        new THREE.SphereGeometry(0.5, 16, 16),
        new THREE.MeshBasicMaterial({
            color: 0xff8800,
            transparent: true,
            opacity: 0.4
        })
    );
    group.add(glow);

    const light = new THREE.PointLight(0xff4400, 2, 10);
    group.add(light);

    group.position.copy(startPos);
    group.userData = {
        direction: direction.clone(),
        speed: 0.5,
        lifetime: 120,
        age: 0
    };

    scene.add(group);
    fireballs.push(group);
    return group;
}

function updateFireballs() {
    for (let i = fireballs.length - 1; i >= 0; i--) {
        const fb = fireballs[i];
        fb.userData.age++;

        fb.position.add(fb.userData.direction.clone().multiplyScalar(fb.userData.speed));

        // Create fire trail particles
        if (Math.random() < 0.3) {
            createParticle(fb.position.x, fb.position.y, fb.position.z, 0xff4400, 0.15);
        }

        // Check collision with enemies
        for (let j = enemies.length - 1; j >= 0; j--) {
            const enemy = enemies[j];
            if (fb.position.distanceTo(enemy.position) < 1.5) {
                damageEnemy(enemy, 50);
                scene.remove(fb);
                fireballs.splice(i, 1);

                // Explosion particles
                for (let k = 0; k < 20; k++) {
                    createParticle(
                        fb.position.x,
                        fb.position.y,
                        fb.position.z,
                        0xff4400,
                        0.2
                    );
                }
                break;
            }
        }

        // Check collision with walls
        for (const wall of walls) {
            const wallBox = new THREE.Box3().setFromObject(wall);
            const fbBox = new THREE.Box3().setFromObject(fb);
            if (wallBox.intersectsBox(fbBox)) {
                scene.remove(fb);
                fireballs.splice(i, 1);
                break;
            }
        }

        if (fb.userData.age >= fb.userData.lifetime) {
            scene.remove(fb);
            fireballs.splice(i, 1);
        }
    }
}

// Controls
const keys = {};
window.addEventListener('keydown', (e) => {
    keys[e.key.toLowerCase()] = true;

    if (e.key.toLowerCase() === 'e') {
        interactWithNearbyObjects();
    }

    if (e.key === ' ') {
        attackNearbyEnemies();
    }

    // Fireball spell (Q key)
    if (e.key.toLowerCase() === 'q') {
        castFireball();
    }

    // Shield (F key)
    if (e.key.toLowerCase() === 'f') {
        toggleShield();
    }

    // Switch weapon (R key)
    if (e.key.toLowerCase() === 'r') {
        switchWeapon();
    }
});

window.addEventListener('keyup', (e) => {
    keys[e.key.toLowerCase()] = false;
});

let mouseLocked = false;
document.addEventListener('click', () => {
    if (!mouseLocked) {
        renderer.domElement.requestPointerLock();
    }
});

document.addEventListener('pointerlockchange', () => {
    mouseLocked = document.pointerLockElement === renderer.domElement;
});

document.addEventListener('mousemove', (e) => {
    if (mouseLocked) {
        player.rotation -= e.movementX * 0.002;
        camera.rotation.y = player.rotation;
    }
});

// Shield system
let shieldMesh = null;
function toggleShield() {
    if (gameState.mana < 20) {
        showNotification('Not enough mana!', 'warning');
        return;
    }

    gameState.shieldActive = !gameState.shieldActive;

    if (gameState.shieldActive) {
        if (!shieldMesh) {
            const shieldGeom = new THREE.SphereGeometry(1.5, 16, 16);
            const shieldMat = new THREE.MeshBasicMaterial({
                color: 0x00ffff,
                transparent: true,
                opacity: 0.3,
                wireframe: true
            });
            shieldMesh = new THREE.Mesh(shieldGeom, shieldMat);
        }
        shieldMesh.position.copy(player.position);
        scene.add(shieldMesh);
        showNotification('Shield activated!', 'success');
    } else {
        if (shieldMesh) {
            scene.remove(shieldMesh);
        }
        showNotification('Shield deactivated', 'info');
    }
    updateUI();
}

function switchWeapon() {
    const weapons = ['sword', 'staff', 'bow'];
    const currentIndex = weapons.indexOf(gameState.weapon);
    gameState.weapon = weapons[(currentIndex + 1) % weapons.length];
    showNotification(`Switched to ${gameState.weapon}!`, 'info');
    updateUI();
}

function castFireball() {
    if (gameState.mana < 25) {
        showNotification('Not enough mana!', 'warning');
        return;
    }

    gameState.mana -= 25;
    const direction = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), player.rotation);
    const startPos = player.position.clone().add(new THREE.Vector3(0, 1, 0)).add(direction);
    createFireball(startPos, direction);
    showNotification('Fireball cast!', 'magic');
    updateUI();
}

function checkCollision(position) {
    for (const wall of walls) {
        const wallBox = new THREE.Box3().setFromObject(wall);
        const playerBox = new THREE.Box3(
            new THREE.Vector3(position.x - 0.5, position.y - player.height, position.z - 0.5),
            new THREE.Vector3(position.x + 0.5, position.y, position.z + 0.5)
        );
        if (wallBox.intersectsBox(playerBox)) {
            return true;
        }
    }
    return false;
}

function interactWithNearbyObjects() {
    const interactDistance = 3;

    // Chests
    for (const chest of chests) {
        const distance = player.position.distanceTo(chest.position);
        if (distance < interactDistance && !chest.userData.opened) {
            chest.userData.opened = true;
            gameState.gold += chest.userData.goldValue;
            gameState.score += chest.userData.goldValue;

            const lid = chest.children[1];
            lid.rotation.x = Math.PI / 3;
            lid.position.z -= 0.2;

            for (let i = 0; i < 15; i++) {
                createParticle(chest.position.x, chest.position.y + 0.5, chest.position.z, 0xFFD700, 0.15);
            }

            showNotification(`+${chest.userData.goldValue} gold!`, 'success');
            updateUI();
        }
    }

    // Potions
    for (const potion of potions) {
        const distance = player.position.distanceTo(potion.position);
        if (distance < interactDistance && !potion.userData.collected) {
            potion.userData.collected = true;
            scene.remove(potion);

            const healAmount = 30;
            gameState.health = Math.min(gameState.maxHealth, gameState.health + healAmount);

            for (let i = 0; i < 10; i++) {
                createParticle(potion.position.x, potion.position.y, potion.position.z, 0x00ff00, 0.2);
            }

            showNotification(`+${healAmount} health!`, 'success');
            updateUI();
        }
    }
}

function attackNearbyEnemies() {
    const attackDistance = gameState.weapon === 'bow' ? 15 : 2.5;
    const damage = gameState.weapon === 'sword' ? 25 : gameState.weapon === 'staff' ? 35 : 20;

    for (let i = enemies.length - 1; i >= 0; i--) {
        const enemy = enemies[i];
        const distance = player.position.distanceTo(enemy.position);

        if (distance < attackDistance) {
            damageEnemy(enemy, damage);
        }
    }
}

function damageEnemy(enemy, damage) {
    enemy.userData.health -= damage;

    // Hit particles
    for (let j = 0; j < 10; j++) {
        createParticle(enemy.position.x, enemy.position.y + 1, enemy.position.z, 0xff0000, 0.15);
    }

    if (enemy.userData.health <= 0) {
        // Death particles
        for (let j = 0; j < 30; j++) {
            createParticle(enemy.position.x, enemy.position.y + 1, enemy.position.z, 0x8B0000, 0.2);
        }

        scene.remove(enemy);
        const enemyIndex = enemies.indexOf(enemy);
        if (enemyIndex > -1) enemies.splice(enemyIndex, 1);

        const expGain = enemy.userData.type === 'boss' ? 100 : 20;
        const goldGain = enemy.userData.type === 'boss' ? 50 : 20;

        gameState.kills++;
        gameState.score += expGain * 5;
        gameState.gold += goldGain;
        gameState.exp += expGain;

        if (gameState.exp >= gameState.level * 100) {
            levelUp();
        }

        showNotification(`Enemy defeated! +${expGain} XP`, 'success');
        updateUI();
    } else {
        enemy.children[0].material.emissive = new THREE.Color(0xff0000);
        setTimeout(() => {
            if (enemy.children[0]) {
                enemy.children[0].material.emissive = new THREE.Color(enemy.userData.type === 'boss' ? 0x330000 : 0x220000);
            }
        }, 100);
    }
}

function levelUp() {
    gameState.level++;
    gameState.exp = 0;
    gameState.maxHealth += 20;
    gameState.health = gameState.maxHealth;
    gameState.maxMana += 20;
    gameState.mana = gameState.maxMana;

    showNotification(`LEVEL UP! Now level ${gameState.level}!`, 'levelup');

    for (let i = 0; i < 50; i++) {
        createParticle(player.position.x, player.position.y + 1, player.position.z, 0xFFD700, 0.2);
    }
    updateUI();
}

function updateEnemies() {
    for (const enemy of enemies) {
        const distanceToPlayer = enemy.position.distanceTo(player.position);

        if (distanceToPlayer < 15) {
            const direction = new THREE.Vector3()
                .subVectors(player.position, enemy.position)
                .normalize();

            const newPos = enemy.position.clone()
                .add(direction.multiplyScalar(enemy.userData.speed));

            newPos.y = 1;
            let collision = false;
            for (const wall of walls) {
                const wallBox = new THREE.Box3().setFromObject(wall);
                const enemyBox = new THREE.Box3(
                    new THREE.Vector3(newPos.x - 0.5, 0, newPos.z - 0.5),
                    new THREE.Vector3(newPos.x + 0.5, 2, newPos.z + 0.5)
                );
                if (wallBox.intersectsBox(enemyBox)) {
                    collision = true;
                    break;
                }
            }

            if (!collision) {
                enemy.position.copy(newPos);
            }

            enemy.lookAt(player.position);

            if (distanceToPlayer < 1.5) {
                if (!gameState.shieldActive) {
                    gameState.health -= enemy.userData.damage;
                    if (gameState.health < 0) gameState.health = 0;
                    updateUI();
                }
            }
        } else {
            const direction = new THREE.Vector3()
                .subVectors(enemy.userData.originalPos, enemy.position)
                .normalize();
            enemy.position.add(direction.multiplyScalar(enemy.userData.speed * 0.5));
        }

        enemy.position.y = 1 + Math.sin(Date.now() * 0.003) * 0.1;
    }
}

function updateUI() {
    document.getElementById('health').textContent = Math.floor(gameState.health);
    document.getElementById('score').textContent = gameState.score;
    document.getElementById('gold').textContent = gameState.gold;
    document.getElementById('kills').textContent = gameState.kills;
    document.getElementById('level').textContent = gameState.level;
    document.getElementById('exp').textContent = gameState.exp + '/' + (gameState.level * 100);
    document.getElementById('mana').textContent = Math.floor(gameState.mana);
    document.getElementById('weapon').textContent = gameState.weapon.toUpperCase();

    const healthBar = document.getElementById('health-bar');
    healthBar.style.width = (gameState.health / gameState.maxHealth * 100) + '%';

    if (gameState.health < 30) {
        healthBar.style.backgroundColor = '#ff0000';
    } else if (gameState.health < 60) {
        healthBar.style.backgroundColor = '#ffaa00';
    } else {
        healthBar.style.backgroundColor = '#00ff00';
    }

    const manaBar = document.getElementById('mana-bar');
    manaBar.style.width = (gameState.mana / gameState.maxMana * 100) + '%';
}

// Notifications
function showNotification(message, type = 'info') {
    const notif = document.createElement('div');
    notif.className = 'notification ' + type;
    notif.textContent = message;
    document.body.appendChild(notif);

    setTimeout(() => notif.classList.add('show'), 10);
    setTimeout(() => {
        notif.classList.remove('show');
        setTimeout(() => document.body.removeChild(notif), 300);
    }, 2000);
}

function animateTorches() {
    torches.forEach((torch, index) => {
        const time = Date.now() * 0.003 + index;
        torch.flame.position.y = 2.5 + Math.sin(time * 2) * 0.1;
        torch.flame.scale.set(
            1 + Math.sin(time * 3) * 0.1,
            1 + Math.cos(time * 2.5) * 0.15,
            1 + Math.sin(time * 3.2) * 0.1
        );
        torch.light.intensity = 3.5 + Math.sin(time * 4) * 0.3;
    });
}

// Game loop
function animate() {
    requestAnimationFrame(animate);

    const moveSpeed = player.speed;
    const forward = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), player.rotation);
    const right = new THREE.Vector3(1, 0, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), player.rotation);

    let newPosition = player.position.clone();

    if (keys['w']) newPosition.add(forward.multiplyScalar(moveSpeed));
    if (keys['s']) newPosition.add(forward.multiplyScalar(-moveSpeed));
    if (keys['a']) newPosition.add(right.multiplyScalar(-moveSpeed));
    if (keys['d']) newPosition.add(right.multiplyScalar(moveSpeed));

    if (!checkCollision(newPosition)) {
        player.position.copy(newPosition);
    }

    camera.position.x = player.position.x;
    camera.position.y = player.position.y + player.height;
    camera.position.z = player.position.z;

    if (shieldMesh && gameState.shieldActive) {
        shieldMesh.position.copy(player.position);
        shieldMesh.rotation.y += 0.02;
        gameState.mana -= 0.1;
        if (gameState.mana <= 0) {
            gameState.mana = 0;
            toggleShield();
        }
    } else if (!gameState.shieldActive && gameState.mana < gameState.maxMana) {
        gameState.mana += 0.2;
        if (gameState.mana > gameState.maxMana) gameState.mana = gameState.maxMana;
    }

    updateEnemies();
    animateTorches();
    updateParticles();
    updateFireballs();

    if (Math.floor(Date.now() / 100) % 5 === 0) {
        updateUI();
    }

    if (gameState.health <= 0) {
        showNotification('GAME OVER! Final Score: ' + gameState.score, 'gameover');
        setTimeout(() => location.reload(), 3000);
    }

    renderer.render(scene, camera);
}

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

updateUI();
animate();

console.log('🐉 Enhanced 3D DND Dungeon!');
console.log('Controls: WASD - Move | Mouse - Look | Space - Attack | E - Interact');
console.log('Q - Fireball | F - Shield | R - Switch Weapon');
