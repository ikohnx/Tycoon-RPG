const RPGEngine = (function() {
    const TILE = 16;
    const SCALE = 3;
    const TS = TILE * SCALE;
    const STEP_DURATION = 180;

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
    let dialogueSpeed = 22;
    let keys = {};
    let lastTime = 0;
    let gameRunning = false;
    let onScreenControls = { up: false, down: false, left: false, right: false };
    let mapTransitions = [];
    let hudData = {};
    let screenFlash = null;
    let transitionCooldown = 0;
    let gt = 0;

    let choiceActive = false;
    let choiceOptions = [];
    let choiceIndex = 0;
    let choiceCallback = null;
    let choicePrompt = '';

    const C = {
        g1: '#2d8a2d', g2: '#258025', g3: '#3ba03b', gd: '#1a6e1a', gdd: '#145a14',
        p1: '#c8aa70', p2: '#b89860', p3: '#a88850', pe: '#987848',
        w1: '#3058b0', w2: '#3868c0', w3: '#2848a0', wf: '#88b0e0', ws: '#5080d0',
        bk1: '#808898', bk2: '#707888', bk3: '#909aa8', bkl: '#606070',
        rf1: '#b03030', rf2: '#c84848', rf3: '#882020', rfl: '#701818',
        dr1: '#704020', dr2: '#905830', drk: '#e8c840',
        wn1: '#58a0d8', wn2: '#78c0f0', wnf: '#505060',
        wd1: '#886030', wd2: '#a07840', wd3: '#685020',
        st1: '#787878', st2: '#909090', st3: '#606060',
        tr1: '#1a6428', tr2: '#228838', tr3: '#125018', tk1: '#604020', tk2: '#785030',
        fr: '#e84050', fy: '#e8c020', fp: '#b838e8', fw: '#f0e8f0',
        sg1: '#a87840', sg2: '#c89050', sgp: '#604020',
        pt1: '#5828a8', pt2: '#7838d8', pt3: '#a058f0',
        hg1: '#186020', hg2: '#207030',
        ch1: '#c89030', ch2: '#a87020', chl: '#e8d050',
        dbg1: '#000848', dbg2: '#101070',
        db1: '#e8e8f0', db2: '#8888c0', db3: '#484888',
        dt: '#ffffff', ds: '#000030',
        hbg: '#000840', hb: '#b0b0d0', hg: '#e8c020', hgr: '#40d840', hr: '#e84040', hbl: '#50a0f0',
        ng: '#f0d850',
        cbg: '#101060', cbo: '#c0c0e0', cc: '#e8e8f0',
        sh: 'rgba(0,0,0,0.3)',
        lp: '#e8c840', lpg: '#fff8d0',
        mk: '#cc3030', mkd: '#aa2020',
        bn: '#886030',
        wl: '#787878'
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
            if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' ','Enter','w','a','s','d'].includes(e.key)) e.preventDefault();
            if (choiceActive) {
                if (e.key === 'ArrowUp' || e.key === 'w') choiceIndex = Math.max(0, choiceIndex - 1);
                if (e.key === 'ArrowDown' || e.key === 's') choiceIndex = Math.min(choiceOptions.length - 1, choiceIndex + 1);
                if (e.key === 'Enter' || e.key === ' ') resolveChoice();
                if (e.key === 'Escape' || e.key === 'b' || e.key === 'B') { choiceIndex = choiceOptions.length - 1; resolveChoice(); }
                return;
            }
            if ((e.key === 'Enter' || e.key === ' ') && dialogueActive) { advanceDialogue(); return; }
            if ((e.key === 'Enter' || e.key === ' ') && !dialogueActive) { tryInteract(); return; }
        });
        window.addEventListener('keyup', e => { keys[e.key] = false; });
        if (options.onInteract) interactCallback = options.onInteract;
        if (options.onTransition) transitionCallback = options.onTransition;
        if (options.hudData) hudData = options.hudData;
        setupTouch();
    }

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        ctx.imageSmoothingEnabled = false;
    }

    function setupTouch() {
        function setDir(d, v) { onScreenControls[d] = v; }
        ['up','down','left','right'].forEach(d => {
            const b = document.getElementById('dpad-' + d);
            if (!b) return;
            b.addEventListener('touchstart', e => { e.preventDefault(); setDir(d, true); });
            b.addEventListener('touchend', e => { e.preventDefault(); setDir(d, false); });
            b.addEventListener('mousedown', () => setDir(d, true));
            b.addEventListener('mouseup', () => setDir(d, false));
        });
        const ab = document.getElementById('btn-action');
        if (ab) {
            const act = () => {
                if (choiceActive) { resolveChoice(); return; }
                if (dialogueActive) advanceDialogue();
                else tryInteract();
            };
            ab.addEventListener('touchstart', e => { e.preventDefault(); act(); });
            ab.addEventListener('click', act);
        }
        const cb = document.getElementById('btn-cancel');
        if (cb) {
            const cancel = () => { if (choiceActive) { choiceIndex = choiceOptions.length - 1; resolveChoice(); } };
            cb.addEventListener('touchstart', e => { e.preventDefault(); cancel(); });
            cb.addEventListener('click', cancel);
        }
        ['up','down'].forEach(d => {
            const b = document.getElementById('dpad-' + d);
            if (!b) return;
            b.addEventListener('touchstart', e => {
                if (choiceActive) {
                    e.preventDefault();
                    if (d === 'up') choiceIndex = Math.max(0, choiceIndex - 1);
                    if (d === 'down') choiceIndex = Math.min(choiceOptions.length - 1, choiceIndex + 1);
                }
            }, { capture: true });
        });
    }

    function loadMap(mapData, spawnXOverride, spawnYOverride) {
        currentMap = { ...mapData };
        npcs = [];
        mapTransitions = currentMap.transitions || [];
        if (currentMap.npcs) {
            currentMap.npcs.forEach(n => {
                npcs.push({ ...n, tileX: n.x, tileY: n.y, px: n.x * TS, py: n.y * TS,
                    animFrame: 0, animTimer: 0, idleTimer: Math.random() * 3000, facing: n.facing || 'down',
                    stepping: false, stepFrom: null, stepTo: null, stepProgress: 0, patrolTimer: 0 });
            });
        }
        const sx = spawnXOverride !== undefined ? spawnXOverride : (currentMap.spawnX || 5);
        const sy = spawnYOverride !== undefined ? spawnYOverride : (currentMap.spawnY || 5);
        if (!player) {
            player = { tileX: sx, tileY: sy, px: sx * TS, py: sy * TS, facing: 'down',
                stepping: false, stepFrom: null, stepTo: null, stepProgress: 0,
                animFrame: 0, animTimer: 0 };
        } else {
            player.tileX = sx; player.px = sx * TS;
            player.tileY = sy; player.py = sy * TS;
            player.stepping = false;
        }
        camera.x = player.px - canvas.width / 2 + TS / 2;
        camera.y = player.py - canvas.height / 2 + TS / 2;
        clampCamera();
    }

    function start() { if (gameRunning) return; gameRunning = true; lastTime = performance.now(); requestAnimationFrame(loop); }
    function stop() { gameRunning = false; }

    function loop(ts) {
        if (!gameRunning) return;
        const dt = Math.min(ts - lastTime, 50);
        lastTime = ts;
        gt += dt;
        update(dt);
        render();
        requestAnimationFrame(loop);
    }

    function update(dt) {
        if (overlayActive) return;
        if (choiceActive) return;
        if (dialogueActive) { updateDialogue(dt); return; }
        updatePlayer(dt);
        updateNPCs(dt);
        updateCamera(dt);
        checkTransitions();
        if (screenFlash) { screenFlash.timer -= dt; if (screenFlash.timer <= 0) screenFlash = null; }
        if (transitionCooldown > 0) transitionCooldown -= dt;
    }

    function updatePlayer(dt) {
        if (player.stepping) {
            player.stepProgress += dt / STEP_DURATION;
            if (player.stepProgress >= 1) {
                player.stepProgress = 0;
                player.stepping = false;
                player.tileX = player.stepTo.x;
                player.tileY = player.stepTo.y;
                player.px = player.tileX * TS;
                player.py = player.tileY * TS;
                player.animFrame = 0;
            } else {
                const t = player.stepProgress;
                player.px = player.stepFrom.x * TS + (player.stepTo.x - player.stepFrom.x) * t * TS;
                player.py = player.stepFrom.y * TS + (player.stepTo.y - player.stepFrom.y) * t * TS;
                player.animTimer += dt;
                if (player.animTimer > STEP_DURATION / 4) {
                    player.animTimer = 0;
                    player.animFrame = (player.animFrame + 1) % 4;
                }
            }
            return;
        }

        let dir = null;
        if (keys['ArrowUp'] || keys['w'] || onScreenControls.up) dir = 'up';
        else if (keys['ArrowDown'] || keys['s'] || onScreenControls.down) dir = 'down';
        else if (keys['ArrowLeft'] || keys['a'] || onScreenControls.left) dir = 'left';
        else if (keys['ArrowRight'] || keys['d'] || onScreenControls.right) dir = 'right';

        if (!dir) return;
        player.facing = dir;

        const dx = dir === 'left' ? -1 : dir === 'right' ? 1 : 0;
        const dy = dir === 'up' ? -1 : dir === 'down' ? 1 : 0;
        const nx = player.tileX + dx;
        const ny = player.tileY + dy;

        if (canWalk(nx, ny)) {
            player.stepping = true;
            player.stepFrom = { x: player.tileX, y: player.tileY };
            player.stepTo = { x: nx, y: ny };
            player.stepProgress = 0;
            player.animFrame = 1;
            player.animTimer = 0;
        }
    }

    function canWalk(tx, ty) {
        if (!currentMap) return false;
        if (tx < 0 || ty < 0 || tx >= currentMap.width || ty >= currentMap.height) return false;
        if (currentMap.collision[ty] && currentMap.collision[ty][tx] === 1) return false;
        for (let n of npcs) {
            if (n.tileX === tx && n.tileY === ty) return false;
        }
        return true;
    }

    function updateNPCs(dt) {
        npcs.forEach(npc => {
            if (npc.stepping) {
                npc.stepProgress += dt / (STEP_DURATION * 1.5);
                if (npc.stepProgress >= 1) {
                    npc.stepping = false;
                    npc.tileX = npc.stepTo.x;
                    npc.tileY = npc.stepTo.y;
                    npc.px = npc.tileX * TS;
                    npc.py = npc.tileY * TS;
                    npc.animFrame = 0;
                } else {
                    npc.px = npc.stepFrom.x * TS + (npc.stepTo.x - npc.stepFrom.x) * npc.stepProgress * TS;
                    npc.py = npc.stepFrom.y * TS + (npc.stepTo.y - npc.stepFrom.y) * npc.stepProgress * TS;
                    npc.animTimer += dt;
                    if (npc.animTimer > STEP_DURATION / 3) { npc.animTimer = 0; npc.animFrame = (npc.animFrame + 1) % 4; }
                }
                return;
            }

            npc.patrolTimer = (npc.patrolTimer || 0) + dt;
            npc.idleTimer = (npc.idleTimer || 0) + dt;
            if (npc.idleTimer > 2500 + Math.random() * 2000) {
                npc.idleTimer = 0;
                const dirs = ['up','down','left','right'];
                npc.facing = dirs[Math.floor(Math.random() * dirs.length)];
            }

            if (!npc.stationary && npc.patrolTimer > 3000 + Math.random() * 4000) {
                npc.patrolTimer = 0;
                const dirs = [{dx:0,dy:-1,f:'up'},{dx:0,dy:1,f:'down'},{dx:-1,dy:0,f:'left'},{dx:1,dy:0,f:'right'}];
                const d = dirs[Math.floor(Math.random() * dirs.length)];
                const nx = npc.tileX + d.dx;
                const ny = npc.tileY + d.dy;
                if (canWalkNPC(nx, ny, npc)) {
                    npc.facing = d.f;
                    npc.stepping = true;
                    npc.stepFrom = { x: npc.tileX, y: npc.tileY };
                    npc.stepTo = { x: nx, y: ny };
                    npc.stepProgress = 0;
                    npc.animFrame = 1;
                    npc.animTimer = 0;
                }
            }
        });
    }

    function canWalkNPC(tx, ty, self) {
        if (!currentMap) return false;
        if (tx < 0 || ty < 0 || tx >= currentMap.width || ty >= currentMap.height) return false;
        if (currentMap.collision[ty] && currentMap.collision[ty][tx] === 1) return false;
        if (player && player.tileX === tx && player.tileY === ty) return false;
        for (let n of npcs) {
            if (n === self) continue;
            if (n.tileX === tx && n.tileY === ty) return false;
        }
        return true;
    }

    function updateCamera(dt) {
        const tx = player.px - canvas.width / 2 + TS / 2;
        const ty = player.py - canvas.height / 2 + TS / 2;
        camera.x += (tx - camera.x) * 0.12;
        camera.y += (ty - camera.y) * 0.12;
        clampCamera();
    }

    function clampCamera() {
        if (!currentMap) return;
        const mw = currentMap.width * TS;
        const mh = currentMap.height * TS;
        camera.x = Math.max(0, Math.min(mw - canvas.width, camera.x));
        camera.y = Math.max(0, Math.min(mh - canvas.height, camera.y));
        if (mw < canvas.width) camera.x = (mw - canvas.width) / 2;
        if (mh < canvas.height) camera.y = (mh - canvas.height) / 2;
    }

    function checkTransitions() {
        if (transitionCooldown > 0 || player.stepping) return;
        for (let t of mapTransitions) {
            if (player.tileX === t.x && player.tileY === t.y) {
                if (transitionCallback) {
                    transitionCooldown = 1000;
                    screenFlash = { color: '#000', timer: 400, maxTimer: 400 };
                    transitionCallback(t.target, t.spawnX, t.spawnY);
                }
                return;
            }
        }
    }

    function tryInteract() {
        if (!player || dialogueActive || choiceActive || player.stepping) return;
        const dirs = { up:{dx:0,dy:-1}, down:{dx:0,dy:1}, left:{dx:-1,dy:0}, right:{dx:1,dy:0} };
        const d = dirs[player.facing];
        const fx = player.tileX + d.dx;
        const fy = player.tileY + d.dy;

        for (let npc of npcs) {
            if (npc.tileX === fx && npc.tileY === fy) {
                npc.facing = oppDir(player.facing);
                if (npc.dialogue) showDialogue(npc.dialogue, npc.name, npc);
                else if (interactCallback) interactCallback(npc);
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

    function oppDir(d) { return {up:'down',down:'up',left:'right',right:'left'}[d]; }

    function showDialogue(msgs, speaker, npc) {
        if (typeof msgs === 'string') msgs = [msgs];
        dialogueQueue = [...msgs];
        dialogueActive = true;
        currentDialogue = { text: dialogueQueue.shift(), speaker: speaker || '', npc, complete: false };
        dialogueCharIndex = 0;
        dialogueTimer = 0;
    }

    function updateDialogue(dt) {
        if (!currentDialogue) return;
        if (!currentDialogue.complete) {
            dialogueTimer += dt;
            if (dialogueTimer >= dialogueSpeed) { dialogueTimer = 0; dialogueCharIndex++; if (dialogueCharIndex >= currentDialogue.text.length) currentDialogue.complete = true; }
        }
    }

    function advanceDialogue() {
        if (!currentDialogue) return;
        if (!currentDialogue.complete) { dialogueCharIndex = currentDialogue.text.length; currentDialogue.complete = true; return; }
        if (dialogueQueue.length > 0) {
            currentDialogue.text = dialogueQueue.shift();
            currentDialogue.complete = false;
            dialogueCharIndex = 0;
            dialogueTimer = 0;
        } else {
            const npc = currentDialogue.npc;
            dialogueActive = false;
            currentDialogue = null;
            if (npc && npc.action && npc.route) {
                showChoice('Visit ' + npc.name + '?', ['Yes', 'No'], idx => {
                    if (idx === 0 && interactCallback) interactCallback(npc);
                });
            }
        }
    }

    function showChoice(prompt, options, callback) {
        choiceActive = true; choiceOptions = options; choiceIndex = 0; choiceCallback = callback; choicePrompt = prompt;
    }
    function resolveChoice() {
        if (!choiceActive) return;
        choiceActive = false;
        if (choiceCallback) choiceCallback(choiceIndex);
    }

    function render() {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        if (!currentMap) return;

        ctx.save();
        ctx.translate(-Math.round(camera.x), -Math.round(camera.y));
        renderTiles();
        renderShadows();
        renderEntities();
        renderOverlay();
        ctx.restore();

        renderHUD();
        if (dialogueActive) renderDialogue();
        if (choiceActive) renderChoiceBox();
        if (screenFlash) renderFlash();
    }

    function renderTiles() {
        const sc = Math.max(0, Math.floor(camera.x / TS) - 1);
        const ec = Math.min(currentMap.width - 1, Math.ceil((camera.x + canvas.width) / TS) + 1);
        const sr = Math.max(0, Math.floor(camera.y / TS) - 1);
        const er = Math.min(currentMap.height - 1, Math.ceil((camera.y + canvas.height) / TS) + 1);
        for (let r = sr; r <= er; r++) {
            for (let c = sc; c <= ec; c++) {
                drawTile(currentMap.tiles[r][c], c * TS, r * TS, r, c);
            }
        }
    }

    function renderOverlay() {
        if (!currentMap.overlay) return;
        const sc = Math.max(0, Math.floor(camera.x / TS) - 1);
        const ec = Math.min(currentMap.width - 1, Math.ceil((camera.x + canvas.width) / TS) + 1);
        const sr = Math.max(0, Math.floor(camera.y / TS) - 1);
        const er = Math.min(currentMap.height - 1, Math.ceil((camera.y + canvas.height) / TS) + 1);
        for (let r = sr; r <= er; r++) {
            for (let c = sc; c <= ec; c++) {
                const t = currentMap.overlay[r] ? currentMap.overlay[r][c] : 0;
                if (t > 0) drawTile(t, c * TS, r * TS, r, c);
            }
        }
    }

    function renderShadows() {
        ctx.fillStyle = C.sh;
        const drawSh = (x, y) => {
            ctx.beginPath();
            ctx.ellipse(x + TS * 0.5, y + TS * 0.92, TS * 0.28, TS * 0.08, 0, 0, Math.PI * 2);
            ctx.fill();
        };
        npcs.forEach(n => drawSh(n.px, n.py));
        if (player) drawSh(player.px, player.py);
    }

    function renderEntities() {
        const ents = [];
        npcs.forEach(n => {
            ents.push({ type: 'npc', data: n, x: n.px, y: n.py, sortY: n.py });
        });
        if (player) ents.push({ type: 'player', data: player, x: player.px, y: player.py, sortY: player.py });
        ents.sort((a, b) => a.sortY - b.sortY);

        ents.forEach(e => {
            if (e.type === 'npc') {
                const n = e.data;
                drawSprite('npc', e.x, e.y, n.facing, n.animFrame || 0, n.stepping, n.color, n.spriteId);
                if (!dialogueActive && !choiceActive && player) {
                    const dist = Math.abs(player.px - e.x) + Math.abs(player.py - e.y);
                    if (dist < TS * 2.2 && dist > 0) renderBubble(e.x, e.y);
                }
            } else {
                drawSprite('hero', e.x, e.y, player.facing, player.animFrame, player.stepping);
            }
        });
    }

    function renderBubble(x, y) {
        const bob = Math.sin(gt / 300) * 3 * SCALE;
        const ix = x + TS / 2;
        const iy = y - 4 * SCALE + bob;
        ctx.fillStyle = C.ng;
        ctx.beginPath();
        ctx.moveTo(ix - 3 * SCALE, iy - 5 * SCALE);
        ctx.lineTo(ix + 3 * SCALE, iy - 5 * SCALE);
        ctx.lineTo(ix, iy);
        ctx.closePath();
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.globalAlpha = 0.5;
        ctx.fillRect(ix - 2 * SCALE, iy - 4 * SCALE, SCALE, SCALE);
        ctx.globalAlpha = 1;
    }

    function drawTile(id, x, y, row, col) {
        const s = TS;
        const p = SCALE;
        const sd = (row * 131 + col * 97) & 0xFF;
        const t = gt;

        switch(id) {
            case 0: break;
            case 1: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.g3;
                for (let i = 0; i < 6; i++) {
                    const gx = ((sd * 7 + i * 31) % 14) * p;
                    const gy = ((sd * 11 + i * 23) % 14) * p;
                    ctx.fillRect(x + gx, y + gy, p, p * 2);
                    if (i < 3) { ctx.fillStyle = C.gd; ctx.fillRect(x + gx + p, y + gy + p, p, p); ctx.fillStyle = C.g3; }
                }
                ctx.fillStyle = C.gdd;
                ctx.fillRect(x + ((sd * 3) % 13) * p, y + ((sd * 5) % 13) * p, p, p);
                break;
            }
            case 2: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                for (let br = 0; br < 3; br++) {
                    for (let bc = 0; bc < 2; bc++) {
                        ctx.fillStyle = C.p2;
                        const bx = (bc * 8 + (br % 2) * 4) * p;
                        const by = br * 5 * p;
                        ctx.fillRect(x + bx + p, y + by + p, p * 6, p * 4);
                        ctx.fillStyle = C.p3;
                        ctx.fillRect(x + bx + p, y + by + 4 * p, p * 6, p);
                    }
                }
                ctx.fillStyle = C.pe;
                for (let i = 0; i <= 3; i++) ctx.fillRect(x, y + i * 5 * p, s, p);
                ctx.fillRect(x + 8 * p, y, p, s);
                if ((sd & 3) === 0) { ctx.fillStyle = C.p3; ctx.fillRect(x + ((sd*7)%12)*p, y + ((sd*3)%12)*p, p*2, p); }
                break;
            }
            case 3: {
                ctx.fillStyle = C.w1;
                ctx.fillRect(x, y, s, s);
                const wt = t / 500;
                ctx.fillStyle = C.w2;
                for (let i = 0; i < 4; i++) {
                    const wx = (Math.sin(wt + i * 1.5 + col * 0.7) * 3 + 6) * p;
                    ctx.fillRect(x + wx, y + (i * 4 + 1) * p, p * 5, p);
                    ctx.fillStyle = C.ws;
                    ctx.fillRect(x + wx + p, y + (i * 4 + 2) * p, p * 3, p);
                    ctx.fillStyle = C.w2;
                }
                ctx.fillStyle = C.wf;
                ctx.globalAlpha = 0.25 + Math.sin(wt + col + row) * 0.1;
                ctx.fillRect(x + ((sd * 3) % 8) * p, y + ((sd * 7) % 10) * p, p * 3, p);
                ctx.globalAlpha = 1;
                break;
            }
            case 4: {
                ctx.fillStyle = C.bk1;
                ctx.fillRect(x, y, s, s);
                for (let br = 0; br < 4; br++) {
                    for (let bc = 0; bc < 2; bc++) {
                        ctx.fillStyle = ((br + bc) & 1) ? C.bk2 : C.bk3;
                        const bx = (bc * 8 + (br % 2) * 4) * p;
                        ctx.fillRect(x + bx, y + br * 4 * p, p * 7, p * 3);
                    }
                }
                ctx.fillStyle = C.bkl;
                for (let i = 0; i < 5; i++) ctx.fillRect(x, y + i * 4 * p, s, p);
                ctx.fillRect(x + 8 * p, y, p, s);
                ctx.fillRect(x + 4 * p, y + 4 * p, p, 4 * p);
                ctx.fillRect(x + 12 * p, y + 4 * p, p, 4 * p);
                ctx.fillStyle = 'rgba(0,0,0,0.08)';
                ctx.fillRect(x, y + s - 2 * p, s, 2 * p);
                break;
            }
            case 5: {
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.bk1;
                ctx.fillRect(x, y + 10 * p, s, 6 * p);
                ctx.fillStyle = C.bkl;
                ctx.fillRect(x, y + 10 * p, s, p);
                for (let i = 0; i < 4; i++) ctx.fillRect(x + i * 4 * p, y, p * 3, 4 * p);
                ctx.fillStyle = 'rgba(255,255,255,0.06)';
                ctx.fillRect(x, y, s, 3 * p);
                break;
            }
            case 6: {
                ctx.fillStyle = C.rf1;
                ctx.fillRect(x, y, s, s);
                for (let r = 0; r < 4; r++) {
                    for (let c = 0; c < 4; c++) {
                        ctx.fillStyle = ((r + c) & 1) ? C.rf2 : C.rf1;
                        ctx.fillRect(x + (c * 4 + (r % 2) * 2) * p, y + r * 4 * p, p * 3, p * 3);
                    }
                }
                ctx.fillStyle = C.rf3;
                for (let i = 0; i < 4; i++) ctx.fillRect(x, y + i * 4 * p + 3 * p, s, p);
                ctx.fillStyle = C.rfl;
                ctx.fillRect(x, y + s - p, s, p);
                ctx.fillStyle = 'rgba(255,255,255,0.08)';
                ctx.fillRect(x, y, s, 2 * p);
                break;
            }
            case 7: {
                ctx.fillStyle = C.bk1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.dr1;
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 10, p * 14);
                ctx.fillStyle = C.dr2;
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 8, p * 12);
                ctx.fillStyle = C.dr1;
                ctx.fillRect(x + 7.5 * p, y + 3 * p, p, p * 12);
                ctx.fillRect(x + 4 * p, y + 8 * p, p * 8, p);
                ctx.fillStyle = C.drk;
                ctx.fillRect(x + 10 * p, y + 9 * p, p * 2, p * 2);
                ctx.fillStyle = '#c0a030';
                ctx.fillRect(x + 10 * p, y + 9 * p, p, p);
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x + 2 * p, y + p, p * 12, p);
                ctx.fillRect(x + 2 * p, y + p, p, p * 15);
                ctx.fillRect(x + 13 * p, y + p, p, p * 15);
                break;
            }
            case 8: {
                ctx.fillStyle = C.bk1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.wnf;
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 10, p * 10);
                ctx.fillStyle = C.wn1;
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 8, p * 8);
                const sh = Math.sin(t / 800 + col) * 0.15 + 0.85;
                ctx.fillStyle = C.wn2;
                ctx.globalAlpha = sh;
                ctx.fillRect(x + 5 * p, y + 4 * p, p * 3, p * 3);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wnf;
                ctx.fillRect(x + 7.5 * p, y + 3 * p, p, p * 8);
                ctx.fillRect(x + 4 * p, y + 6.5 * p, p * 8, p);
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x + 3 * p, y + 12 * p, p * 10, p * 2);
                break;
            }
            case 9: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.tk1;
                ctx.fillRect(x + 6 * p, y + 10 * p, p * 4, p * 6);
                ctx.fillStyle = C.tk2;
                ctx.fillRect(x + 7 * p, y + 10 * p, p * 2, p * 6);
                ctx.fillStyle = C.tr3;
                ctx.fillRect(x + p, y + 2 * p, p * 14, p * 10);
                ctx.fillStyle = C.tr1;
                ctx.fillRect(x + 2 * p, y + p, p * 12, p * 9);
                ctx.fillStyle = C.tr2;
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 5, p * 5);
                ctx.fillRect(x + 9 * p, y + 3 * p, p * 4, p * 4);
                const sway = Math.sin(t / 2500 + sd) * p * 0.4;
                ctx.fillStyle = C.tr2;
                ctx.fillRect(x + 4 * p + sway, y + p, p * 4, p * 2);
                ctx.fillStyle = C.tr3;
                ctx.fillRect(x + 2 * p, y + 9 * p, p * 3, p * 2);
                ctx.fillRect(x + 11 * p, y + 8 * p, p * 3, p * 2);
                break;
            }
            case 10: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                const fs = Math.sin(t / 700 + sd) * p * 0.4;
                [{cx:3,cy:3,c:C.fr},{cx:9,cy:5,c:C.fy},{cx:5,cy:10,c:C.fp},{cx:12,cy:8,c:C.fw},{cx:7,cy:2,c:C.fr}].forEach((f,i) => {
                    ctx.fillStyle = '#228822';
                    ctx.fillRect(x + (f.cx + 0.5) * p, y + (f.cy + 2) * p, p, p * 3);
                    ctx.fillStyle = f.c;
                    ctx.fillRect(x + f.cx * p + (i % 2 ? fs : -fs), y + f.cy * p, p * 2, p * 2);
                    ctx.fillStyle = C.fy;
                    ctx.fillRect(x + (f.cx + 0.5) * p + (i % 2 ? fs : -fs), y + (f.cy + 0.5) * p, p, p);
                });
                break;
            }
            case 11: {
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.wd2;
                for (let i = 0; i < 4; i++) ctx.fillRect(x + (i * 4 + (sd & 1)) * p, y, p * 3, s);
                ctx.fillStyle = C.wd3;
                for (let i = 0; i <= 4; i++) ctx.fillRect(x, y + i * 4 * p, s, p);
                break;
            }
            case 12: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.sgp;
                ctx.fillRect(x + 7 * p, y + 8 * p, p * 2, p * 8);
                ctx.fillStyle = C.sg1;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p * 7);
                ctx.fillStyle = C.sg2;
                ctx.fillRect(x + 3 * p, y + 3 * p, p * 10, p * 5);
                ctx.fillStyle = C.sgp;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p);
                ctx.fillRect(x + 2 * p, y + 8 * p, p * 12, p);
                ctx.fillRect(x + 2 * p, y + 2 * p, p, p * 7);
                ctx.fillRect(x + 13 * p, y + 2 * p, p, p * 7);
                break;
            }
            case 13: {
                ctx.fillStyle = '#d8b868';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#c8a858';
                for (let i = 0; i < 5; i++) ctx.fillRect(x + ((sd * 3 + i * 7) % 13) * p, y + ((sd * 5 + i * 11) % 13) * p, p * 2, p);
                break;
            }
            case 14: {
                ctx.fillStyle = C.st1;
                ctx.fillRect(x, y, s, s);
                for (let r = 0; r < 2; r++) {
                    for (let c = 0; c < 2; c++) {
                        ctx.fillStyle = C.st2;
                        ctx.fillRect(x + (c * 8 + (r % 2) * 4 + 1) * p, y + (r * 8 + 1) * p, p * 6, p * 6);
                    }
                }
                ctx.fillStyle = C.st3;
                ctx.fillRect(x, y, s, p); ctx.fillRect(x, y + 8 * p, s, p);
                ctx.fillRect(x, y, p, s); ctx.fillRect(x + 8 * p, y, p, s);
                break;
            }
            case 15: {
                ctx.fillStyle = C.hg1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.hg2;
                ctx.fillRect(x + 2 * p, y + p, p * 12, p * 12);
                ctx.fillStyle = C.tr2;
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 4, p * 4);
                ctx.fillRect(x + 8 * p, y + 5 * p, p * 4, p * 3);
                ctx.fillStyle = C.tr3;
                ctx.fillRect(x + p, y + 13 * p, p * 14, p * 3);
                break;
            }
            case 16: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.ch2;
                ctx.fillRect(x + 3 * p, y + 5 * p, p * 10, p * 9);
                ctx.fillStyle = C.ch1;
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 8, p * 4);
                ctx.fillRect(x + 4 * p, y + 8 * p, p * 8, p * 5);
                ctx.fillStyle = C.chl;
                ctx.fillRect(x + 7 * p, y + 6 * p, p * 2, p * 4);
                ctx.fillStyle = '#906010';
                ctx.fillRect(x + 4 * p, y + 7 * p, p * 8, p);
                break;
            }
            case 17: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                const pt = t / 350;
                ctx.fillStyle = C.pt1;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p * 12);
                for (let i = 0; i < 8; i++) {
                    const a = pt + i * Math.PI / 4;
                    const r = 4 * p;
                    ctx.fillStyle = i % 2 ? C.pt2 : C.pt3;
                    ctx.fillRect(x + 8 * p + Math.cos(a) * r - p, y + 8 * p + Math.sin(a) * r - p, p * 2, p * 2);
                }
                ctx.fillStyle = C.pt3;
                ctx.globalAlpha = 0.4 + Math.sin(pt * 2) * 0.3;
                ctx.fillRect(x + 5 * p, y + 5 * p, p * 6, p * 6);
                ctx.globalAlpha = 1;
                break;
            }
            case 18: {
                ctx.fillStyle = C.st1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.st2;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p * 12);
                ctx.fillStyle = C.w1;
                ctx.fillRect(x + 3 * p, y + 3 * p, p * 10, p * 10);
                const ft = t / 400;
                ctx.fillStyle = C.w2;
                ctx.fillRect(x + 4 * p, y + (4 + Math.sin(ft) * 1.2) * p, p * 3, p * 2);
                ctx.fillRect(x + 9 * p, y + (6 + Math.cos(ft) * 1.2) * p, p * 3, p * 2);
                ctx.fillStyle = C.st1;
                ctx.fillRect(x + 7 * p, y + 4 * p, p * 2, p * 8);
                ctx.fillStyle = C.wf;
                ctx.globalAlpha = 0.4 + Math.sin(ft * 2) * 0.25;
                ctx.fillRect(x + 6 * p, y + 2 * p, p * 4, p * 3);
                ctx.globalAlpha = 1;
                break;
            }
            case 19: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#404040';
                ctx.fillRect(x + 7 * p, y + 4 * p, p * 2, p * 12);
                ctx.fillStyle = '#505050';
                ctx.fillRect(x + 5 * p, y + 14 * p, p * 6, p * 2);
                const lg = 0.5 + Math.sin(t / 1200 + sd) * 0.25;
                ctx.fillStyle = C.lp;
                ctx.globalAlpha = lg;
                ctx.fillRect(x + 5 * p, y + p, p * 6, p * 4);
                ctx.fillStyle = C.lpg;
                ctx.fillRect(x + 6 * p, y + 2 * p, p * 4, p * 2);
                ctx.globalAlpha = lg * 0.15;
                ctx.fillStyle = C.lpg;
                ctx.beginPath();
                ctx.arc(x + 8 * p, y + 3 * p, 8 * p, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
                break;
            }
            case 20: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + p, y + 6 * p, p * 14, p * 10);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 2 * p, y + 7 * p, p * 12, p * 8);
                ctx.fillStyle = C.mk;
                ctx.fillRect(x + p, y + p, p * 14, p * 5);
                ctx.fillStyle = C.mkd;
                for (let i = 0; i < 7; i++) ctx.fillRect(x + (1 + i * 2) * p, y + 5 * p, p * 2, p * 2);
                ctx.fillStyle = C.fy;
                ctx.fillRect(x + 3 * p, y + 8 * p, p * 3, p * 3);
                ctx.fillStyle = C.fr;
                ctx.fillRect(x + 8 * p, y + 8 * p, p * 3, p * 3);
                break;
            }
            case 21: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 2 * p, y + 8 * p, p * 12, p * 3);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 2 * p, y + 5 * p, p * 12, p * 2);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 3 * p, y + 11 * p, p * 2, p * 4);
                ctx.fillRect(x + 11 * p, y + 11 * p, p * 2, p * 4);
                break;
            }
            case 22: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.st2;
                ctx.fillRect(x + 3 * p, y + 6 * p, p * 10, p * 10);
                ctx.fillStyle = C.st1;
                ctx.fillRect(x + 4 * p, y + 7 * p, p * 8, p * 8);
                ctx.fillStyle = C.w1;
                ctx.fillRect(x + 5 * p, y + 8 * p, p * 6, p * 6);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 7 * p, y + 2 * p, p * 2, p * 5);
                ctx.fillRect(x + 4 * p, y + 2 * p, p * 8, p * 2);
                break;
            }
            case 23: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#8B4513';
                ctx.fillRect(x + 2 * p, y + 4 * p, p * 5, p * 4);
                ctx.fillRect(x + 2 * p, y + 9 * p, p * 5, p * 4);
                ctx.fillStyle = '#A0522D';
                ctx.fillRect(x + 3 * p, y + 5 * p, p * 3, p * 2);
                ctx.fillRect(x + 3 * p, y + 10 * p, p * 3, p * 2);
                ctx.fillStyle = '#8B4513';
                ctx.fillRect(x + 9 * p, y + 6 * p, p * 5, p * 5);
                ctx.fillStyle = '#A0522D';
                ctx.fillRect(x + 10 * p, y + 7 * p, p * 3, p * 3);
                break;
            }
            case 24: {
                ctx.fillStyle = C.bk1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#505860';
                ctx.fillRect(x + 2 * p, y + 6 * p, p * 12, p * 10);
                ctx.fillStyle = '#404850';
                ctx.fillRect(x + 3 * p, y + 7 * p, p * 10, p * 8);
                ctx.fillStyle = '#d04010';
                ctx.fillRect(x + 5 * p, y + 9 * p, p * 6, p * 4);
                ctx.fillStyle = '#e06020';
                const flicker = 0.7 + Math.sin(t / 200 + sd * 3) * 0.3;
                ctx.globalAlpha = flicker;
                ctx.fillRect(x + 6 * p, y + 8 * p, p * 4, p * 3);
                ctx.fillStyle = '#f0a040';
                ctx.fillRect(x + 7 * p, y + 9 * p, p * 2, p * 2);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#606870';
                ctx.fillRect(x + 6 * p, y + 2 * p, p * 4, p * 5);
                ctx.fillRect(x + 5 * p, y + 3 * p, p * 6, p);
                break;
            }
            case 25: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#c0a070';
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 10, p * 12);
                ctx.fillStyle = '#d8b880';
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 8, p * 10);
                ctx.fillStyle = '#a08060';
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 8, p);
                ctx.fillRect(x + 4 * p, y + 7 * p, p * 8, p);
                ctx.fillRect(x + 4 * p, y + 11 * p, p * 8, p);
                ctx.fillStyle = '#604020';
                ctx.fillRect(x + 5 * p, y + 4 * p, p * 3, p * 2);
                ctx.fillRect(x + 9 * p, y + 4 * p, p * 2, p * 2);
                ctx.fillRect(x + 5 * p, y + 8 * p, p * 6, p * 2);
                break;
            }
            default:
                ctx.fillStyle = '#ff00ff';
                ctx.fillRect(x, y, s, s);
        }
    }

    function drawSprite(type, x, y, facing, frame, moving, color, spriteId) {
        const p = SCALE;
        const isHero = type === 'hero';
        const pal = isHero ? {
            hair: '#443322', hairHL: '#665544',
            skin: '#f0c888', skinSh: '#d0a868',
            eye: '#203060',
            tunic: '#2040a8', tunicHL: '#3060c8', tunicDk: '#182878',
            belt: '#c89830', beltBk: '#a07820',
            pants: '#304888', pantsDk: '#203060',
            boots: '#503820', bootsHL: '#685030',
            cape: '#a82020', capeDk: '#801818',
            outline: '#181020'
        } : getNPCPal(color, spriteId);

        const bob = moving ? Math.sin(frame * Math.PI / 2) * p * 0.8 : 0;
        const wc = moving ? frame % 4 : 0;
        const legL = wc === 1 ? 2 * p : wc === 3 ? -p : 0;
        const legR = wc === 1 ? -p : wc === 3 ? 2 * p : 0;
        const armSwing = moving ? Math.sin(frame * Math.PI / 2) * 2 * p : 0;

        const by = -bob;
        switch(facing) {
            case 'down':
                ctx.fillStyle = pal.outline;
                ctx.fillRect(x + 3 * p, y + by, p * 10, p);
                ctx.fillRect(x + 2 * p, y + p + by, p, p * 3);
                ctx.fillRect(x + 13 * p, y + p + by, p, p * 3);
                ctx.fillStyle = pal.hair;
                ctx.fillRect(x + 3 * p, y + by, p * 10, p * 4);
                ctx.fillStyle = pal.hairHL;
                ctx.fillRect(x + 5 * p, y + p + by, p * 4, p);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + 4 * p, y + 3 * p + by, p * 8, p * 4);
                ctx.fillStyle = pal.skinSh;
                ctx.fillRect(x + 4 * p, y + 6 * p + by, p * 8, p);
                ctx.fillStyle = pal.eye;
                ctx.fillRect(x + 5 * p, y + 4 * p + by, p * 2, p * 2);
                ctx.fillRect(x + 9 * p, y + 4 * p + by, p * 2, p * 2);
                ctx.fillStyle = '#fff';
                ctx.fillRect(x + 5 * p, y + 4 * p + by, p, p);
                ctx.fillRect(x + 9 * p, y + 4 * p + by, p, p);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + 7 * p, y + 6 * p + by, p * 2, p);
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(x + 3 * p, y + 7 * p + by, p * 10, p * 4);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(x + 5 * p, y + 7 * p + by, p * 3, p * 3);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(x + 3 * p, y + 10 * p + by, p * 10, p);
                ctx.fillStyle = pal.belt;
                ctx.fillRect(x + 3 * p, y + 10 * p + by, p * 10, p);
                ctx.fillStyle = pal.beltBk;
                ctx.fillRect(x + 7 * p, y + 10 * p + by, p * 2, p);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + (2 + armSwing / p) * p, y + 8 * p + by, p * 2, p * 3);
                ctx.fillRect(x + (12 - armSwing / p) * p, y + 8 * p + by, p * 2, p * 3);
                ctx.fillStyle = pal.pants;
                ctx.fillRect(x + 4 * p, y + 11 * p, p * 3, p * 2);
                ctx.fillRect(x + 9 * p, y + 11 * p, p * 3, p * 2);
                ctx.fillStyle = pal.boots;
                ctx.fillRect(x + 4 * p, y + 13 * p + legL, p * 3, p * 3);
                ctx.fillRect(x + 9 * p, y + 13 * p + legR, p * 3, p * 3);
                ctx.fillStyle = pal.bootsHL;
                ctx.fillRect(x + 4 * p, y + 13 * p + legL, p * 3, p);
                ctx.fillRect(x + 9 * p, y + 13 * p + legR, p * 3, p);
                break;
            case 'up':
                ctx.fillStyle = pal.hair;
                ctx.fillRect(x + 3 * p, y + by, p * 10, p * 7);
                ctx.fillStyle = pal.hairHL;
                ctx.fillRect(x + 5 * p, y + p + by, p * 4, p * 2);
                if (isHero) {
                    ctx.fillStyle = pal.cape;
                    ctx.fillRect(x + 3 * p, y + 7 * p + by, p * 10, p * 5);
                    ctx.fillStyle = pal.capeDk;
                    ctx.fillRect(x + 7.5 * p, y + 7 * p + by, p, p * 5);
                } else {
                    ctx.fillStyle = pal.tunic;
                    ctx.fillRect(x + 3 * p, y + 7 * p + by, p * 10, p * 4);
                    ctx.fillStyle = pal.tunicDk;
                    ctx.fillRect(x + 7.5 * p, y + 7 * p + by, p, p * 4);
                }
                ctx.fillStyle = pal.belt;
                ctx.fillRect(x + 3 * p, y + 10 * p + by, p * 10, p);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + (2 + armSwing / p) * p, y + 8 * p + by, p * 2, p * 3);
                ctx.fillRect(x + (12 - armSwing / p) * p, y + 8 * p + by, p * 2, p * 3);
                ctx.fillStyle = pal.pants;
                ctx.fillRect(x + 4 * p, y + 11 * p, p * 3, p * 2);
                ctx.fillRect(x + 9 * p, y + 11 * p, p * 3, p * 2);
                ctx.fillStyle = pal.boots;
                ctx.fillRect(x + 4 * p, y + 13 * p + legL, p * 3, p * 3);
                ctx.fillRect(x + 9 * p, y + 13 * p + legR, p * 3, p * 3);
                break;
            case 'left':
                ctx.fillStyle = pal.hair;
                ctx.fillRect(x + 3 * p, y + by, p * 8, p * 4);
                ctx.fillStyle = pal.hairHL;
                ctx.fillRect(x + 4 * p, y + p + by, p * 3, p);
                ctx.fillStyle = pal.hair;
                ctx.fillRect(x + 3 * p, y + 3 * p + by, p * 3, p * 3);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + 5 * p, y + 3 * p + by, p * 6, p * 4);
                ctx.fillStyle = pal.skinSh;
                ctx.fillRect(x + 5 * p, y + 6 * p + by, p * 6, p);
                ctx.fillStyle = pal.eye;
                ctx.fillRect(x + 5 * p, y + 4 * p + by, p * 2, p * 2);
                ctx.fillStyle = '#fff';
                ctx.fillRect(x + 5 * p, y + 4 * p + by, p, p);
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(x + 4 * p, y + 7 * p + by, p * 8, p * 4);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(x + 5 * p, y + 7 * p + by, p * 2, p * 3);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(x + 10 * p, y + 7 * p + by, p * 2, p * 4);
                ctx.fillStyle = pal.belt;
                ctx.fillRect(x + 4 * p, y + 10 * p + by, p * 8, p);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + (3 + armSwing / p) * p, y + 8 * p + by, p * 2, p * 3);
                ctx.fillStyle = pal.pants;
                ctx.fillRect(x + 5 * p, y + 11 * p, p * 6, p * 2);
                ctx.fillStyle = pal.pantsDk;
                ctx.fillRect(x + 5 * p, y + 11 * p, p * 2, p * 2);
                ctx.fillStyle = pal.boots;
                ctx.fillRect(x + 5 * p, y + 13 * p + legL, p * 3, p * 3);
                ctx.fillRect(x + 8 * p, y + 13 * p + legR, p * 3, p * 3);
                break;
            case 'right':
                ctx.fillStyle = pal.hair;
                ctx.fillRect(x + 5 * p, y + by, p * 8, p * 4);
                ctx.fillStyle = pal.hairHL;
                ctx.fillRect(x + 9 * p, y + p + by, p * 3, p);
                ctx.fillStyle = pal.hair;
                ctx.fillRect(x + 10 * p, y + 3 * p + by, p * 3, p * 3);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + 5 * p, y + 3 * p + by, p * 6, p * 4);
                ctx.fillStyle = pal.skinSh;
                ctx.fillRect(x + 5 * p, y + 6 * p + by, p * 6, p);
                ctx.fillStyle = pal.eye;
                ctx.fillRect(x + 9 * p, y + 4 * p + by, p * 2, p * 2);
                ctx.fillStyle = '#fff';
                ctx.fillRect(x + 10 * p, y + 4 * p + by, p, p);
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(x + 4 * p, y + 7 * p + by, p * 8, p * 4);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(x + 9 * p, y + 7 * p + by, p * 2, p * 3);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(x + 4 * p, y + 7 * p + by, p * 2, p * 4);
                ctx.fillStyle = pal.belt;
                ctx.fillRect(x + 4 * p, y + 10 * p + by, p * 8, p);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + (11 - armSwing / p) * p, y + 8 * p + by, p * 2, p * 3);
                ctx.fillStyle = pal.pants;
                ctx.fillRect(x + 5 * p, y + 11 * p, p * 6, p * 2);
                ctx.fillStyle = pal.pantsDk;
                ctx.fillRect(x + 9 * p, y + 11 * p, p * 2, p * 2);
                ctx.fillStyle = pal.boots;
                ctx.fillRect(x + 4 * p, y + 13 * p + legL, p * 3, p * 3);
                ctx.fillRect(x + 7 * p, y + 13 * p + legR, p * 3, p * 3);
                break;
        }
    }

    function getNPCPal(color, spriteId) {
        const c = color || '#44aa44';
        const h = hexToHSL(c);
        return {
            hair: hslHex((h.h + 30) % 360, Math.min(h.s, 40), 30),
            hairHL: hslHex((h.h + 30) % 360, Math.min(h.s, 40), 45),
            skin: '#f0c888', skinSh: '#d0a868', eye: '#203060',
            tunic: c, tunicHL: shade(c, 25), tunicDk: shade(c, -30),
            belt: '#a08030', beltBk: '#806020',
            pants: shade(c, -40), pantsDk: shade(c, -55),
            boots: '#504030', bootsHL: '#685040',
            cape: shade(c, -15), capeDk: shade(c, -35),
            outline: '#181020'
        };
    }

    function hexToHSL(hex) {
        let r = parseInt(hex.slice(1,3),16)/255, g = parseInt(hex.slice(3,5),16)/255, b = parseInt(hex.slice(5,7),16)/255;
        let mx = Math.max(r,g,b), mn = Math.min(r,g,b), h = 0, s = 0, l = (mx+mn)/2;
        if (mx !== mn) {
            let d = mx - mn;
            s = l > 0.5 ? d / (2-mx-mn) : d / (mx+mn);
            switch(mx) { case r: h=((g-b)/d+(g<b?6:0))*60; break; case g: h=((b-r)/d+2)*60; break; case b: h=((r-g)/d+4)*60; break; }
        }
        return { h: Math.round(h), s: Math.round(s*100), l: Math.round(l*100) };
    }

    function hslHex(h, s, l) {
        s/=100; l/=100;
        const k=n=>(n+h/30)%12, a=s*Math.min(l,1-l), f=n=>l-a*Math.max(-1,Math.min(k(n)-3,9-k(n),1));
        const th=n=>Math.round(n*255).toString(16).padStart(2,'0');
        return '#'+th(f(0))+th(f(8))+th(f(4));
    }

    function shade(c, pct) {
        const n = parseInt(c.replace('#',''),16), a = Math.round(2.55*pct);
        const R=Math.max(0,Math.min(255,(n>>16)+a)), G=Math.max(0,Math.min(255,((n>>8)&0xFF)+a)), B=Math.max(0,Math.min(255,(n&0xFF)+a));
        return '#'+(0x1000000+R*0x10000+G*0x100+B).toString(16).slice(1);
    }

    function renderHUD() {
        const h = 44;
        const grd = ctx.createLinearGradient(0, 0, 0, h);
        grd.addColorStop(0, '#101080');
        grd.addColorStop(0.5, '#080848');
        grd.addColorStop(1, '#040430');
        ctx.fillStyle = grd;
        ctx.fillRect(0, 0, canvas.width, h);
        ctx.fillStyle = '#b0b0d0';
        ctx.fillRect(0, h - 2, canvas.width, 2);
        ctx.fillStyle = '#484888';
        ctx.fillRect(0, h - 3, canvas.width, 1);
        ctx.fillStyle = '#e8e8f8';
        ctx.fillRect(0, 0, canvas.width, 1);

        ctx.font = 'bold 12px "Press Start 2P", monospace';
        ctx.textBaseline = 'middle';
        ctx.shadowColor = '#000030';
        ctx.shadowOffsetX = 1;
        ctx.shadowOffsetY = 1;

        let xp = 12;
        const ym = h / 2;

        if (hudData.capital !== undefined) {
            ctx.fillStyle = C.hg;
            ctx.fillText('G', xp, ym);
            ctx.fillStyle = '#fff';
            ctx.font = '11px "Press Start 2P", monospace';
            ctx.fillText(Number(hudData.capital).toLocaleString(), xp + 16, ym);
            xp += 110;
        }
        ctx.font = 'bold 10px "Press Start 2P", monospace';
        if (hudData.morale !== undefined) {
            ctx.fillStyle = C.hgr;
            ctx.fillText('MOR', xp, ym - 6);
            drawBar(xp + 38, ym - 12, 55, 9, hudData.morale / 100, C.hgr, '#104010');
            xp += 100;
        }
        if (hudData.brand !== undefined) {
            ctx.fillStyle = C.hr;
            ctx.fillText('BRD', xp, ym - 6);
            drawBar(xp + 38, ym - 12, 55, 9, hudData.brand / 100, C.hr, '#401010');
            xp += 100;
        }
        if (hudData.energy !== undefined) {
            ctx.fillStyle = '#f0a030';
            ctx.fillText('EN', xp, ym + 8);
            drawBar(xp + 28, ym + 2, 55, 9, hudData.energy / 100, '#f0a030', '#402810');
            xp += 90;
        }
        if (hudData.quarter !== undefined) {
            ctx.fillStyle = C.hbl;
            ctx.font = 'bold 10px "Press Start 2P", monospace';
            ctx.fillText('Q' + hudData.quarter, xp, ym);
        }
        if (currentMap && currentMap.name) {
            ctx.fillStyle = '#d0d0e0';
            ctx.font = '10px "Press Start 2P", monospace';
            ctx.textAlign = 'right';
            ctx.fillText(currentMap.name, canvas.width - 12, ym);
            ctx.textAlign = 'left';
        }
        ctx.shadowColor = 'transparent'; ctx.shadowOffsetX = 0; ctx.shadowOffsetY = 0;
    }

    function drawBar(x, y, w, h, pct, fc, bg) {
        pct = Math.max(0, Math.min(1, pct));
        ctx.fillStyle = bg; ctx.fillRect(x, y, w, h);
        ctx.fillStyle = fc; ctx.fillRect(x, y, Math.round(w * pct), h);
        ctx.fillStyle = 'rgba(255,255,255,0.25)';
        ctx.fillRect(x, y, Math.round(w * pct), Math.floor(h / 2));
        ctx.strokeStyle = '#c0c0e0'; ctx.lineWidth = 1; ctx.strokeRect(x, y, w, h);
    }

    function renderDialogue() {
        if (!currentDialogue) return;
        const m = 16, dh = 120;
        const dx = m, dy = canvas.height - dh - m, dw = canvas.width - m * 2;
        drawFFBox(dx, dy, dw, dh);
        if (currentDialogue.speaker) {
            const nw = Math.max(100, currentDialogue.speaker.length * 10 + 24);
            drawFFBox(dx + 8, dy - 22, nw, 24);
            ctx.fillStyle = C.ng;
            ctx.font = 'bold 11px "Press Start 2P", monospace';
            ctx.shadowColor = '#000030'; ctx.shadowOffsetX = 1; ctx.shadowOffsetY = 1;
            ctx.fillText(currentDialogue.speaker, dx + 18, dy - 7);
            ctx.shadowColor = 'transparent'; ctx.shadowOffsetX = 0; ctx.shadowOffsetY = 0;
        }
        ctx.fillStyle = C.dt;
        ctx.font = '11px "Press Start 2P", monospace';
        ctx.shadowColor = '#000030'; ctx.shadowOffsetX = 1; ctx.shadowOffsetY = 1;
        wrapText(ctx, currentDialogue.text.substring(0, dialogueCharIndex), dx + 20, dy + 26, dw - 40, 20);
        ctx.shadowColor = 'transparent'; ctx.shadowOffsetX = 0; ctx.shadowOffsetY = 0;
        if (currentDialogue.complete) {
            const blink = Math.sin(gt / 300) > 0;
            if (blink) {
                ctx.fillStyle = C.dt;
                ctx.beginPath();
                ctx.moveTo(dx + dw - 28, dy + dh - 22);
                ctx.lineTo(dx + dw - 18, dy + dh - 22);
                ctx.lineTo(dx + dw - 23, dy + dh - 14);
                ctx.closePath();
                ctx.fill();
            }
        }
    }

    function renderChoiceBox() {
        const bw = 180, bh = 24 + choiceOptions.length * 28;
        const bx = canvas.width - bw - 24, by = canvas.height - 120 - 24 - bh;
        drawFFBox(bx, by, bw, bh);
        ctx.font = '11px "Press Start 2P", monospace';
        ctx.shadowColor = '#000030'; ctx.shadowOffsetX = 1; ctx.shadowOffsetY = 1;
        choiceOptions.forEach((opt, i) => {
            const oy = by + 16 + i * 28;
            if (i === choiceIndex) {
                ctx.fillStyle = C.cc;
                const cb = Math.sin(gt / 200) * 2;
                ctx.beginPath();
                ctx.moveTo(bx + 14 + cb, oy - 4);
                ctx.lineTo(bx + 22 + cb, oy + 2);
                ctx.lineTo(bx + 14 + cb, oy + 8);
                ctx.closePath();
                ctx.fill();
            }
            ctx.fillStyle = i === choiceIndex ? '#fff' : '#a0a0c0';
            ctx.fillText(opt, bx + 30, oy + 4);
        });
        ctx.shadowColor = 'transparent'; ctx.shadowOffsetX = 0; ctx.shadowOffsetY = 0;
    }

    function drawFFBox(x, y, w, h) {
        const grd = ctx.createLinearGradient(x, y, x, y + h);
        grd.addColorStop(0, '#181888');
        grd.addColorStop(0.3, '#101060');
        grd.addColorStop(1, '#080840');
        ctx.fillStyle = grd;
        ctx.fillRect(x + 2, y + 2, w - 4, h - 4);
        ctx.strokeStyle = C.db1;
        ctx.lineWidth = 2;
        ctx.strokeRect(x + 1, y + 1, w - 2, h - 2);
        ctx.strokeStyle = C.db2;
        ctx.lineWidth = 1;
        ctx.strokeRect(x + 4, y + 4, w - 8, h - 8);
        ctx.fillStyle = C.db1;
        ctx.fillRect(x, y, 2, 2);
        ctx.fillRect(x + w - 2, y, 2, 2);
        ctx.fillRect(x, y + h - 2, 2, 2);
        ctx.fillRect(x + w - 2, y + h - 2, 2, 2);
    }

    function renderFlash() {
        if (!screenFlash) return;
        ctx.fillStyle = screenFlash.color;
        ctx.globalAlpha = screenFlash.timer / screenFlash.maxTimer;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.globalAlpha = 1;
    }

    function wrapText(ctx, text, x, y, maxW, lh) {
        const words = text.split(' ');
        let line = '', ty = y;
        for (let i = 0; i < words.length; i++) {
            const test = line + words[i] + ' ';
            if (ctx.measureText(test).width > maxW && i > 0) {
                ctx.fillText(line.trim(), x, ty);
                line = words[i] + ' ';
                ty += lh;
            } else line = test;
        }
        ctx.fillText(line.trim(), x, ty);
    }

    function updateHUD(data) { hudData = { ...hudData, ...data }; }
    function setPlayerPosition(tx, ty) {
        if (player) { player.tileX = tx; player.tileY = ty; player.px = tx * TS; player.py = ty * TS; }
    }
    function isDialogueActive() { return dialogueActive; }

    let overlayActive = false;
    function setOverlayActive(v) { overlayActive = v; }
    function isOverlayActive() { return overlayActive; }

    return { init, loadMap, start, stop, updateHUD, setPlayerPosition, showDialogue, showChoice, isDialogueActive, isOverlayActive, setOverlayActive, PAL: C, SCALED_TILE: TS };
})();
