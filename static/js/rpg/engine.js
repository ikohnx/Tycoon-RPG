const RPGEngine = (function() {
    const TILE_SIZE = 16;
    const SCALE = 3;
    const SCALED_TILE = TILE_SIZE * SCALE;
    const PLAYER_SPEED = 2;
    const ANIM_FRAME_DURATION = 150;

    let canvas, ctx;
    let camera = { x: 0, y: 0 };
    let currentMap = null;
    let player = null;
    let npcs = [];
    let interactCallback = null;
    let transitionCallback = null;
    let dialogueActive = false;
    let dialogueQueue = [];
    let currentDialogue = null;
    let dialogueCharIndex = 0;
    let dialogueTimer = 0;
    let dialogueSpeed = 25;
    let keys = {};
    let lastTime = 0;
    let animFrame = 0;
    let animTimer = 0;
    let gameRunning = false;
    let onScreenControls = { up: false, down: false, left: false, right: false, action: false };
    let mapTransitions = [];
    let hudData = {};
    let screenFlash = null;
    let transitionCooldown = 0;
    let globalTime = 0;

    let choiceActive = false;
    let choiceOptions = [];
    let choiceIndex = 0;
    let choiceCallback = null;

    let stepSoundTimer = 0;

    const PAL = {
        grass1: '#2a8c2a', grass2: '#1e7a1e', grass3: '#38a838', grassDk: '#186818',
        path1: '#c8a870', path2: '#b89860', path3: '#a08050', pathEdge: '#907040',
        water1: '#2850a8', water2: '#3060b8', water3: '#2040a0', waterFoam: '#90b8e8',
        wall1: '#808898', wall2: '#707888', wall3: '#909aa8', wallLine: '#606878',
        roof1: '#a83030', roof2: '#c84040', roof3: '#882020', roofLine: '#701818',
        door1: '#704020', door2: '#905828', doorKnob: '#e8c840',
        window1: '#58a0d8', window2: '#78c0f0', windowFrame: '#505868',
        wood1: '#886030', wood2: '#a87840', wood3: '#685020',
        stone1: '#787878', stone2: '#989898', stone3: '#585858',
        tree1: '#186028', tree2: '#208038', tree3: '#105018', trunk1: '#604020', trunk2: '#785030',
        flower_r: '#e83850', flower_y: '#e8c020', flower_p: '#b838e8', flower_w: '#f0e8f0',
        sand1: '#d8b868', sand2: '#c8a858',
        sign1: '#a87840', sign2: '#c89050', signPost: '#604020',
        portal1: '#5828a8', portal2: '#7838d8', portal3: '#a058f0',
        hedge1: '#186020', hedge2: '#207030',
        chest1: '#c89030', chest2: '#a87020', chestLock: '#e8d050',
        black: '#000000', white: '#ffffff',
        dialogBg1: '#000848', dialogBg2: '#101070', dialogBorder1: '#e8e8f0', dialogBorder2: '#8888c0', dialogBorder3: '#484888',
        dialogText: '#ffffff', dialogShadow: '#000030',
        hudBg: '#000840', hudBorder: '#b0b0d0', hudGold: '#e8c020', hudGreen: '#40d840', hudRed: '#e84040', hudBlue: '#50a0f0',
        nameGold: '#f0d850',
        choiceBg: '#101060', choiceBorder: '#c0c0e0', choiceCursor: '#e8e8f0',
        shadow: 'rgba(0,0,0,0.25)'
    };

    function init(canvasId, options = {}) {
        canvas = document.getElementById(canvasId);
        if (!canvas) return;
        ctx = canvas.getContext('2d');
        ctx.imageSmoothingEnabled = false;

        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        window.addEventListener('keydown', e => {
            keys[e.key] = true;
            if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' ','Enter'].includes(e.key)) {
                e.preventDefault();
            }
            if (choiceActive) {
                if (e.key === 'ArrowUp' || e.key === 'w') { choiceIndex = Math.max(0, choiceIndex - 1); }
                if (e.key === 'ArrowDown' || e.key === 's') { choiceIndex = Math.min(choiceOptions.length - 1, choiceIndex + 1); }
                if (e.key === 'Enter' || e.key === ' ') { resolveChoice(); }
                if (e.key === 'Escape' || e.key === 'b' || e.key === 'B') { choiceIndex = choiceOptions.length - 1; resolveChoice(); }
                return;
            }
            if ((e.key === 'Enter' || e.key === ' ') && dialogueActive) {
                advanceDialogue();
            }
            if ((e.key === 'Enter' || e.key === ' ') && !dialogueActive) {
                tryInteract();
            }
        });
        window.addEventListener('keyup', e => { keys[e.key] = false; });

        if (options.onInteract) interactCallback = options.onInteract;
        if (options.onTransition) transitionCallback = options.onTransition;
        if (options.hudData) hudData = options.hudData;

        setupTouchControls();
    }

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        ctx.imageSmoothingEnabled = false;
    }

    function setupTouchControls() {
        const dpad = document.getElementById('dpad');
        if (!dpad) return;

        function setDir(dir, val) { onScreenControls[dir] = val; }

        ['up','down','left','right'].forEach(dir => {
            const btn = document.getElementById('dpad-' + dir);
            if (!btn) return;
            btn.addEventListener('touchstart', e => { e.preventDefault(); setDir(dir, true); });
            btn.addEventListener('touchend', e => { e.preventDefault(); setDir(dir, false); });
            btn.addEventListener('mousedown', e => { setDir(dir, true); });
            btn.addEventListener('mouseup', e => { setDir(dir, false); });
        });

        const actionBtn = document.getElementById('btn-action');
        if (actionBtn) {
            actionBtn.addEventListener('touchstart', e => {
                e.preventDefault();
                if (choiceActive) { resolveChoice(); return; }
                if (dialogueActive) advanceDialogue();
                else tryInteract();
            });
            actionBtn.addEventListener('click', e => {
                if (choiceActive) { resolveChoice(); return; }
                if (dialogueActive) advanceDialogue();
                else tryInteract();
            });
        }

        const cancelBtn = document.getElementById('btn-cancel');
        if (cancelBtn) {
            cancelBtn.addEventListener('touchstart', e => {
                e.preventDefault();
                if (choiceActive) { choiceIndex = choiceOptions.length - 1; resolveChoice(); }
            });
            cancelBtn.addEventListener('click', e => {
                if (choiceActive) { choiceIndex = choiceOptions.length - 1; resolveChoice(); }
            });
        }

        ['up','down'].forEach(dir => {
            const btn = document.getElementById('dpad-' + dir);
            if (!btn) return;
            btn.addEventListener('touchstart', e => {
                if (choiceActive) {
                    e.preventDefault();
                    if (dir === 'up') choiceIndex = Math.max(0, choiceIndex - 1);
                    if (dir === 'down') choiceIndex = Math.min(choiceOptions.length - 1, choiceIndex + 1);
                }
            }, { capture: true });
        });
    }

    function loadMap(mapData) {
        currentMap = mapData;
        npcs = [];
        mapTransitions = mapData.transitions || [];

        if (mapData.npcs) {
            mapData.npcs.forEach(npcData => {
                npcs.push({
                    ...npcData,
                    animFrame: 0,
                    animTimer: 0,
                    idleTimer: Math.random() * 3000,
                    facing: npcData.facing || 'down'
                });
            });
        }

        if (!player) {
            player = {
                x: (mapData.spawnX || 5) * SCALED_TILE,
                y: (mapData.spawnY || 5) * SCALED_TILE,
                facing: 'down',
                moving: false,
                animFrame: 0,
                animTimer: 0,
                spriteType: mapData.playerSprite || 'hero'
            };
        } else {
            if (mapData.spawnX !== undefined) player.x = mapData.spawnX * SCALED_TILE;
            if (mapData.spawnY !== undefined) player.y = mapData.spawnY * SCALED_TILE;
        }
    }

    function start() {
        if (gameRunning) return;
        gameRunning = true;
        lastTime = performance.now();
        requestAnimationFrame(gameLoop);
    }

    function stop() { gameRunning = false; }

    function gameLoop(timestamp) {
        if (!gameRunning) return;
        const dt = timestamp - lastTime;
        lastTime = timestamp;
        globalTime += dt;
        update(dt);
        render();
        requestAnimationFrame(gameLoop);
    }

    function update(dt) {
        if (choiceActive) return;
        if (dialogueActive) { updateDialogue(dt); return; }
        updatePlayer(dt);
        updateNPCs(dt);
        updateCamera();
        checkTransitions();
        if (screenFlash) { screenFlash.timer -= dt; if (screenFlash.timer <= 0) screenFlash = null; }
        if (transitionCooldown > 0) transitionCooldown -= dt;
    }

    function updatePlayer(dt) {
        let dx = 0, dy = 0;
        let moving = false;

        if (keys['ArrowUp'] || keys['w'] || onScreenControls.up) { dy = -PLAYER_SPEED * SCALE; player.facing = 'up'; moving = true; }
        if (keys['ArrowDown'] || keys['s'] || onScreenControls.down) { dy = PLAYER_SPEED * SCALE; player.facing = 'down'; moving = true; }
        if (keys['ArrowLeft'] || keys['a'] || onScreenControls.left) { dx = -PLAYER_SPEED * SCALE; player.facing = 'left'; moving = true; }
        if (keys['ArrowRight'] || keys['d'] || onScreenControls.right) { dx = PLAYER_SPEED * SCALE; player.facing = 'right'; moving = true; }

        player.moving = moving;

        if (moving) {
            player.animTimer += dt;
            if (player.animTimer >= ANIM_FRAME_DURATION) {
                player.animTimer = 0;
                player.animFrame = (player.animFrame + 1) % 4;
            }
        } else {
            player.animFrame = 0;
            player.animTimer = 0;
        }

        if (dx !== 0 && dy !== 0) { dx *= 0.707; dy *= 0.707; }

        let newX = player.x + dx;
        let newY = player.y + dy;

        const pw = SCALED_TILE * 0.5;
        const ph = SCALED_TILE * 0.3;
        const pox = (SCALED_TILE - pw) / 2;
        const poy = SCALED_TILE * 0.6;

        if (!checkCollision(newX + pox, player.y + poy, pw, ph)) player.x = newX;
        if (!checkCollision(player.x + pox, newY + poy, pw, ph)) player.y = newY;

        const mapW = currentMap.width * SCALED_TILE;
        const mapH = currentMap.height * SCALED_TILE;
        player.x = Math.max(0, Math.min(mapW - SCALED_TILE, player.x));
        player.y = Math.max(0, Math.min(mapH - SCALED_TILE, player.y));
    }

    function checkCollision(x, y, w, h) {
        if (!currentMap || !currentMap.collision) return false;

        const startCol = Math.floor(x / SCALED_TILE);
        const endCol = Math.floor((x + w - 1) / SCALED_TILE);
        const startRow = Math.floor(y / SCALED_TILE);
        const endRow = Math.floor((y + h - 1) / SCALED_TILE);

        for (let row = startRow; row <= endRow; row++) {
            for (let col = startCol; col <= endCol; col++) {
                if (row < 0 || row >= currentMap.height || col < 0 || col >= currentMap.width) return true;
                if (currentMap.collision[row] && currentMap.collision[row][col] === 1) return true;
            }
        }

        for (let i = 0; i < npcs.length; i++) {
            const npc = npcs[i];
            const nx = npc.x * SCALED_TILE;
            const ny = npc.y * SCALED_TILE;
            if (x < nx + SCALED_TILE * 0.7 && x + w > nx + SCALED_TILE * 0.3 &&
                y < ny + SCALED_TILE * 0.7 && y + h > ny + SCALED_TILE * 0.3) {
                return true;
            }
        }
        return false;
    }

    function updateNPCs(dt) {
        npcs.forEach(npc => {
            npc.idleTimer = (npc.idleTimer || 0) + dt;
            if (npc.idleTimer >= 3000 + Math.random() * 2000) {
                npc.idleTimer = 0;
                if (!npc.stationary) {
                    const dirs = ['up','down','left','right'];
                    npc.facing = dirs[Math.floor(Math.random() * dirs.length)];
                }
                npc.animFrame = (npc.animFrame || 0) === 0 ? 1 : 0;
            }
        });
    }

    function updateCamera() {
        const targetX = player.x - canvas.width / 2 + SCALED_TILE / 2;
        const targetY = player.y - canvas.height / 2 + SCALED_TILE / 2;
        camera.x += (targetX - camera.x) * 0.08;
        camera.y += (targetY - camera.y) * 0.08;
        const mapW = currentMap.width * SCALED_TILE;
        const mapH = currentMap.height * SCALED_TILE;
        camera.x = Math.max(0, Math.min(mapW - canvas.width, camera.x));
        camera.y = Math.max(0, Math.min(mapH - canvas.height, camera.y));
    }

    function checkTransitions() {
        if (transitionCooldown > 0) return;
        const ptx = Math.floor((player.x + SCALED_TILE / 2) / SCALED_TILE);
        const pty = Math.floor((player.y + SCALED_TILE / 2) / SCALED_TILE);
        for (let t of mapTransitions) {
            if (ptx === t.x && pty === t.y) {
                if (transitionCallback) {
                    transitionCooldown = 1000;
                    screenFlash = { color: '#000000', timer: 500, maxTimer: 500 };
                    transitionCallback(t.target, t.spawnX, t.spawnY);
                }
                return;
            }
        }
    }

    function tryInteract() {
        if (!player || dialogueActive || choiceActive) return;
        let fx = Math.floor((player.x + SCALED_TILE / 2) / SCALED_TILE);
        let fy = Math.floor((player.y + SCALED_TILE / 2) / SCALED_TILE);
        switch (player.facing) {
            case 'up': fy -= 1; break;
            case 'down': fy += 1; break;
            case 'left': fx -= 1; break;
            case 'right': fx += 1; break;
        }

        for (let npc of npcs) {
            if (npc.x === fx && npc.y === fy) {
                npc.facing = getOppositeDir(player.facing);
                if (npc.dialogue) {
                    showDialogue(npc.dialogue, npc.name, npc);
                } else if (interactCallback) {
                    interactCallback(npc);
                }
                return;
            }
        }

        if (currentMap.interactables) {
            for (let obj of currentMap.interactables) {
                if (obj.x === fx && obj.y === fy) {
                    if (obj.dialogue) showDialogue(obj.dialogue, obj.name);
                    if (obj.action && interactCallback) interactCallback(obj);
                    return;
                }
            }
        }
    }

    function getOppositeDir(dir) {
        return { up: 'down', down: 'up', left: 'right', right: 'left' }[dir];
    }

    function showDialogue(messages, speakerName, npc) {
        if (typeof messages === 'string') messages = [messages];
        dialogueQueue = [...messages];
        dialogueActive = true;
        currentDialogue = { text: dialogueQueue.shift(), speaker: speakerName || '', npc: npc, complete: false };
        dialogueCharIndex = 0;
        dialogueTimer = 0;
    }

    function updateDialogue(dt) {
        if (!currentDialogue) return;
        if (!currentDialogue.complete) {
            dialogueTimer += dt;
            if (dialogueTimer >= dialogueSpeed) {
                dialogueTimer = 0;
                dialogueCharIndex++;
                if (dialogueCharIndex >= currentDialogue.text.length) currentDialogue.complete = true;
            }
        }
    }

    function advanceDialogue() {
        if (!currentDialogue) return;
        if (!currentDialogue.complete) {
            dialogueCharIndex = currentDialogue.text.length;
            currentDialogue.complete = true;
            return;
        }
        if (dialogueQueue.length > 0) {
            currentDialogue.text = dialogueQueue.shift();
            currentDialogue.complete = false;
            dialogueCharIndex = 0;
            dialogueTimer = 0;
        } else {
            const finishedNpc = currentDialogue.npc;
            dialogueActive = false;
            currentDialogue = null;
            if (finishedNpc && finishedNpc.action && finishedNpc.route) {
                showChoice('Visit ' + finishedNpc.name + '?', ['Yes', 'No'], function(idx) {
                    if (idx === 0 && interactCallback) interactCallback(finishedNpc);
                });
            }
        }
    }

    function showChoice(prompt, options, callback) {
        choiceActive = true;
        choiceOptions = options;
        choiceIndex = 0;
        choiceCallback = callback;
        choicePrompt = prompt;
    }

    function resolveChoice() {
        if (!choiceActive) return;
        choiceActive = false;
        if (choiceCallback) choiceCallback(choiceIndex);
    }

    let choicePrompt = '';

    // ==================== RENDERING ====================

    function render() {
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        if (!currentMap) return;

        ctx.save();
        ctx.translate(-Math.round(camera.x), -Math.round(camera.y));

        renderMap();
        renderShadows();
        renderEntities();
        renderMapOverlay();

        ctx.restore();

        renderHUD();
        if (dialogueActive) renderDialogue();
        if (choiceActive) renderChoiceBox();
        if (screenFlash) renderScreenFlash();
    }

    function renderMap() {
        const startCol = Math.max(0, Math.floor(camera.x / SCALED_TILE));
        const endCol = Math.min(currentMap.width - 1, Math.ceil((camera.x + canvas.width) / SCALED_TILE));
        const startRow = Math.max(0, Math.floor(camera.y / SCALED_TILE));
        const endRow = Math.min(currentMap.height - 1, Math.ceil((camera.y + canvas.height) / SCALED_TILE));

        for (let row = startRow; row <= endRow; row++) {
            for (let col = startCol; col <= endCol; col++) {
                const tile = currentMap.tiles[row][col];
                const x = col * SCALED_TILE;
                const y = row * SCALED_TILE;
                drawTile(tile, x, y, row, col);
            }
        }
    }

    function renderMapOverlay() {
        if (!currentMap.overlay) return;
        const startCol = Math.max(0, Math.floor(camera.x / SCALED_TILE));
        const endCol = Math.min(currentMap.width - 1, Math.ceil((camera.x + canvas.width) / SCALED_TILE));
        const startRow = Math.max(0, Math.floor(camera.y / SCALED_TILE));
        const endRow = Math.min(currentMap.height - 1, Math.ceil((camera.y + canvas.height) / SCALED_TILE));
        for (let row = startRow; row <= endRow; row++) {
            for (let col = startCol; col <= endCol; col++) {
                const tile = currentMap.overlay[row] ? currentMap.overlay[row][col] : 0;
                if (tile > 0) drawTile(tile, col * SCALED_TILE, row * SCALED_TILE, row, col);
            }
        }
    }

    function renderShadows() {
        ctx.fillStyle = PAL.shadow;
        npcs.forEach(npc => {
            const x = npc.x * SCALED_TILE;
            const y = npc.y * SCALED_TILE;
            drawEllipse(x + SCALED_TILE * 0.2, y + SCALED_TILE * 0.85, SCALED_TILE * 0.6, SCALED_TILE * 0.15);
        });
        if (player) {
            drawEllipse(player.x + SCALED_TILE * 0.2, player.y + SCALED_TILE * 0.85, SCALED_TILE * 0.6, SCALED_TILE * 0.15);
        }
    }

    function drawEllipse(x, y, w, h) {
        ctx.beginPath();
        ctx.ellipse(x + w/2, y + h/2, w/2, h/2, 0, 0, Math.PI * 2);
        ctx.fill();
    }

    function renderEntities() {
        const entities = [];
        npcs.forEach(npc => {
            entities.push({ type: 'npc', data: npc, y: npc.y * SCALED_TILE });
        });
        if (player) {
            entities.push({ type: 'player', data: player, y: player.y });
        }
        entities.sort((a, b) => a.y - b.y);

        entities.forEach(e => {
            if (e.type === 'npc') {
                const npc = e.data;
                const x = npc.x * SCALED_TILE;
                const y = npc.y * SCALED_TILE;
                drawFFSprite(npc.spriteType || 'npc', x, y, npc.facing, npc.animFrame || 0, false, npc.color, npc.spriteId);
                if (!dialogueActive && !choiceActive && player) {
                    const dist = Math.sqrt((player.x - x) ** 2 + (player.y - y) ** 2);
                    if (dist < SCALED_TILE * 1.8) {
                        renderInteractIndicator(x, y);
                    }
                }
            } else {
                drawFFSprite('hero', Math.round(player.x), Math.round(player.y), player.facing, player.animFrame, player.moving);
            }
        });
    }

    function renderInteractIndicator(x, y) {
        const bob = Math.sin(globalTime / 250) * 3 * SCALE;
        const ix = x + SCALED_TILE / 2;
        const iy = y - 6 * SCALE + bob;
        ctx.fillStyle = PAL.nameGold;
        ctx.beginPath();
        ctx.moveTo(ix - 3 * SCALE, iy - 5 * SCALE);
        ctx.lineTo(ix + 3 * SCALE, iy - 5 * SCALE);
        ctx.lineTo(ix, iy);
        ctx.closePath();
        ctx.fill();
    }

    // ==================== FF-STYLE TILE RENDERING ====================

    function drawTile(tileId, x, y, row, col) {
        const s = SCALED_TILE;
        const p = SCALE;
        const seed = (row * 131 + col * 97) & 0xFF;

        switch(tileId) {
            case 0: break;

            case 1: // Grass - lush, varied
                ctx.fillStyle = (seed & 1) ? PAL.grass1 : PAL.grass2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.grass3;
                for (let i = 0; i < 5; i++) {
                    const gx = ((seed * 7 + i * 31) % 13) * p;
                    const gy = ((seed * 11 + i * 23) % 13) * p;
                    ctx.fillRect(x + gx, y + gy, p, p * 2);
                }
                ctx.fillStyle = PAL.grassDk;
                ctx.fillRect(x + ((seed * 3) % 12) * p, y + ((seed * 5) % 12) * p, p, p);
                ctx.fillRect(x + ((seed * 9) % 11) * p, y + ((seed * 7) % 10) * p, p, p);
                break;

            case 2: // Path - cobblestone FF style
                ctx.fillStyle = PAL.path1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.path2;
                for (let i = 0; i < 3; i++) {
                    for (let j = 0; j < 2; j++) {
                        const bx = ((i * 5 + (seed & 3)) % 4) * p * 3;
                        const by = (j * 7 + (seed >> 2 & 3)) * p;
                        ctx.fillRect(x + bx + p, y + by + p, p * 4, p * 3);
                    }
                }
                ctx.fillStyle = PAL.path3;
                ctx.fillRect(x + ((seed * 3) % 10) * p, y + ((seed * 7) % 12) * p, p * 3, p);
                ctx.fillRect(x + ((seed * 11) % 8) * p, y + ((seed * 5) % 10) * p, p, p * 2);
                ctx.fillStyle = PAL.pathEdge;
                ctx.fillRect(x, y, s, p);
                ctx.fillRect(x, y, p, s);
                break;

            case 3: // Water - animated waves
                ctx.fillStyle = PAL.water1;
                ctx.fillRect(x, y, s, s);
                const wt = globalTime / 600;
                ctx.fillStyle = PAL.water2;
                for (let i = 0; i < 4; i++) {
                    const wx = (Math.sin(wt + i * 1.5 + col * 0.8) * 4 + 6) * p;
                    const wy = (i * 4 + 1) * p;
                    ctx.fillRect(x + wx, y + wy, p * 4, p);
                }
                ctx.fillStyle = PAL.water3;
                for (let i = 0; i < 3; i++) {
                    const wx2 = (Math.cos(wt * 0.8 + i * 2 + row) * 3 + 5) * p;
                    const wy2 = (i * 5 + 3) * p;
                    ctx.fillRect(x + wx2, y + wy2, p * 3, p);
                }
                ctx.fillStyle = PAL.waterFoam;
                ctx.globalAlpha = 0.3 + Math.sin(wt + col + row) * 0.15;
                ctx.fillRect(x + ((seed * 3) % 8) * p, y + ((seed * 7) % 10) * p, p * 2, p);
                ctx.globalAlpha = 1;
                break;

            case 4: // Wall - brick pattern
                ctx.fillStyle = PAL.wall1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.wall2;
                for (let r = 0; r < 4; r++) {
                    for (let c = 0; c < 2; c++) {
                        const brickX = (c * 8 + (r % 2) * 4) * p;
                        const brickY = r * 4 * p;
                        ctx.fillRect(x + brickX, y + brickY, p * 7, p * 3);
                    }
                }
                ctx.fillStyle = PAL.wallLine;
                for (let i = 0; i < 4; i++) {
                    ctx.fillRect(x, y + i * 4 * p, s, p);
                }
                ctx.fillRect(x + 8 * p, y, p, s);
                ctx.fillRect(x + 4 * p, y + 4 * p, p, 4 * p);
                ctx.fillRect(x + 12 * p, y + 4 * p, p, 4 * p);
                break;

            case 5: // Wall top - parapet
                ctx.fillStyle = PAL.wall3;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.wall1;
                ctx.fillRect(x, y + 10 * p, s, 6 * p);
                ctx.fillStyle = PAL.wallLine;
                ctx.fillRect(x, y + 10 * p, s, p);
                for (let i = 0; i < 4; i++) {
                    ctx.fillRect(x + i * 4 * p, y, p * 3, 4 * p);
                }
                break;

            case 6: // Roof - shingle pattern
                ctx.fillStyle = PAL.roof1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.roof2;
                for (let r = 0; r < 4; r++) {
                    for (let c = 0; c < 4; c++) {
                        const sx = (c * 4 + (r % 2) * 2) * p;
                        const sy = r * 4 * p;
                        ctx.fillRect(x + sx, y + sy, p * 3, p * 2);
                    }
                }
                ctx.fillStyle = PAL.roof3;
                for (let r = 0; r < 4; r++) {
                    ctx.fillRect(x, y + r * 4 * p + 3 * p, s, p);
                }
                ctx.fillStyle = PAL.roofLine;
                ctx.fillRect(x, y + s - p, s, p);
                break;

            case 7: // Door
                ctx.fillStyle = PAL.wall1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.door1;
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 10, p * 14);
                ctx.fillStyle = PAL.door2;
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 8, p * 12);
                ctx.fillStyle = PAL.door1;
                ctx.fillRect(x + 7.5 * p, y + 3 * p, p, p * 12);
                ctx.fillStyle = '#503018';
                ctx.fillRect(x + 4 * p, y + 8 * p, p * 8, p);
                ctx.fillStyle = PAL.doorKnob;
                ctx.fillRect(x + 10 * p, y + 9 * p, p * 2, p * 2);
                ctx.fillStyle = '#c0a030';
                ctx.fillRect(x + 10 * p, y + 9 * p, p, p);
                ctx.fillStyle = PAL.wall3;
                ctx.fillRect(x + 2 * p, y + p, p * 12, p);
                ctx.fillRect(x + 2 * p, y + p, p, p * 15);
                ctx.fillRect(x + 13 * p, y + p, p, p * 15);
                break;

            case 8: // Window
                ctx.fillStyle = PAL.wall1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.windowFrame;
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 10, p * 10);
                ctx.fillStyle = PAL.window1;
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 8, p * 8);
                const shimmer = Math.sin(globalTime / 1000 + col) * 0.15 + 0.85;
                ctx.fillStyle = PAL.window2;
                ctx.globalAlpha = shimmer;
                ctx.fillRect(x + 5 * p, y + 4 * p, p * 3, p * 3);
                ctx.globalAlpha = 1;
                ctx.fillStyle = PAL.windowFrame;
                ctx.fillRect(x + 7.5 * p, y + 3 * p, p, p * 8);
                ctx.fillRect(x + 4 * p, y + 6.5 * p, p * 8, p);
                ctx.fillStyle = PAL.wall3;
                ctx.fillRect(x + 3 * p, y + 12 * p, p * 10, p * 2);
                break;

            case 9: // Tree - detailed with depth
                ctx.fillStyle = (seed & 1) ? PAL.grass1 : PAL.grass2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.trunk1;
                ctx.fillRect(x + 6 * p, y + 9 * p, p * 4, p * 7);
                ctx.fillStyle = PAL.trunk2;
                ctx.fillRect(x + 7 * p, y + 9 * p, p * 2, p * 7);
                ctx.fillStyle = PAL.tree3;
                ctx.fillRect(x + 1 * p, y + 2 * p, p * 14, p * 9);
                ctx.fillStyle = PAL.tree1;
                ctx.fillRect(x + 2 * p, y + 1 * p, p * 12, p * 8);
                ctx.fillStyle = PAL.tree2;
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 5, p * 4);
                ctx.fillRect(x + 9 * p, y + 3 * p, p * 3, p * 3);
                ctx.fillStyle = PAL.tree3;
                ctx.fillRect(x + 2 * p, y + 8 * p, p * 3, p * 2);
                ctx.fillRect(x + 11 * p, y + 7 * p, p * 3, p * 2);
                const sway = Math.sin(globalTime / 2000 + seed) * p * 0.5;
                ctx.fillStyle = PAL.tree2;
                ctx.fillRect(x + 4 * p + sway, y + p, p * 3, p * 2);
                break;

            case 10: // Flowers - animated
                ctx.fillStyle = (seed & 1) ? PAL.grass1 : PAL.grass2;
                ctx.fillRect(x, y, s, s);
                const flowerSway = Math.sin(globalTime / 800 + seed) * p * 0.5;
                const flowers = [
                    { cx: 3, cy: 3, color: PAL.flower_r },
                    { cx: 9, cy: 5, color: PAL.flower_y },
                    { cx: 5, cy: 10, color: PAL.flower_p },
                    { cx: 12, cy: 8, color: PAL.flower_w },
                    { cx: 7, cy: 2, color: PAL.flower_r },
                ];
                flowers.forEach((f, i) => {
                    ctx.fillStyle = '#228822';
                    ctx.fillRect(x + (f.cx + 0.5) * p, y + (f.cy + 2) * p, p, p * 3);
                    ctx.fillStyle = f.color;
                    const sw = (i % 2 === 0) ? flowerSway : -flowerSway;
                    ctx.fillRect(x + f.cx * p + sw, y + f.cy * p, p * 2, p * 2);
                    ctx.fillStyle = PAL.flower_y;
                    ctx.fillRect(x + (f.cx + 0.5) * p + sw, y + (f.cy + 0.5) * p, p, p);
                });
                break;

            case 11: // Wood floor
                ctx.fillStyle = PAL.wood1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.wood2;
                for (let i = 0; i < 4; i++) {
                    const plankX = (i * 4 + (seed & 1)) * p;
                    ctx.fillRect(x + plankX, y, p * 3, s);
                }
                ctx.fillStyle = PAL.wood3;
                for (let i = 0; i <= 4; i++) {
                    ctx.fillRect(x, y + i * 4 * p, s, p);
                }
                break;

            case 12: // Sign
                ctx.fillStyle = (seed & 1) ? PAL.grass1 : PAL.grass2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.signPost;
                ctx.fillRect(x + 7 * p, y + 8 * p, p * 2, p * 8);
                ctx.fillStyle = PAL.sign1;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p * 7);
                ctx.fillStyle = PAL.sign2;
                ctx.fillRect(x + 3 * p, y + 3 * p, p * 10, p * 5);
                ctx.fillStyle = PAL.signPost;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p);
                ctx.fillRect(x + 2 * p, y + 8 * p, p * 12, p);
                ctx.fillRect(x + 2 * p, y + 2 * p, p, p * 7);
                ctx.fillRect(x + 13 * p, y + 2 * p, p, p * 7);
                break;

            case 13: // Sand
                ctx.fillStyle = PAL.sand1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.sand2;
                for (let i = 0; i < 4; i++) {
                    ctx.fillRect(x + ((seed * 3 + i * 7) % 12) * p, y + ((seed * 5 + i * 11) % 12) * p, p * 2, p);
                }
                break;

            case 14: // Stone floor - detailed cobble
                ctx.fillStyle = PAL.stone1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.stone2;
                for (let r = 0; r < 2; r++) {
                    for (let c = 0; c < 2; c++) {
                        const bx = (c * 8 + (r % 2) * 4) * p;
                        const by = r * 8 * p;
                        ctx.fillRect(x + bx + p, y + by + p, p * 6, p * 6);
                    }
                }
                ctx.fillStyle = PAL.stone3;
                ctx.fillRect(x, y, s, p);
                ctx.fillRect(x, y + 8 * p, s, p);
                ctx.fillRect(x, y, p, s);
                ctx.fillRect(x + 8 * p, y, p, s);
                ctx.fillRect(x + 4 * p, y + 8 * p, p, 8 * p);
                ctx.fillRect(x + 12 * p, y, p, 8 * p);
                break;

            case 15: // Hedge
                ctx.fillStyle = PAL.hedge1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.hedge2;
                ctx.fillRect(x + 2 * p, y + p, p * 12, p * 12);
                ctx.fillStyle = PAL.tree2;
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 4, p * 4);
                ctx.fillRect(x + 8 * p, y + 5 * p, p * 4, p * 3);
                ctx.fillStyle = PAL.tree3;
                ctx.fillRect(x + p, y + 13 * p, p * 14, p * 3);
                break;

            case 16: // Chest
                ctx.fillStyle = PAL.path1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.chest2;
                ctx.fillRect(x + 3 * p, y + 5 * p, p * 10, p * 9);
                ctx.fillStyle = PAL.chest1;
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 8, p * 4);
                ctx.fillRect(x + 4 * p, y + 8 * p, p * 8, p * 5);
                ctx.fillStyle = PAL.chestLock;
                ctx.fillRect(x + 7 * p, y + 6 * p, p * 2, p * 4);
                ctx.fillStyle = '#906010';
                ctx.fillRect(x + 4 * p, y + 7 * p, p * 8, p);
                break;

            case 17: // Portal - animated swirl
                ctx.fillStyle = (seed & 1) ? PAL.grass1 : PAL.grass2;
                ctx.fillRect(x, y, s, s);
                const pt = globalTime / 400;
                ctx.fillStyle = PAL.portal1;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p * 12);
                for (let i = 0; i < 6; i++) {
                    const angle = pt + i * Math.PI / 3;
                    const pr = 4 * p;
                    const px = x + 8 * p + Math.cos(angle) * pr;
                    const py = y + 8 * p + Math.sin(angle) * pr;
                    ctx.fillStyle = i % 2 === 0 ? PAL.portal2 : PAL.portal3;
                    ctx.fillRect(px - p, py - p, p * 2, p * 2);
                }
                ctx.fillStyle = PAL.portal3;
                ctx.globalAlpha = 0.5 + Math.sin(pt * 2) * 0.3;
                ctx.fillRect(x + 5 * p, y + 5 * p, p * 6, p * 6);
                ctx.globalAlpha = 1;
                break;

            case 18: // Fountain base
                ctx.fillStyle = PAL.stone1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.stone2;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p * 12);
                ctx.fillStyle = PAL.water1;
                ctx.fillRect(x + 3 * p, y + 3 * p, p * 10, p * 10);
                ctx.fillStyle = PAL.water2;
                const ft = globalTime / 500;
                ctx.fillRect(x + 4 * p, y + (4 + Math.sin(ft) * 1) * p, p * 3, p * 2);
                ctx.fillRect(x + 9 * p, y + (6 + Math.cos(ft) * 1) * p, p * 3, p * 2);
                ctx.fillStyle = PAL.stone1;
                ctx.fillRect(x + 7 * p, y + 4 * p, p * 2, p * 8);
                ctx.fillStyle = PAL.waterFoam;
                ctx.globalAlpha = 0.5 + Math.sin(ft * 2) * 0.3;
                ctx.fillRect(x + 6 * p, y + 3 * p, p * 4, p * 2);
                ctx.globalAlpha = 1;
                break;

            case 19: // Lamp post
                ctx.fillStyle = PAL.path1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#404040';
                ctx.fillRect(x + 7 * p, y + 4 * p, p * 2, p * 12);
                ctx.fillStyle = '#505050';
                ctx.fillRect(x + 5 * p, y + 14 * p, p * 6, p * 2);
                ctx.fillStyle = '#e8c840';
                const lampGlow = 0.6 + Math.sin(globalTime / 1500) * 0.2;
                ctx.globalAlpha = lampGlow;
                ctx.fillRect(x + 5 * p, y + p, p * 6, p * 4);
                ctx.fillStyle = '#fff8d0';
                ctx.fillRect(x + 6 * p, y + 2 * p, p * 4, p * 2);
                ctx.globalAlpha = 1;
                break;

            case 20: // Market stall
                ctx.fillStyle = PAL.path1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.wood1;
                ctx.fillRect(x + p, y + 6 * p, p * 14, p * 10);
                ctx.fillStyle = PAL.wood2;
                ctx.fillRect(x + 2 * p, y + 7 * p, p * 12, p * 8);
                ctx.fillStyle = '#cc3030';
                ctx.fillRect(x + p, y + p, p * 14, p * 5);
                ctx.fillStyle = '#aa2020';
                for (let i = 0; i < 7; i++) {
                    ctx.fillRect(x + (1 + i * 2) * p, y + 5 * p, p * 2, p * 2);
                }
                ctx.fillStyle = PAL.flower_y;
                ctx.fillRect(x + 3 * p, y + 8 * p, p * 3, p * 3);
                ctx.fillStyle = PAL.flower_r;
                ctx.fillRect(x + 8 * p, y + 8 * p, p * 3, p * 3);
                break;

            case 21: // Bench
                ctx.fillStyle = (seed & 1) ? PAL.grass1 : PAL.grass2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.wood1;
                ctx.fillRect(x + 2 * p, y + 8 * p, p * 12, p * 3);
                ctx.fillStyle = PAL.wood2;
                ctx.fillRect(x + 2 * p, y + 5 * p, p * 12, p * 2);
                ctx.fillStyle = PAL.wood3;
                ctx.fillRect(x + 3 * p, y + 11 * p, p * 2, p * 4);
                ctx.fillRect(x + 11 * p, y + 11 * p, p * 2, p * 4);
                break;

            case 22: // Well
                ctx.fillStyle = (seed & 1) ? PAL.grass1 : PAL.grass2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = PAL.stone2;
                ctx.fillRect(x + 3 * p, y + 6 * p, p * 10, p * 10);
                ctx.fillStyle = PAL.stone1;
                ctx.fillRect(x + 4 * p, y + 7 * p, p * 8, p * 8);
                ctx.fillStyle = PAL.water1;
                ctx.fillRect(x + 5 * p, y + 8 * p, p * 6, p * 6);
                ctx.fillStyle = PAL.wood1;
                ctx.fillRect(x + 7 * p, y + 2 * p, p * 2, p * 5);
                ctx.fillRect(x + 4 * p, y + 2 * p, p * 8, p * 2);
                ctx.fillStyle = '#808080';
                ctx.fillRect(x + 7 * p, y + 3 * p, p * 2, p);
                break;

            default:
                ctx.fillStyle = '#ff00ff';
                ctx.fillRect(x, y, s, s);
        }
    }

    // ==================== FF-STYLE CHARACTER SPRITES ====================

    function drawFFSprite(type, x, y, facing, frame, moving, color, spriteId) {
        const p = SCALE;
        const isHero = type === 'hero';

        const palette = isHero ? {
            hair: '#554422', hairHL: '#776644',
            skin: '#f0c888', skinSh: '#d0a868',
            eye: '#203060',
            tunic: '#2040a8', tunicHL: '#3060c8', tunicDk: '#182878',
            belt: '#c89830', beltBk: '#a07820',
            pants: '#304888', pantsDk: '#203060',
            boots: '#503820', bootsHL: '#685030',
            cape: '#a82020', capeDk: '#801818',
            outline: '#181020'
        } : getNPCPalette(color, spriteId);

        const bob = moving ? Math.sin(frame * Math.PI / 2) * p : 0;
        const walkCycle = moving ? frame % 4 : 0;
        const legL = walkCycle === 1 ? 2 * p : walkCycle === 3 ? -1 * p : 0;
        const legR = walkCycle === 1 ? -1 * p : walkCycle === 3 ? 2 * p : 0;
        const armL = moving ? Math.sin(frame * Math.PI / 2) * 2 * p : 0;
        const armR = moving ? -Math.sin(frame * Math.PI / 2) * 2 * p : 0;

        switch(facing) {
            case 'down':
                ctx.fillStyle = palette.outline;
                ctx.fillRect(x + 4 * p, y + (0 - bob/p) * p, p * 8, p);
                ctx.fillRect(x + 3 * p, y + (1 - bob/p) * p, p, p * 3);
                ctx.fillRect(x + 12 * p, y + (1 - bob/p) * p, p, p * 3);

                ctx.fillStyle = palette.hair;
                ctx.fillRect(x + 4 * p, y + (0 - bob/p) * p, p * 8, p * 3);
                ctx.fillStyle = palette.hairHL;
                ctx.fillRect(x + 5 * p, y + (1 - bob/p) * p, p * 3, p);

                ctx.fillStyle = palette.skin;
                ctx.fillRect(x + 4 * p, y + (3 - bob/p) * p, p * 8, p * 4);
                ctx.fillStyle = palette.skinSh;
                ctx.fillRect(x + 4 * p, y + (6 - bob/p) * p, p * 8, p);

                ctx.fillStyle = palette.eye;
                ctx.fillRect(x + 5 * p, y + (4 - bob/p) * p, p * 2, p * 2);
                ctx.fillRect(x + 9 * p, y + (4 - bob/p) * p, p * 2, p * 2);
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(x + 5 * p, y + (4 - bob/p) * p, p, p);
                ctx.fillRect(x + 9 * p, y + (4 - bob/p) * p, p, p);

                ctx.fillStyle = palette.skin;
                ctx.fillRect(x + 7 * p, y + (6 - bob/p) * p, p * 2, p);

                ctx.fillStyle = palette.tunic;
                ctx.fillRect(x + 3 * p, y + (7 - bob/p) * p, p * 10, p * 4);
                ctx.fillStyle = palette.tunicHL;
                ctx.fillRect(x + 5 * p, y + (7 - bob/p) * p, p * 2, p * 3);
                ctx.fillStyle = palette.tunicDk;
                ctx.fillRect(x + 3 * p, y + (10 - bob/p) * p, p * 10, p);

                ctx.fillStyle = palette.belt;
                ctx.fillRect(x + 3 * p, y + (10 - bob/p) * p, p * 10, p);
                ctx.fillStyle = palette.beltBk;
                ctx.fillRect(x + 7 * p, y + (10 - bob/p) * p, p * 2, p);

                ctx.fillStyle = palette.skin;
                ctx.fillRect(x + (2 + armL/p) * p, y + (8 - bob/p) * p, p * 2, p * 3);
                ctx.fillRect(x + (12 + armR/p) * p, y + (8 - bob/p) * p, p * 2, p * 3);

                ctx.fillStyle = palette.pants;
                ctx.fillRect(x + 4 * p, y + 11 * p, p * 3, p * 2);
                ctx.fillRect(x + 9 * p, y + 11 * p, p * 3, p * 2);

                ctx.fillStyle = palette.boots;
                ctx.fillRect(x + (4) * p, y + (13 + legL/p) * p, p * 3, p * 3);
                ctx.fillRect(x + (9) * p, y + (13 + legR/p) * p, p * 3, p * 3);
                ctx.fillStyle = palette.bootsHL;
                ctx.fillRect(x + 4 * p, y + (13 + legL/p) * p, p * 3, p);
                ctx.fillRect(x + 9 * p, y + (13 + legR/p) * p, p * 3, p);
                break;

            case 'up':
                ctx.fillStyle = palette.hair;
                ctx.fillRect(x + 3 * p, y + (0 - bob/p) * p, p * 10, p * 7);
                ctx.fillStyle = palette.hairHL;
                ctx.fillRect(x + 5 * p, y + (1 - bob/p) * p, p * 3, p * 2);
                ctx.fillRect(x + 9 * p, y + (2 - bob/p) * p, p * 2, p * 2);

                if (isHero) {
                    ctx.fillStyle = palette.cape;
                    ctx.fillRect(x + 3 * p, y + (7 - bob/p) * p, p * 10, p * 5);
                    ctx.fillStyle = palette.capeDk;
                    ctx.fillRect(x + 7 * p, y + (7 - bob/p) * p, p, p * 5);
                } else {
                    ctx.fillStyle = palette.tunic;
                    ctx.fillRect(x + 3 * p, y + (7 - bob/p) * p, p * 10, p * 4);
                    ctx.fillStyle = palette.tunicDk;
                    ctx.fillRect(x + 7 * p, y + (7 - bob/p) * p, p, p * 4);
                }

                ctx.fillStyle = palette.belt;
                ctx.fillRect(x + 3 * p, y + (10 - bob/p) * p, p * 10, p);

                ctx.fillStyle = palette.skin;
                ctx.fillRect(x + (2 + armL/p) * p, y + (8 - bob/p) * p, p * 2, p * 3);
                ctx.fillRect(x + (12 + armR/p) * p, y + (8 - bob/p) * p, p * 2, p * 3);

                ctx.fillStyle = palette.pants;
                ctx.fillRect(x + 4 * p, y + 11 * p, p * 3, p * 2);
                ctx.fillRect(x + 9 * p, y + 11 * p, p * 3, p * 2);

                ctx.fillStyle = palette.boots;
                ctx.fillRect(x + 4 * p, y + (13 + legL/p) * p, p * 3, p * 3);
                ctx.fillRect(x + 9 * p, y + (13 + legR/p) * p, p * 3, p * 3);
                break;

            case 'left':
                ctx.fillStyle = palette.hair;
                ctx.fillRect(x + 3 * p, y + (0 - bob/p) * p, p * 8, p * 4);
                ctx.fillStyle = palette.hairHL;
                ctx.fillRect(x + 4 * p, y + (1 - bob/p) * p, p * 3, p);
                ctx.fillStyle = palette.hair;
                ctx.fillRect(x + 3 * p, y + (3 - bob/p) * p, p * 3, p * 3);

                ctx.fillStyle = palette.skin;
                ctx.fillRect(x + 5 * p, y + (3 - bob/p) * p, p * 6, p * 4);
                ctx.fillStyle = palette.skinSh;
                ctx.fillRect(x + 5 * p, y + (6 - bob/p) * p, p * 6, p);
                ctx.fillStyle = palette.eye;
                ctx.fillRect(x + 5 * p, y + (4 - bob/p) * p, p * 2, p * 2);
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(x + 5 * p, y + (4 - bob/p) * p, p, p);

                ctx.fillStyle = palette.tunic;
                ctx.fillRect(x + 4 * p, y + (7 - bob/p) * p, p * 8, p * 4);
                ctx.fillStyle = palette.tunicHL;
                ctx.fillRect(x + 5 * p, y + (7 - bob/p) * p, p * 2, p * 3);
                ctx.fillStyle = palette.tunicDk;
                ctx.fillRect(x + 10 * p, y + (7 - bob/p) * p, p * 2, p * 4);

                ctx.fillStyle = palette.belt;
                ctx.fillRect(x + 4 * p, y + (10 - bob/p) * p, p * 8, p);

                ctx.fillStyle = palette.skin;
                ctx.fillRect(x + (3 + armL/p) * p, y + (8 - bob/p) * p, p * 2, p * 3);

                ctx.fillStyle = palette.pants;
                ctx.fillRect(x + 5 * p, y + 11 * p, p * 6, p * 2);
                ctx.fillStyle = palette.pantsDk;
                ctx.fillRect(x + 5 * p, y + 11 * p, p * 2, p * 2);

                ctx.fillStyle = palette.boots;
                ctx.fillRect(x + 5 * p, y + (13 + legL/p) * p, p * 3, p * 3);
                ctx.fillRect(x + 8 * p, y + (13 + legR/p) * p, p * 3, p * 3);
                break;

            case 'right':
                ctx.fillStyle = palette.hair;
                ctx.fillRect(x + 5 * p, y + (0 - bob/p) * p, p * 8, p * 4);
                ctx.fillStyle = palette.hairHL;
                ctx.fillRect(x + 9 * p, y + (1 - bob/p) * p, p * 3, p);
                ctx.fillStyle = palette.hair;
                ctx.fillRect(x + 10 * p, y + (3 - bob/p) * p, p * 3, p * 3);

                ctx.fillStyle = palette.skin;
                ctx.fillRect(x + 5 * p, y + (3 - bob/p) * p, p * 6, p * 4);
                ctx.fillStyle = palette.skinSh;
                ctx.fillRect(x + 5 * p, y + (6 - bob/p) * p, p * 6, p);
                ctx.fillStyle = palette.eye;
                ctx.fillRect(x + 9 * p, y + (4 - bob/p) * p, p * 2, p * 2);
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(x + 10 * p, y + (4 - bob/p) * p, p, p);

                ctx.fillStyle = palette.tunic;
                ctx.fillRect(x + 4 * p, y + (7 - bob/p) * p, p * 8, p * 4);
                ctx.fillStyle = palette.tunicHL;
                ctx.fillRect(x + 9 * p, y + (7 - bob/p) * p, p * 2, p * 3);
                ctx.fillStyle = palette.tunicDk;
                ctx.fillRect(x + 4 * p, y + (7 - bob/p) * p, p * 2, p * 4);

                ctx.fillStyle = palette.belt;
                ctx.fillRect(x + 4 * p, y + (10 - bob/p) * p, p * 8, p);

                ctx.fillStyle = palette.skin;
                ctx.fillRect(x + (11 + armR/p) * p, y + (8 - bob/p) * p, p * 2, p * 3);

                ctx.fillStyle = palette.pants;
                ctx.fillRect(x + 5 * p, y + 11 * p, p * 6, p * 2);
                ctx.fillStyle = palette.pantsDk;
                ctx.fillRect(x + 9 * p, y + 11 * p, p * 2, p * 2);

                ctx.fillStyle = palette.boots;
                ctx.fillRect(x + 4 * p, y + (13 + legL/p) * p, p * 3, p * 3);
                ctx.fillRect(x + 7 * p, y + (13 + legR/p) * p, p * 3, p * 3);
                break;
        }
    }

    function getNPCPalette(color, spriteId) {
        const c = color || '#44aa44';
        const h = hexToHSL(c);

        return {
            hair: hslToHex((h.h + 30) % 360, Math.min(h.s, 40), 30),
            hairHL: hslToHex((h.h + 30) % 360, Math.min(h.s, 40), 45),
            skin: '#f0c888', skinSh: '#d0a868',
            eye: '#203060',
            tunic: c,
            tunicHL: shadeColor(c, 25),
            tunicDk: shadeColor(c, -30),
            belt: '#a08030', beltBk: '#806020',
            pants: shadeColor(c, -40),
            pantsDk: shadeColor(c, -55),
            boots: '#504030', bootsHL: '#685040',
            cape: shadeColor(c, -15), capeDk: shadeColor(c, -35),
            outline: '#181020'
        };
    }

    function hexToHSL(hex) {
        let r = parseInt(hex.slice(1,3),16)/255;
        let g = parseInt(hex.slice(3,5),16)/255;
        let b = parseInt(hex.slice(5,7),16)/255;
        let max = Math.max(r,g,b), min = Math.min(r,g,b);
        let h = 0, s = 0, l = (max + min) / 2;
        if (max !== min) {
            let d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch(max) {
                case r: h = ((g-b)/d + (g < b ? 6 : 0)) * 60; break;
                case g: h = ((b-r)/d + 2) * 60; break;
                case b: h = ((r-g)/d + 4) * 60; break;
            }
        }
        return { h: Math.round(h), s: Math.round(s * 100), l: Math.round(l * 100) };
    }

    function hslToHex(h, s, l) {
        s /= 100; l /= 100;
        const k = n => (n + h / 30) % 12;
        const a = s * Math.min(l, 1 - l);
        const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, 9 - k(n), 1));
        const toHex = n => Math.round(n * 255).toString(16).padStart(2, '0');
        return '#' + toHex(f(0)) + toHex(f(8)) + toHex(f(4));
    }

    function shadeColor(color, percent) {
        const num = parseInt(color.replace('#', ''), 16);
        const amt = Math.round(2.55 * percent);
        const R = Math.max(0, Math.min(255, (num >> 16) + amt));
        const G = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) + amt));
        const B = Math.max(0, Math.min(255, (num & 0x0000FF) + amt));
        return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
    }

    // ==================== FF-STYLE HUD ====================

    function renderHUD() {
        const hudH = 48;
        const bw = 2;

        const grd = ctx.createLinearGradient(0, 0, 0, hudH);
        grd.addColorStop(0, '#101080');
        grd.addColorStop(0.5, '#080848');
        grd.addColorStop(1, '#040430');
        ctx.fillStyle = grd;
        ctx.fillRect(0, 0, canvas.width, hudH);

        ctx.fillStyle = PAL.hudBorder;
        ctx.fillRect(0, hudH - bw, canvas.width, bw);
        ctx.fillStyle = '#484888';
        ctx.fillRect(0, hudH - bw - 1, canvas.width, 1);
        ctx.fillStyle = '#e8e8f8';
        ctx.fillRect(0, 0, canvas.width, 1);

        ctx.font = 'bold 13px "Press Start 2P", monospace';
        ctx.textBaseline = 'middle';
        ctx.shadowColor = '#000030';
        ctx.shadowBlur = 0;
        ctx.shadowOffsetX = 1;
        ctx.shadowOffsetY = 1;

        let xPos = 12;
        const yMid = hudH / 2;

        if (hudData.capital !== undefined) {
            ctx.fillStyle = PAL.hudGold;
            ctx.fillText('G', xPos, yMid);
            ctx.fillStyle = '#ffffff';
            ctx.font = '12px "Press Start 2P", monospace';
            ctx.fillText(Number(hudData.capital).toLocaleString(), xPos + 16, yMid);
            xPos += 120;
        }

        ctx.font = 'bold 11px "Press Start 2P", monospace';
        if (hudData.morale !== undefined) {
            ctx.fillStyle = PAL.hudGreen;
            ctx.fillText('MOR', xPos, yMid - 7);
            drawBar(xPos + 40, yMid - 13, 60, 10, hudData.morale / 100, PAL.hudGreen, '#104010');
            xPos += 110;
        }

        if (hudData.brand !== undefined) {
            ctx.fillStyle = PAL.hudRed;
            ctx.fillText('BRD', xPos, yMid - 7);
            drawBar(xPos + 40, yMid - 13, 60, 10, hudData.brand / 100, PAL.hudRed, '#401010');
            xPos += 110;
        }

        if (hudData.energy !== undefined) {
            ctx.fillStyle = '#f0a030';
            ctx.fillText('EN', xPos, yMid + 9);
            drawBar(xPos + 30, yMid + 3, 60, 10, hudData.energy / 100, '#f0a030', '#402810');
            xPos += 100;
        }

        if (hudData.quarter !== undefined) {
            ctx.fillStyle = PAL.hudBlue;
            ctx.font = 'bold 11px "Press Start 2P", monospace';
            ctx.fillText('Q' + hudData.quarter, xPos, yMid);
        }

        if (currentMap && currentMap.name) {
            ctx.fillStyle = '#d0d0e0';
            ctx.font = '11px "Press Start 2P", monospace';
            ctx.textAlign = 'right';
            ctx.fillText(currentMap.name, canvas.width - 12, yMid);
            ctx.textAlign = 'left';
        }

        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
    }

    function drawBar(x, y, w, h, pct, fillColor, bgColor) {
        pct = Math.max(0, Math.min(1, pct));
        ctx.fillStyle = bgColor;
        ctx.fillRect(x, y, w, h);
        ctx.fillStyle = fillColor;
        ctx.fillRect(x, y, Math.round(w * pct), h);
        ctx.fillStyle = 'rgba(255,255,255,0.3)';
        ctx.fillRect(x, y, Math.round(w * pct), Math.floor(h / 2));
        ctx.strokeStyle = '#c0c0e0';
        ctx.lineWidth = 1;
        ctx.strokeRect(x, y, w, h);
    }

    // ==================== FF-STYLE DIALOGUE BOX ====================

    function renderDialogue() {
        if (!currentDialogue) return;

        const margin = 16;
        const dh = 130;
        const dx = margin;
        const dy = canvas.height - dh - margin;
        const dw = canvas.width - margin * 2;

        drawFFBox(dx, dy, dw, dh);

        if (currentDialogue.speaker) {
            const nameW = Math.max(100, currentDialogue.speaker.length * 10 + 24);
            drawFFBox(dx + 8, dy - 24, nameW, 26);
            ctx.fillStyle = PAL.nameGold;
            ctx.font = 'bold 12px "Press Start 2P", monospace';
            ctx.shadowColor = '#000030';
            ctx.shadowOffsetX = 1;
            ctx.shadowOffsetY = 1;
            ctx.fillText(currentDialogue.speaker, dx + 20, dy - 8);
            ctx.shadowColor = 'transparent';
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 0;
        }

        ctx.fillStyle = PAL.dialogText;
        ctx.font = '12px "Press Start 2P", monospace';
        ctx.shadowColor = '#000030';
        ctx.shadowOffsetX = 1;
        ctx.shadowOffsetY = 1;
        const displayText = currentDialogue.text.substring(0, dialogueCharIndex);
        wrapText(ctx, displayText, dx + 20, dy + 28, dw - 40, 22);
        ctx.shadowColor = 'transparent';
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;

        if (currentDialogue.complete) {
            const blink = Math.sin(globalTime / 300) > 0;
            if (blink) {
                const ax = dx + dw - 28;
                const ay = dy + dh - 22;
                ctx.fillStyle = PAL.dialogText;
                ctx.beginPath();
                ctx.moveTo(ax, ay);
                ctx.lineTo(ax + 10, ay);
                ctx.lineTo(ax + 5, ay + 8);
                ctx.closePath();
                ctx.fill();
            }
        }
    }

    function renderChoiceBox() {
        const boxW = 180;
        const boxH = 24 + choiceOptions.length * 28;
        const bx = canvas.width - boxW - 24;
        const by = canvas.height - 130 - 24 - boxH;

        drawFFBox(bx, by, boxW, boxH);

        ctx.font = '12px "Press Start 2P", monospace';
        ctx.shadowColor = '#000030';
        ctx.shadowOffsetX = 1;
        ctx.shadowOffsetY = 1;

        choiceOptions.forEach((opt, i) => {
            const oy = by + 16 + i * 28;
            if (i === choiceIndex) {
                ctx.fillStyle = PAL.choiceCursor;
                const cursorBob = Math.sin(globalTime / 200) * 2;
                ctx.beginPath();
                ctx.moveTo(bx + 14 + cursorBob, oy - 4);
                ctx.lineTo(bx + 22 + cursorBob, oy + 2);
                ctx.lineTo(bx + 14 + cursorBob, oy + 8);
                ctx.closePath();
                ctx.fill();
            }

            ctx.fillStyle = i === choiceIndex ? '#ffffff' : '#a0a0c0';
            ctx.fillText(opt, bx + 30, oy + 4);
        });

        ctx.shadowColor = 'transparent';
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
    }

    function drawFFBox(x, y, w, h) {
        const grd = ctx.createLinearGradient(x, y, x, y + h);
        grd.addColorStop(0, '#181888');
        grd.addColorStop(0.3, '#101060');
        grd.addColorStop(1, '#080840');
        ctx.fillStyle = grd;
        ctx.fillRect(x + 2, y + 2, w - 4, h - 4);

        ctx.strokeStyle = PAL.dialogBorder1;
        ctx.lineWidth = 2;
        ctx.strokeRect(x + 1, y + 1, w - 2, h - 2);

        ctx.strokeStyle = PAL.dialogBorder2;
        ctx.lineWidth = 1;
        ctx.strokeRect(x + 4, y + 4, w - 8, h - 8);

        ctx.fillStyle = PAL.dialogBorder1;
        ctx.fillRect(x, y, 2, 2);
        ctx.fillRect(x + w - 2, y, 2, 2);
        ctx.fillRect(x, y + h - 2, 2, 2);
        ctx.fillRect(x + w - 2, y + h - 2, 2, 2);
    }

    function renderScreenFlash() {
        if (!screenFlash) return;
        const alpha = screenFlash.timer / screenFlash.maxTimer;
        ctx.fillStyle = screenFlash.color;
        ctx.globalAlpha = alpha;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.globalAlpha = 1;
    }

    function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
        const words = text.split(' ');
        let line = '';
        let testY = y;
        for (let n = 0; n < words.length; n++) {
            const testLine = line + words[n] + ' ';
            const metrics = ctx.measureText(testLine);
            if (metrics.width > maxWidth && n > 0) {
                ctx.fillText(line.trim(), x, testY);
                line = words[n] + ' ';
                testY += lineHeight;
            } else {
                line = testLine;
            }
        }
        ctx.fillText(line.trim(), x, testY);
    }

    function updateHUD(data) { hudData = { ...hudData, ...data }; }
    function setPlayerPosition(tileX, tileY) {
        if (player) { player.x = tileX * SCALED_TILE; player.y = tileY * SCALED_TILE; }
    }
    function isDialogueActive() { return dialogueActive; }

    return {
        init, loadMap, start, stop, updateHUD, setPlayerPosition, showDialogue, isDialogueActive,
        PAL, SCALED_TILE
    };
})();
