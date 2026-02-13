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
    let dialogueSpeed = 30;
    let keys = {};
    let lastTime = 0;
    let animFrame = 0;
    let animTimer = 0;
    let gameRunning = false;
    let onScreenControls = { up: false, down: false, left: false, right: false, action: false };
    let tilesetColors = {};
    let mapTransitions = [];
    let hudData = {};
    let showMinimap = false;
    let screenFlash = null;
    let transitionCooldown = 0;

    const COLORS = {
        grass: '#2d5a1e',
        grassAlt: '#3a6b2a',
        path: '#8b7355',
        pathEdge: '#6b5535',
        water: '#1a4a7a',
        waterLight: '#2a6aaa',
        wall: '#4a4a5a',
        wallDark: '#3a3a4a',
        wallTop: '#5a5a6a',
        roof: '#8b3030',
        roofDark: '#6b2020',
        door: '#6b4520',
        doorFrame: '#8b6530',
        window: '#5599cc',
        windowFrame: '#4a4a5a',
        wood: '#7a5a30',
        woodDark: '#5a4020',
        stone: '#6a6a6a',
        stoneLight: '#8a8a8a',
        flower1: '#ff4466',
        flower2: '#ffaa22',
        flower3: '#aa44ff',
        tree: '#1a4a0e',
        treeLight: '#2a6a1e',
        trunk: '#5a3a1a',
        sand: '#c4a050',
        sign: '#8b6530',
        signPost: '#5a3a1a',
        black: '#000000',
        white: '#ffffff',
        dialogBg: '#000033',
        dialogBorder: '#4444aa',
        dialogText: '#ffffff',
        hud: '#000022',
        hudBorder: '#3333aa',
        hudText: '#ffffff',
        hudGold: '#ffcc00',
        hudRed: '#ff4444',
        hudGreen: '#44ff44',
        hudBlue: '#4488ff',
        npcHighlight: '#ffff00'
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
        const container = canvas.parentElement;
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
        ctx.imageSmoothingEnabled = false;
    }

    function setupTouchControls() {
        const dpad = document.getElementById('dpad');
        if (!dpad) return;

        function setDir(dir, val) {
            onScreenControls[dir] = val;
        }

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
                if (dialogueActive) advanceDialogue();
                else tryInteract();
            });
            actionBtn.addEventListener('click', e => {
                if (dialogueActive) advanceDialogue();
                else tryInteract();
            });
        }
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

    function stop() {
        gameRunning = false;
    }

    function gameLoop(timestamp) {
        if (!gameRunning) return;
        const dt = timestamp - lastTime;
        lastTime = timestamp;

        update(dt);
        render();

        requestAnimationFrame(gameLoop);
    }

    function update(dt) {
        if (dialogueActive) {
            updateDialogue(dt);
            return;
        }

        updatePlayer(dt);
        updateNPCs(dt);
        updateCamera();
        checkTransitions();

        if (screenFlash) {
            screenFlash.timer -= dt;
            if (screenFlash.timer <= 0) screenFlash = null;
        }

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

        if (dx !== 0 && dy !== 0) {
            dx *= 0.707;
            dy *= 0.707;
        }

        let newX = player.x + dx;
        let newY = player.y + dy;

        const pw = SCALED_TILE * 0.6;
        const ph = SCALED_TILE * 0.4;
        const pox = (SCALED_TILE - pw) / 2;
        const poy = SCALED_TILE * 0.5;

        if (!checkCollision(newX + pox, player.y + poy, pw, ph)) {
            player.x = newX;
        }
        if (!checkCollision(player.x + pox, newY + poy, pw, ph)) {
            player.y = newY;
        }

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
            if (x < nx + SCALED_TILE * 0.8 && x + w > nx + SCALED_TILE * 0.2 &&
                y < ny + SCALED_TILE * 0.8 && y + h > ny + SCALED_TILE * 0.2) {
                return true;
            }
        }

        return false;
    }

    function updateNPCs(dt) {
        npcs.forEach(npc => {
            if (npc.patrol) {
                npc.animTimer = (npc.animTimer || 0) + dt;
                if (npc.animTimer >= 2000) {
                    npc.animTimer = 0;
                    const dirs = ['up','down','left','right'];
                    npc.facing = dirs[Math.floor(Math.random() * dirs.length)];
                }
            }
        });
    }

    function updateCamera() {
        const targetX = player.x - canvas.width / 2 + SCALED_TILE / 2;
        const targetY = player.y - canvas.height / 2 + SCALED_TILE / 2;

        camera.x += (targetX - camera.x) * 0.1;
        camera.y += (targetY - camera.y) * 0.1;

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
                    screenFlash = { color: '#000000', timer: 300, maxTimer: 300 };
                    transitionCallback(t.target, t.spawnX, t.spawnY);
                }
                return;
            }
        }
    }

    function tryInteract() {
        if (!player || dialogueActive) return;

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
                    if (obj.dialogue) {
                        showDialogue(obj.dialogue, obj.name);
                    }
                    if (obj.action && interactCallback) {
                        interactCallback(obj);
                    }
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
        currentDialogue = {
            text: dialogueQueue.shift(),
            speaker: speakerName || '',
            npc: npc,
            complete: false
        };
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
                if (dialogueCharIndex >= currentDialogue.text.length) {
                    currentDialogue.complete = true;
                }
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

            if (interactCallback && finishedNpc && finishedNpc.action) {
                interactCallback(finishedNpc);
            }
        }
    }

    function render() {
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        if (!currentMap) return;

        ctx.save();
        ctx.translate(-Math.round(camera.x), -Math.round(camera.y));

        renderMap();
        renderNPCs();
        renderPlayer();
        renderMapOverlay();

        ctx.restore();

        renderHUD();
        if (dialogueActive) renderDialogue();
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
                drawTile(tile, x, y);
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
                if (tile > 0) {
                    const x = col * SCALED_TILE;
                    const y = row * SCALED_TILE;
                    drawTile(tile, x, y);
                }
            }
        }
    }

    function drawTile(tileId, x, y) {
        const s = SCALED_TILE;
        const p = SCALE;

        switch(tileId) {
            case 0: break;
            case 1:
                ctx.fillStyle = COLORS.grass;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.grassAlt;
                for (let i = 0; i < 3; i++) {
                    const gx = x + ((tileId * 7 + i * 13) % 12) * p;
                    const gy = y + ((tileId * 11 + i * 17) % 12) * p;
                    ctx.fillRect(gx, gy, p, p * 2);
                }
                break;
            case 2:
                ctx.fillStyle = COLORS.path;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.pathEdge;
                for (let i = 0; i < 2; i++) {
                    const px = x + ((i * 23) % 14) * p;
                    const py = y + ((i * 19) % 14) * p;
                    ctx.fillRect(px, py, p * 2, p);
                }
                break;
            case 3:
                ctx.fillStyle = COLORS.water;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.waterLight;
                const waveOffset = (Date.now() / 500) % 4;
                for (let i = 0; i < 3; i++) {
                    const wx = x + ((i * 5 + Math.floor(waveOffset)) % 14) * p;
                    ctx.fillRect(wx, y + (4 + i * 4) * p, p * 3, p);
                }
                break;
            case 4:
                ctx.fillStyle = COLORS.wall;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.wallDark;
                ctx.fillRect(x, y + 14 * p, s, p * 2);
                ctx.fillStyle = COLORS.stoneLight;
                for (let i = 0; i < 4; i++) {
                    ctx.fillRect(x + (i * 4) * p, y + (i % 2 === 0 ? 2 : 8) * p, p * 3, p);
                }
                break;
            case 5:
                ctx.fillStyle = COLORS.wallTop;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.wall;
                ctx.fillRect(x, y + 12 * p, s, p * 4);
                break;
            case 6:
                ctx.fillStyle = COLORS.roof;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.roofDark;
                for (let i = 0; i < 8; i++) {
                    ctx.fillRect(x + i * 2 * p, y + (i % 2) * p, p * 2, p);
                }
                break;
            case 7:
                ctx.fillStyle = COLORS.wall;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.door;
                ctx.fillRect(x + 3 * p, y + 4 * p, p * 10, p * 12);
                ctx.fillStyle = COLORS.doorFrame;
                ctx.fillRect(x + 2 * p, y + 3 * p, p * 12, p * 2);
                ctx.fillRect(x + 2 * p, y + 3 * p, p * 2, p * 13);
                ctx.fillRect(x + 12 * p, y + 3 * p, p * 2, p * 13);
                ctx.fillStyle = COLORS.hudGold;
                ctx.fillRect(x + 11 * p, y + 10 * p, p, p);
                break;
            case 8:
                ctx.fillStyle = COLORS.wall;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.windowFrame;
                ctx.fillRect(x + 3 * p, y + 3 * p, p * 10, p * 8);
                ctx.fillStyle = COLORS.window;
                ctx.fillRect(x + 4 * p, y + 4 * p, p * 8, p * 6);
                ctx.fillStyle = COLORS.windowFrame;
                ctx.fillRect(x + 7.5 * p, y + 4 * p, p, p * 6);
                ctx.fillRect(x + 4 * p, y + 6.5 * p, p * 8, p);
                break;
            case 9:
                ctx.fillStyle = COLORS.grass;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.trunk;
                ctx.fillRect(x + 6 * p, y + 8 * p, p * 4, p * 8);
                ctx.fillStyle = COLORS.tree;
                ctx.fillRect(x + 2 * p, y + 1 * p, p * 12, p * 9);
                ctx.fillStyle = COLORS.treeLight;
                ctx.fillRect(x + 4 * p, y + 2 * p, p * 4, p * 3);
                ctx.fillRect(x + 3 * p, y + 4 * p, p * 3, p * 2);
                break;
            case 10:
                ctx.fillStyle = COLORS.grass;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.flower1;
                ctx.fillRect(x + 3 * p, y + 4 * p, p * 2, p * 2);
                ctx.fillStyle = COLORS.flower2;
                ctx.fillRect(x + 9 * p, y + 7 * p, p * 2, p * 2);
                ctx.fillStyle = COLORS.flower3;
                ctx.fillRect(x + 6 * p, y + 11 * p, p * 2, p * 2);
                ctx.fillStyle = '#22aa22';
                ctx.fillRect(x + 4 * p, y + 6 * p, p, p * 2);
                ctx.fillRect(x + 10 * p, y + 9 * p, p, p * 2);
                ctx.fillRect(x + 7 * p, y + 13 * p, p, p * 2);
                break;
            case 11:
                ctx.fillStyle = COLORS.wood;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.woodDark;
                for (let i = 0; i < 4; i++) {
                    ctx.fillRect(x, y + i * 4 * p, s, p);
                }
                break;
            case 12:
                ctx.fillStyle = COLORS.grass;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.signPost;
                ctx.fillRect(x + 7 * p, y + 8 * p, p * 2, p * 8);
                ctx.fillStyle = COLORS.sign;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p * 7);
                ctx.fillStyle = COLORS.woodDark;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p);
                ctx.fillRect(x + 2 * p, y + 8 * p, p * 12, p);
                break;
            case 13:
                ctx.fillStyle = COLORS.sand;
                ctx.fillRect(x, y, s, s);
                break;
            case 14:
                ctx.fillStyle = COLORS.stone;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = COLORS.stoneLight;
                for (let i = 0; i < 3; i++) {
                    for (let j = 0; j < 3; j++) {
                        ctx.fillRect(x + (1 + j * 5) * p, y + (1 + i * 5) * p, p * 4, p * 4);
                    }
                }
                ctx.fillStyle = '#5a5a5a';
                for (let i = 0; i < 4; i++) {
                    ctx.fillRect(x, y + i * 4 * p, s, p);
                    ctx.fillRect(x + (i * 4 + (Math.floor(i/2) * 2)) * p, y, p, s);
                }
                break;
            case 15:
                ctx.fillStyle = '#1a3a0e';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#0f2a08';
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 10, p * 12);
                break;
            case 16:
                ctx.fillStyle = COLORS.path;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#ffcc00';
                ctx.fillRect(x + 4 * p, y + 4 * p, p * 8, p * 8);
                ctx.fillStyle = '#aa8800';
                ctx.fillRect(x + 5 * p, y + 5 * p, p * 6, p * 6);
                ctx.fillStyle = '#ffcc00';
                ctx.fillRect(x + 6 * p, y + 6 * p, p * 4, p * 4);
                break;
            case 17:
                ctx.fillStyle = '#2a1a3a';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#3a2a4a';
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p * 12);
                ctx.fillStyle = '#6644aa';
                ctx.fillRect(x + 5 * p, y + 5 * p, p * 6, p * 6);
                break;
            default:
                ctx.fillStyle = '#ff00ff';
                ctx.fillRect(x, y, s, s);
        }
    }

    function renderPlayer() {
        if (!player) return;
        const x = Math.round(player.x);
        const y = Math.round(player.y);
        drawSprite('hero', x, y, player.facing, player.animFrame, player.moving);

        if (!dialogueActive) {
            for (let npc of npcs) {
                const nx = npc.x * SCALED_TILE;
                const ny = npc.y * SCALED_TILE;
                const dist = Math.sqrt((player.x - nx) ** 2 + (player.y - ny) ** 2);
                if (dist < SCALED_TILE * 2) {
                    ctx.fillStyle = COLORS.npcHighlight;
                    ctx.globalAlpha = 0.3 + Math.sin(Date.now() / 300) * 0.2;
                    ctx.fillRect(nx + 2 * SCALE, ny - 4 * SCALE, SCALED_TILE - 4 * SCALE, 3 * SCALE);
                    ctx.globalAlpha = 1;
                }
            }
        }
    }

    function renderNPCs() {
        npcs.forEach(npc => {
            const x = npc.x * SCALED_TILE;
            const y = npc.y * SCALED_TILE;
            drawSprite(npc.spriteType || 'npc', x, y, npc.facing, 0, false, npc.color);
        });
    }

    function drawSprite(type, x, y, facing, frame, moving, color) {
        const p = SCALE;
        const s = SCALED_TILE;

        const skinColor = color || (type === 'hero' ? '#ffcc88' : '#ddaa66');
        const hairColor = type === 'hero' ? '#554422' : (color ? shadeColor(color, -40) : '#886644');
        const bodyColor = type === 'hero' ? '#2244aa' : (color || '#44aa44');
        const bodyColor2 = type === 'hero' ? '#1a3388' : shadeColor(bodyColor, -20);
        const bootColor = '#553322';

        const bobY = moving ? Math.sin(frame * Math.PI / 2) * p : 0;

        ctx.fillStyle = bodyColor;
        ctx.fillRect(x + 4 * p, y + (7 - bobY / p) * p, p * 8, p * 5);
        ctx.fillStyle = bodyColor2;
        ctx.fillRect(x + 4 * p, y + (11 - bobY / p) * p, p * 8, p);

        ctx.fillStyle = bootColor;
        if (moving) {
            const legOffset = Math.sin(frame * Math.PI / 2) * 2;
            ctx.fillRect(x + (4 + legOffset) * p, y + 12 * p, p * 3, p * 4);
            ctx.fillRect(x + (9 - legOffset) * p, y + 12 * p, p * 3, p * 4);
        } else {
            ctx.fillRect(x + 4 * p, y + 12 * p, p * 3, p * 4);
            ctx.fillRect(x + 9 * p, y + 12 * p, p * 3, p * 4);
        }

        ctx.fillStyle = skinColor;
        ctx.fillRect(x + 5 * p, y + (2 - bobY / p) * p, p * 6, p * 6);

        ctx.fillStyle = hairColor;
        switch (facing) {
            case 'down':
                ctx.fillRect(x + 4 * p, y + (1 - bobY / p) * p, p * 8, p * 3);
                ctx.fillStyle = '#000000';
                ctx.fillRect(x + 6 * p, y + (4 - bobY / p) * p, p, p);
                ctx.fillRect(x + 9 * p, y + (4 - bobY / p) * p, p, p);
                ctx.fillStyle = skinColor;
                ctx.fillRect(x + 7 * p, y + (6 - bobY / p) * p, p * 2, p);
                break;
            case 'up':
                ctx.fillRect(x + 4 * p, y + (1 - bobY / p) * p, p * 8, p * 5);
                break;
            case 'left':
                ctx.fillRect(x + 4 * p, y + (1 - bobY / p) * p, p * 8, p * 3);
                ctx.fillRect(x + 4 * p, y + (3 - bobY / p) * p, p * 3, p * 3);
                ctx.fillStyle = '#000000';
                ctx.fillRect(x + 6 * p, y + (4 - bobY / p) * p, p, p);
                break;
            case 'right':
                ctx.fillRect(x + 4 * p, y + (1 - bobY / p) * p, p * 8, p * 3);
                ctx.fillRect(x + 9 * p, y + (3 - bobY / p) * p, p * 3, p * 3);
                ctx.fillStyle = '#000000';
                ctx.fillRect(x + 9 * p, y + (4 - bobY / p) * p, p, p);
                break;
        }

        if (moving && type === 'hero') {
            ctx.fillStyle = skinColor;
            const armSwing = Math.sin(frame * Math.PI / 2) * 2;
            ctx.fillRect(x + 2 * p, y + (8 + armSwing - bobY / p) * p, p * 2, p * 3);
            ctx.fillRect(x + 12 * p, y + (8 - armSwing - bobY / p) * p, p * 2, p * 3);
        } else {
            ctx.fillStyle = skinColor;
            ctx.fillRect(x + 2 * p, y + (8 - bobY / p) * p, p * 2, p * 3);
            ctx.fillRect(x + 12 * p, y + (8 - bobY / p) * p, p * 2, p * 3);
        }
    }

    function shadeColor(color, percent) {
        const num = parseInt(color.replace('#', ''), 16);
        const amt = Math.round(2.55 * percent);
        const R = Math.max(0, Math.min(255, (num >> 16) + amt));
        const G = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) + amt));
        const B = Math.max(0, Math.min(255, (num & 0x0000FF) + amt));
        return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
    }

    function renderHUD() {
        const hudH = 40;
        ctx.fillStyle = COLORS.hud;
        ctx.globalAlpha = 0.85;
        ctx.fillRect(0, 0, canvas.width, hudH);
        ctx.globalAlpha = 1;
        ctx.fillStyle = COLORS.hudBorder;
        ctx.fillRect(0, hudH - 2, canvas.width, 2);

        ctx.font = 'bold 14px monospace';
        ctx.textBaseline = 'middle';

        if (hudData.capital !== undefined) {
            ctx.fillStyle = COLORS.hudGold;
            ctx.fillText('$ ' + Number(hudData.capital).toLocaleString(), 10, hudH / 2);
        }

        if (hudData.morale !== undefined) {
            ctx.fillStyle = COLORS.hudGreen;
            ctx.fillText('MOR ' + hudData.morale, 160, hudH / 2);
        }

        if (hudData.brand !== undefined) {
            ctx.fillStyle = COLORS.hudRed;
            ctx.fillText('BRD ' + hudData.brand, 260, hudH / 2);
        }

        if (hudData.quarter !== undefined) {
            ctx.fillStyle = COLORS.hudBlue;
            ctx.fillText('Q' + hudData.quarter, 360, hudH / 2);
        }

        if (hudData.energy !== undefined) {
            ctx.fillStyle = '#ff8800';
            ctx.fillText('EN ' + hudData.energy, 420, hudH / 2);
        }

        if (currentMap && currentMap.name) {
            ctx.fillStyle = COLORS.dialogText;
            ctx.textAlign = 'right';
            ctx.fillText(currentMap.name, canvas.width - 10, hudH / 2);
            ctx.textAlign = 'left';
        }
    }

    function renderDialogue() {
        if (!currentDialogue) return;

        const dh = 120;
        const dx = 20;
        const dy = canvas.height - dh - 20;
        const dw = canvas.width - 40;

        ctx.fillStyle = COLORS.dialogBg;
        ctx.globalAlpha = 0.92;
        ctx.fillRect(dx, dy, dw, dh);
        ctx.globalAlpha = 1;

        ctx.strokeStyle = COLORS.dialogBorder;
        ctx.lineWidth = 3;
        ctx.strokeRect(dx, dy, dw, dh);

        ctx.strokeStyle = '#6666cc';
        ctx.lineWidth = 1;
        ctx.strokeRect(dx + 3, dy + 3, dw - 6, dh - 6);

        if (currentDialogue.speaker) {
            const nameW = ctx.measureText(currentDialogue.speaker).width + 20;
            ctx.fillStyle = COLORS.dialogBg;
            ctx.fillRect(dx + 10, dy - 14, nameW, 18);
            ctx.strokeStyle = COLORS.dialogBorder;
            ctx.lineWidth = 2;
            ctx.strokeRect(dx + 10, dy - 14, nameW, 18);

            ctx.fillStyle = COLORS.hudGold;
            ctx.font = 'bold 13px monospace';
            ctx.fillText(currentDialogue.speaker, dx + 20, dy - 2);
        }

        ctx.fillStyle = COLORS.dialogText;
        ctx.font = '14px monospace';
        const displayText = currentDialogue.text.substring(0, dialogueCharIndex);
        wrapText(ctx, displayText, dx + 16, dy + 24, dw - 32, 20);

        if (currentDialogue.complete) {
            const blink = Math.sin(Date.now() / 300) > 0;
            if (blink) {
                ctx.fillStyle = COLORS.dialogText;
                const triX = dx + dw - 24;
                const triY = dy + dh - 18;
                ctx.beginPath();
                ctx.moveTo(triX, triY);
                ctx.lineTo(triX + 8, triY);
                ctx.lineTo(triX + 4, triY + 6);
                ctx.closePath();
                ctx.fill();
            }
        }
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

    function updateHUD(data) {
        hudData = { ...hudData, ...data };
    }

    function setPlayerPosition(tileX, tileY) {
        if (player) {
            player.x = tileX * SCALED_TILE;
            player.y = tileY * SCALED_TILE;
        }
    }

    function isDialogueActive() {
        return dialogueActive;
    }

    return {
        init,
        loadMap,
        start,
        stop,
        updateHUD,
        setPlayerPosition,
        showDialogue,
        isDialogueActive,
        COLORS,
        SCALED_TILE
    };
})();
