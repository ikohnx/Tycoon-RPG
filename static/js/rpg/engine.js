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
        g1: '#2a9e3a', g2: '#1e8830', g3: '#3cb858', g4: '#50c868', gd: '#1a7028', gdd: '#105818', gb: '#5a4830',
        p1: '#c8a870', p2: '#b89860', p3: '#a88850', p4: '#d8b880', pe: '#8a7040', pm: '#6e5838',
        w1: '#1848a8', w2: '#2058c0', w3: '#103888', w4: '#2868d0', wf: '#90c0f0', ws: '#4070c0', wd: '#0c2870', wsp: '#c8e0ff',
        bk1: '#788098', bk2: '#687088', bk3: '#8890a8', bk4: '#9098b0', bkl: '#505868', bkd: '#404850', bkh: '#a0a8b8',
        rf1: '#c84838', rf2: '#d85848', rf3: '#b83828', rf4: '#e86858', rfl: '#882018', rfh: '#f08878', rfs: '#981818',
        dr1: '#704828', dr2: '#886038', dr3: '#5a3818', drk: '#e8c840', drf: '#604020', drh: '#a87848',
        wn1: '#4898d0', wn2: '#68b8f0', wn3: '#3880b8', wnf: '#484858', wns: '#a8d8ff', wnc: '#c06048',
        wd1: '#886038', wd2: '#a07848', wd3: '#685028', wd4: '#b89058', wdg: '#504018', wdk: '#4a3820',
        st1: '#708088', st2: '#8898a0', st3: '#586870', st4: '#98a8b0', stm: '#485058',
        tr1: '#187828', tr2: '#28a040', tr3: '#0e5818', tr4: '#38b858', trh: '#48c868', trs: '#084010', tk1: '#5a3818', tk2: '#704828', tk3: '#483010',
        fr: '#e83848', fy: '#f0d020', fp: '#c040e8', fw: '#f0e8f0', fo: '#f09030', fb: '#4080f0',
        sg1: '#a87840', sg2: '#c89050', sg3: '#e0a860', sgp: '#5a3818', sgd: '#483010',
        pt1: '#4820a0', pt2: '#6830d0', pt3: '#9050f0', pt4: '#b878ff', ptg: '#d0a0ff',
        hg1: '#186828', hg2: '#208838', hg3: '#28a048', hg4: '#10501a', hgs: '#0c4014',
        ch1: '#d09830', ch2: '#a87828', ch3: '#886018', chl: '#f0d860', chm: '#706020', chb: '#584810',
        dbg1: '#000848', dbg2: '#101070',
        db1: '#e8e8f0', db2: '#8888c0', db3: '#484888',
        dt: '#ffffff', ds: '#000030',
        hbg: '#000840', hb: '#b0b0d0', hg: '#e8c020', hgr: '#40d840', hr: '#e84040', hbl: '#50a0f0',
        ng: '#f0d850',
        cbg: '#101060', cbo: '#c0c0e0', cc: '#e8e8f0',
        sh: 'rgba(0,0,0,0.3)',
        lp: '#f0d040', lpg: '#fff8d0', lpo: '#e8a020', lpw: '#ffe8a0',
        mk: '#cc3030', mkd: '#a82020', mkc: '#e8e0c0',
        bn: '#886038', bns: '#704828',
        wl: '#788090',
        sa1: '#e0c070', sa2: '#d0b060', sa3: '#c8a050', sa4: '#e8d088', sap: '#907050',
        fp1: '#606878', fp2: '#505860', fp3: '#404850', fph: '#d04010', fpf: '#f08030', fpb: '#f0c040',
        bk5: '#303840'
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
        const drawSh = (x, y, size) => {
            const cx = x + TS * 0.5;
            const cy = y + TS * 0.94;
            const rx = TS * (size || 0.3);
            const ry = TS * 0.07;
            ctx.fillStyle = 'rgba(0,0,0,0.22)';
            ctx.beginPath();
            ctx.ellipse(cx, cy, rx + SCALE, ry + SCALE * 0.5, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = 'rgba(0,0,0,0.35)';
            ctx.beginPath();
            ctx.ellipse(cx, cy, rx * 0.7, ry * 0.7, 0, 0, Math.PI * 2);
            ctx.fill();
        };
        npcs.forEach(n => drawSh(n.px, n.py, 0.28));
        if (player) drawSh(player.px, player.py, 0.3);
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
        const p = SCALE;
        const bob = Math.sin(gt / 350) * 2 * p;
        const pulse = 0.85 + Math.sin(gt / 250) * 0.15;
        const ix = x + TS / 2;
        const iy = y - 6 * p + bob;
        ctx.fillStyle = '#000820';
        ctx.globalAlpha = 0.5;
        ctx.beginPath();
        ctx.ellipse(ix, iy - 2*p, 5*p*pulse, 4*p*pulse, 0, 0, Math.PI*2);
        ctx.fill();
        ctx.globalAlpha = 1;
        ctx.fillStyle = '#f8e838';
        ctx.beginPath();
        ctx.ellipse(ix, iy - 2*p, 4*p*pulse, 3*p*pulse, 0, 0, Math.PI*2);
        ctx.fill();
        ctx.fillStyle = '#ffffa0';
        ctx.beginPath();
        ctx.ellipse(ix, iy - 2.5*p, 2*p*pulse, 1.5*p*pulse, 0, 0, Math.PI*2);
        ctx.fill();
        ctx.fillStyle = '#e0a000';
        ctx.font = `bold ${Math.round(10*p/3)}px monospace`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('!', ix + p*0.3, iy - 2*p);
        ctx.fillStyle = '#fff';
        ctx.fillText('!', ix, iy - 2.3*p);
        ctx.textAlign = 'left';
        ctx.textBaseline = 'alphabetic';
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
                ctx.fillStyle = C.gd;
                for (let i = 0; i < 8; i++) {
                    const gx = ((sd * 7 + i * 31) % 14) * p;
                    const gy = ((sd * 11 + i * 23) % 14) * p;
                    ctx.fillRect(x + gx, y + gy, p, p);
                }
                ctx.fillStyle = C.g3;
                for (let i = 0; i < 10; i++) {
                    const gx = ((sd * 3 + i * 17) % 14) * p;
                    const gy = ((sd * 13 + i * 29) % 13) * p;
                    ctx.fillRect(x + gx, y + gy, p, p * 2);
                    if (i < 5) { ctx.fillRect(x + gx - p, y + gy + p, p, p); }
                }
                ctx.fillStyle = C.g4;
                for (let i = 0; i < 4; i++) {
                    const gx = ((sd * 5 + i * 41) % 13) * p;
                    const gy = ((sd * 9 + i * 37) % 12) * p;
                    ctx.fillRect(x + gx, y + gy, p, p * 3);
                    ctx.fillRect(x + gx + p, y + gy + p, p, p);
                }
                if ((sd & 7) < 3) {
                    ctx.fillStyle = C.gb;
                    const dx = ((sd * 11) % 10) * p;
                    const dy = ((sd * 7) % 10) * p;
                    ctx.fillRect(x + dx, y + dy, p * 3, p * 2);
                    ctx.fillRect(x + dx + p, y + dy + p * 2, p * 2, p);
                }
                ctx.fillStyle = C.gdd;
                for (let i = 0; i < 3; i++) {
                    ctx.fillRect(x + ((sd * 3 + i * 47) % 13) * p, y + ((sd * 5 + i * 53) % 13) * p, p, p);
                }
                if ((sd & 15) === 0) {
                    ctx.fillStyle = C.g4;
                    const cx = ((sd * 9) % 11) * p;
                    const cy = ((sd * 13) % 11) * p;
                    ctx.fillRect(x + cx + p, y + cy, p, p);
                    ctx.fillRect(x + cx, y + cy + p, p * 3, p);
                    ctx.fillRect(x + cx + p, y + cy + p * 2, p, p);
                }
                break;
            }

            case 2: {
                ctx.fillStyle = C.pm;
                ctx.fillRect(x, y, s, s);
                const stoneW = [5, 3, 4, 6, 3, 5, 4, 3];
                for (let br = 0; br < 4; br++) {
                    let cx = (br % 2) * 3;
                    const by = br * 4 * p;
                    let si = (sd + br * 3) & 7;
                    while (cx < 16) {
                        const sw = stoneW[si % stoneW.length];
                        const cw = Math.min(sw, 16 - cx);
                        const shade = ((si + br) & 3);
                        ctx.fillStyle = shade === 0 ? C.p1 : shade === 1 ? C.p2 : shade === 2 ? C.p4 : C.p3;
                        ctx.fillRect(x + cx * p, y + by, cw * p, 3 * p);
                        ctx.fillStyle = C.pe;
                        ctx.fillRect(x + cx * p, y + by + 3 * p, cw * p, p);
                        ctx.fillRect(x + (cx + cw - 1) * p, y + by, p, 3 * p);
                        if (shade === 0) {
                            ctx.fillStyle = 'rgba(255,255,255,0.1)';
                            ctx.fillRect(x + cx * p, y + by, cw * p, p);
                        }
                        if (shade === 3) {
                            ctx.fillStyle = 'rgba(0,0,0,0.08)';
                            ctx.fillRect(x + (cx + 1) * p, y + by + p, (cw - 2) * p, p);
                        }
                        cx += cw;
                        si++;
                    }
                }
                if ((sd & 7) < 2) {
                    ctx.fillStyle = 'rgba(0,0,0,0.06)';
                    ctx.fillRect(x + ((sd * 3) % 10) * p, y + ((sd * 7) % 10) * p, p * 3, p * 2);
                }
                break;
            }

            case 3: {
                const wt = t / 600;
                ctx.fillStyle = C.w3;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.w1;
                ctx.fillRect(x, y + 2 * p, s, s - 4 * p);
                ctx.fillStyle = C.wd;
                ctx.fillRect(x, y + 12 * p, s, 4 * p);
                for (let i = 0; i < 5; i++) {
                    const wx = (Math.sin(wt + i * 1.3 + col * 0.8) * 3 + 6) * p;
                    const wy = (i * 3 + 1) * p;
                    ctx.fillStyle = C.w2;
                    ctx.fillRect(x + wx, y + wy, p * 5, p);
                    ctx.fillStyle = C.w4;
                    ctx.fillRect(x + wx + p, y + wy - p, p * 3, p);
                    ctx.fillStyle = C.ws;
                    ctx.fillRect(x + wx + p * 2, y + wy + p, p * 2, p);
                }
                ctx.fillStyle = C.wf;
                ctx.globalAlpha = 0.3 + Math.sin(wt * 1.5 + col + row) * 0.15;
                ctx.fillRect(x + ((sd * 3) % 8) * p, y + ((sd * 7) % 8) * p, p * 2, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wsp;
                ctx.globalAlpha = 0.5 + Math.sin(wt * 3 + sd) * 0.4;
                ctx.fillRect(x + ((sd * 11) % 12) * p, y + ((sd * 5) % 12) * p, p, p);
                ctx.globalAlpha = 0.3 + Math.sin(wt * 2.5 + sd * 2) * 0.3;
                ctx.fillRect(x + ((sd * 7 + 5) % 12) * p, y + ((sd * 3 + 7) % 12) * p, p, p);
                ctx.globalAlpha = 1;
                break;
            }

            case 4: {
                ctx.fillStyle = C.bkd;
                ctx.fillRect(x, y, s, s);
                const brickW = [7, 5, 6, 8, 5, 7];
                for (let br = 0; br < 4; br++) {
                    let cx = (br % 2) * 4;
                    const by = br * 4 * p;
                    let si = (sd + br * 2) & 5;
                    while (cx < 16) {
                        const bw = Math.min(brickW[si % brickW.length], 16 - cx);
                        const shade = ((si + br + sd) & 3);
                        ctx.fillStyle = shade === 0 ? C.bk1 : shade === 1 ? C.bk2 : shade === 2 ? C.bk3 : C.bk4;
                        ctx.fillRect(x + cx * p, y + by, bw * p, 3 * p);
                        ctx.fillStyle = C.bkl;
                        ctx.fillRect(x + cx * p, y + by + 3 * p, bw * p, p);
                        ctx.fillRect(x + (cx + bw) * p, y + by, p, 3 * p);
                        ctx.fillStyle = C.bkh;
                        ctx.globalAlpha = 0.15;
                        ctx.fillRect(x + cx * p, y + by, bw * p, p);
                        ctx.globalAlpha = 1;
                        if ((si & 3) === 0 && bw > 2) {
                            ctx.fillStyle = 'rgba(0,0,0,0.1)';
                            ctx.fillRect(x + (cx + 1) * p, y + by + p, p * 2, p);
                        }
                        cx += bw;
                        si++;
                    }
                }
                ctx.fillStyle = 'rgba(0,0,0,0.12)';
                ctx.fillRect(x, y + s - 3 * p, s, 3 * p);
                ctx.fillStyle = 'rgba(255,255,255,0.06)';
                ctx.fillRect(x, y, s, 2 * p);
                break;
            }

            case 5: {
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x, y, s, s);
                for (let i = 0; i < 4; i++) {
                    const bx = i * 4 * p;
                    ctx.fillStyle = C.bk4;
                    ctx.fillRect(x + bx, y, p * 3, 5 * p);
                    ctx.fillStyle = C.bkh;
                    ctx.globalAlpha = 0.2;
                    ctx.fillRect(x + bx, y, p * 3, p);
                    ctx.globalAlpha = 1;
                    ctx.fillStyle = C.bkl;
                    ctx.fillRect(x + bx + 3 * p, y, p, 5 * p);
                }
                ctx.fillStyle = C.bk1;
                ctx.fillRect(x, y + 5 * p, s, p);
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y + 6 * p, s, 10 * p);
                for (let br = 0; br < 2; br++) {
                    let cx = (br % 2) * 4;
                    while (cx < 16) {
                        const bw = Math.min(6, 16 - cx);
                        ctx.fillStyle = ((cx + br) & 1) ? C.bk3 : C.bk1;
                        ctx.fillRect(x + cx * p, y + (7 + br * 4) * p, bw * p, 3 * p);
                        ctx.fillStyle = C.bkl;
                        ctx.fillRect(x + cx * p, y + (10 + br * 4) * p, bw * p, p);
                        ctx.fillRect(x + (cx + bw) * p, y + (7 + br * 4) * p, p, 3 * p);
                        cx += bw + 1;
                    }
                }
                ctx.fillStyle = 'rgba(255,255,255,0.08)';
                ctx.fillRect(x, y, s, 2 * p);
                ctx.fillStyle = 'rgba(0,0,0,0.1)';
                ctx.fillRect(x, y + 5 * p, s, p);
                break;
            }

            case 6: {
                ctx.fillStyle = C.rf3;
                ctx.fillRect(x, y, s, s);
                for (let r = 0; r < 4; r++) {
                    const rowOff = (r % 2) * 3;
                    for (let c = -1; c < 5; c++) {
                        const tx = (c * 4 + rowOff) * p;
                        const ty = r * 4 * p;
                        if (tx < 0 || tx >= s) continue;
                        const shade = ((r + c + sd) & 3);
                        ctx.fillStyle = shade === 0 ? C.rf1 : shade === 1 ? C.rf2 : shade === 2 ? C.rf4 : C.rf1;
                        ctx.fillRect(x + tx, y + ty, p * 3, p * 3);
                        ctx.fillStyle = C.rfh;
                        ctx.globalAlpha = 0.2;
                        ctx.fillRect(x + tx, y + ty, p * 3, p);
                        ctx.globalAlpha = 1;
                        ctx.fillStyle = C.rfs;
                        ctx.fillRect(x + tx, y + ty + 3 * p, p * 3, p);
                    }
                }
                ctx.fillStyle = C.rfl;
                ctx.fillRect(x, y + s - p, s, p);
                ctx.fillStyle = 'rgba(255,200,150,0.1)';
                ctx.fillRect(x, y, s, 2 * p);
                break;
            }

            case 7: {
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.bkl;
                ctx.fillRect(x + 2 * p, y + p, p * 12, p);
                ctx.fillRect(x + 2 * p, y + p, p, p * 15);
                ctx.fillRect(x + 13 * p, y + p, p, p * 15);
                ctx.fillStyle = C.bk4;
                ctx.fillRect(x + 2 * p, y + p, p * 12, p);
                ctx.fillStyle = C.dr3;
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 10, p * 14);
                ctx.fillStyle = C.dr1;
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 3, p * 12);
                ctx.fillRect(x + 9 * p, y + 3 * p, p * 3, p * 12);
                ctx.fillStyle = C.dr2;
                ctx.fillRect(x + 5 * p, y + 4 * p, p, p * 10);
                ctx.fillRect(x + 10 * p, y + 4 * p, p, p * 10);
                ctx.fillStyle = C.drh;
                ctx.globalAlpha = 0.3;
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 8, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.drf;
                ctx.fillRect(x + 7.5 * p, y + 3 * p, p, p * 12);
                ctx.fillRect(x + 4 * p, y + 8 * p, p * 8, p);
                ctx.fillStyle = C.bkl;
                ctx.fillRect(x + 3 * p, y + 4 * p, p, p * 2);
                ctx.fillRect(x + 3 * p, y + 10 * p, p, p * 2);
                ctx.fillRect(x + 12 * p, y + 4 * p, p, p * 2);
                ctx.fillRect(x + 12 * p, y + 10 * p, p, p * 2);
                ctx.fillStyle = C.drk;
                ctx.fillRect(x + 10 * p, y + 9 * p, p * 2, p * 2);
                ctx.fillStyle = '#d4b030';
                ctx.fillRect(x + 10 * p, y + 9 * p, p, p);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.3;
                ctx.fillRect(x + 10 * p, y + 9 * p, p, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.bk4;
                ctx.fillRect(x + 3 * p, y + 15 * p, p * 10, p);
                break;
            }

            case 8: {
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.wnf;
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 10, p * 10);
                ctx.fillStyle = C.wn3;
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 3, p * 3);
                ctx.fillRect(x + 9 * p, y + 3 * p, p * 3, p * 3);
                ctx.fillRect(x + 4 * p, y + 8 * p, p * 3, p * 3);
                ctx.fillRect(x + 9 * p, y + 8 * p, p * 3, p * 3);
                ctx.fillStyle = C.wn1;
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 3, p * 3);
                ctx.fillRect(x + 9 * p, y + 3 * p, p * 3, p * 3);
                const sh = Math.sin(t / 800 + col) * 0.15 + 0.85;
                ctx.fillStyle = C.wn2;
                ctx.globalAlpha = sh;
                ctx.fillRect(x + 5 * p, y + 4 * p, p * 2, p);
                ctx.fillRect(x + 10 * p, y + 4 * p, p, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wns;
                ctx.globalAlpha = 0.3;
                ctx.fillRect(x + 4 * p, y + 3 * p, p, p);
                ctx.fillRect(x + 9 * p, y + 3 * p, p, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wnf;
                ctx.fillRect(x + 7.5 * p, y + 2 * p, p, p * 10);
                ctx.fillRect(x + 3 * p, y + 6.5 * p, p * 10, p);
                ctx.fillStyle = C.wnc;
                ctx.globalAlpha = 0.35;
                ctx.fillRect(x + 4 * p, y + 8 * p, p * 3, p * 3);
                ctx.fillRect(x + 9 * p, y + 8 * p, p * 3, p * 3);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x + 3 * p, y + 12 * p, p * 10, p * 2);
                ctx.fillStyle = C.bk4;
                ctx.fillRect(x + 3 * p, y + 12 * p, p * 10, p);
                ctx.fillStyle = 'rgba(0,0,0,0.15)';
                ctx.fillRect(x + 3 * p, y + 13 * p, p * 10, p);
                break;
            }

            case 9: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.g3;
                for (let i = 0; i < 4; i++) {
                    const gx = ((sd * 3 + i * 41) % 14) * p;
                    const gy = (12 + ((sd * 7 + i * 19) % 4)) * p;
                    ctx.fillRect(x + gx, y + gy, p, p * 2);
                }
                const sway = Math.sin(t / 2000 + sd * 0.5) * p * 0.5;
                ctx.fillStyle = C.tk3;
                ctx.fillRect(x + 7 * p, y + 11 * p, p * 2, p * 5);
                ctx.fillStyle = C.tk1;
                ctx.fillRect(x + 6 * p, y + 10 * p, p * 4, p * 6);
                ctx.fillStyle = C.tk2;
                ctx.fillRect(x + 7 * p, y + 10 * p, p * 2, p * 6);
                ctx.fillStyle = C.tk1;
                ctx.fillRect(x + 5 * p, y + 13 * p, p * 2, p * 2);
                ctx.fillRect(x + 9 * p, y + 12 * p, p * 2, p * 2);
                ctx.fillStyle = C.trs;
                ctx.fillRect(x + 3 * p + sway, y + 6 * p, p * 10, p * 6);
                ctx.fillRect(x + 4 * p + sway, y + 4 * p, p * 8, p * 2);
                ctx.fillRect(x + 5 * p + sway, y + 3 * p, p * 6, p);
                ctx.fillStyle = C.tr3;
                ctx.fillRect(x + 3 * p + sway, y + 5 * p, p * 10, p * 5);
                ctx.fillRect(x + 4 * p + sway, y + 3 * p, p * 8, p * 2);
                ctx.fillRect(x + 5 * p + sway, y + 2 * p, p * 6, p);
                ctx.fillStyle = C.tr1;
                ctx.fillRect(x + 4 * p + sway, y + 4 * p, p * 8, p * 4);
                ctx.fillRect(x + 5 * p + sway, y + 3 * p, p * 6, p);
                ctx.fillRect(x + 6 * p + sway, y + 2 * p, p * 4, p);
                ctx.fillStyle = C.tr2;
                ctx.fillRect(x + 5 * p + sway, y + 4 * p, p * 4, p * 3);
                ctx.fillRect(x + 6 * p + sway, y + 3 * p, p * 3, p);
                ctx.fillStyle = C.tr4;
                ctx.fillRect(x + 6 * p + sway, y + 4 * p, p * 2, p * 2);
                ctx.fillStyle = C.trh;
                ctx.globalAlpha = 0.4;
                ctx.fillRect(x + 6 * p + sway, y + 3 * p, p * 3, p);
                ctx.fillRect(x + 7 * p + sway, y + 2 * p, p * 2, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.trs;
                ctx.fillRect(x + 3 * p + sway, y + 10 * p, p * 3, p * 2);
                ctx.fillRect(x + 10 * p + sway, y + 9 * p, p * 3, p * 2);
                ctx.fillRect(x + 2 * p + sway, y + 8 * p, p * 2, p * 2);
                ctx.fillRect(x + 12 * p + sway, y + 7 * p, p * 2, p * 2);
                ctx.fillStyle = C.tr3;
                for (let i = 0; i < 5; i++) {
                    const lx = ((sd * 7 + i * 31) % 8 + 3) * p;
                    const ly = ((sd * 3 + i * 17) % 6 + 3) * p;
                    ctx.fillRect(x + lx + sway, y + ly, p, p);
                }
                break;
            }

            case 10: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.g3;
                for (let i = 0; i < 6; i++) {
                    const gx = ((sd * 3 + i * 31) % 14) * p;
                    const gy = ((sd * 11 + i * 23) % 14) * p;
                    ctx.fillRect(x + gx, y + gy, p, p * 2);
                }
                const fs = Math.sin(t / 700 + sd) * p * 0.5;
                const flowers = [
                    {cx:2,cy:4,c:C.fr,s:2},{cx:8,cy:3,c:C.fy,s:2},{cx:5,cy:9,c:C.fp,s:2},
                    {cx:11,cy:7,c:C.fw,s:2},{cx:7,cy:12,c:C.fo,s:2},{cx:13,cy:10,c:C.fb,s:1},
                    {cx:1,cy:11,c:C.fr,s:1},{cx:10,cy:1,c:C.fp,s:1}
                ];
                flowers.forEach((f, i) => {
                    const sw = (i % 2 ? fs : -fs) * 0.6;
                    ctx.fillStyle = C.gd;
                    ctx.fillRect(x + (f.cx + 0.5) * p, y + (f.cy + f.s) * p, p, p * 3);
                    if (f.s > 1) {
                        ctx.fillRect(x + (f.cx - 0.5) * p, y + (f.cy + f.s + 1) * p, p, p * 2);
                    }
                    ctx.fillStyle = f.c;
                    ctx.fillRect(x + f.cx * p + sw, y + f.cy * p, p * f.s, p * f.s);
                    if (f.s > 1) {
                        ctx.fillRect(x + (f.cx + 0.5) * p + sw, y + (f.cy - 0.5) * p, p, p);
                        ctx.fillRect(x + (f.cx - 0.5) * p + sw, y + (f.cy + 0.5) * p, p, p);
                        ctx.fillRect(x + (f.cx + f.s) * p + sw, y + (f.cy + 0.5) * p, p, p);
                    }
                    ctx.fillStyle = C.fy;
                    ctx.fillRect(x + (f.cx + 0.5) * p + sw, y + (f.cy + 0.5) * p, p, p);
                });
                break;
            }

            case 11: {
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x, y, s, s);
                const plankW = [4, 3, 5, 4];
                let px2 = 0;
                for (let i = 0; i < 4 && px2 < 16; i++) {
                    const pw = plankW[(i + (sd & 3)) % 4];
                    const cw = Math.min(pw, 16 - px2);
                    const shade = ((i + sd) & 1);
                    ctx.fillStyle = shade ? C.wd1 : C.wd2;
                    ctx.fillRect(x + px2 * p, y, cw * p, s);
                    ctx.fillStyle = C.wd4;
                    ctx.globalAlpha = 0.15;
                    for (let gy = 0; gy < 16; gy += 2) {
                        const goff = ((sd + i * 7 + gy * 3) % 3);
                        if (goff === 0) ctx.fillRect(x + (px2 + 1) * p, y + gy * p, (cw - 2) * p, p);
                    }
                    ctx.globalAlpha = 1;
                    ctx.fillStyle = C.wdk;
                    ctx.fillRect(x + (px2 + cw) * p - p, y, p, s);
                    if ((sd + i * 37) % 11 < 2 && cw > 2) {
                        ctx.fillStyle = C.wdg;
                        const ky = ((sd * 7 + i * 41) % 10 + 3) * p;
                        ctx.fillRect(x + (px2 + 1) * p, y + ky, p * 2, p * 2);
                        ctx.fillStyle = C.wd3;
                        ctx.fillRect(x + (px2 + 1) * p + p, y + ky + p, p, p);
                    }
                    px2 += cw;
                }
                ctx.fillStyle = C.wd3;
                for (let i = 0; i <= 4; i++) {
                    const ny = ((sd * 3 + i * 61) % 4) * 4;
                    ctx.fillRect(x, y + ny * p, s, p);
                }
                break;
            }

            case 12: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.g3;
                for (let i = 0; i < 3; i++) ctx.fillRect(x + ((sd * 5 + i * 31) % 14) * p, y + (12 + i) * p, p, p * 2);
                ctx.fillStyle = C.sgd;
                ctx.fillRect(x + 7 * p, y + 8 * p, p * 2, p * 8);
                ctx.fillStyle = C.sgp;
                ctx.fillRect(x + 7 * p, y + 9 * p, p * 2, p * 6);
                ctx.fillStyle = C.sgp;
                ctx.fillRect(x + 6 * p, y + 14 * p, p * 4, p * 2);
                ctx.fillStyle = C.sg1;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p * 7);
                ctx.fillStyle = C.sg2;
                ctx.fillRect(x + 3 * p, y + 3 * p, p * 10, p * 5);
                ctx.fillStyle = C.sg3;
                ctx.globalAlpha = 0.25;
                ctx.fillRect(x + 3 * p, y + 3 * p, p * 10, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.sgp;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p);
                ctx.fillRect(x + 2 * p, y + 8 * p, p * 12, p);
                ctx.fillRect(x + 2 * p, y + 2 * p, p, p * 7);
                ctx.fillRect(x + 13 * p, y + 2 * p, p, p * 7);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.15;
                ctx.fillRect(x + 4 * p, y + 4 * p, p * 8, p);
                ctx.fillRect(x + 4 * p, y + 6 * p, p * 6, p);
                ctx.globalAlpha = 1;
                break;
            }

            case 13: {
                ctx.fillStyle = C.sa2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.sa1;
                for (let i = 0; i < 8; i++) {
                    const sx2 = ((sd * 7 + i * 31) % 13) * p;
                    const sy2 = ((sd * 11 + i * 23) % 13) * p;
                    ctx.fillRect(x + sx2, y + sy2, p * 2, p);
                }
                ctx.fillStyle = C.sa4;
                ctx.globalAlpha = 0.3;
                for (let i = 0; i < 3; i++) {
                    const rx = ((sd * 3 + i * 47) % 10) * p;
                    ctx.fillRect(x + rx, y + (4 + i * 4) * p, p * 6, p);
                    ctx.fillRect(x + rx + p, y + (5 + i * 4) * p, p * 4, p);
                }
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.sa3;
                for (let i = 0; i < 5; i++) {
                    ctx.fillRect(x + ((sd * 5 + i * 37) % 13) * p, y + ((sd * 9 + i * 41) % 13) * p, p, p);
                }
                ctx.fillStyle = C.sap;
                for (let i = 0; i < 2; i++) {
                    ctx.fillRect(x + ((sd * 13 + i * 53) % 12) * p, y + ((sd * 3 + i * 47) % 12) * p, p, p);
                }
                break;
            }

            case 14: {
                ctx.fillStyle = C.stm;
                ctx.fillRect(x, y, s, s);
                for (let r = 0; r < 2; r++) {
                    for (let c = 0; c < 2; c++) {
                        const off = (r % 2) * 4;
                        const shade = ((r + c + sd) & 3);
                        ctx.fillStyle = shade === 0 ? C.st1 : shade === 1 ? C.st2 : shade === 2 ? C.st4 : C.st1;
                        ctx.fillRect(x + (c * 8 + off + 1) * p, y + (r * 8 + 1) * p, p * 6, p * 6);
                        ctx.fillStyle = 'rgba(255,255,255,0.1)';
                        ctx.fillRect(x + (c * 8 + off + 1) * p, y + (r * 8 + 1) * p, p * 6, p);
                        ctx.fillStyle = 'rgba(0,0,0,0.08)';
                        ctx.fillRect(x + (c * 8 + off + 1) * p, y + (r * 8 + 6) * p, p * 6, p);
                        if (shade === 2) {
                            ctx.fillStyle = 'rgba(255,255,255,0.05)';
                            ctx.fillRect(x + (c * 8 + off + 2) * p, y + (r * 8 + 2) * p, p * 3, p * 2);
                        }
                    }
                }
                ctx.fillStyle = C.st3;
                ctx.fillRect(x, y, s, p);
                ctx.fillRect(x, y + 8 * p, s, p);
                ctx.fillRect(x, y, p, s);
                ctx.fillRect(x + 8 * p, y, p, s);
                break;
            }

            case 15: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.g3;
                for (let i = 0; i < 3; i++) ctx.fillRect(x + ((sd * 7 + i * 31) % 14) * p, y + (13 + i) * p, p, p * 2);
                ctx.fillStyle = C.hgs;
                ctx.fillRect(x + p, y + 11 * p, p * 14, p * 5);
                ctx.fillRect(x + 2 * p, y + 10 * p, p * 12, p);
                ctx.fillStyle = C.hg4;
                ctx.fillRect(x + p, y + 4 * p, p * 14, p * 9);
                ctx.fillRect(x + 2 * p, y + 3 * p, p * 12, p);
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 10, p);
                ctx.fillRect(x + 4 * p, y + p, p * 8, p);
                ctx.fillStyle = C.hg1;
                ctx.fillRect(x + 2 * p, y + 4 * p, p * 12, p * 7);
                ctx.fillRect(x + 3 * p, y + 3 * p, p * 10, p);
                ctx.fillRect(x + 4 * p, y + 2 * p, p * 8, p);
                ctx.fillRect(x + 5 * p, y + p, p * 6, p);
                ctx.fillStyle = C.hg2;
                ctx.fillRect(x + 3 * p, y + 4 * p, p * 5, p * 4);
                ctx.fillRect(x + 9 * p, y + 5 * p, p * 4, p * 3);
                ctx.fillStyle = C.hg3;
                ctx.fillRect(x + 4 * p, y + 4 * p, p * 3, p * 2);
                ctx.fillRect(x + 10 * p, y + 5 * p, p * 2, p * 2);
                ctx.fillStyle = C.hg4;
                for (let i = 0; i < 6; i++) {
                    const lx = ((sd * 5 + i * 29) % 10 + 2) * p;
                    const ly = ((sd * 3 + i * 17) % 8 + 2) * p;
                    ctx.fillRect(x + lx, y + ly, p, p);
                }
                break;
            }

            case 16: {
                ctx.fillStyle = C.st2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.st3;
                for (let i = 0; i < 3; i++) ctx.fillRect(x + ((sd * 5 + i * 31) % 14) * p, y + ((sd * 7 + i * 23) % 14) * p, p, p);
                ctx.fillStyle = C.chb;
                ctx.fillRect(x + 3 * p, y + 5 * p, p * 10, p * 10);
                ctx.fillStyle = C.ch3;
                ctx.fillRect(x + 3 * p, y + 6 * p, p * 10, p * 8);
                ctx.fillStyle = C.ch2;
                ctx.fillRect(x + 4 * p, y + 7 * p, p * 8, p * 6);
                ctx.fillStyle = C.ch1;
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 8, p * 4);
                ctx.fillRect(x + 3 * p, y + 4 * p, p * 10, p * 2);
                ctx.fillStyle = C.chl;
                ctx.globalAlpha = 0.3;
                ctx.fillRect(x + 4 * p, y + 3 * p, p * 8, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.chm;
                ctx.fillRect(x + 3 * p, y + 7 * p, p * 10, p);
                ctx.fillRect(x + 3 * p, y + 12 * p, p * 10, p);
                ctx.fillStyle = '#e0c040';
                ctx.fillRect(x + 3 * p, y + 5 * p, p * 10, p);
                ctx.fillRect(x + 3 * p, y + 9 * p, p * 10, p);
                ctx.fillStyle = C.chl;
                ctx.fillRect(x + 7 * p, y + 5 * p, p * 2, p * 3);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.3;
                ctx.fillRect(x + 7 * p, y + 5 * p, p, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#402800';
                ctx.fillRect(x + 7.5 * p, y + 10 * p, p, p * 2);
                ctx.fillStyle = 'rgba(0,0,0,0.15)';
                ctx.fillRect(x + 4 * p, y + 13 * p, p * 8, p * 2);
                break;
            }

            case 17: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                const pt = t / 300;
                ctx.fillStyle = C.pt1;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p * 12);
                ctx.fillStyle = C.pt2;
                ctx.globalAlpha = 0.5 + Math.sin(pt) * 0.3;
                ctx.fillRect(x + 3 * p, y + 3 * p, p * 10, p * 10);
                ctx.globalAlpha = 1;
                for (let i = 0; i < 12; i++) {
                    const a = pt + i * Math.PI / 6;
                    const r1 = (3 + Math.sin(pt * 2 + i) * 1.5) * p;
                    ctx.fillStyle = i % 3 === 0 ? C.pt3 : i % 3 === 1 ? C.pt4 : C.ptg;
                    ctx.globalAlpha = 0.6 + Math.sin(pt + i * 0.8) * 0.3;
                    ctx.fillRect(x + 8 * p + Math.cos(a) * r1 - p * 0.5, y + 8 * p + Math.sin(a) * r1 - p * 0.5, p, p);
                }
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.pt4;
                ctx.globalAlpha = 0.4 + Math.sin(pt * 2.5) * 0.3;
                ctx.fillRect(x + 6 * p, y + 6 * p, p * 4, p * 4);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.ptg;
                ctx.globalAlpha = 0.6 + Math.sin(pt * 3) * 0.3;
                ctx.fillRect(x + 7 * p, y + 7 * p, p * 2, p * 2);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.3 + Math.sin(pt * 4) * 0.2;
                ctx.fillRect(x + 7.5 * p, y + 7.5 * p, p, p);
                ctx.globalAlpha = 1;
                break;
            }

            case 18: {
                ctx.fillStyle = C.st2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.st3;
                ctx.fillRect(x + 2 * p, y + 6 * p, p * 12, p * 10);
                ctx.fillStyle = C.st4;
                ctx.fillRect(x + 3 * p, y + 6 * p, p * 10, p);
                ctx.fillStyle = C.st1;
                ctx.fillRect(x + 3 * p, y + 7 * p, p * 10, p * 8);
                ctx.fillStyle = C.w1;
                ctx.fillRect(x + 4 * p, y + 8 * p, p * 8, p * 6);
                const ft = t / 400;
                ctx.fillStyle = C.w2;
                ctx.fillRect(x + 5 * p, y + (9 + Math.sin(ft) * 0.8) * p, p * 3, p);
                ctx.fillRect(x + 9 * p, y + (10 + Math.cos(ft) * 0.8) * p, p * 2, p);
                ctx.fillStyle = C.st3;
                ctx.fillRect(x + 7 * p, y + 6 * p, p * 2, p * 8);
                ctx.fillStyle = C.st4;
                ctx.fillRect(x + 7 * p, y + 3 * p, p * 2, p * 4);
                ctx.fillRect(x + 6 * p, y + 4 * p, p * 4, p);
                ctx.fillStyle = C.wf;
                const sprayH = 2 + Math.sin(ft * 1.5) * 1.5;
                ctx.globalAlpha = 0.5 + Math.sin(ft * 2) * 0.2;
                ctx.fillRect(x + 7 * p, y + (3 - sprayH * 0.5) * p, p * 2, sprayH * p);
                ctx.globalAlpha = 0.3;
                ctx.fillRect(x + 6 * p, y + (4 - sprayH * 0.3) * p, p, sprayH * 0.5 * p);
                ctx.fillRect(x + 9 * p, y + (4 - sprayH * 0.3) * p, p, sprayH * 0.5 * p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wsp;
                ctx.globalAlpha = 0.5 + Math.sin(ft * 3) * 0.3;
                ctx.fillRect(x + 7.5 * p, y + (2 - sprayH * 0.3) * p, p, p);
                ctx.globalAlpha = 1;
                break;
            }

            case 19: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#383838';
                ctx.fillRect(x + 7 * p, y + 4 * p, p * 2, p * 12);
                ctx.fillStyle = '#484848';
                ctx.fillRect(x + 7 * p, y + 5 * p, p, p * 10);
                ctx.fillStyle = '#383838';
                ctx.fillRect(x + 5 * p, y + 14 * p, p * 6, p * 2);
                ctx.fillRect(x + 6 * p, y + 13 * p, p * 4, p);
                ctx.fillStyle = '#505050';
                ctx.fillRect(x + 5 * p, y + 14 * p, p * 6, p);
                ctx.fillStyle = '#484848';
                ctx.fillRect(x + 6 * p, y + 3 * p, p * 4, p * 2);
                ctx.fillRect(x + 5 * p, y + 4 * p, p * 6, p);
                const lg = 0.5 + Math.sin(t / 1000 + sd) * 0.25;
                const lg2 = 0.5 + Math.sin(t / 700 + sd + 2) * 0.2;
                ctx.fillStyle = C.lpo;
                ctx.globalAlpha = lg;
                ctx.fillRect(x + 5 * p, y + p, p * 6, p * 3);
                ctx.fillStyle = C.lp;
                ctx.fillRect(x + 6 * p, y + p, p * 4, p * 2);
                ctx.fillStyle = C.lpg;
                ctx.globalAlpha = lg2;
                ctx.fillRect(x + 7 * p, y + p, p * 2, p);
                ctx.globalAlpha = lg * 0.12;
                ctx.fillStyle = C.lpw;
                ctx.beginPath();
                ctx.arc(x + 8 * p, y + 3 * p, 9 * p, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = lg * 0.06;
                ctx.beginPath();
                ctx.arc(x + 8 * p, y + 3 * p, 14 * p, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
                break;
            }

            case 20: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + p, y + 7 * p, p, p * 9);
                ctx.fillRect(x + 14 * p, y + 7 * p, p, p * 9);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + p, y + 7 * p, p * 14, p * 9);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 2 * p, y + 8 * p, p * 12, p * 7);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 2 * p, y + 11 * p, p * 12, p);
                ctx.fillStyle = C.mk;
                ctx.fillRect(x + p, y + p, p * 14, p * 6);
                ctx.fillStyle = C.mkd;
                ctx.fillRect(x + p, y + 5 * p, p * 14, p * 2);
                for (let i = 0; i < 7; i++) {
                    ctx.fillStyle = C.mkd;
                    ctx.fillRect(x + (1 + i * 2) * p, y + 6 * p, p * 2, p);
                }
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.1;
                ctx.fillRect(x + 2 * p, y + 2 * p, p * 12, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.fy;
                ctx.fillRect(x + 3 * p, y + 8 * p, p * 2, p * 2);
                ctx.fillRect(x + 3 * p, y + 12 * p, p * 3, p * 2);
                ctx.fillStyle = C.fr;
                ctx.fillRect(x + 7 * p, y + 8 * p, p * 2, p * 2);
                ctx.fillStyle = C.fo;
                ctx.fillRect(x + 10 * p, y + 9 * p, p * 2, p * 2);
                ctx.fillStyle = C.mkc;
                ctx.fillRect(x + 10 * p, y + 12 * p, p * 3, p * 2);
                break;
            }

            case 21: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.g3;
                for (let i = 0; i < 4; i++) ctx.fillRect(x + ((sd * 3 + i * 37) % 14) * p, y + ((sd * 7 + i * 41) % 5 + 11) * p, p, p * 2);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 3 * p, y + 10 * p, p * 2, p * 5);
                ctx.fillRect(x + 11 * p, y + 10 * p, p * 2, p * 5);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 2 * p, y + 7 * p, p * 12, p * 4);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 3 * p, y + 5 * p, p * 10, p * 2);
                ctx.fillRect(x + 3 * p, y + 9 * p, p * 10, p);
                ctx.fillStyle = C.wd4;
                ctx.globalAlpha = 0.2;
                ctx.fillRect(x + 3 * p, y + 5 * p, p * 10, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 2 * p, y + 10 * p, p * 12, p);
                ctx.fillRect(x + 5 * p, y + 7 * p, p, p * 3);
                ctx.fillRect(x + 8 * p, y + 7 * p, p, p * 3);
                ctx.fillRect(x + 11 * p, y + 7 * p, p, p * 3);
                ctx.fillStyle = C.bns;
                ctx.fillRect(x + 3 * p, y + 10 * p, p, p * 2);
                ctx.fillRect(x + 12 * p, y + 10 * p, p, p * 2);
                break;
            }

            case 22: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.g3;
                for (let i = 0; i < 3; i++) ctx.fillRect(x + ((sd * 5 + i * 31) % 14) * p, y + (13 + i) * p, p, p * 2);
                ctx.fillStyle = C.st3;
                ctx.fillRect(x + 3 * p, y + 7 * p, p * 10, p * 9);
                ctx.fillStyle = C.st2;
                ctx.fillRect(x + 4 * p, y + 7 * p, p * 8, p);
                ctx.fillStyle = C.st1;
                ctx.fillRect(x + 4 * p, y + 8 * p, p * 8, p * 7);
                ctx.fillStyle = C.w1;
                ctx.fillRect(x + 5 * p, y + 9 * p, p * 6, p * 5);
                ctx.fillStyle = C.w2;
                ctx.globalAlpha = 0.5;
                ctx.fillRect(x + 6 * p, y + 10 * p, p * 3, p * 2);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 4 * p, y + 2 * p, p * 8, p * 2);
                ctx.fillRect(x + 7 * p, y + 2 * p, p * 2, p * 6);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 4 * p, y + 2 * p, p * 8, p);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 3 * p, y + 4 * p, p, p * 2);
                ctx.fillRect(x + 12 * p, y + 4 * p, p, p * 2);
                ctx.fillStyle = C.st3;
                ctx.fillRect(x + 6 * p, y + 5 * p, p * 4, p * 2);
                ctx.fillStyle = '#a0a0a0';
                ctx.fillRect(x + 7.5 * p, y + 5 * p, p, p * 3);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 8 * p, y + 7 * p, p * 2, p);
                break;
            }

            case 23: {
                ctx.fillStyle = C.st2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + p, y + 8 * p, p * 6, p * 6);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + p, y + 9 * p, p * 6, p * 4);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 2 * p, y + 9 * p, p * 4, p * 3);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + p, y + 8 * p, p * 6, p);
                ctx.fillRect(x + p, y + 11 * p, p * 6, p);
                ctx.fillRect(x + p, y + 13 * p, p * 6, p);
                ctx.fillStyle = '#606060';
                ctx.fillRect(x + 3 * p, y + 9 * p, p, p);
                ctx.fillRect(x + 5 * p, y + 12 * p, p, p);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + p, y + 3 * p, p * 6, p * 5);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + p, y + 4 * p, p * 6, p * 3);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 2 * p, y + 4 * p, p * 4, p * 2);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + p, y + 3 * p, p * 6, p);
                ctx.fillRect(x + p, y + 6 * p, p * 6, p);
                ctx.fillStyle = '#606060';
                ctx.fillRect(x + 4 * p, y + 4 * p, p, p);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 9 * p, y + 5 * p, p * 5, p * 7);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 9 * p, y + 6 * p, p * 5, p * 5);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 10 * p, y + 7 * p, p * 3, p * 3);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 9 * p, y + 5 * p, p * 5, p);
                ctx.fillRect(x + 9 * p, y + 8 * p, p * 5, p);
                ctx.fillRect(x + 9 * p, y + 11 * p, p * 5, p);
                ctx.fillStyle = '#606060';
                ctx.fillRect(x + 11 * p, y + 7 * p, p, p);
                ctx.fillRect(x + 12 * p, y + 10 * p, p, p);
                break;
            }

            case 24: {
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.fp2;
                ctx.fillRect(x + 2 * p, y + 6 * p, p * 12, p * 10);
                ctx.fillStyle = C.fp3;
                ctx.fillRect(x + 3 * p, y + 7 * p, p * 10, p * 8);
                ctx.fillStyle = C.fp1;
                ctx.fillRect(x + 2 * p, y + 6 * p, p * 12, p);
                ctx.fillRect(x + p, y + 5 * p, p * 14, p);
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x + p, y + 5 * p, p, p * 11);
                ctx.fillRect(x + 14 * p, y + 5 * p, p, p * 11);
                const flk1 = 0.6 + Math.sin(t / 150 + sd * 3) * 0.35;
                const flk2 = 0.6 + Math.sin(t / 200 + sd * 5 + 1) * 0.3;
                const flk3 = 0.7 + Math.sin(t / 180 + sd * 7 + 2) * 0.25;
                ctx.fillStyle = C.fph;
                ctx.globalAlpha = flk1;
                ctx.fillRect(x + 4 * p, y + 10 * p, p * 3, p * 4);
                ctx.fillRect(x + 9 * p, y + 11 * p, p * 3, p * 3);
                ctx.fillStyle = C.fpf;
                ctx.globalAlpha = flk2;
                ctx.fillRect(x + 5 * p, y + 9 * p, p * 2, p * 3);
                ctx.fillRect(x + 10 * p, y + 10 * p, p * 2, p * 2);
                ctx.fillRect(x + 7 * p, y + 10 * p, p * 2, p * 3);
                ctx.fillStyle = C.fpb;
                ctx.globalAlpha = flk3;
                ctx.fillRect(x + 6 * p, y + 9 * p, p * 4, p);
                ctx.fillRect(x + 7 * p, y + 8 * p, p * 2, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = flk1 * 0.4;
                ctx.fillRect(x + 7 * p, y + 9 * p, p, p);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.fp1;
                ctx.fillRect(x + 5 * p, y + 2 * p, p * 6, p * 4);
                ctx.fillRect(x + 6 * p, y + p, p * 4, p);
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x + 5 * p, y + 3 * p, p * 6, p);
                ctx.fillStyle = flk1 > 0.7 ? C.fpf : C.fp1;
                ctx.globalAlpha = flk2 * 0.15;
                ctx.fillRect(x + 3 * p, y + 6 * p, p * 10, p * 3);
                ctx.globalAlpha = 1;
                break;
            }

            case 25: {
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 2 * p, y + p, p * 12, p * 14);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 10, p * 12);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 3 * p, y + 2 * p, p * 10, p);
                ctx.fillRect(x + 3 * p, y + 6 * p, p * 10, p);
                ctx.fillRect(x + 3 * p, y + 10 * p, p * 10, p);
                ctx.fillRect(x + 3 * p, y + 13 * p, p * 10, p);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 2 * p, y + p, p, p * 14);
                ctx.fillRect(x + 13 * p, y + p, p, p * 14);
                const books = [
                    {x:3,w:2,h:3,c:'#8b2020'},{x:5,w:1,h:3,c:'#204080'},{x:6,w:2,h:3,c:'#208040'},
                    {x:8,w:2,h:3,c:'#a06020'},{x:10,w:1,h:2,c:'#602080'},{x:11,w:2,h:3,c:'#c08020'},
                    {x:4,w:2,h:3,c:'#306090'},{x:6,w:1,h:2,c:'#903030'},{x:7,w:2,h:3,c:'#409040'},
                    {x:9,w:2,h:3,c:'#704020'},{x:11,w:1,h:3,c:'#2050a0'},{x:3,w:1,h:2,c:'#a04040'},
                    {x:4,w:2,h:3,c:'#30a060'},{x:6,w:2,h:3,c:'#806020'},{x:8,w:1,h:2,c:'#5020a0'},
                    {x:9,w:3,h:3,c:'#c04040'},{x:12,w:1,h:3,c:'#2080a0'}
                ];
                const shelves = [3, 7, 11];
                shelves.forEach((sy2, si) => {
                    for (let bi = si * 6; bi < si * 6 + 6 && bi < books.length; bi++) {
                        const b = books[bi];
                        ctx.fillStyle = b.c;
                        ctx.fillRect(x + b.x * p, y + (sy2 - b.h) * p, b.w * p, b.h * p);
                        ctx.fillStyle = 'rgba(255,255,255,0.15)';
                        ctx.fillRect(x + b.x * p, y + (sy2 - b.h) * p, b.w * p, p);
                        if (b.w > 1) {
                            ctx.fillStyle = 'rgba(255,220,150,0.25)';
                            ctx.fillRect(x + (b.x + 0.5) * p, y + (sy2 - b.h + 1) * p, p, (b.h - 1) * p);
                        }
                    }
                });
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
            hair: '#3a2518', hairHL: '#5a4030', hairDk: '#241008',
            skin: '#f4d0a0', skinHL: '#ffe8c8', skinSh: '#d8a870', skinDk: '#c09060',
            eyeW: '#f0f0ff', eye: '#1830a0', eyeHL: '#4060d0', pupil: '#080830',
            mouth: '#c07050',
            tunic: '#2848c0', tunicHL: '#4870e0', tunicMd: '#3058d0', tunicDk: '#182878', tunicSh: '#101850',
            collar: '#e0d8c0', collarSh: '#c0b898',
            belt: '#d8a830', beltBk: '#b08020', beltHL: '#f0c848',
            pants: '#384898', pantsDk: '#283068', pantsHL: '#4858a8',
            boots: '#503020', bootsHL: '#704830', bootsDk: '#301810', bootsSh: '#402818',
            cape: '#c82828', capeMd: '#a82020', capeDk: '#781818', capeHL: '#e04040',
            glove: '#e8d8b8', gloveSh: '#c8b890',
            outline: '#181020', outlineHL: '#282838'
        } : getNPCPal(color, spriteId);

        const bob = moving ? Math.sin(frame * Math.PI / 2) * p * 0.6 : 0;
        const breathe = !moving ? Math.sin(gt / 800) * p * 0.2 : 0;
        const wc = moving ? frame % 4 : 0;
        const legL = wc === 1 ? 2 * p : wc === 3 ? -p : 0;
        const legR = wc === 1 ? -p : wc === 3 ? 2 * p : 0;
        const armL = moving ? Math.sin(frame * Math.PI / 2) * 2 * p : 0;
        const armR = moving ? -Math.sin(frame * Math.PI / 2) * 2 * p : 0;
        const by = -bob + breathe;

        switch(facing) {
            case 'down': {
                ctx.fillStyle = pal.outline;
                ctx.fillRect(x + 3*p, y + by - p, p*10, p);
                ctx.fillRect(x + 2*p, y + by, p, p*4);
                ctx.fillRect(x + 13*p, y + by, p, p*4);
                ctx.fillRect(x + 3*p, y + 4*p + by, p, p*3);
                ctx.fillRect(x + 12*p, y + 4*p + by, p, p*3);
                ctx.fillStyle = pal.hairDk || pal.hair;
                ctx.fillRect(x + 3*p, y + by - p, p*10, p*2);
                ctx.fillStyle = pal.hair;
                ctx.fillRect(x + 3*p, y + by, p*10, p*4);
                ctx.fillRect(x + 2*p, y + p + by, p*2, p*3);
                ctx.fillRect(x + 12*p, y + p + by, p*2, p*3);
                ctx.fillStyle = pal.hairHL;
                ctx.fillRect(x + 5*p, y + p + by, p*6, p);
                ctx.fillRect(x + 6*p, y + by, p*4, p);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + 4*p, y + 3*p + by, p*8, p*4);
                ctx.fillStyle = pal.skinHL || pal.skin;
                ctx.fillRect(x + 5*p, y + 3*p + by, p*6, p);
                ctx.fillStyle = pal.skinSh;
                ctx.fillRect(x + 4*p, y + 6*p + by, p*8, p);
                ctx.fillStyle = pal.skinDk || pal.skinSh;
                ctx.fillRect(x + 6*p, y + 6*p + by, p*4, p);
                ctx.fillStyle = pal.eyeW || '#f0f0ff';
                ctx.fillRect(x + 5*p, y + 4*p + by, p*2, p*2);
                ctx.fillRect(x + 9*p, y + 4*p + by, p*2, p*2);
                ctx.fillStyle = pal.eye;
                ctx.fillRect(x + 5*p, y + 4*p + by, p*2, p*2);
                ctx.fillRect(x + 9*p, y + 4*p + by, p*2, p*2);
                ctx.fillStyle = pal.eyeHL || '#4060d0';
                ctx.fillRect(x + 6*p, y + 4*p + by, p, p);
                ctx.fillRect(x + 10*p, y + 4*p + by, p, p);
                ctx.fillStyle = pal.pupil || '#080830';
                ctx.fillRect(x + 6*p, y + 5*p + by, p, p);
                ctx.fillRect(x + 10*p, y + 5*p + by, p, p);
                ctx.fillStyle = '#fff';
                ctx.fillRect(x + 5*p, y + 4*p + by, p, p);
                ctx.fillRect(x + 9*p, y + 4*p + by, p, p);
                ctx.fillStyle = pal.mouth || pal.skinSh;
                ctx.fillRect(x + 7*p, y + 6*p + by, p*2, p);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(x + 5*p, y + 7*p + by, p*6, p);
                ctx.fillStyle = pal.collarSh || pal.tunic;
                ctx.fillRect(x + 6*p, y + 7*p + by, p*4, p);
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(x + 3*p, y + 8*p + by, p*10, p*3);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(x + 5*p, y + 8*p + by, p*3, p*2);
                ctx.fillStyle = pal.tunicMd || pal.tunic;
                ctx.fillRect(x + 8*p, y + 8*p + by, p*3, p*2);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(x + 3*p, y + 10*p + by, p*10, p);
                ctx.fillStyle = pal.tunicSh || pal.tunicDk;
                ctx.fillRect(x + 7*p, y + 8*p + by, p, p*3);
                ctx.fillStyle = pal.belt;
                ctx.fillRect(x + 3*p, y + 10*p + by, p*10, p);
                ctx.fillStyle = pal.beltHL || pal.belt;
                ctx.fillRect(x + 4*p, y + 10*p + by, p*3, p);
                ctx.fillStyle = pal.beltBk;
                ctx.fillRect(x + 7*p, y + 10*p + by, p*2, p);
                ctx.fillStyle = pal.glove || pal.skin;
                const laX = Math.round(2 + armL / p);
                const raX = Math.round(12 + armR / p);
                ctx.fillRect(x + laX*p, y + 8*p + by, p*2, p*3);
                ctx.fillRect(x + raX*p, y + 8*p + by, p*2, p*3);
                ctx.fillStyle = pal.gloveSh || pal.skinSh;
                ctx.fillRect(x + laX*p, y + 10*p + by, p*2, p);
                ctx.fillRect(x + raX*p, y + 10*p + by, p*2, p);
                ctx.fillStyle = pal.pants;
                ctx.fillRect(x + 4*p, y + 11*p, p*3, p*2);
                ctx.fillRect(x + 9*p, y + 11*p, p*3, p*2);
                ctx.fillStyle = pal.pantsDk;
                ctx.fillRect(x + 7*p, y + 11*p, p*2, p*2);
                ctx.fillStyle = pal.pantsHL || pal.pants;
                ctx.fillRect(x + 5*p, y + 11*p, p, p);
                ctx.fillRect(x + 10*p, y + 11*p, p, p);
                ctx.fillStyle = pal.boots;
                ctx.fillRect(x + 4*p, y + 13*p + legL, p*3, p*3);
                ctx.fillRect(x + 9*p, y + 13*p + legR, p*3, p*3);
                ctx.fillStyle = pal.bootsHL;
                ctx.fillRect(x + 4*p, y + 13*p + legL, p*3, p);
                ctx.fillRect(x + 9*p, y + 13*p + legR, p*3, p);
                ctx.fillStyle = pal.bootsDk || pal.boots;
                ctx.fillRect(x + 4*p, y + 15*p + legL, p*3, p);
                ctx.fillRect(x + 9*p, y + 15*p + legR, p*3, p);
                break;
            }
            case 'up': {
                ctx.fillStyle = pal.outline;
                ctx.fillRect(x + 3*p, y + by - p, p*10, p);
                ctx.fillRect(x + 2*p, y + by, p, p*4);
                ctx.fillRect(x + 13*p, y + by, p, p*4);
                ctx.fillStyle = pal.hairDk || pal.hair;
                ctx.fillRect(x + 3*p, y + by - p, p*10, p*2);
                ctx.fillStyle = pal.hair;
                ctx.fillRect(x + 2*p, y + by, p*12, p*7);
                ctx.fillStyle = pal.hairHL;
                ctx.fillRect(x + 5*p, y + p + by, p*6, p*2);
                ctx.fillRect(x + 7*p, y + by, p*3, p);
                ctx.fillStyle = pal.hairDk || pal.hair;
                ctx.fillRect(x + 4*p, y + 5*p + by, p*8, p*2);
                if (isHero) {
                    ctx.fillStyle = pal.cape;
                    ctx.fillRect(x + 2*p, y + 7*p + by, p*12, p*5);
                    ctx.fillStyle = pal.capeMd || pal.capeDk;
                    ctx.fillRect(x + 7*p, y + 7*p + by, p, p*5);
                    ctx.fillStyle = pal.capeHL || pal.cape;
                    ctx.fillRect(x + 4*p, y + 7*p + by, p*2, p*4);
                    ctx.fillStyle = pal.capeDk;
                    ctx.fillRect(x + 10*p, y + 8*p + by, p*3, p*4);
                    ctx.fillRect(x + 2*p, y + 11*p + by, p*12, p);
                } else {
                    ctx.fillStyle = pal.tunic;
                    ctx.fillRect(x + 3*p, y + 7*p + by, p*10, p*4);
                    ctx.fillStyle = pal.tunicHL;
                    ctx.fillRect(x + 4*p, y + 7*p + by, p*3, p*3);
                    ctx.fillStyle = pal.tunicDk;
                    ctx.fillRect(x + 7*p, y + 7*p + by, p, p*4);
                    ctx.fillRect(x + 3*p, y + 10*p + by, p*10, p);
                }
                ctx.fillStyle = pal.belt;
                ctx.fillRect(x + 3*p, y + 10*p + by, p*10, p);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + Math.round(2 + armL/p)*p, y + 8*p + by, p*2, p*3);
                ctx.fillRect(x + Math.round(12 + armR/p)*p, y + 8*p + by, p*2, p*3);
                ctx.fillStyle = pal.pants;
                ctx.fillRect(x + 4*p, y + 11*p, p*3, p*2);
                ctx.fillRect(x + 9*p, y + 11*p, p*3, p*2);
                ctx.fillStyle = pal.pantsDk;
                ctx.fillRect(x + 7*p, y + 11*p, p*2, p*2);
                ctx.fillStyle = pal.boots;
                ctx.fillRect(x + 4*p, y + 13*p + legL, p*3, p*3);
                ctx.fillRect(x + 9*p, y + 13*p + legR, p*3, p*3);
                ctx.fillStyle = pal.bootsHL;
                ctx.fillRect(x + 4*p, y + 13*p + legL, p*3, p);
                ctx.fillRect(x + 9*p, y + 13*p + legR, p*3, p);
                break;
            }
            case 'left': {
                ctx.fillStyle = pal.outline;
                ctx.fillRect(x + 2*p, y + by - p, p*9, p);
                ctx.fillRect(x + p, y + by, p, p*4);
                ctx.fillRect(x + 11*p, y + by, p, p*3);
                ctx.fillStyle = pal.hairDk || pal.hair;
                ctx.fillRect(x + 2*p, y + by - p, p*9, p*2);
                ctx.fillStyle = pal.hair;
                ctx.fillRect(x + 2*p, y + by, p*9, p*4);
                ctx.fillRect(x + p, y + p + by, p*2, p*4);
                ctx.fillStyle = pal.hairHL;
                ctx.fillRect(x + 4*p, y + p + by, p*4, p);
                ctx.fillStyle = pal.hair;
                ctx.fillRect(x + 2*p, y + 3*p + by, p*3, p*3);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + 4*p, y + 3*p + by, p*7, p*4);
                ctx.fillStyle = pal.skinHL || pal.skin;
                ctx.fillRect(x + 5*p, y + 3*p + by, p*5, p);
                ctx.fillStyle = pal.skinSh;
                ctx.fillRect(x + 4*p, y + 6*p + by, p*7, p);
                ctx.fillStyle = pal.eyeW || '#f0f0ff';
                ctx.fillRect(x + 4*p, y + 4*p + by, p*3, p*2);
                ctx.fillStyle = pal.eye;
                ctx.fillRect(x + 4*p, y + 4*p + by, p*2, p*2);
                ctx.fillStyle = pal.eyeHL || '#4060d0';
                ctx.fillRect(x + 5*p, y + 4*p + by, p, p);
                ctx.fillStyle = pal.pupil || '#080830';
                ctx.fillRect(x + 4*p, y + 5*p + by, p, p);
                ctx.fillStyle = '#fff';
                ctx.fillRect(x + 5*p, y + 4*p + by, p, p);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + 7*p, y + 5*p + by, p, p);
                ctx.fillStyle = pal.mouth || pal.skinSh;
                ctx.fillRect(x + 5*p, y + 6*p + by, p*2, p);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(x + 5*p, y + 7*p + by, p*4, p);
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(x + 4*p, y + 8*p + by, p*8, p*3);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(x + 5*p, y + 8*p + by, p*3, p*2);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(x + 10*p, y + 8*p + by, p*2, p*3);
                ctx.fillRect(x + 4*p, y + 10*p + by, p*8, p);
                ctx.fillStyle = pal.belt;
                ctx.fillRect(x + 4*p, y + 10*p + by, p*8, p);
                ctx.fillStyle = pal.glove || pal.skin;
                ctx.fillRect(x + Math.round(2 + armL/p)*p, y + 8*p + by, p*2, p*3);
                ctx.fillStyle = pal.pants;
                ctx.fillRect(x + 5*p, y + 11*p, p*6, p*2);
                ctx.fillStyle = pal.pantsDk;
                ctx.fillRect(x + 5*p, y + 11*p, p*2, p*2);
                ctx.fillStyle = pal.boots;
                ctx.fillRect(x + 4*p, y + 13*p + legL, p*3, p*3);
                ctx.fillRect(x + 8*p, y + 13*p + legR, p*3, p*3);
                ctx.fillStyle = pal.bootsHL;
                ctx.fillRect(x + 4*p, y + 13*p + legL, p*3, p);
                ctx.fillRect(x + 8*p, y + 13*p + legR, p*3, p);
                break;
            }
            case 'right': {
                ctx.fillStyle = pal.outline;
                ctx.fillRect(x + 5*p, y + by - p, p*9, p);
                ctx.fillRect(x + 4*p, y + by, p, p*3);
                ctx.fillRect(x + 14*p, y + by, p, p*4);
                ctx.fillStyle = pal.hairDk || pal.hair;
                ctx.fillRect(x + 5*p, y + by - p, p*9, p*2);
                ctx.fillStyle = pal.hair;
                ctx.fillRect(x + 5*p, y + by, p*9, p*4);
                ctx.fillRect(x + 13*p, y + p + by, p*2, p*4);
                ctx.fillStyle = pal.hairHL;
                ctx.fillRect(x + 8*p, y + p + by, p*4, p);
                ctx.fillStyle = pal.hair;
                ctx.fillRect(x + 11*p, y + 3*p + by, p*3, p*3);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + 5*p, y + 3*p + by, p*7, p*4);
                ctx.fillStyle = pal.skinHL || pal.skin;
                ctx.fillRect(x + 6*p, y + 3*p + by, p*5, p);
                ctx.fillStyle = pal.skinSh;
                ctx.fillRect(x + 5*p, y + 6*p + by, p*7, p);
                ctx.fillStyle = pal.eyeW || '#f0f0ff';
                ctx.fillRect(x + 9*p, y + 4*p + by, p*3, p*2);
                ctx.fillStyle = pal.eye;
                ctx.fillRect(x + 10*p, y + 4*p + by, p*2, p*2);
                ctx.fillStyle = pal.eyeHL || '#4060d0';
                ctx.fillRect(x + 10*p, y + 4*p + by, p, p);
                ctx.fillStyle = pal.pupil || '#080830';
                ctx.fillRect(x + 11*p, y + 5*p + by, p, p);
                ctx.fillStyle = '#fff';
                ctx.fillRect(x + 10*p, y + 4*p + by, p, p);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + 8*p, y + 5*p + by, p, p);
                ctx.fillStyle = pal.mouth || pal.skinSh;
                ctx.fillRect(x + 9*p, y + 6*p + by, p*2, p);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(x + 7*p, y + 7*p + by, p*4, p);
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(x + 4*p, y + 8*p + by, p*8, p*3);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(x + 8*p, y + 8*p + by, p*3, p*2);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(x + 4*p, y + 8*p + by, p*2, p*3);
                ctx.fillRect(x + 4*p, y + 10*p + by, p*8, p);
                ctx.fillStyle = pal.belt;
                ctx.fillRect(x + 4*p, y + 10*p + by, p*8, p);
                ctx.fillStyle = pal.glove || pal.skin;
                ctx.fillRect(x + Math.round(12 + armR/p)*p, y + 8*p + by, p*2, p*3);
                ctx.fillStyle = pal.pants;
                ctx.fillRect(x + 5*p, y + 11*p, p*6, p*2);
                ctx.fillStyle = pal.pantsDk;
                ctx.fillRect(x + 9*p, y + 11*p, p*2, p*2);
                ctx.fillStyle = pal.boots;
                ctx.fillRect(x + 4*p, y + 13*p + legL, p*3, p*3);
                ctx.fillRect(x + 8*p, y + 13*p + legR, p*3, p*3);
                ctx.fillStyle = pal.bootsHL;
                ctx.fillRect(x + 4*p, y + 13*p + legL, p*3, p);
                ctx.fillRect(x + 8*p, y + 13*p + legR, p*3, p);
                break;
            }
        }
    }

    function getNPCPal(color, spriteId) {
        const c = color || '#44aa44';
        const h = hexToHSL(c);
        return {
            hair: hslHex((h.h + 40) % 360, Math.min(h.s + 10, 50), 25),
            hairHL: hslHex((h.h + 40) % 360, Math.min(h.s + 10, 50), 40),
            hairDk: hslHex((h.h + 40) % 360, Math.min(h.s + 10, 50), 15),
            skin: '#f4d0a0', skinHL: '#ffe8c8', skinSh: '#d8a870', skinDk: '#c09060',
            eyeW: '#f0f0ff', eye: '#203060', eyeHL: '#3050a0', pupil: '#080830',
            mouth: '#c07050',
            tunic: c, tunicHL: shade(c, 30), tunicMd: shade(c, 10), tunicDk: shade(c, -30), tunicSh: shade(c, -45),
            collar: shade(c, 50), collarSh: shade(c, 30),
            belt: '#b09030', beltBk: '#806020', beltHL: '#d0b040',
            pants: shade(c, -35), pantsDk: shade(c, -50), pantsHL: shade(c, -20),
            boots: '#504030', bootsHL: '#685040', bootsDk: '#382818', bootsSh: '#402818',
            glove: '#e8d8b8', gloveSh: '#c8b890',
            cape: shade(c, -15), capeMd: shade(c, -25), capeDk: shade(c, -40), capeHL: shade(c, 5),
            outline: '#181020', outlineHL: '#282838'
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
