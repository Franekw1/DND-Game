// Game State
const gameState = {
    score: 0,
    health: 100,
    gold: 0,
    kills: 0
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
    speed: 0.1,
    turnSpeed: 0.05,
    position: new THREE.Vector3(0, 1, 0),
    velocity: new THREE.Vector3(0, 0, 0),
    rotation: 0
};

camera.position.copy(player.position);
camera.position.y = player.height;

// Lighting - Much Brighter!
const ambientLight = new THREE.AmbientLight(0x666666, 1.2);
scene.add(ambientLight);

// Add directional light for overall brightness
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

    // Torch holder
    const torchGeometry = new THREE.CylinderGeometry(0.1, 0.1, 2, 8);
    const torchMaterial = new THREE.MeshStandardMaterial({ color: 0x4a2511 });
    const torchHolder = new THREE.Mesh(torchGeometry, torchMaterial);
    torchHolder.position.set(x, 1, z);
    torchHolder.castShadow = true;
    scene.add(torchHolder);

    // Flame effect
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

// Create ceiling
const ceilingGeometry = new THREE.PlaneGeometry(50, 50);
const ceilingMaterial = new THREE.MeshStandardMaterial({ color: 0x3a3a3a });
const ceiling = new THREE.Mesh(ceilingGeometry, ceilingMaterial);
ceiling.rotation.x = Math.PI / 2;
ceiling.position.y = 5;
ceiling.receiveShadow = true;
scene.add(ceiling);

// Create dungeon walls
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

// Create maze-like dungeon layout
const walls = [];
walls.push(createWall(0, 2.5, -25, 50, 5, 1)); // North wall
walls.push(createWall(0, 2.5, 25, 50, 5, 1));  // South wall
walls.push(createWall(-25, 2.5, 0, 1, 5, 50)); // West wall
walls.push(createWall(25, 2.5, 0, 1, 5, 50));  // East wall

// Interior walls for maze
walls.push(createWall(-10, 2.5, -10, 20, 5, 1));
walls.push(createWall(10, 2.5, 10, 20, 5, 1));
walls.push(createWall(-10, 2.5, 10, 1, 5, 20));
walls.push(createWall(10, 2.5, -10, 1, 5, 15));

// Add torches
const torches = [
    createTorch(-20, -20),
    createTorch(20, -20),
    createTorch(-20, 20),
    createTorch(20, 20),
    createTorch(0, 0),
    createTorch(-10, 0),
    createTorch(10, 0)
];

// Create treasure chests
const chests = [];
function createChest(x, z) {
    const chestGroup = new THREE.Group();

    // Chest base
    const baseGeometry = new THREE.BoxGeometry(1, 0.7, 0.7);
    const baseMaterial = new THREE.MeshStandardMaterial({ color: 0x8B4513 });
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    base.castShadow = true;
    chestGroup.add(base);

    // Chest lid
    const lidGeometry = new THREE.BoxGeometry(1, 0.3, 0.7);
    const lid = new THREE.Mesh(lidGeometry, baseMaterial);
    lid.position.y = 0.5;
    lid.castShadow = true;
    chestGroup.add(lid);

    // Gold trim
    const trimGeometry = new THREE.BoxGeometry(1.1, 0.1, 0.75);
    const trimMaterial = new THREE.MeshStandardMaterial({ color: 0xFFD700 });
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

// Create enemies (simple cubes with eyes)
const enemies = [];
function createEnemy(x, z) {
    const enemyGroup = new THREE.Group();

    // Body
    const bodyGeometry = new THREE.BoxGeometry(1, 2, 1);
    const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0x8B0000 });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.castShadow = true;
    enemyGroup.add(body);

    // Eyes
    const eyeGeometry = new THREE.SphereGeometry(0.1, 8, 8);
    const eyeMaterial = new THREE.MeshBasicMaterial({ color: 0xFFFF00 });

    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.2, 0.5, 0.5);
    enemyGroup.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.2, 0.5, 0.5);
    enemyGroup.add(rightEye);

    enemyGroup.position.set(x, 1, z);
    enemyGroup.userData = {
        type: 'enemy',
        health: 50,
        speed: 0.02,
        originalPos: new THREE.Vector3(x, 1, z)
    };
    scene.add(enemyGroup);
    enemies.push(enemyGroup);

    return enemyGroup;
}

createEnemy(-8, -8);
createEnemy(8, 8);
createEnemy(-8, 8);
createEnemy(5, -15);

// Controls
const keys = {};
window.addEventListener('keydown', (e) => {
    keys[e.key.toLowerCase()] = true;

    // Interact with nearby objects (E key)
    if (e.key.toLowerCase() === 'e') {
        interactWithNearbyObjects();
    }

    // Attack (Space key)
    if (e.key === ' ') {
        attackNearbyEnemies();
    }
});

window.addEventListener('keyup', (e) => {
    keys[e.key.toLowerCase()] = false;
});

// Mouse look controls
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

// Collision detection
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

// Interact with objects
function interactWithNearbyObjects() {
    const interactDistance = 3;

    for (const chest of chests) {
        const distance = player.position.distanceTo(chest.position);
        if (distance < interactDistance && !chest.userData.opened) {
            chest.userData.opened = true;
            gameState.gold += chest.userData.goldValue;
            gameState.score += chest.userData.goldValue;

            // Animate chest opening
            const lid = chest.children[1];
            lid.rotation.x = Math.PI / 3;
            lid.position.z -= 0.2;

            updateUI();
            console.log(`Opened chest! Found ${chest.userData.goldValue} gold!`);
        }
    }
}

// Attack enemies
function attackNearbyEnemies() {
    const attackDistance = 2.5;

    for (let i = enemies.length - 1; i >= 0; i--) {
        const enemy = enemies[i];
        const distance = player.position.distanceTo(enemy.position);

        if (distance < attackDistance) {
            enemy.userData.health -= 25;

            if (enemy.userData.health <= 0) {
                scene.remove(enemy);
                enemies.splice(i, 1);
                gameState.kills++;
                gameState.score += 100;
                gameState.gold += 20;
                updateUI();
                console.log('Enemy defeated! +100 points, +20 gold');
            } else {
                // Enemy flash red when hit
                enemy.children[0].material.emissive = new THREE.Color(0xff0000);
                setTimeout(() => {
                    if (enemy.children[0]) {
                        enemy.children[0].material.emissive = new THREE.Color(0x000000);
                    }
                }, 100);
            }
        }
    }
}

// Simple AI for enemies
function updateEnemies() {
    for (const enemy of enemies) {
        const distanceToPlayer = enemy.position.distanceTo(player.position);

        if (distanceToPlayer < 15) {
            // Chase player
            const direction = new THREE.Vector3()
                .subVectors(player.position, enemy.position)
                .normalize();

            const newPos = enemy.position.clone()
                .add(direction.multiplyScalar(enemy.userData.speed));

            // Check if enemy would collide with walls
            newPos.y = 1; // Keep at ground level
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

            // Look at player
            enemy.lookAt(player.position);

            // Damage player if too close
            if (distanceToPlayer < 1.5) {
                gameState.health -= 0.1;
                if (gameState.health < 0) gameState.health = 0;
                updateUI();
            }
        } else {
            // Return to original position
            const direction = new THREE.Vector3()
                .subVectors(enemy.userData.originalPos, enemy.position)
                .normalize();
            enemy.position.add(direction.multiplyScalar(enemy.userData.speed * 0.5));
        }

        // Bob up and down
        enemy.position.y = 1 + Math.sin(Date.now() * 0.003) * 0.1;
    }
}

// Update UI
function updateUI() {
    document.getElementById('health').textContent = Math.floor(gameState.health);
    document.getElementById('score').textContent = gameState.score;
    document.getElementById('gold').textContent = gameState.gold;
    document.getElementById('kills').textContent = gameState.kills;

    // Update health bar
    const healthBar = document.getElementById('health-bar');
    healthBar.style.width = gameState.health + '%';

    if (gameState.health < 30) {
        healthBar.style.backgroundColor = '#ff0000';
    } else if (gameState.health < 60) {
        healthBar.style.backgroundColor = '#ffaa00';
    } else {
        healthBar.style.backgroundColor = '#00ff00';
    }
}

// Animate torch flames
function animateTorches() {
    torches.forEach((torch, index) => {
        const time = Date.now() * 0.003 + index;
        torch.flame.position.y = 2.5 + Math.sin(time * 2) * 0.1;
        torch.flame.scale.set(
            1 + Math.sin(time * 3) * 0.1,
            1 + Math.cos(time * 2.5) * 0.15,
            1 + Math.sin(time * 3.2) * 0.1
        );
        torch.light.intensity = 1.5 + Math.sin(time * 4) * 0.3;
    });
}

// Game loop
function animate() {
    requestAnimationFrame(animate);

    // Player movement
    const moveSpeed = player.speed;
    const forward = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), player.rotation);
    const right = new THREE.Vector3(1, 0, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), player.rotation);

    let newPosition = player.position.clone();

    if (keys['w']) newPosition.add(forward.multiplyScalar(moveSpeed));
    if (keys['s']) newPosition.add(forward.multiplyScalar(-moveSpeed));
    if (keys['a']) newPosition.add(right.multiplyScalar(-moveSpeed));
    if (keys['d']) newPosition.add(right.multiplyScalar(moveSpeed));

    // Check collision before moving
    if (!checkCollision(newPosition)) {
        player.position.copy(newPosition);
    }

    // Update camera position
    camera.position.x = player.position.x;
    camera.position.y = player.position.y + player.height;
    camera.position.z = player.position.z;

    // Update enemies
    updateEnemies();

    // Animate torches
    animateTorches();

    // Check if player died
    if (gameState.health <= 0) {
        alert('Game Over! Final Score: ' + gameState.score);
        location.reload();
    }

    renderer.render(scene, camera);
}

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Start game
updateUI();
animate();

console.log('Welcome to the 3D DND Dungeon! Controls: WASD to move, Mouse to look, E to interact, Space to attack');
