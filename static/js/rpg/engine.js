const RPGEngine = (function() {
    const TILE = 16;
    const SCALE = 3;
    const TS = TILE * SCALE;
    const STEP_DURATION = 180;
    const SPRITE_H = 80;
    const SPRITE_YOFF = SPRITE_H - TS;

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

    const C = RPGColors.C;

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
                RPGTiles.drawTile(ctx, RPGColors.C, currentMap.tiles[r][c], c * TS, r * TS, r, c, gt, TS);
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
                if (t > 0) RPGTiles.drawTile(ctx, RPGColors.C, t, c * TS, r * TS, r, c, gt, TS);
            }
        }
    }

    function renderShadows() {
        const drawSh = (x, y, size) => {
            const cx = x + TS * 0.5;
            const cy = y + TS * 0.92;
            const rx = TS * (size || 0.35);
            const ry = TS * 0.10;
            const layers = [
                { dr: 12, da: 4, a: 0.02 },
                { dr: 8, da: 3, a: 0.04 },
                { dr: 5, da: 2, a: 0.08 },
                { dr: 2, da: 1, a: 0.16 },
                { dr: -2, da: -1, a: 0.28 }
            ];
            for (const l of layers) {
                ctx.fillStyle = 'rgba(0,0,0,' + l.a + ')';
                ctx.beginPath();
                ctx.ellipse(cx, cy, rx + l.dr, ry + l.da, 0, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.fillStyle = 'rgba(0,0,0,0.18)';
            ctx.fillRect(cx - 4, cy - 1, 8, 2);
            ctx.fillStyle = 'rgba(0,0,0,0.10)';
            for (let i = -3; i <= 3; i++) {
                ctx.fillRect(cx + i * 3 - 1, cy, 2, 1);
            }
        };
        npcs.forEach(n => drawSh(n.px, n.py, 0.22));
        if (player) drawSh(player.px, player.py, 0.24);
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
                RPGSprites.drawSprite(ctx, gt, 'npc', e.x, e.y, n.facing, n.animFrame || 0, n.stepping, n.color, n.spriteId, TS, SPRITE_YOFF);
                if (!dialogueActive && !choiceActive && player) {
                    const dist = Math.abs(player.px - e.x) + Math.abs(player.py - e.y);
                    if (dist < TS * 2.2 && dist > 0) renderBubble(e.x, e.y);
                }
            } else {
                RPGSprites.drawSprite(ctx, gt, 'hero', e.x, e.y, player.facing, player.animFrame, player.stepping, undefined, undefined, TS, SPRITE_YOFF);
            }
        });
    }

    function renderBubble(x, y) {
        const bob = Math.sin(gt / 350) * 5;
        const pulse = 0.88 + Math.sin(gt / 250) * 0.12;
        const sparkle = Math.sin(gt / 180) * 0.3 + 0.7;
        const sparkle2 = Math.sin(gt / 220 + 1.5) * 0.3 + 0.7;
        const sparkle3 = Math.sin(gt / 160 + 3.0) * 0.3 + 0.7;
        const ix = x + TS / 2;
        const iy = y - SPRITE_YOFF - 14 + bob;
        ctx.fillStyle = C.hl1;
        ctx.globalAlpha = 0.04;
        ctx.beginPath();
        ctx.ellipse(ix, iy - 6, 30 * pulse, 26 * pulse, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#f8e838';
        ctx.globalAlpha = 0.06;
        ctx.beginPath();
        ctx.ellipse(ix, iy - 6, 26 * pulse, 22 * pulse, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 0.10;
        ctx.beginPath();
        ctx.ellipse(ix, iy - 6, 20 * pulse, 16 * pulse, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
        ctx.fillStyle = '#000820';
        ctx.globalAlpha = 0.55;
        ctx.beginPath();
        ctx.ellipse(ix, iy - 6, 14 * pulse, 11 * pulse, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
        ctx.fillStyle = '#c8a010';
        ctx.beginPath();
        ctx.ellipse(ix, iy - 6, 13 * pulse, 10 * pulse, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#f8e838';
        ctx.beginPath();
        ctx.ellipse(ix, iy - 6, 11 * pulse, 8.5 * pulse, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#ffffa0';
        ctx.beginPath();
        ctx.ellipse(ix, iy - 8, 7 * pulse, 4 * pulse, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.globalAlpha = sparkle * 0.7;
        ctx.fillRect(ix - 4, iy - 11, 2, 2);
        ctx.globalAlpha = sparkle2 * 0.6;
        ctx.fillRect(ix + 5, iy - 4, 2, 2);
        ctx.globalAlpha = sparkle3 * 0.5;
        ctx.fillRect(ix - 7, iy - 3, 1, 1);
        ctx.globalAlpha = sparkle * 0.4;
        ctx.fillRect(ix + 8, iy - 8, 1, 1);
        ctx.globalAlpha = sparkle2 * 0.35;
        ctx.fillRect(ix - 2, iy + 1, 1, 1);
        ctx.globalAlpha = 1;
        ctx.fillStyle = '#b08000';
        ctx.font = 'bold 11px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('!', ix + 1, iy - 5);
        ctx.fillStyle = '#fff';
        ctx.fillText('!', ix, iy - 6);
        ctx.fillStyle = '#ffe880';
        ctx.globalAlpha = sparkle * 0.4;
        ctx.fillText('!', ix, iy - 6);
        ctx.globalAlpha = 1;
        ctx.textAlign = 'left';
        ctx.textBaseline = 'alphabetic';
        const tbob = Math.sin(gt / 300) * 2;
        ctx.fillStyle = '#f8e838';
        ctx.beginPath();
        ctx.moveTo(ix - 4, iy + 4 + tbob);
        ctx.lineTo(ix + 4, iy + 4 + tbob);
        ctx.lineTo(ix, iy + 11 + tbob);
        ctx.closePath();
        ctx.fill();
        ctx.fillStyle = '#ffffa0';
        ctx.globalAlpha = 0.5;
        ctx.beginPath();
        ctx.moveTo(ix - 2, iy + 5 + tbob);
        ctx.lineTo(ix + 2, iy + 5 + tbob);
        ctx.lineTo(ix, iy + 9 + tbob);
        ctx.closePath();
        ctx.fill();
        ctx.globalAlpha = 1;
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
