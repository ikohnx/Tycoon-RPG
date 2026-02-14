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
        g5: '#45d270', g6: '#0d4518', g7: '#88e898', g8: '#247a2e', g9: '#328c3a', g10: '#168020',
        p1: '#c8a870', p2: '#b89860', p3: '#a88850', p4: '#d8b880', pe: '#8a7040', pm: '#6e5838',
        p5: '#9e7838', p6: '#d4b478', p7: '#bca068',
        w1: '#1848a8', w2: '#2058c0', w3: '#103888', w4: '#2868d0', wf: '#90c0f0', ws: '#4070c0', wd: '#0c2870', wsp: '#c8e0ff',
        w5: '#3878e0', w6: '#0a1848', w7: '#1040a0', w8: '#5090d8', w9: '#183898',
        bk1: '#788098', bk2: '#687088', bk3: '#8890a8', bk4: '#9098b0', bkl: '#505868', bkd: '#404850', bkh: '#a0a8b8',
        bk5: '#303840', bk6: '#a8b0c0', bk7: '#586070', bk8: '#98a0b0',
        rf1: '#c84838', rf2: '#d85848', rf3: '#b83828', rf4: '#e86858', rfl: '#882018', rfh: '#f08878', rfs: '#981818',
        rf5: '#a83020', rf6: '#d04838',
        dr1: '#704828', dr2: '#886038', dr3: '#5a3818', drk: '#e8c840', drf: '#604020', drh: '#a87848',
        dr4: '#9a7050', dr5: '#503018',
        wn1: '#4898d0', wn2: '#68b8f0', wn3: '#3880b8', wnf: '#484858', wns: '#a8d8ff', wnc: '#c06048',
        wn4: '#5888b0', wn5: '#3068a0',
        wd1: '#886038', wd2: '#a07848', wd3: '#685028', wd4: '#b89058', wdg: '#504018', wdk: '#4a3820',
        wd5: '#907048', wd6: '#785830', wd7: '#c0a068',
        st1: '#708088', st2: '#8898a0', st3: '#586870', st4: '#98a8b0', stm: '#485058',
        st5: '#7888a0', st6: '#607078', st7: '#a0b0b8',
        tr1: '#187828', tr2: '#28a040', tr3: '#0e5818', tr4: '#38b858', trh: '#48c868', trs: '#084010', tk1: '#5a3818', tk2: '#704828', tk3: '#483010',
        tr5: '#1a6820', tr6: '#309848', tk4: '#624020',
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
        sa5: '#b8a058', sa6: '#f0e0a0',
        fp1: '#606878', fp2: '#505860', fp3: '#404850', fph: '#d04010', fpf: '#f08030', fpb: '#f0c040',
        fp4: '#707888', fp5: '#e85020',
        moss: '#2a6830',
        mtl1: '#c0c8d0', mtl2: '#909aa8', mtl3: '#606878', mtlh: '#e8f0f8', mtl4: '#485060',
        wdm1: '#7a5030', wdm2: '#946840', wdm3: '#5e4020',
        bkm1: '#707888', bkm2: '#808898', bkm3: '#606070',
        rfm1: '#c04030', rfm2: '#b03828', rfm3: '#d85040',
        stm1: '#6a7880', stm2: '#7a8890', stm3: '#5a6870',
        gsh1: '#0a3010', gsh2: '#0e3818', gsh3: '#124020',
        tkh: '#886040', tkg: '#604020',
        trc: '#0c4810', trd: '#165818',
        pe2: '#7a6040', pe3: '#9a8050',
        wdp: '#081838',
        rk1: '#8b7355', rk2: '#a08868', rk3: '#6b5540', rk4: '#c0a880', rk5: '#504030',
        rk6: '#d8c8a8', rkh: '#e0d0b0', rkd: '#3a2c20', rkm: '#7a6548',
        mv1: '#2a6028', mv2: '#387838', mv3: '#1e4820', mv4: '#4a9048',
        wml: '#f8e8c0', wmd: '#d0b880',
        wms: '#b8d8f8', wmm: '#d0e8ff',
        dsh1: '#1a1420', dsh2: '#281e30',
        hl1: '#fff8e0', hl2: '#f0e0b0',
        g11: '#6adc78', g12: '#92eea0', g13: '#1c6e24', g14: '#3aa842',
        rk7: '#b8a070', rk8: '#907050', rk9: '#c8b890',
        w10: '#6898d0', w11: '#88b8e0', w12: '#a0d0f0',
        bk9: '#b0b8c8', bk10: '#c0c8d0',
        rf7: '#e87060', rf8: '#f09888',
        tk5: '#7a5028', tk6: '#a87840', tk7: '#c89860',
        mv5: '#5aac58', mv6: '#78c870',
        fl1: '#c8b898', fl2: '#d8c8a8', fl3: '#b0a080', fl4: '#a09070'
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
            const ry = TS * 0.08;
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
        const bob = Math.sin(gt / 350) * 5;
        const pulse = 0.88 + Math.sin(gt / 250) * 0.12;
        const sparkle = Math.sin(gt / 180) * 0.3 + 0.7;
        const sparkle2 = Math.sin(gt / 220 + 1.5) * 0.3 + 0.7;
        const sparkle3 = Math.sin(gt / 160 + 3.0) * 0.3 + 0.7;
        const ix = x + TS / 2;
        const iy = y - 20 + bob;
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

    function dither(x, y, w, h, c1, c2) {
        ctx.fillStyle = c1;
        ctx.fillRect(x, y, w, h);
        ctx.fillStyle = c2;
        for (let py = 0; py < h; py++) {
            for (let px = (py & 1); px < w; px += 2) {
                ctx.fillRect(x + px, y + py, 1, 1);
            }
        }
    }

    function ditherFast(x, y, w, h, c1, c2) {
        ctx.fillStyle = c1;
        ctx.fillRect(x, y, w, h);
        ctx.fillStyle = c2;
        for (let py = 0; py < h; py += 2) {
            for (let px = 0; px < w; px += 2) {
                ctx.fillRect(x + px, y + py, 1, 1);
                ctx.fillRect(x + px + 1, y + py + 1, 1, 1);
            }
        }
    }

    function drawTile(id, x, y, row, col) {
        const s = TS;
        const D = 1;
        const sd = (row * 131 + col * 97) & 0xFF;
        const t = gt;

        switch(id) {
            case 0: break;

            case 1: {
                ditherFast(x, y + 34, s, 14, C.gsh2, C.gsh3);
                ditherFast(x, y + 22, s, 16, C.gsh3, C.gd);
                ditherFast(x, y + 12, s, 16, C.gd, C.g2);
                ditherFast(x, y, s, 16, C.g2, C.g1);
                ditherFast(x + 6, y + 3, 36, 16, C.g1, C.g3);
                ditherFast(x + 12, y + 2, 24, 12, C.g3, C.g4);
                dither(x + 16, y + 3, 16, 8, C.g4, C.g5);
                ctx.fillStyle = C.g11;
                ctx.globalAlpha = 0.15;
                ctx.fillRect(x + 10, y + 6, 28, 8);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.gsh1;
                ctx.globalAlpha = 0.35;
                for (let i = 0; i < 4; i++) {
                    const sx2 = (sd * 7 + i * 47) % 28 + 6;
                    const sy2 = (sd * 11 + i * 37) % 18 + 22;
                    dither(x + sx2, y + sy2, 10, 7, C.gsh1, C.gsh2);
                }
                ctx.globalAlpha = 1;
                for (let i = 0; i < 16; i++) {
                    const gx = (sd * 7 + i * 29) % 42 + 3;
                    const gy = (sd * 11 + i * 19) % 38 + 4;
                    const gc = [C.g3, C.g4, C.gd, C.g5, C.g10, C.g8, C.g9, C.g11, C.mv2, C.g14, C.g13][i % 11];
                    ctx.fillStyle = gc;
                    const bh = 3 + (i % 3);
                    ctx.fillRect(x + gx, y + gy, D, bh);
                    ctx.fillRect(x + gx - 1, y + gy + 1, D, bh - 1);
                    ctx.fillRect(x + gx + 1, y + gy + 1, D, bh - 1);
                    if (i < 10) {
                        ctx.fillRect(x + gx - 2, y + gy + 2, D, D);
                        ctx.fillRect(x + gx + 2, y + gy + 2, D, D);
                    }
                }
                ctx.fillStyle = C.gdd;
                for (let i = 0; i < 10; i++) {
                    ctx.fillRect(x + ((sd * 3 + i * 43) % 42) + 3, y + ((sd * 5 + i * 47) % 42) + 3, D, D);
                }
                if ((sd & 7) < 3) {
                    ctx.fillStyle = '#808078';
                    const rx = ((sd * 11) % 28) + 8;
                    const ry = ((sd * 7) % 28) + 12;
                    ctx.fillRect(x + rx, y + ry, 3, 2);
                    ctx.fillStyle = '#989890';
                    ctx.fillRect(x + rx, y + ry, 2, D);
                    ctx.fillStyle = '#606058';
                    ctx.fillRect(x + rx + 1, y + ry + 1, 2, D);
                }
                if ((sd & 15) < 2) {
                    const mx = (sd * 9) % 32 + 8;
                    const my = (sd * 13) % 26 + 12;
                    ctx.fillStyle = '#c83020';
                    ctx.fillRect(x + mx, y + my, 3, 2);
                    ctx.fillStyle = '#e84838';
                    ctx.fillRect(x + mx, y + my, 2, D);
                    ctx.fillStyle = '#f8e848';
                    ctx.fillRect(x + mx + 1, y + my - 1, D, D);
                    ctx.fillStyle = '#a87848';
                    ctx.fillRect(x + mx + 1, y + my + 2, D, 2);
                }
                if ((sd & 15) > 12) {
                    const lx = (sd * 3) % 28 + 8;
                    const ly = (sd * 7) % 28 + 12;
                    ctx.fillStyle = '#a07020';
                    ctx.fillRect(x + lx, y + ly, 4, D);
                    ctx.fillRect(x + lx + 1, y + ly + 1, D, D);
                    ctx.fillStyle = '#c09030';
                    ctx.fillRect(x + lx, y + ly, D, D);
                }
                ctx.fillStyle = C.g1;
                ctx.globalAlpha = 0.25;
                ctx.fillRect(x, y, s, 3);
                ctx.fillRect(x, y + 45, s, 3);
                ctx.globalAlpha = 1;
                break;
            }

            case 2: {
                ditherFast(x, y, s, s, C.pe2, C.pm);
                ditherFast(x + 3, y + 3, 42, 42, C.pm, C.p2);
                ditherFast(x + 8, y + 8, 32, 32, C.p2, C.pe3);
                ditherFast(x + 14, y + 14, 20, 20, C.pe3, C.p4);
                ctx.fillStyle = C.gd;
                ctx.globalAlpha = 0.12;
                ctx.fillRect(x, y, s, 3);
                ctx.fillRect(x, y + 45, s, 3);
                ctx.globalAlpha = 1;
                const stones = [
                    {sx:2,sy:2,sw:10,sh:8},{sx:14,sy:1,sw:12,sh:9},{sx:28,sy:3,sw:9,sh:7},{sx:38,sy:1,sw:8,sh:8},
                    {sx:5,sy:14,sw:11,sh:8},{sx:18,sy:13,sw:10,sh:9},{sx:30,sy:15,sw:12,sh:7},
                    {sx:1,sy:26,sw:9,sh:8},{sx:12,sy:25,sw:12,sh:9},{sx:26,sy:27,sw:10,sh:7},{sx:38,sy:25,sw:8,sh:9},
                    {sx:4,sy:37,sw:10,sh:8},{sx:16,sy:38,sw:11,sh:7},{sx:29,sy:36,sw:9,sh:9},{sx:40,sy:38,sw:7,sh:7}
                ];
                stones.forEach((st, i) => {
                    const si2 = (sd + i * 37) & 0xFF;
                    const sh2 = si2 & 3;
                    const mc = sh2 === 0 ? C.p1 : sh2 === 1 ? C.p2 : sh2 === 2 ? C.p4 : C.p7;
                    ctx.fillStyle = mc;
                    ctx.fillRect(x + st.sx + 1, y + st.sy, st.sw - 2, st.sh);
                    ctx.fillRect(x + st.sx, y + st.sy + 1, st.sw, st.sh - 2);
                    ctx.fillStyle = C.p6;
                    ctx.fillRect(x + st.sx + 1, y + st.sy, st.sw - 2, D);
                    ctx.fillRect(x + st.sx, y + st.sy + 1, D, st.sh - 3);
                    ctx.fillStyle = 'rgba(255,255,255,0.15)';
                    ctx.fillRect(x + st.sx + 2, y + st.sy + 1, st.sw - 4, D);
                    ctx.fillRect(x + st.sx + 1, y + st.sy + 1, D, 2);
                    ctx.fillStyle = C.pe;
                    ctx.fillRect(x + st.sx + 1, y + st.sy + st.sh - 1, st.sw - 2, D);
                    ctx.fillRect(x + st.sx + st.sw - 1, y + st.sy + 1, D, st.sh - 3);
                    ctx.fillStyle = 'rgba(0,0,0,0.15)';
                    ctx.fillRect(x + st.sx + 2, y + st.sy + st.sh - 2, st.sw - 4, D);
                    ctx.fillRect(x + st.sx + st.sw - 2, y + st.sy + 2, D, st.sh - 4);
                    if (st.sw > 5) {
                        ctx.fillStyle = 'rgba(0,0,0,0.06)';
                        ctx.fillRect(x + st.sx + 3, y + st.sy + 3, 2, D);
                    }
                });
                ctx.fillStyle = C.pe2;
                for (let i = 0; i < 6; i++) {
                    ctx.fillRect(x + ((sd * 3 + i * 31) % 40) + 4, y + ((sd * 7 + i * 37) % 40) + 4, 2, D);
                }
                if ((sd & 3) === 0) {
                    ctx.fillStyle = C.gd;
                    const gx = (sd * 7) % 34 + 4;
                    ctx.fillRect(x + gx, y + 1, D, 3);
                    ctx.fillRect(x + gx - 1, y + 2, D, 2);
                    ctx.fillRect(x + gx + 1, y + 2, D, 2);
                }
                if ((sd & 3) === 1) {
                    ctx.fillStyle = C.g3;
                    const gx2 = (sd * 5) % 34 + 4;
                    ctx.fillRect(x + gx2, y + 44, D, 3);
                    ctx.fillRect(x + gx2 - 1, y + 45, D, 2);
                }
                if ((sd & 7) === 0) {
                    ctx.fillStyle = C.w2;
                    ctx.globalAlpha = 0.3;
                    ctx.beginPath();
                    ctx.ellipse(x + (sd % 30) + 9, y + (sd % 20) + 14, 3, 2, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = '#fff';
                    ctx.globalAlpha = 0.4;
                    ctx.fillRect(x + (sd % 30) + 9, y + (sd % 20) + 13, D, D);
                    ctx.globalAlpha = 1;
                }
                break;
            }

            case 3: {
                const wt = t / 600;
                ctx.fillStyle = C.wdp;
                ctx.fillRect(x, y, s, s);
                ditherFast(x, y + 38, s, 10, C.wdp, C.w6);
                ditherFast(x, y + 26, s, 16, C.w6, C.wd);
                ditherFast(x, y + 14, s, 16, C.wd, C.w3);
                ditherFast(x, y, s, 18, C.w3, C.w1);
                ditherFast(x + 4, y + 1, 40, 12, C.w1, C.w2);
                dither(x + 10, y + 3, 28, 8, C.w2, C.w10);
                for (let i = 0; i < 10; i++) {
                    const wx = Math.sin(wt + i * 0.75 + col * 0.7) * 9 + 10;
                    const wy = i * 5 + 1;
                    const ww = 18 + Math.sin(wt * 0.5 + i) * 4;
                    ctx.fillStyle = C.w2;
                    ctx.fillRect(x + wx, y + wy, ww, D);
                    ctx.fillStyle = C.w4;
                    ctx.fillRect(x + wx + 2, y + wy - 1, ww - 4, D);
                    ctx.fillStyle = C.w8;
                    ctx.fillRect(x + wx + 4, y + wy + 1, ww - 8, D);
                    ctx.fillStyle = C.ws;
                    ctx.fillRect(x + wx + 6, y + wy + 2, Math.max(1, ww - 12), D);
                }
                for (let i = 0; i < 6; i++) {
                    const dx2 = Math.sin(wt * 1.3 + i * 1.4 + sd * 0.4) * 12 + 16;
                    const dy2 = Math.sin(wt * 0.7 + i * 2.2 + sd * 0.6) * 10 + 16;
                    ctx.fillStyle = C.w4;
                    ctx.globalAlpha = 0.35;
                    ctx.fillRect(x + dx2, y + dy2, 4, D);
                    ctx.fillRect(x + dx2 + 1, y + dy2 + 1, 2, D);
                    ctx.fillRect(x + dx2 + 2, y + dy2 - 1, 2, D);
                    ctx.fillRect(x + dx2 - 1, y + dy2 + 1, D, 2);
                    ctx.fillRect(x + dx2 + 4, y + dy2 - 1, D, 2);
                    ctx.globalAlpha = 1;
                }
                ctx.fillStyle = C.wsp;
                for (let i = 0; i < 5; i++) {
                    const spx = ((sd * (11 + i * 7)) % 34) + 7;
                    const spy = ((sd * (5 + i * 3)) % 30) + 9;
                    const spA = 0.4 + Math.sin(wt * (2.5 + i * 0.5) + sd * (i + 1)) * 0.4;
                    ctx.globalAlpha = spA;
                    ctx.fillRect(x + spx, y + spy, 2, D);
                    ctx.fillRect(x + spx + 1, y + spy - 1, D, D);
                }
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.14 + Math.sin(wt * 1.5 + col + row) * 0.08;
                for (let i = 0; i < 8; i++) {
                    ctx.fillRect(x + ((sd * 3 + i * 23) % 38) + 5, y + ((sd * 7 + i * 29) % 38) + 5, D, D);
                }
                ctx.globalAlpha = 0.25 + Math.sin(wt * 4 + sd * 2) * 0.2;
                ctx.fillRect(x + ((sd * 13) % 28) + 10, y + ((sd * 9) % 18) + 8, 3, D);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wms;
                ctx.globalAlpha = 0.08;
                ctx.fillRect(x, y, s, 6);
                ctx.globalAlpha = 1;
                break;
            }

            case 4: {
                ditherFast(x, y, s, s, C.bkd, C.bk5);
                const bw2 = [10, 8, 11, 9, 7, 10, 8, 12];
                for (let br = 0; br < 4; br++) {
                    let cx2 = (br % 2) * 5;
                    const by2 = br * 12;
                    let si2 = (sd + br * 2) & 7;
                    while (cx2 < 47) {
                        const bw3 = Math.min(bw2[si2 & 7], 47 - cx2);
                        if (bw3 < 3) { cx2 += bw3 + 1; si2++; continue; }
                        const sh2 = ((si2 + br + sd) & 3);
                        const bc = sh2 === 0 ? C.bk1 : sh2 === 1 ? C.bk2 : sh2 === 2 ? C.bk3 : C.bk4;
                        ctx.fillStyle = bc;
                        ctx.fillRect(x + cx2, y + by2, bw3, 11);
                        if (bw3 > 5) {
                            dither(x + cx2 + 1, y + by2 + 1, bw3 - 2, 4, bc, C.bk6);
                        }
                        ctx.fillStyle = C.bkh;
                        ctx.globalAlpha = 0.3;
                        ctx.fillRect(x + cx2, y + by2, bw3, D);
                        ctx.fillRect(x + cx2, y + by2, D, 11);
                        ctx.globalAlpha = 0.15;
                        ctx.fillRect(x + cx2 + 1, y + by2 + 1, bw3 - 2, D);
                        ctx.globalAlpha = 1;
                        ctx.fillStyle = C.bkl;
                        ctx.fillRect(x + cx2, y + by2 + 11, bw3, D);
                        ctx.fillRect(x + cx2 + bw3, y + by2, D, 11);
                        ctx.fillStyle = C.bk5;
                        ctx.fillRect(x + cx2 + bw3 - 1, y + by2 + 9, D, 2);
                        ctx.fillRect(x + cx2 + bw3 - 1, y + by2 + 10, 2, D);
                        if ((si2 & 3) === 0 && bw3 > 4) {
                            ctx.fillStyle = C.bkm3;
                            ctx.fillRect(x + cx2 + 2, y + by2 + 3, 3, D);
                            ctx.fillRect(x + cx2 + 3, y + by2 + 4, 2, D);
                            ctx.fillRect(x + cx2 + bw3 - 4, y + by2 + 6, 2, D);
                        }
                        if (sh2 === 2 && bw3 > 5) {
                            ctx.fillStyle = 'rgba(0,0,0,0.08)';
                            ctx.fillRect(x + cx2 + 2, y + by2 + 5, bw3 - 4, 3);
                        }
                        if (((si2 + br) & 7) === 0) {
                            ctx.fillStyle = C.moss;
                            ctx.globalAlpha = 0.22;
                            ctx.fillRect(x + cx2 + 1, y + by2 + 8, bw3 - 2, 2);
                            ctx.fillStyle = C.mv1;
                            ctx.fillRect(x + cx2 + 2, y + by2 + 9, bw3 - 4, D);
                            ctx.globalAlpha = 1;
                        }
                        cx2 += bw3 + 1;
                        si2++;
                    }
                }
                ctx.fillStyle = 'rgba(0,0,0,0.18)';
                ctx.fillRect(x, y + 40, s, 8);
                ctx.fillStyle = 'rgba(0,0,0,0.10)';
                ctx.fillRect(x, y + 38, s, 4);
                ctx.fillStyle = 'rgba(255,255,255,0.10)';
                ctx.fillRect(x, y, s, 3);
                ctx.fillStyle = 'rgba(255,255,255,0.05)';
                ctx.fillRect(x, y + 3, s, 2);
                break;
            }

            case 5: {
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x, y, s, s);
                dither(x, y + 18, s, 30, C.bk2, C.bk7);
                for (let i = 0; i < 4; i++) {
                    const bx2 = i * 12;
                    ctx.fillStyle = C.bk4;
                    ctx.fillRect(x + bx2, y, 10, 16);
                    dither(x + bx2 + 1, y + 2, 8, 6, C.bk4, C.rk1);
                    ctx.fillStyle = C.bkh;
                    ctx.globalAlpha = 0.3;
                    ctx.fillRect(x + bx2, y, 10, 2);
                    ctx.fillRect(x + bx2, y, 2, 16);
                    ctx.globalAlpha = 1;
                    ctx.fillStyle = C.bkl;
                    ctx.fillRect(x + bx2 + 10, y, D, 16);
                    ctx.fillRect(x + bx2, y + 14, 10, 2);
                    ctx.fillStyle = C.bkm1;
                    ctx.globalAlpha = 0.15;
                    for (let j = 0; j < 3; j++) {
                        ctx.fillRect(x + bx2 + ((sd + i * 7 + j * 3) % 6) + 2, y + 4 + j * 4, D, D);
                    }
                    ctx.globalAlpha = 1;
                }
                ctx.fillStyle = C.bk5;
                ctx.fillRect(x, y + 16, s, 2);
                ctx.fillStyle = C.rkd;
                ctx.globalAlpha = 0.15;
                ctx.fillRect(x, y + 16, s, 3);
                ctx.globalAlpha = 1;
                for (let br = 0; br < 2; br++) {
                    let cx2 = (br & 1) * 6;
                    while (cx2 < 47) {
                        const bw3 = Math.min(10, 47 - cx2);
                        ctx.fillStyle = ((cx2 + br) & 1) ? C.bk3 : C.bk1;
                        ctx.fillRect(x + cx2, y + 20 + br * 14, bw3, 12);
                        ctx.fillStyle = C.bkh;
                        ctx.globalAlpha = 0.12;
                        ctx.fillRect(x + cx2, y + 20 + br * 14, bw3, D);
                        ctx.fillRect(x + cx2, y + 20 + br * 14, D, 12);
                        ctx.globalAlpha = 1;
                        ctx.fillStyle = C.bkl;
                        ctx.fillRect(x + cx2, y + 32 + br * 14, bw3, D);
                        ctx.fillRect(x + cx2 + bw3, y + 20 + br * 14, D, 12);
                        cx2 += bw3 + 2;
                    }
                }
                ctx.fillStyle = 'rgba(255,255,255,0.08)';
                ctx.fillRect(x, y, s, 3);
                ctx.fillStyle = 'rgba(0,0,0,0.12)';
                ctx.fillRect(x, y + 16, s, 2);
                break;
            }

            case 6: {
                ctx.fillStyle = C.rf3;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.rf5;
                ctx.globalAlpha = 0.25;
                for (let py = 0; py < 48; py += 2) {
                    ctx.fillRect(x, y + py, s, 1);
                }
                ctx.globalAlpha = 1;
                for (let r2 = 0; r2 < 5; r2++) {
                    const rOff = (r2 % 2) * 5;
                    for (let c2 = -1; c2 < 6; c2++) {
                        const tx2 = c2 * 10 + rOff;
                        const ty2 = r2 * 10;
                        if (tx2 < -8 || tx2 >= s) continue;
                        const sh2 = ((r2 + c2 + sd) & 3);
                        ctx.fillStyle = sh2 === 0 ? C.rf1 : sh2 === 1 ? C.rf2 : sh2 === 2 ? C.rf4 : C.rfm1;
                        const clx = Math.max(0, tx2);
                        const clw = Math.min(9, s - clx);
                        ctx.fillRect(x + clx, y + ty2, clw, 9);
                        ctx.fillStyle = C.rfh;
                        ctx.globalAlpha = 0.3;
                        ctx.fillRect(x + clx, y + ty2, clw, 2);
                        ctx.globalAlpha = 0.15;
                        ctx.fillRect(x + clx, y + ty2 + 2, clw, D);
                        ctx.globalAlpha = 1;
                        ctx.fillStyle = C.rfs;
                        ctx.fillRect(x + clx, y + ty2 + 7, clw, 2);
                        ctx.fillStyle = C.rf5;
                        ctx.fillRect(x + clx, y + ty2 + 9, clw, D);
                        if (sh2 === 3) {
                            ctx.fillStyle = C.rfm2;
                            ctx.fillRect(x + clx + 2, y + ty2 + 4, 2, D);
                            ctx.fillRect(x + clx + 4, y + ty2 + 5, D, D);
                        }
                        if (sh2 === 1 && clw > 5) {
                            ctx.fillStyle = C.rf7;
                            ctx.globalAlpha = 0.12;
                            ctx.fillRect(x + clx + 2, y + ty2 + 3, clw - 4, 3);
                            ctx.globalAlpha = 1;
                        }
                    }
                }
                ctx.fillStyle = C.rfl;
                ctx.fillRect(x, y + s - 2, s, 2);
                ctx.fillStyle = 'rgba(255,200,150,0.10)';
                ctx.fillRect(x, y, s, 4);
                break;
            }

            case 7: {
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.bkl;
                ctx.fillRect(x + 4, y + 1, 40, 3);
                ctx.fillRect(x + 4, y + 1, 3, 46);
                ctx.fillRect(x + 41, y + 1, 3, 46);
                ctx.fillStyle = C.bk4;
                ctx.fillRect(x + 4, y + 1, 40, D);
                ctx.fillRect(x + 4, y + 1, D, 46);
                ctx.fillStyle = C.bkl;
                ctx.fillRect(x + 43, y + 1, D, 46);
                ctx.fillRect(x + 4, y + 46, 40, D);
                ctx.fillStyle = C.dr3;
                ctx.fillRect(x + 7, y + 3, 34, 43);
                ctx.fillStyle = C.dr1;
                ctx.fillRect(x + 9, y + 5, 14, 18);
                ctx.fillRect(x + 25, y + 5, 14, 18);
                ctx.fillStyle = C.dr2;
                for (let i = 0; i < 9; i++) {
                    ctx.fillRect(x + 9, y + 6 + i * 2, 14, D);
                    ctx.fillRect(x + 25, y + 6 + i * 2, 14, D);
                }
                ctx.fillStyle = C.tk5;
                ctx.globalAlpha = 0.08;
                for (let i = 0; i < 5; i++) {
                    const kx = (sd * 3 + i * 11) % 10 + 10;
                    ctx.fillRect(x + kx, y + 6, D, 16);
                    ctx.fillRect(x + kx + 16, y + 6, D, 16);
                }
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.dr4;
                for (let i = 0; i < 9; i++) {
                    ctx.fillRect(x + 9, y + 25 + i * 2, 14, D);
                    ctx.fillRect(x + 25, y + 25 + i * 2, 14, D);
                }
                ctx.fillStyle = C.drh;
                ctx.globalAlpha = 0.25;
                ctx.fillRect(x + 9, y + 5, 30, 2);
                ctx.globalAlpha = 0.12;
                ctx.fillRect(x + 9, y + 7, 30, D);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.drf;
                ctx.fillRect(x + 23, y + 3, 2, 43);
                ctx.fillRect(x + 9, y + 24, 30, 2);
                ctx.fillStyle = C.dr5;
                ctx.fillRect(x + 9, y + 24, 30, D);
                ctx.fillStyle = C.mtl2;
                ctx.fillRect(x + 7, y + 8, 2, 7);
                ctx.fillRect(x + 7, y + 28, 2, 7);
                ctx.fillStyle = C.mtlh;
                ctx.fillRect(x + 7, y + 8, D, D);
                ctx.fillRect(x + 7, y + 28, D, D);
                ctx.fillStyle = C.mtl3;
                ctx.fillRect(x + 8, y + 14, D, D);
                ctx.fillRect(x + 8, y + 34, D, D);
                ctx.fillStyle = C.mtl4;
                ctx.fillRect(x + 7, y + 9, 2, 5);
                ctx.fillRect(x + 7, y + 29, 2, 5);
                ctx.fillStyle = C.drk;
                ctx.fillRect(x + 30, y + 26, 5, 6);
                ctx.fillStyle = '#d4b030';
                ctx.fillRect(x + 31, y + 27, 3, 4);
                ctx.fillStyle = C.mtlh;
                ctx.globalAlpha = 0.5;
                ctx.fillRect(x + 31, y + 27, 2, 2);
                ctx.globalAlpha = 0.25;
                ctx.fillRect(x + 32, y + 28, D, D);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.bk5;
                ctx.fillRect(x + 7, y + 45, 34, 3);
                ctx.fillStyle = 'rgba(0,0,0,0.22)';
                ctx.fillRect(x + 7, y + 44, 34, 2);
                ctx.fillStyle = 'rgba(0,0,0,0.10)';
                ctx.fillRect(x + 7, y + 42, 34, 2);
                ctx.fillStyle = C.dr1;
                ctx.fillRect(x + 9, y + 25, 14, 18);
                ctx.fillRect(x + 25, y + 25, 14, 18);
                ctx.fillStyle = C.dr2;
                for (let i = 0; i < 9; i++) {
                    ctx.fillRect(x + 9, y + 26 + i * 2, 14, D);
                    ctx.fillRect(x + 25, y + 26 + i * 2, 14, D);
                }
                break;
            }

            case 8: {
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.bk4;
                ctx.fillRect(x + 4, y + 2, 40, 40);
                ctx.fillStyle = C.bk6;
                ctx.fillRect(x + 4, y + 2, 40, 2);
                ctx.fillRect(x + 4, y + 2, 2, 40);
                ctx.fillStyle = C.bkl;
                ctx.fillRect(x + 42, y + 2, 2, 40);
                ctx.fillRect(x + 4, y + 40, 40, 2);
                ctx.fillStyle = C.bk9;
                ctx.globalAlpha = 0.2;
                ctx.fillRect(x + 5, y + 3, 38, D);
                ctx.fillRect(x + 5, y + 3, D, 37);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.w1;
                ctx.fillRect(x + 7, y + 5, 16, 16);
                ctx.fillRect(x + 25, y + 5, 16, 16);
                ctx.fillRect(x + 7, y + 23, 16, 16);
                ctx.fillRect(x + 25, y + 23, 16, 16);
                ctx.fillStyle = C.w2;
                ctx.globalAlpha = 0.4;
                ctx.fillRect(x + 9, y + 7, 12, 12);
                ctx.fillRect(x + 27, y + 7, 12, 12);
                ctx.fillRect(x + 9, y + 25, 12, 12);
                ctx.fillRect(x + 27, y + 25, 12, 12);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.35;
                ctx.fillRect(x + 30, y + 7, 6, D);
                ctx.fillRect(x + 32, y + 8, 4, D);
                ctx.fillRect(x + 34, y + 9, 2, D);
                ctx.fillRect(x + 12, y + 25, 5, D);
                ctx.fillRect(x + 14, y + 26, 3, D);
                ctx.globalAlpha = 0.15;
                ctx.fillRect(x + 10, y + 8, D, D);
                ctx.fillRect(x + 35, y + 28, D, D);
                ctx.fillRect(x + 28, y + 13, D, D);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#c06030';
                ctx.globalAlpha = 0.12;
                ctx.fillRect(x + 8, y + 10, 14, 10);
                ctx.fillRect(x + 26, y + 12, 14, 8);
                ctx.fillRect(x + 8, y + 28, 14, 10);
                ctx.fillRect(x + 26, y + 28, 14, 10);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x + 23, y + 5, 2, 34);
                ctx.fillRect(x + 7, y + 21, 34, 2);
                ctx.fillStyle = C.bk4;
                ctx.fillRect(x + 4, y + 42, 40, 6);
                ctx.fillStyle = C.bk6;
                ctx.fillRect(x + 4, y + 42, 40, D);
                ctx.fillStyle = 'rgba(0,0,0,0.15)';
                ctx.fillRect(x + 4, y + 46, 40, 2);
                break;
            }

            case 9: {
                const sway = Math.sin(t / 1200 + sd * 0.5) * 1.5;
                const tw = 16;
                const tl = x + (s - tw) / 2;
                ctx.fillStyle = C.tk2;
                ctx.fillRect(tl + 2, y + 22, tw - 4, 26);
                ctx.fillRect(tl, y + 38, tw, 10);
                ctx.fillRect(tl - 2, y + 42, tw + 4, 6);
                ctx.fillStyle = C.tk3;
                ctx.fillRect(tl + 2, y + 22, 3, 26);
                ctx.fillStyle = C.tkh;
                ctx.fillRect(tl + 2, y + 22, 2, 26);
                ctx.fillStyle = C.tk1;
                ctx.fillRect(tl + tw - 5, y + 22, 3, 26);
                ctx.fillStyle = C.tkg;
                ctx.fillRect(tl + tw - 4, y + 22, 2, 26);
                ctx.fillStyle = C.tk6;
                ctx.globalAlpha = 0.12;
                for (let i = 0; i < 4; i++) {
                    ctx.fillRect(tl + 4 + i * 3, y + 23, D, 24);
                }
                ctx.globalAlpha = 0.08;
                ctx.fillStyle = C.tk5;
                ctx.fillRect(tl + 2, y + 28, tw - 4, 2);
                ctx.fillRect(tl + 2, y + 36, tw - 4, 2);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.rkd;
                ctx.beginPath();
                ctx.ellipse(tl + 8, y + 33, 3, 2, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.rk3;
                ctx.beginPath();
                ctx.ellipse(tl + 8, y + 33, 2, 1.5, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.tk1;
                ctx.fillRect(tl - 2, y + 42, 4, 5);
                ctx.fillRect(tl + tw - 2, y + 42, 4, 5);
                ctx.fillRect(tl + 5, y + 44, 6, 4);
                ctx.fillStyle = C.tk2;
                ctx.fillRect(tl - 1, y + 43, 3, 3);
                ctx.fillRect(tl + tw - 1, y + 43, 3, 3);
                ctx.fillStyle = 'rgba(0,0,0,0.12)';
                ctx.fillRect(tl - 2, y + 46, tw + 4, 2);
                const cx2 = tl + tw / 2 + sway;
                const cy2 = y + 14;
                const layers = [
                    { c: C.trc, rx: 24, ry: 16 },
                    { c: C.g7, rx: 22, ry: 14 },
                    { c: C.g6, rx: 19, ry: 12 },
                    { c: C.g2, rx: 16, ry: 10 },
                    { c: C.g3, rx: 13, ry: 8 },
                    { c: C.g4, rx: 9, ry: 6 },
                    { c: C.g11, rx: 6, ry: 4 }
                ];
                for (const l of layers) {
                    ctx.fillStyle = l.c;
                    ctx.beginPath();
                    ctx.ellipse(cx2, cy2, l.rx, l.ry, 0, 0, Math.PI * 2);
                    ctx.fill();
                }
                const bumps = [
                    { a: 0, dr: 4 }, { a: 0.8, dr: 3 }, { a: 1.6, dr: 5 },
                    { a: 2.4, dr: 3 }, { a: 3.2, dr: 4 }, { a: 4.0, dr: 3 },
                    { a: 4.8, dr: 5 }, { a: 5.6, dr: 3 }
                ];
                for (const b of bumps) {
                    const bx2 = cx2 + Math.cos(b.a) * 22;
                    const by2 = cy2 + Math.sin(b.a) * 14;
                    ctx.fillStyle = (b.dr > 3) ? C.g7 : C.trc;
                    ctx.beginPath();
                    ctx.ellipse(bx2, by2, b.dr + 1, b.dr, 0, 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.fillStyle = C.g12;
                ctx.globalAlpha = 0.6;
                ctx.beginPath();
                ctx.ellipse(cx2 - 5, cy2 - 4, 5, 3, -0.3, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(cx2 + 6, cy2 - 2, 4, 2.5, 0.2, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.trd;
                ctx.globalAlpha = 0.5;
                ctx.beginPath();
                ctx.ellipse(cx2 + 3, cy2 + 5, 4, 3, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(cx2 - 7, cy2 + 3, 3, 2, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.mv2;
                ctx.globalAlpha = 0.6;
                ctx.fillRect(cx2 - 8, cy2 + 12, D, 4);
                ctx.fillRect(cx2 - 9, cy2 + 13, D, 3);
                ctx.fillRect(cx2 + 7, cy2 + 11, D, 5);
                ctx.fillRect(cx2 + 8, cy2 + 12, D, 3);
                ctx.globalAlpha = 1;
                ctx.fillStyle = 'rgba(0,0,0,0.12)';
                ctx.fillRect(tl + 2, y + 22, tw - 4, 4);
                break;
            }

            case 10: {
                ctx.fillStyle = C.g1;
                ctx.fillRect(x, y, s, s);
                ditherFast(x, y + 30, s, 18, C.g1, C.gsh3);
                ctx.fillStyle = C.g3;
                for (let i = 0; i < 5; i++) ctx.fillRect(x + ((sd * 3 + i * 37) % 44), y + ((sd * 7 + i * 41) % 6 + 38), D, 3);
                ctx.fillStyle = C.fl1;
                ctx.fillRect(x + 3, y + 3, 42, 30);
                ctx.fillStyle = C.fl2;
                ctx.fillRect(x + 5, y + 5, 38, 26);
                const ncs = [C.fl1, C.fl2, C.fl3, C.fl4];
                for (let fy = 0; fy < 3; fy++) {
                    for (let fx2 = 0; fx2 < 4; fx2++) {
                        const fc = ncs[(fy * 4 + fx2 + sd) % 4];
                        ctx.fillStyle = fc;
                        ctx.fillRect(x + 5 + fx2 * 10, y + 5 + fy * 9, 8, 8);
                        ctx.fillStyle = 'rgba(255,255,255,0.15)';
                        ctx.fillRect(x + 5 + fx2 * 10, y + 5 + fy * 9, 8, 2);
                        ctx.fillStyle = 'rgba(0,0,0,0.10)';
                        ctx.fillRect(x + 5 + fx2 * 10, y + 11 + fy * 9, 8, 2);
                    }
                }
                ctx.fillStyle = C.fl3;
                ctx.fillRect(x + 3, y + 3, 42, 2);
                ctx.fillRect(x + 3, y + 3, 2, 30);
                ctx.fillStyle = C.fl4;
                ctx.fillRect(x + 43, y + 3, 2, 30);
                ctx.fillRect(x + 3, y + 31, 42, 2);
                break;
            }

            case 11: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ditherFast(x, y + 32, s, 16, C.g1, C.gsh3);
                ctx.fillStyle = C.g3;
                for (let i = 0; i < 4; i++) ctx.fillRect(x + ((sd * 3 + i * 37) % 44), y + ((sd * 7 + i * 41) % 8 + 36), D, 3);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 3, y + 13, 42, 24);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 5, y + 15, 38, 20);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 7, y + 17, 34, 16);
                ctx.fillStyle = C.wd5;
                ctx.globalAlpha = 0.1;
                for (let py = 0; py < 16; py += 2) ctx.fillRect(x + 7, y + 17 + py, 34, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.12;
                ctx.fillRect(x + 5, y + 15, 38, 2);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 3, y + 13, 42, 2);
                ctx.fillRect(x + 3, y + 35, 42, 2);
                ctx.fillStyle = 'rgba(0,0,0,0.10)';
                ctx.fillRect(x + 3, y + 36, 42, 2);
                break;
            }

            case 12: {
                ctx.fillStyle = C.st1;
                ctx.fillRect(x, y, s, s);
                dither(x, y, s, s, C.st1, C.st2);
                ctx.fillStyle = C.stm1;
                ctx.globalAlpha = 0.15;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.st6;
                ctx.fillRect(x + 16, y + 16, 16, 16);
                ctx.fillStyle = C.st7;
                ctx.fillRect(x + 18, y + 18, 12, 12);
                ctx.fillStyle = C.st3;
                ctx.fillRect(x + 20, y + 20, 8, 8);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.15;
                ctx.fillRect(x + 20, y + 20, 8, 2);
                ctx.globalAlpha = 1;
                break;
            }

            case 13: {
                ditherFast(x, y, s, s, C.p1, C.p5);
                ctx.fillStyle = C.p3;
                ctx.globalAlpha = 0.15;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.rk2;
                ctx.fillRect(x + 8, y + 8, 32, 36);
                ctx.fillStyle = C.rk1;
                ctx.fillRect(x + 10, y + 10, 28, 32);
                ctx.fillStyle = C.rk4;
                ctx.globalAlpha = 0.3;
                ctx.fillRect(x + 12, y + 12, 24, 4);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.rkd;
                ctx.fillRect(x + 12, y + 38, 24, 4);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 12, y + 16, 24, 22);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 14, y + 18, 20, 18);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 14, y + 20, 20, 14);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.1;
                ctx.fillRect(x + 14, y + 18, 20, 2);
                ctx.globalAlpha = 1;
                break;
            }

            case 14: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.p5;
                ctx.globalAlpha = 0.2;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.rk2;
                ctx.fillRect(x + 3, y + 10, 42, 34);
                ctx.fillStyle = C.rk1;
                ctx.fillRect(x + 5, y + 12, 38, 30);
                ctx.fillStyle = C.rk4;
                ctx.globalAlpha = 0.2;
                ctx.fillRect(x + 5, y + 12, 38, 3);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#ffeedd';
                ctx.fillRect(x + 7, y + 16, 34, 24);
                ctx.fillStyle = '#fff8f0';
                ctx.fillRect(x + 9, y + 18, 30, 20);
                ctx.fillStyle = 'rgba(0,0,0,0.06)';
                for (let py = 0; py < 20; py += 2) ctx.fillRect(x + 9, y + 18 + py, 30, 1);
                ctx.fillStyle = C.rk3;
                ctx.fillRect(x + 7, y + 38, 34, 4);
                ctx.fillStyle = '#d0c0a0';
                ctx.fillRect(x + 14, y + 20, 20, 16);
                ctx.fillStyle = '#b0a080';
                ctx.fillRect(x + 14, y + 20, 20, 2);
                ctx.fillRect(x + 14, y + 34, 20, 2);
                ctx.fillRect(x + 14, y + 20, 2, 16);
                ctx.fillRect(x + 32, y + 20, 2, 16);
                break;
            }

            case 15: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.p5;
                ctx.globalAlpha = 0.2;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.g3;
                ctx.fillRect(x + 8, y + 8, 14, 16);
                ctx.fillStyle = C.g4;
                ctx.fillRect(x + 10, y + 10, 10, 12);
                ctx.fillStyle = C.g1;
                ctx.fillRect(x + 12, y + 12, 6, 8);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.15;
                ctx.fillRect(x + 12, y + 12, 6, 2);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.g3;
                ctx.fillRect(x + 28, y + 22, 14, 16);
                ctx.fillStyle = C.g4;
                ctx.fillRect(x + 30, y + 24, 10, 12);
                ctx.fillStyle = C.g1;
                ctx.fillRect(x + 32, y + 26, 6, 8);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.15;
                ctx.fillRect(x + 32, y + 26, 6, 2);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.rk2;
                ctx.fillRect(x + 30, y + 6, 12, 12);
                ctx.fillStyle = C.rk4;
                ctx.fillRect(x + 32, y + 8, 8, 8);
                ctx.fillStyle = C.rkh;
                ctx.globalAlpha = 0.2;
                ctx.fillRect(x + 32, y + 8, 8, 2);
                ctx.globalAlpha = 1;
                break;
            }

            case 16: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.p5;
                ctx.globalAlpha = 0.2;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.rk2;
                ctx.fillRect(x + 6, y + 20, 36, 24);
                ctx.fillStyle = C.rk1;
                ctx.fillRect(x + 8, y + 22, 32, 20);
                ctx.fillStyle = C.rk4;
                ctx.globalAlpha = 0.2;
                ctx.fillRect(x + 8, y + 22, 32, 3);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 10, y + 25, 28, 12);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 12, y + 27, 24, 8);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.1;
                ctx.fillRect(x + 12, y + 27, 24, 2);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 10, y + 37, 28, 3);
                ctx.fillRect(x + 22, y + 25, 2, 12);
                ctx.fillStyle = C.rk3;
                ctx.fillRect(x + 8, y + 40, 32, 4);
                break;
            }

            case 17: {
                const pt = t / 800;
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.p5;
                ctx.globalAlpha = 0.2;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.rk2;
                ctx.fillRect(x + 10, y + 12, 28, 28);
                ctx.fillStyle = C.rk1;
                ctx.fillRect(x + 12, y + 14, 24, 24);
                ctx.fillStyle = C.rk4;
                ctx.globalAlpha = 0.2;
                ctx.fillRect(x + 12, y + 14, 24, 3);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.pt4;
                ctx.globalAlpha = 0.45 + Math.sin(pt * 2.5) * 0.3;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + 24, 9, 9, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.ptg;
                ctx.globalAlpha = 0.6 + Math.sin(pt * 3) * 0.3;
                ctx.fillRect(x + 20, y + 20, 8, 8);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.35 + Math.sin(pt * 4) * 0.25;
                ctx.fillRect(x + 22, y + 22, 3, 3);
                ctx.globalAlpha = 0.2 + Math.sin(pt * 5) * 0.15;
                ctx.fillRect(x + 21, y + 21, D, D);
                ctx.globalAlpha = 1;
                break;
            }

            case 18: {
                ctx.fillStyle = C.st2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.stm1;
                ctx.globalAlpha = 0.2;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.st3;
                ctx.fillRect(x + 4, y + 17, 40, 29);
                ctx.fillStyle = C.st7;
                ctx.fillRect(x + 6, y + 17, 36, 2);
                ctx.fillStyle = C.st1;
                ctx.fillRect(x + 6, y + 19, 36, 25);
                ctx.fillStyle = C.w1;
                ctx.fillRect(x + 8, y + 21, 32, 21);
                const ft = t / 400;
                ctx.fillStyle = C.w2;
                ctx.fillRect(x + 11, y + 23 + Math.sin(ft) * 2, 12, 2);
                ctx.fillRect(x + 27, y + 27 + Math.cos(ft) * 2, 10, 2);
                ctx.fillStyle = C.w4;
                ctx.fillRect(x + 15, y + 30 + Math.sin(ft * 0.7) * 2, 8, D);
                ctx.fillStyle = C.w10;
                ctx.globalAlpha = 0.2;
                ctx.fillRect(x + 12, y + 25, 24, 12);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.st3;
                ctx.fillRect(x + 19, y + 17, 10, 25);
                ctx.fillStyle = C.st4;
                ctx.fillRect(x + 19, y + 7, 10, 12);
                ctx.fillRect(x + 16, y + 10, 16, 2);
                ctx.fillStyle = C.wf;
                const sprayH = 5 + Math.sin(ft * 1.5) * 3;
                ctx.globalAlpha = 0.5 + Math.sin(ft * 2) * 0.2;
                ctx.fillRect(x + 20, y + 7 - sprayH, 8, sprayH);
                ctx.globalAlpha = 0.25;
                ctx.fillRect(x + 17, y + 9 - sprayH * 0.5, 3, sprayH * 0.3);
                ctx.fillRect(x + 28, y + 9 - sprayH * 0.5, 3, sprayH * 0.3);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wsp;
                ctx.globalAlpha = 0.5 + Math.sin(ft * 3) * 0.3;
                ctx.fillRect(x + 22, y + 5 - sprayH * 0.4, 3, 2);
                ctx.globalAlpha = 0.3 + Math.sin(ft * 4) * 0.2;
                ctx.fillRect(x + 19, y + 6 - sprayH * 0.3, 2, D);
                ctx.fillRect(x + 27, y + 6 - sprayH * 0.3, 2, D);
                ctx.globalAlpha = 1;
                break;
            }

            case 19: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.p5;
                ctx.globalAlpha = 0.2;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.mtl4;
                ctx.fillRect(x + 20, y + 11, 8, 37);
                ctx.fillStyle = C.mtl3;
                ctx.fillRect(x + 21, y + 13, 6, 33);
                ctx.fillStyle = C.mtl2;
                ctx.fillRect(x + 21, y + 14, 3, 31);
                ctx.fillStyle = C.mtlh;
                ctx.globalAlpha = 0.15;
                ctx.fillRect(x + 22, y + 15, D, 28);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.mtl4;
                ctx.fillRect(x + 14, y + 42, 20, 6);
                ctx.fillRect(x + 16, y + 40, 16, 2);
                ctx.fillStyle = C.mtl2;
                ctx.fillRect(x + 14, y + 42, 20, 2);
                ctx.fillStyle = C.mtl3;
                ctx.fillRect(x + 16, y + 7, 16, 7);
                ctx.fillRect(x + 14, y + 9, 20, 3);
                ctx.fillStyle = C.mtl1;
                ctx.fillRect(x + 17, y + 8, 14, D);
                const lg = 0.5 + Math.sin(t / 1000 + sd) * 0.25;
                const lg2 = 0.5 + Math.sin(t / 700 + sd + 2) * 0.2;
                ctx.fillStyle = C.lpo;
                ctx.globalAlpha = lg;
                ctx.fillRect(x + 14, y + 1, 20, 10);
                ctx.fillStyle = C.lp;
                ctx.fillRect(x + 16, y + 2, 16, 8);
                ctx.fillStyle = C.lpg;
                ctx.globalAlpha = lg2;
                ctx.fillRect(x + 19, y + 3, 10, 5);
                ctx.globalAlpha = lg * 0.12;
                ctx.fillStyle = C.lpw;
                ctx.beginPath();
                ctx.arc(x + 24, y + 7, 22, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = lg * 0.05;
                ctx.beginPath();
                ctx.arc(x + 24, y + 7, 34, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
                break;
            }

            case 20: {
                ctx.fillStyle = C.p1;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.p5;
                ctx.globalAlpha = 0.2;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 1, y + 19, 4, 29);
                ctx.fillRect(x + 43, y + 19, 4, 29);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 1, y + 19, 46, 27);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 3, y + 21, 42, 23);
                ctx.fillStyle = C.wd5;
                ctx.globalAlpha = 0.12;
                for (let py = 0; py < 23; py += 2) ctx.fillRect(x + 3, y + 21 + py, 42, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.1;
                ctx.fillRect(x + 3, y + 21, 42, 2);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 3, y + 31, 42, 2);
                ctx.fillStyle = C.mk;
                ctx.fillRect(x + 1, y + 1, 46, 18);
                ctx.fillStyle = C.mkd;
                ctx.fillRect(x + 1, y + 13, 46, 6);
                for (let i = 0; i < 7; i++) {
                    ctx.fillStyle = (i & 1) ? C.mk : C.mkd;
                    ctx.fillRect(x + 1 + i * 7, y + 17, 6, 2);
                }
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.10;
                ctx.fillRect(x + 3, y + 3, 42, 2);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.fy;
                ctx.fillRect(x + 7, y + 23, 7, 7);
                ctx.fillRect(x + 7, y + 35, 9, 7);
                ctx.fillStyle = C.fr;
                ctx.fillRect(x + 19, y + 23, 7, 7);
                ctx.fillStyle = C.fo;
                ctx.fillRect(x + 30, y + 25, 7, 7);
                ctx.fillStyle = C.mkc;
                ctx.fillRect(x + 30, y + 35, 11, 7);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.10;
                ctx.fillRect(x + 7, y + 23, 7, 2);
                ctx.fillRect(x + 19, y + 23, 7, 2);
                ctx.fillRect(x + 30, y + 25, 7, 2);
                ctx.globalAlpha = 1;
                break;
            }

            case 21: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.g8;
                ctx.globalAlpha = 0.3;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.g3;
                for (let i = 0; i < 4; i++) ctx.fillRect(x + ((sd * 3 + i * 37) % 44), y + ((sd * 7 + i * 41) % 8 + 36), D, 3);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 7, y + 29, 6, 18);
                ctx.fillRect(x + 35, y + 29, 6, 18);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 4, y + 19, 40, 12);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 6, y + 13, 36, 8);
                ctx.fillRect(x + 6, y + 25, 36, 5);
                ctx.fillStyle = C.wd5;
                ctx.globalAlpha = 0.1;
                for (let py = 0; py < 18; py += 2) ctx.fillRect(x + 6, y + 13 + py, 36, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.12;
                ctx.fillRect(x + 6, y + 13, 36, 2);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 6, y + 17, 36, D);
                ctx.fillRect(x + 6, y + 21, 36, D);
                ctx.fillRect(x + 6, y + 25, 36, D);
                ctx.fillRect(x + 14, y + 19, D, 11);
                ctx.fillRect(x + 24, y + 19, D, 11);
                ctx.fillRect(x + 34, y + 19, D, 11);
                ctx.fillStyle = C.wd7;
                ctx.globalAlpha = 0.12;
                ctx.fillRect(x + 6, y + 13, 36, 2);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.bns;
                ctx.fillRect(x + 7, y + 29, 3, 6);
                ctx.fillRect(x + 38, y + 29, 3, 6);
                ctx.fillStyle = 'rgba(0,0,0,0.12)';
                ctx.fillRect(x + 7, y + 44, 34, 3);
                break;
            }

            case 22: {
                ctx.fillStyle = ((sd + row) & 1) ? C.g1 : C.g2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.g3;
                for (let i = 0; i < 4; i++) ctx.fillRect(x + ((sd * 5 + i * 31) % 44), y + 40 + (i & 3), D, 3);
                ctx.fillStyle = C.st3;
                ctx.fillRect(x + 7, y + 19, 34, 27);
                ctx.fillStyle = C.st7;
                ctx.fillRect(x + 9, y + 19, 30, 2);
                ctx.fillStyle = C.st1;
                ctx.fillRect(x + 9, y + 21, 30, 23);
                ctx.fillStyle = C.w1;
                ctx.fillRect(x + 13, y + 25, 22, 17);
                ctx.fillStyle = C.w2;
                ctx.globalAlpha = 0.5;
                ctx.fillRect(x + 16, y + 29, 12, 8);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wsp;
                ctx.globalAlpha = 0.3;
                ctx.fillRect(x + 17, y + 27, 2, 2);
                ctx.globalAlpha = 0.2;
                ctx.fillRect(x + 28, y + 30, D, D);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 9, y + 4, 30, 6);
                ctx.fillRect(x + 19, y + 4, 10, 18);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 9, y + 4, 30, 2);
                ctx.fillStyle = C.mtl2;
                ctx.fillRect(x + 22, y + 9, 3, 14);
                ctx.fillStyle = C.mtlh;
                ctx.fillRect(x + 22, y + 9, D, D);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 19, y + 21, 10, 4);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 7, y + 9, 3, 6);
                ctx.fillRect(x + 38, y + 9, 3, 6);
                ctx.fillStyle = C.st6;
                ctx.fillRect(x + 15, y + 13, 16, 5);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.08;
                ctx.fillRect(x + 15, y + 13, 16, 2);
                ctx.globalAlpha = 1;
                break;
            }

            case 23: {
                ctx.fillStyle = C.st2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.stm1;
                ctx.globalAlpha = 0.2;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                const drawShelf = (sx, sy, sw, sh2) => {
                    ctx.fillStyle = C.wd3;
                    ctx.fillRect(x + sx, y + sy, sw, sh2);
                    ctx.fillStyle = C.wd1;
                    ctx.fillRect(x + sx, y + sy + 2, sw, sh2 - 4);
                    ctx.fillStyle = C.wd2;
                    ctx.fillRect(x + sx + 2, y + sy + 2, sw - 4, sh2 - 6);
                    ctx.fillStyle = C.wd3;
                    ctx.fillRect(x + sx, y + sy, sw, 2);
                    ctx.fillRect(x + sx, y + sy + sh2 - 2, sw, 2);
                    ctx.fillStyle = C.wd7;
                    ctx.globalAlpha = 0.1;
                    ctx.fillRect(x + sx, y + sy, sw, D);
                    ctx.globalAlpha = 1;
                };
                drawShelf(1, 7, 22, 16);
                drawShelf(1, 23, 22, 22);
                drawShelf(25, 13, 20, 24);
                ctx.fillStyle = C.mtl3;
                ctx.fillRect(x + 8, y + 11, D, D);
                ctx.fillRect(x + 16, y + 28, D, D);
                ctx.fillRect(x + 34, y + 19, D, D);
                ctx.fillRect(x + 30, y + 30, D, D);
                ctx.fillStyle = C.mtlh;
                ctx.globalAlpha = 0.3;
                ctx.fillRect(x + 8, y + 11, D, D);
                ctx.fillRect(x + 34, y + 19, D, D);
                ctx.globalAlpha = 1;
                break;
            }

            case 24: {
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.bkm1;
                ctx.globalAlpha = 0.2;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.fp2;
                ctx.fillRect(x + 3, y + 15, 42, 33);
                ctx.fillStyle = C.fp3;
                ctx.fillRect(x + 5, y + 17, 38, 29);
                ctx.fillStyle = C.fp1;
                ctx.fillRect(x + 3, y + 15, 42, 3);
                ctx.fillRect(x + 1, y + 12, 46, 3);
                ctx.fillStyle = C.fp4;
                ctx.fillRect(x + 1, y + 12, 46, D);
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x + 1, y + 12, 4, 36);
                ctx.fillRect(x + 43, y + 12, 4, 36);
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x + 13, y + 7, 22, 6);
                ctx.fillRect(x + 15, y + 3, 18, 4);
                const flk1 = 0.6 + Math.sin(t / 150 + sd * 3) * 0.35;
                const flk2 = 0.6 + Math.sin(t / 200 + sd * 5 + 1) * 0.3;
                const flk3 = 0.7 + Math.sin(t / 180 + sd * 7 + 2) * 0.25;
                ctx.fillStyle = C.fph;
                ctx.globalAlpha = flk1;
                ctx.fillRect(x + 9, y + 29, 12, 13);
                ctx.fillRect(x + 25, y + 31, 12, 11);
                ctx.fillStyle = C.fpf;
                ctx.globalAlpha = flk2;
                ctx.fillRect(x + 13, y + 25, 10, 11);
                ctx.fillRect(x + 27, y + 27, 10, 9);
                ctx.fillRect(x + 19, y + 29, 10, 11);
                ctx.fillStyle = C.fpb;
                ctx.globalAlpha = flk3;
                ctx.fillRect(x + 15, y + 23, 16, 4);
                ctx.fillRect(x + 19, y + 21, 10, 4);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = flk1 * 0.45;
                ctx.fillRect(x + 20, y + 25, 4, 2);
                ctx.globalAlpha = flk2 * 0.2;
                ctx.fillRect(x + 16, y + 23, 2, D);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.fp5;
                ctx.globalAlpha = flk2 * 0.15;
                ctx.fillRect(x + 5, y + 17, 38, 10);
                ctx.globalAlpha = 1;
                break;
            }

            case 25: {
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.bkm1;
                ctx.globalAlpha = 0.15;
                for (let py = 0; py < 48; py += 2) ctx.fillRect(x, y + py, s, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 3, y + 1, 42, 46);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 5, y + 3, 38, 42);
                ctx.fillStyle = C.wd5;
                ctx.globalAlpha = 0.1;
                for (let py = 0; py < 42; py += 2) ctx.fillRect(x + 5, y + 3 + py, 38, 1);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 5, y + 3, 38, 2);
                ctx.fillRect(x + 5, y + 15, 38, 2);
                ctx.fillRect(x + 5, y + 27, 38, 2);
                ctx.fillRect(x + 5, y + 39, 38, 2);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 3, y + 1, 2, 46);
                ctx.fillRect(x + 43, y + 1, 2, 46);
                ctx.fillStyle = C.wd7;
                ctx.globalAlpha = 0.12;
                ctx.fillRect(x + 5, y + 3, 38, D);
                ctx.fillRect(x + 5, y + 15, 38, D);
                ctx.fillRect(x + 5, y + 27, 38, D);
                ctx.globalAlpha = 1;
                const books = [
                    {bx:5,w:5,h:10,c:'#8b2020'},{bx:10,w:4,h:10,c:'#204080'},{bx:14,w:5,h:10,c:'#208040'},
                    {bx:19,w:5,h:9,c:'#a06020'},{bx:24,w:4,h:8,c:'#602080'},{bx:28,w:5,h:10,c:'#c08020'},
                    {bx:33,w:4,h:9,c:'#306050'},{bx:37,w:4,h:10,c:'#903030'},
                    {bx:5,w:4,h:10,c:'#306090'},{bx:9,w:4,h:8,c:'#a03030'},{bx:13,w:5,h:10,c:'#409040'},
                    {bx:18,w:5,h:9,c:'#704020'},{bx:23,w:4,h:10,c:'#5020a0'},{bx:27,w:6,h:10,c:'#c04040'},
                    {bx:33,w:4,h:9,c:'#2080a0'},{bx:37,w:4,h:10,c:'#806020'},
                    {bx:5,w:5,h:10,c:'#a04040'},{bx:10,w:5,h:10,c:'#30a060'},{bx:15,w:5,h:9,c:'#806020'},
                    {bx:20,w:4,h:8,c:'#5020a0'},{bx:24,w:6,h:10,c:'#c04040'},{bx:30,w:4,h:10,c:'#2080a0'},
                    {bx:34,w:4,h:9,c:'#604040'},{bx:38,w:3,h:10,c:'#208060'}
                ];
                const shelves = [5, 17, 29];
                shelves.forEach((sy2, si) => {
                    for (let bi = si * 8; bi < si * 8 + 8 && bi < books.length; bi++) {
                        const b = books[bi];
                        ctx.fillStyle = b.c;
                        ctx.fillRect(x + b.bx, y + sy2 + (12 - b.h), b.w, b.h);
                        ctx.fillStyle = 'rgba(255,255,255,0.20)';
                        ctx.fillRect(x + b.bx, y + sy2 + (12 - b.h), b.w, D);
                        ctx.fillStyle = 'rgba(0,0,0,0.14)';
                        ctx.fillRect(x + b.bx, y + sy2 + 12 - 1, b.w, D);
                        if (b.w > 3) {
                            ctx.fillStyle = 'rgba(255,220,150,0.25)';
                            ctx.fillRect(x + b.bx + 1, y + sy2 + (12 - b.h) + 2, D, b.h - 3);
                        }
                        ctx.fillStyle = 'rgba(0,0,0,0.08)';
                        ctx.fillRect(x + b.bx + b.w - 1, y + sy2 + (12 - b.h), D, b.h);
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
        const D = 1;
        const isHero = type === 'hero';
        const pal = isHero ? {
            hair: '#3a2518', hairHL: '#6a5040', hairDk: '#1a0808', hairMd: '#4a3020', hairTip: '#8a6848',
            skin: '#f4d0a0', skinHL: '#ffe8c8', skinSh: '#d8a870', skinDk: '#c09060', skinRim: '#e8c090',
            eyeW: '#f0f0ff', eye: '#1830a0', eyeHL: '#4060d0', pupil: '#080830', eyeLash: '#201018',
            mouth: '#c07050', cheek: '#e8b090', nose: '#d8b080',
            tunic: '#2848c0', tunicHL: '#5878e8', tunicMd: '#3858d0', tunicDk: '#182878', tunicSh: '#101850',
            tunicTrim: '#c0b060', tunicTrimDk: '#908030',
            collar: '#e8e0d0', collarSh: '#c0b898',
            belt: '#d8a830', beltBk: '#b08020', beltHL: '#f0c848',
            pants: '#384898', pantsDk: '#283068', pantsHL: '#5060b0', pantsSeam: '#202858',
            boots: '#503020', bootsHL: '#785838', bootsDk: '#2a1408', bootsSh: '#402818', bootsCuff: '#685030', bootsSole: '#201008',
            cape: '#c82828', capeMd: '#a82020', capeDk: '#681010', capeHL: '#e84848', capeEdge: '#500808',
            glove: '#e8d8b8', gloveSh: '#c8b890', gloveCuff: '#b8a870',
            shoulder: '#3050d0', shoulderHL: '#5070e8',
            outline: '#100818', outlineHL: '#282838',
            weapon: '#a0a8b8', weaponHL: '#d0d8e0', weaponDk: '#606878'
        } : getNPCPal(color, spriteId);

        const bob = moving ? Math.sin(frame * Math.PI / 2) * 2.0 : 0;
        const breathe = !moving ? Math.sin(gt / 700) * 0.8 : 0;
        const wc = moving ? frame % 4 : 0;
        const legL = wc === 1 ? 4 : wc === 3 ? -3 : 0;
        const legR = wc === 1 ? -3 : wc === 3 ? 4 : 0;
        const armL = moving ? Math.sin(frame * Math.PI / 2) * 5 : 0;
        const armR = moving ? -Math.sin(frame * Math.PI / 2) * 5 : 0;
        const by = Math.round(-bob + breathe);
        const hasHat = !isHero && ((spriteId || 0) % 3 === 0);
        const hasApron = !isHero && ((spriteId || 0) % 4 === 0);

        switch(facing) {
            case 'down': {
                ctx.fillStyle = pal.outline;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + by + 8, 15, 13, 0, 0, Math.PI * 2);
                ctx.fill();
                if (hasHat) {
                    ctx.fillStyle = pal.hat || pal.hair;
                    ctx.beginPath();
                    ctx.ellipse(x + 24, y + by + 2, 17, 8, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hatHL || pal.hairHL;
                    ctx.beginPath();
                    ctx.ellipse(x + 22, y + by + 1, 12, 5, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hatDk || pal.hairDk;
                    ctx.fillRect(x + 8, y + by + 4, 32, 3);
                    ctx.fillStyle = pal.hatMd || pal.hat || pal.hair;
                    ctx.fillRect(x + 12, y + by + 2, 24, 2);
                } else {
                    ctx.fillStyle = pal.hairDk || pal.hair;
                    ctx.beginPath();
                    ctx.ellipse(x + 24, y + by + 3, 15, 10, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hair;
                    ctx.beginPath();
                    ctx.ellipse(x + 24, y + by + 5, 14, 9, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hairHL;
                    ctx.beginPath();
                    ctx.ellipse(x + 22, y + by + 3, 8, 5, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hairMd || pal.hair;
                    ctx.fillRect(x + 9, y + by + 8, 30, 4);
                    ctx.fillStyle = pal.hairTip || pal.hairHL;
                    ctx.fillRect(x + 18, y + by + 1, 4, 2);
                    ctx.fillRect(x + 24, y + by + 0, 3, 2);
                    if (isHero) {
                        ctx.fillStyle = pal.hair;
                        ctx.fillRect(x + 7, y + by + 2, 4, 8);
                        ctx.fillRect(x + 37, y + by + 2, 4, 8);
                        ctx.fillStyle = pal.hairDk || pal.hair;
                        ctx.fillRect(x + 13, y + by - 4, 3, 5);
                        ctx.fillRect(x + 20, y + by - 6, 3, 7);
                        ctx.fillRect(x + 28, y + by - 5, 3, 6);
                        ctx.fillRect(x + 34, y + by - 3, 3, 4);
                        ctx.fillStyle = pal.hairHL;
                        ctx.fillRect(x + 14, y + by - 3, D, 3);
                        ctx.fillRect(x + 21, y + by - 5, D, 4);
                        ctx.fillRect(x + 29, y + by - 4, D, 3);
                    }
                }
                ctx.fillStyle = pal.skin;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + by + 14, 12, 9, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = pal.skinHL || pal.skin;
                ctx.beginPath();
                ctx.ellipse(x + 22, y + by + 12, 7, 5, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = pal.skinSh;
                ctx.fillRect(x + 12, y + by + 18, 24, 3);
                ctx.fillStyle = pal.skinRim || pal.skinSh;
                ctx.fillRect(x + 14, y + by + 20, 20, D);
                ctx.fillStyle = pal.eyeW || '#f0f0ff';
                ctx.fillRect(x + 14, y + by + 12, 8, 5);
                ctx.fillRect(x + 26, y + by + 12, 8, 5);
                ctx.fillStyle = pal.outline;
                ctx.fillRect(x + 14, y + by + 11, 8, D);
                ctx.fillRect(x + 26, y + by + 11, 8, D);
                ctx.fillRect(x + 13, y + by + 12, D, 5);
                ctx.fillRect(x + 22, y + by + 12, D, 5);
                ctx.fillRect(x + 25, y + by + 12, D, 5);
                ctx.fillRect(x + 34, y + by + 12, D, 5);
                ctx.fillRect(x + 14, y + by + 17, 8, D);
                ctx.fillRect(x + 26, y + by + 17, 8, D);
                ctx.fillStyle = pal.eye;
                ctx.fillRect(x + 16, y + by + 13, 5, 4);
                ctx.fillRect(x + 28, y + by + 13, 5, 4);
                ctx.fillStyle = pal.eyeHL || '#4060d0';
                ctx.fillRect(x + 17, y + by + 13, 3, 2);
                ctx.fillRect(x + 29, y + by + 13, 3, 2);
                ctx.fillStyle = pal.pupil || '#080830';
                ctx.fillRect(x + 18, y + by + 14, 2, 3);
                ctx.fillRect(x + 30, y + by + 14, 2, 3);
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(x + 16, y + by + 13, D, D);
                ctx.fillRect(x + 28, y + by + 13, D, D);
                ctx.globalAlpha = 0.5;
                ctx.fillRect(x + 20, y + by + 15, D, D);
                ctx.fillRect(x + 32, y + by + 15, D, D);
                ctx.globalAlpha = 1;
                ctx.fillStyle = pal.eyeLash || pal.outline;
                ctx.fillRect(x + 14, y + by + 11, 2, D);
                ctx.fillRect(x + 20, y + by + 11, 2, D);
                ctx.fillRect(x + 26, y + by + 11, 2, D);
                ctx.fillRect(x + 32, y + by + 11, 2, D);
                ctx.fillStyle = pal.nose || pal.skinSh;
                ctx.fillRect(x + 22, y + by + 16, 4, 2);
                ctx.fillStyle = pal.skinDk || pal.skinSh;
                ctx.fillRect(x + 23, y + by + 17, 2, D);
                ctx.fillStyle = pal.mouth || pal.skinSh;
                ctx.fillRect(x + 21, y + by + 19, 6, D);
                ctx.fillStyle = pal.skinHL || pal.skin;
                ctx.fillRect(x + 22, y + by + 19, 4, D);
                if (pal.cheek) {
                    ctx.fillStyle = pal.cheek;
                    ctx.globalAlpha = 0.3;
                    ctx.beginPath();
                    ctx.ellipse(x + 14, y + by + 16, 3, 2, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.beginPath();
                    ctx.ellipse(x + 34, y + by + 16, 3, 2, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.globalAlpha = 1;
                }
                ctx.fillStyle = pal.outline;
                ctx.fillRect(x + 16, y + by + 20, 16, D);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(x + 12, y + by + 21, 24, 3);
                ctx.fillStyle = pal.collarSh || pal.tunic;
                ctx.fillRect(x + 16, y + by + 22, 16, 2);
                ctx.fillRect(x + 22, y + by + 21, 4, 3);
                ctx.fillStyle = pal.shoulder || pal.tunic;
                ctx.beginPath();
                ctx.ellipse(x + 10, y + by + 25, 5, 4, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(x + 38, y + by + 25, 5, 4, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = pal.shoulderHL || pal.tunicHL;
                ctx.fillRect(x + 8, y + by + 23, 5, 2);
                ctx.fillRect(x + 36, y + by + 23, 5, 2);
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(x + 10, y + by + 24, 28, 9);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(x + 12, y + by + 24, 12, 7);
                ctx.fillStyle = pal.tunicMd || pal.tunic;
                ctx.fillRect(x + 24, y + by + 24, 12, 7);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(x + 10, y + by + 31, 28, 2);
                ctx.fillStyle = pal.tunicSh || pal.tunicDk;
                ctx.fillRect(x + 23, y + by + 24, 2, 9);
                ctx.fillStyle = pal.tunicDk;
                for (let i = 0; i < 3; i++) ctx.fillRect(x + 14 + i * 4, y + by + 27, D, 4);
                ctx.fillRect(x + 16, y + by + 26, 6, D);
                ctx.fillRect(x + 28, y + by + 28, 4, D);
                ctx.fillStyle = pal.tunicTrim || pal.tunicHL;
                ctx.fillRect(x + 10, y + by + 31, 28, D);
                ctx.fillStyle = pal.tunicTrimDk || pal.tunicDk;
                ctx.fillRect(x + 10, y + by + 32, 28, D);
                if (hasApron) {
                    ctx.fillStyle = pal.apron || '#e0d0b0';
                    ctx.fillRect(x + 14, y + by + 28, 20, 7);
                    ctx.fillStyle = pal.apronSh || '#c0b090';
                    ctx.fillRect(x + 14, y + by + 33, 20, 2);
                    ctx.fillStyle = pal.apronHL || '#f0e0c0';
                    ctx.fillRect(x + 16, y + by + 28, 16, D);
                    ctx.fillStyle = pal.apron || '#e0d0b0';
                    ctx.fillRect(x + 22, y + by + 26, 4, 2);
                }
                ctx.fillStyle = pal.belt;
                ctx.fillRect(x + 10, y + by + 31, 28, 3);
                ctx.fillStyle = pal.beltHL || pal.belt;
                ctx.fillRect(x + 12, y + by + 31, 10, D);
                ctx.fillStyle = pal.beltBk;
                ctx.fillRect(x + 22, y + by + 31, 5, 3);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.5;
                ctx.fillRect(x + 23, y + by + 31, 2, D);
                ctx.globalAlpha = 0.25;
                ctx.fillRect(x + 24, y + by + 32, D, D);
                ctx.globalAlpha = 1;
                if (isHero) {
                    ctx.fillStyle = pal.weapon || '#a0a8b8';
                    ctx.fillRect(x + 6, y + by + 28, 3, 8);
                    ctx.fillStyle = pal.weaponHL || '#d0d8e0';
                    ctx.fillRect(x + 6, y + by + 28, D, 6);
                    ctx.fillStyle = pal.weaponDk || '#606878';
                    ctx.fillRect(x + 8, y + by + 29, D, 6);
                    ctx.fillStyle = '#c0a040';
                    ctx.fillRect(x + 5, y + by + 28, 5, 2);
                    ctx.fillStyle = '#e0c060';
                    ctx.fillRect(x + 6, y + by + 28, 3, D);
                }
                ctx.fillStyle = pal.glove || pal.skin;
                const laX = Math.round(5 + armL * 1.3);
                const raX = Math.round(37 + armR * 1.3);
                ctx.fillRect(x + laX, y + by + 24, 6, 10);
                ctx.fillRect(x + raX, y + by + 24, 6, 10);
                ctx.fillStyle = pal.gloveCuff || pal.gloveSh || pal.skinSh;
                ctx.fillRect(x + laX, y + by + 24, 6, 2);
                ctx.fillRect(x + raX, y + by + 24, 6, 2);
                ctx.fillStyle = pal.gloveSh || pal.skinSh;
                ctx.fillRect(x + laX, y + by + 32, 6, 2);
                ctx.fillRect(x + raX, y + by + 32, 6, 2);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + laX + 1, y + by + 32, 4, 2);
                ctx.fillRect(x + raX + 1, y + by + 32, 4, 2);
                ctx.fillStyle = pal.pants;
                ctx.fillRect(x + 12, y + 34, 11, 6);
                ctx.fillRect(x + 25, y + 34, 11, 6);
                ctx.fillStyle = pal.pantsHL || pal.pants;
                ctx.fillRect(x + 14, y + 34, 4, 4);
                ctx.fillRect(x + 30, y + 34, 4, 4);
                ctx.fillStyle = pal.pantsDk;
                ctx.fillRect(x + 23, y + 34, 4, 6);
                ctx.fillStyle = pal.pantsSeam || pal.pantsDk;
                ctx.fillRect(x + 17, y + 34, D, 5);
                ctx.fillRect(x + 31, y + 34, D, 5);
                ctx.fillStyle = pal.pantsDk;
                ctx.fillRect(x + 12, y + 38, 11, 2);
                ctx.fillRect(x + 25, y + 38, 11, 2);
                ctx.fillStyle = pal.boots;
                ctx.fillRect(x + 11, y + 40 + legL, 11, 7);
                ctx.fillRect(x + 26, y + 40 + legR, 11, 7);
                ctx.fillStyle = pal.bootsCuff || pal.bootsHL;
                ctx.fillRect(x + 11, y + 40 + legL, 11, 2);
                ctx.fillRect(x + 26, y + 40 + legR, 11, 2);
                ctx.fillStyle = pal.bootsHL;
                ctx.fillRect(x + 13, y + 40 + legL, 4, D);
                ctx.fillRect(x + 28, y + 40 + legR, 4, D);
                ctx.fillStyle = pal.bootsDk || pal.boots;
                ctx.fillRect(x + 11, y + 45 + legL, 11, D);
                ctx.fillRect(x + 26, y + 45 + legR, 11, D);
                ctx.fillStyle = pal.bootsSole || pal.bootsDk || pal.boots;
                ctx.fillRect(x + 10, y + 46 + legL, 13, 2);
                ctx.fillRect(x + 25, y + 46 + legR, 13, 2);
                ctx.fillStyle = pal.bootsHL;
                ctx.fillRect(x + 15, y + 42 + legL, D, D);
                ctx.fillRect(x + 15, y + 44 + legL, D, D);
                ctx.fillRect(x + 30, y + 42 + legR, D, D);
                ctx.fillRect(x + 30, y + 44 + legR, D, D);
                ctx.fillStyle = pal.bootsSh || pal.bootsDk || pal.boots;
                ctx.fillRect(x + 14, y + 43 + legL, D, D);
                ctx.fillRect(x + 29, y + 43 + legR, D, D);
                break;
            }
            case 'up': {
                ctx.fillStyle = pal.outline;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + by + 8, 15, 13, 0, 0, Math.PI * 2);
                ctx.fill();
                if (hasHat) {
                    ctx.fillStyle = pal.hat || pal.hair;
                    ctx.beginPath();
                    ctx.ellipse(x + 24, y + by + 2, 17, 8, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hatHL || pal.hairHL;
                    ctx.beginPath();
                    ctx.ellipse(x + 22, y + by + 1, 12, 5, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hatDk || pal.hairDk;
                    ctx.fillRect(x + 8, y + by + 4, 32, 3);
                } else {
                    ctx.fillStyle = pal.hairDk || pal.hair;
                    ctx.beginPath();
                    ctx.ellipse(x + 24, y + by + 3, 16, 11, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hair;
                    ctx.beginPath();
                    ctx.ellipse(x + 24, y + by + 6, 15, 12, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hairHL;
                    ctx.beginPath();
                    ctx.ellipse(x + 22, y + by + 4, 9, 6, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hairMd || pal.hair;
                    ctx.fillRect(x + 10, y + by + 12, 28, 6);
                    ctx.fillStyle = pal.hairDk || pal.hair;
                    ctx.fillRect(x + 12, y + by + 16, 24, 5);
                    if (isHero) {
                        ctx.fillStyle = pal.hair;
                        ctx.fillRect(x + 7, y + by + 2, 4, 10);
                        ctx.fillRect(x + 37, y + by + 2, 4, 10);
                        ctx.fillStyle = pal.hairDk || pal.hair;
                        ctx.fillRect(x + 13, y + by - 4, 3, 5);
                        ctx.fillRect(x + 20, y + by - 6, 3, 7);
                        ctx.fillRect(x + 28, y + by - 5, 3, 6);
                        ctx.fillRect(x + 34, y + by - 3, 3, 4);
                    }
                }
                if (isHero) {
                    ctx.fillStyle = pal.cape;
                    ctx.fillRect(x + 8, y + by + 21, 32, 14);
                    ctx.fillStyle = pal.capeHL || pal.cape;
                    ctx.fillRect(x + 10, y + by + 21, 10, 12);
                    ctx.fillStyle = pal.capeMd || pal.capeDk;
                    ctx.fillRect(x + 22, y + by + 21, 3, 14);
                    ctx.fillStyle = pal.capeDk;
                    ctx.fillRect(x + 28, y + by + 22, 10, 13);
                    ctx.fillStyle = pal.capeEdge || pal.capeDk;
                    ctx.fillRect(x + 8, y + by + 33, 32, 2);
                    ctx.fillStyle = pal.cape;
                    for (let i = 0; i < 5; i++) ctx.fillRect(x + 10 + i * 5, y + by + 25, D, 7);
                    const capeWave = moving ? Math.sin(frame * Math.PI / 2) * 3 : Math.sin(gt / 1200) * 0.5;
                    ctx.fillStyle = pal.capeDk;
                    ctx.fillRect(x + 12, y + by + 33 + Math.round(capeWave), 24, 2);
                    ctx.fillStyle = pal.capeHL || pal.cape;
                    ctx.globalAlpha = 0.3;
                    ctx.fillRect(x + 12, y + by + 22, 8, 2);
                    ctx.globalAlpha = 1;
                } else {
                    ctx.fillStyle = pal.tunic;
                    ctx.fillRect(x + 10, y + by + 21, 28, 12);
                    ctx.fillStyle = pal.tunicHL;
                    ctx.fillRect(x + 12, y + by + 21, 10, 8);
                    ctx.fillStyle = pal.tunicDk;
                    ctx.fillRect(x + 22, y + by + 21, 3, 12);
                    ctx.fillRect(x + 10, y + by + 31, 28, 2);
                    ctx.fillStyle = pal.tunicTrim || pal.tunicHL;
                    ctx.fillRect(x + 10, y + by + 31, 28, D);
                    ctx.fillStyle = pal.tunicDk;
                    for (let i = 0; i < 3; i++) ctx.fillRect(x + 14 + i * 4, y + by + 25, D, 5);
                }
                ctx.fillStyle = pal.shoulder || pal.tunic;
                ctx.beginPath();
                ctx.ellipse(x + 10, y + by + 25, 5, 4, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(x + 38, y + by + 25, 5, 4, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = pal.belt;
                ctx.fillRect(x + 10, y + by + 31, 28, 3);
                ctx.fillStyle = pal.beltHL || pal.belt;
                ctx.fillRect(x + 14, y + by + 31, 20, D);
                ctx.fillStyle = pal.skin;
                const ulaX = Math.round(5 + armL * 1.3);
                const uraX = Math.round(37 + armR * 1.3);
                ctx.fillRect(x + ulaX, y + by + 24, 6, 9);
                ctx.fillRect(x + uraX, y + by + 24, 6, 9);
                ctx.fillStyle = pal.gloveCuff || pal.gloveSh || pal.skinSh;
                ctx.fillRect(x + ulaX, y + by + 24, 6, 2);
                ctx.fillRect(x + uraX, y + by + 24, 6, 2);
                ctx.fillStyle = pal.skinSh;
                ctx.fillRect(x + ulaX, y + by + 31, 6, 2);
                ctx.fillRect(x + uraX, y + by + 31, 6, 2);
                ctx.fillStyle = pal.pants;
                ctx.fillRect(x + 12, y + 34, 11, 6);
                ctx.fillRect(x + 25, y + 34, 11, 6);
                ctx.fillStyle = pal.pantsDk;
                ctx.fillRect(x + 23, y + 34, 4, 6);
                ctx.fillRect(x + 12, y + 38, 11, 2);
                ctx.fillRect(x + 25, y + 38, 11, 2);
                ctx.fillStyle = pal.boots;
                ctx.fillRect(x + 11, y + 40 + legL, 11, 7);
                ctx.fillRect(x + 26, y + 40 + legR, 11, 7);
                ctx.fillStyle = pal.bootsCuff || pal.bootsHL;
                ctx.fillRect(x + 11, y + 40 + legL, 11, 2);
                ctx.fillRect(x + 26, y + 40 + legR, 11, 2);
                ctx.fillStyle = pal.bootsDk || pal.boots;
                ctx.fillRect(x + 11, y + 45 + legL, 11, D);
                ctx.fillRect(x + 26, y + 45 + legR, 11, D);
                ctx.fillStyle = pal.bootsSole || pal.bootsDk || pal.boots;
                ctx.fillRect(x + 10, y + 46 + legL, 13, 2);
                ctx.fillRect(x + 25, y + 46 + legR, 13, 2);
                break;
            }
            case 'left': {
                ctx.fillStyle = pal.outline;
                ctx.beginPath();
                ctx.ellipse(x + 20, y + by + 8, 14, 13, 0, 0, Math.PI * 2);
                ctx.fill();
                if (hasHat) {
                    ctx.fillStyle = pal.hat || pal.hair;
                    ctx.beginPath();
                    ctx.ellipse(x + 18, y + by + 2, 16, 8, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hatHL || pal.hairHL;
                    ctx.beginPath();
                    ctx.ellipse(x + 16, y + by + 1, 10, 5, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hatDk || pal.hairDk;
                    ctx.fillRect(x + 4, y + by + 4, 30, 3);
                } else {
                    ctx.fillStyle = pal.hairDk || pal.hair;
                    ctx.beginPath();
                    ctx.ellipse(x + 20, y + by + 3, 15, 11, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hair;
                    ctx.beginPath();
                    ctx.ellipse(x + 20, y + by + 5, 14, 10, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hairHL;
                    ctx.beginPath();
                    ctx.ellipse(x + 18, y + by + 3, 8, 5, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hairMd || pal.hair;
                    ctx.fillRect(x + 6, y + by + 8, 26, 3);
                    ctx.fillStyle = pal.hair;
                    ctx.fillRect(x + 4, y + by + 10, 10, 8);
                    if (isHero) {
                        ctx.fillStyle = pal.hairDk || pal.hair;
                        ctx.fillRect(x + 10, y + by - 4, 3, 5);
                        ctx.fillRect(x + 16, y + by - 5, 3, 6);
                        ctx.fillRect(x + 24, y + by - 3, 3, 4);
                    }
                }
                ctx.fillStyle = pal.skin;
                ctx.beginPath();
                ctx.ellipse(x + 20, y + by + 14, 11, 8, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = pal.skinHL || pal.skin;
                ctx.beginPath();
                ctx.ellipse(x + 18, y + by + 12, 6, 4, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = pal.skinSh;
                ctx.fillRect(x + 10, y + by + 18, 20, 3);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + 8, y + by + 14, 4, 4);
                ctx.fillStyle = pal.skinSh;
                ctx.fillRect(x + 8, y + by + 15, 3, D);
                ctx.fillStyle = pal.eyeW || '#f0f0ff';
                ctx.fillRect(x + 11, y + by + 12, 8, 5);
                ctx.fillStyle = pal.outline;
                ctx.fillRect(x + 11, y + by + 11, 8, D);
                ctx.fillRect(x + 10, y + by + 12, D, 5);
                ctx.fillRect(x + 19, y + by + 12, D, 5);
                ctx.fillRect(x + 11, y + by + 17, 8, D);
                ctx.fillStyle = pal.eye;
                ctx.fillRect(x + 12, y + by + 13, 5, 4);
                ctx.fillStyle = pal.eyeHL || '#4060d0';
                ctx.fillRect(x + 13, y + by + 13, 2, 2);
                ctx.fillStyle = pal.pupil || '#080830';
                ctx.fillRect(x + 12, y + by + 14, 2, 3);
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(x + 14, y + by + 13, D, D);
                ctx.fillStyle = pal.nose || pal.skinSh;
                ctx.fillRect(x + 10, y + by + 16, 2, 2);
                ctx.fillStyle = pal.mouth || pal.skinSh;
                ctx.fillRect(x + 12, y + by + 19, 6, D);
                ctx.fillStyle = pal.outline;
                ctx.fillRect(x + 14, y + by + 20, 10, D);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(x + 12, y + by + 21, 18, 3);
                ctx.fillStyle = pal.collarSh || pal.tunic;
                ctx.fillRect(x + 14, y + by + 22, 14, 2);
                ctx.fillStyle = pal.shoulder || pal.tunic;
                ctx.beginPath();
                ctx.ellipse(x + 8, y + by + 25, 5, 4, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(x + 10, y + by + 24, 22, 9);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(x + 12, y + by + 24, 10, 7);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(x + 26, y + by + 24, 6, 9);
                ctx.fillRect(x + 10, y + by + 31, 22, 2);
                ctx.fillStyle = pal.tunicTrim || pal.tunicHL;
                ctx.fillRect(x + 10, y + by + 31, 22, D);
                ctx.fillStyle = pal.tunicDk;
                for (let i = 0; i < 2; i++) ctx.fillRect(x + 14 + i * 5, y + by + 27, D, 4);
                ctx.fillRect(x + 16, y + by + 26, 5, D);
                if (hasApron) {
                    ctx.fillStyle = pal.apron || '#e0d0b0';
                    ctx.fillRect(x + 12, y + by + 28, 18, 7);
                    ctx.fillStyle = pal.apronSh || '#c0b090';
                    ctx.fillRect(x + 12, y + by + 33, 18, 2);
                }
                ctx.fillStyle = pal.belt;
                ctx.fillRect(x + 10, y + by + 31, 22, 3);
                ctx.fillStyle = pal.beltHL || pal.belt;
                ctx.fillRect(x + 14, y + by + 31, 8, D);
                ctx.fillStyle = pal.beltBk;
                ctx.fillRect(x + 22, y + by + 31, 4, 3);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.4;
                ctx.fillRect(x + 22, y + by + 31, 2, D);
                ctx.globalAlpha = 1;
                if (isHero) {
                    ctx.fillStyle = pal.weapon || '#a0a8b8';
                    ctx.fillRect(x + 30, y + by + 20, 3, 14);
                    ctx.fillStyle = pal.weaponHL || '#d0d8e0';
                    ctx.fillRect(x + 30, y + by + 20, D, 12);
                    ctx.fillStyle = pal.weaponDk || '#606878';
                    ctx.fillRect(x + 32, y + by + 21, D, 12);
                    ctx.fillStyle = '#c0a040';
                    ctx.fillRect(x + 29, y + by + 32, 5, 2);
                }
                ctx.fillStyle = pal.glove || pal.skin;
                const llaX = Math.round(4 + armL * 1.3);
                ctx.fillRect(x + llaX, y + by + 24, 6, 10);
                ctx.fillStyle = pal.gloveCuff || pal.gloveSh || pal.skinSh;
                ctx.fillRect(x + llaX, y + by + 24, 6, 2);
                ctx.fillStyle = pal.gloveSh || pal.skinSh;
                ctx.fillRect(x + llaX, y + by + 32, 6, 2);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + llaX + 1, y + by + 32, 4, 2);
                ctx.fillStyle = pal.pants;
                ctx.fillRect(x + 12, y + 34, 18, 6);
                ctx.fillStyle = pal.pantsDk;
                ctx.fillRect(x + 12, y + 34, 6, 6);
                ctx.fillRect(x + 12, y + 38, 18, 2);
                ctx.fillStyle = pal.pantsHL || pal.pants;
                ctx.fillRect(x + 22, y + 34, 4, 4);
                ctx.fillStyle = pal.pantsSeam || pal.pantsDk;
                ctx.fillRect(x + 20, y + 35, D, 4);
                ctx.fillStyle = pal.boots;
                ctx.fillRect(x + 10, y + 40 + legL, 11, 7);
                ctx.fillRect(x + 23, y + 40 + legR, 11, 7);
                ctx.fillStyle = pal.bootsCuff || pal.bootsHL;
                ctx.fillRect(x + 10, y + 40 + legL, 11, 2);
                ctx.fillRect(x + 23, y + 40 + legR, 11, 2);
                ctx.fillStyle = pal.bootsDk || pal.boots;
                ctx.fillRect(x + 10, y + 45 + legL, 11, D);
                ctx.fillRect(x + 23, y + 45 + legR, 11, D);
                ctx.fillStyle = pal.bootsSole || pal.bootsDk || pal.boots;
                ctx.fillRect(x + 9, y + 46 + legL, 13, 2);
                ctx.fillRect(x + 22, y + 46 + legR, 13, 2);
                ctx.fillStyle = pal.bootsHL;
                ctx.fillRect(x + 14, y + 42 + legL, D, D);
                ctx.fillRect(x + 14, y + 44 + legL, D, D);
                ctx.fillRect(x + 27, y + 42 + legR, D, D);
                break;
            }
            case 'right': {
                ctx.fillStyle = pal.outline;
                ctx.beginPath();
                ctx.ellipse(x + 28, y + by + 8, 14, 13, 0, 0, Math.PI * 2);
                ctx.fill();
                if (hasHat) {
                    ctx.fillStyle = pal.hat || pal.hair;
                    ctx.beginPath();
                    ctx.ellipse(x + 30, y + by + 2, 16, 8, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hatHL || pal.hairHL;
                    ctx.beginPath();
                    ctx.ellipse(x + 32, y + by + 1, 10, 5, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hatDk || pal.hairDk;
                    ctx.fillRect(x + 14, y + by + 4, 30, 3);
                } else {
                    ctx.fillStyle = pal.hairDk || pal.hair;
                    ctx.beginPath();
                    ctx.ellipse(x + 28, y + by + 3, 15, 11, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hair;
                    ctx.beginPath();
                    ctx.ellipse(x + 28, y + by + 5, 14, 10, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hairHL;
                    ctx.beginPath();
                    ctx.ellipse(x + 30, y + by + 3, 8, 5, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = pal.hairMd || pal.hair;
                    ctx.fillRect(x + 16, y + by + 8, 26, 3);
                    ctx.fillStyle = pal.hair;
                    ctx.fillRect(x + 34, y + by + 10, 10, 8);
                    if (isHero) {
                        ctx.fillStyle = pal.hairDk || pal.hair;
                        ctx.fillRect(x + 21, y + by - 4, 3, 5);
                        ctx.fillRect(x + 28, y + by - 5, 3, 6);
                        ctx.fillRect(x + 35, y + by - 3, 3, 4);
                    }
                }
                ctx.fillStyle = pal.skin;
                ctx.beginPath();
                ctx.ellipse(x + 28, y + by + 14, 11, 8, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = pal.skinHL || pal.skin;
                ctx.beginPath();
                ctx.ellipse(x + 30, y + by + 12, 6, 4, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = pal.skinSh;
                ctx.fillRect(x + 18, y + by + 18, 20, 3);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + 36, y + by + 14, 4, 4);
                ctx.fillStyle = pal.skinSh;
                ctx.fillRect(x + 37, y + by + 15, 3, D);
                ctx.fillStyle = pal.eyeW || '#f0f0ff';
                ctx.fillRect(x + 29, y + by + 12, 8, 5);
                ctx.fillStyle = pal.outline;
                ctx.fillRect(x + 29, y + by + 11, 8, D);
                ctx.fillRect(x + 28, y + by + 12, D, 5);
                ctx.fillRect(x + 37, y + by + 12, D, 5);
                ctx.fillRect(x + 29, y + by + 17, 8, D);
                ctx.fillStyle = pal.eye;
                ctx.fillRect(x + 31, y + by + 13, 5, 4);
                ctx.fillStyle = pal.eyeHL || '#4060d0';
                ctx.fillRect(x + 33, y + by + 13, 2, 2);
                ctx.fillStyle = pal.pupil || '#080830';
                ctx.fillRect(x + 34, y + by + 14, 2, 3);
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(x + 33, y + by + 13, D, D);
                ctx.fillStyle = pal.nose || pal.skinSh;
                ctx.fillRect(x + 36, y + by + 16, 2, 2);
                ctx.fillStyle = pal.mouth || pal.skinSh;
                ctx.fillRect(x + 30, y + by + 19, 6, D);
                ctx.fillStyle = pal.outline;
                ctx.fillRect(x + 24, y + by + 20, 10, D);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(x + 18, y + by + 21, 18, 3);
                ctx.fillStyle = pal.collarSh || pal.tunic;
                ctx.fillRect(x + 20, y + by + 22, 14, 2);
                ctx.fillStyle = pal.shoulder || pal.tunic;
                ctx.beginPath();
                ctx.ellipse(x + 40, y + by + 25, 5, 4, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(x + 16, y + by + 24, 22, 9);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(x + 26, y + by + 24, 10, 7);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(x + 16, y + by + 24, 6, 9);
                ctx.fillRect(x + 16, y + by + 31, 22, 2);
                ctx.fillStyle = pal.tunicTrim || pal.tunicHL;
                ctx.fillRect(x + 16, y + by + 31, 22, D);
                ctx.fillStyle = pal.tunicDk;
                for (let i = 0; i < 2; i++) ctx.fillRect(x + 28 + i * 5, y + by + 27, D, 4);
                ctx.fillRect(x + 26, y + by + 26, 5, D);
                if (hasApron) {
                    ctx.fillStyle = pal.apron || '#e0d0b0';
                    ctx.fillRect(x + 18, y + by + 28, 18, 7);
                    ctx.fillStyle = pal.apronSh || '#c0b090';
                    ctx.fillRect(x + 18, y + by + 33, 18, 2);
                }
                ctx.fillStyle = pal.belt;
                ctx.fillRect(x + 16, y + by + 31, 22, 3);
                ctx.fillStyle = pal.beltHL || pal.belt;
                ctx.fillRect(x + 26, y + by + 31, 8, D);
                ctx.fillStyle = pal.beltBk;
                ctx.fillRect(x + 22, y + by + 31, 4, 3);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.4;
                ctx.fillRect(x + 23, y + by + 31, 2, D);
                ctx.globalAlpha = 1;
                if (isHero) {
                    ctx.fillStyle = pal.weapon || '#a0a8b8';
                    ctx.fillRect(x + 15, y + by + 20, 3, 14);
                    ctx.fillStyle = pal.weaponHL || '#d0d8e0';
                    ctx.fillRect(x + 17, y + by + 20, D, 12);
                    ctx.fillStyle = pal.weaponDk || '#606878';
                    ctx.fillRect(x + 15, y + by + 21, D, 12);
                    ctx.fillStyle = '#c0a040';
                    ctx.fillRect(x + 14, y + by + 32, 5, 2);
                }
                ctx.fillStyle = pal.glove || pal.skin;
                const rraX = Math.round(38 + armR * 1.3);
                ctx.fillRect(x + rraX, y + by + 24, 6, 10);
                ctx.fillStyle = pal.gloveCuff || pal.gloveSh || pal.skinSh;
                ctx.fillRect(x + rraX, y + by + 24, 6, 2);
                ctx.fillStyle = pal.gloveSh || pal.skinSh;
                ctx.fillRect(x + rraX, y + by + 32, 6, 2);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(x + rraX + 1, y + by + 32, 4, 2);
                ctx.fillStyle = pal.pants;
                ctx.fillRect(x + 18, y + 34, 18, 6);
                ctx.fillStyle = pal.pantsDk;
                ctx.fillRect(x + 30, y + 34, 6, 6);
                ctx.fillRect(x + 18, y + 38, 18, 2);
                ctx.fillStyle = pal.pantsHL || pal.pants;
                ctx.fillRect(x + 22, y + 34, 4, 4);
                ctx.fillStyle = pal.pantsSeam || pal.pantsDk;
                ctx.fillRect(x + 28, y + 35, D, 4);
                ctx.fillStyle = pal.boots;
                ctx.fillRect(x + 16, y + 40 + legL, 11, 7);
                ctx.fillRect(x + 29, y + 40 + legR, 11, 7);
                ctx.fillStyle = pal.bootsCuff || pal.bootsHL;
                ctx.fillRect(x + 16, y + 40 + legL, 11, 2);
                ctx.fillRect(x + 29, y + 40 + legR, 11, 2);
                ctx.fillStyle = pal.bootsDk || pal.boots;
                ctx.fillRect(x + 16, y + 45 + legL, 11, D);
                ctx.fillRect(x + 29, y + 45 + legR, 11, D);
                ctx.fillStyle = pal.bootsSole || pal.bootsDk || pal.boots;
                ctx.fillRect(x + 15, y + 46 + legL, 13, 2);
                ctx.fillRect(x + 28, y + 46 + legR, 13, 2);
                ctx.fillStyle = pal.bootsHL;
                ctx.fillRect(x + 20, y + 42 + legL, D, D);
                ctx.fillRect(x + 20, y + 44 + legL, D, D);
                ctx.fillRect(x + 33, y + 42 + legR, D, D);
                break;
            }
        }
    }

    function getNPCPal(color, spriteId) {
        const c = color || '#44aa44';
        const h = hexToHSL(c);
        const hatH = (h.h + 180) % 360;
        const hairH = (h.h + 40) % 360;
        const hairS = Math.min(h.s + 10, 50);
        return {
            hair: hslHex(hairH, hairS, 25),
            hairHL: hslHex(hairH, hairS, 42),
            hairDk: hslHex(hairH, hairS, 14),
            hairMd: hslHex(hairH, hairS, 32),
            hairTip: hslHex(hairH, hairS, 50),
            skin: '#f4d0a0', skinHL: '#ffe8c8', skinSh: '#d8a870', skinDk: '#c09060', skinRim: '#e8c090',
            eyeW: '#f0f0ff', eye: '#203060', eyeHL: '#3050a0', pupil: '#080830', eyeLash: '#201018',
            mouth: '#c07050', cheek: '#e8a888', nose: '#d8b080',
            tunic: c, tunicHL: shade(c, 30), tunicMd: shade(c, 15), tunicDk: shade(c, -30), tunicSh: shade(c, -45),
            tunicTrim: shade(c, 40), tunicTrimDk: shade(c, 10),
            collar: shade(c, 50), collarSh: shade(c, 30),
            shoulder: shade(c, 5), shoulderHL: shade(c, 25),
            belt: '#b09030', beltBk: '#806020', beltHL: '#d0b040',
            pants: shade(c, -35), pantsDk: shade(c, -50), pantsHL: shade(c, -20), pantsSeam: shade(c, -55),
            boots: '#504030', bootsHL: '#685040', bootsDk: '#382818', bootsSh: '#402818', bootsCuff: '#605038', bootsSole: '#201008',
            glove: '#e8d8b8', gloveSh: '#c8b890', gloveCuff: '#b8a870',
            cape: shade(c, -15), capeMd: shade(c, -25), capeDk: shade(c, -40), capeHL: shade(c, 5), capeEdge: shade(c, -50),
            outline: '#181020', outlineHL: '#282838',
            weapon: '#a0a8b8', weaponHL: '#d0d8e0', weaponDk: '#606878',
            hat: hslHex(hatH, Math.min(h.s + 5, 60), 35),
            hatHL: hslHex(hatH, Math.min(h.s + 5, 60), 52),
            hatDk: hslHex(hatH, Math.min(h.s + 5, 60), 20),
            hatMd: hslHex(hatH, Math.min(h.s + 5, 60), 42),
            apron: shade(c, 45), apronSh: shade(c, 25), apronHL: shade(c, 55)
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
