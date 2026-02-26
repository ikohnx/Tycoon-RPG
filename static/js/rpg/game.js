const Game = (function() {
    let canvas, ctx;
    let gameTime = 0;
    let lastTime = 0;
    let running = false;
    let currentState = 'LOADING';
    let keys = {};
    let onScreenControls = { up: false, down: false, left: false, right: false };

    let playerData = null;
    let allPlayers = [];
    let csrfToken = '';

    const titleState = {};
    const charSelectState = { step: 0, name: '', nameActive: false, cursorBlink: 0, worldIndex: 0, industryIndex: 0, careerIndex: 0, characterIndex: 0 };
    const loginState = { playerId: null, playerName: '', password: '', active: false, error: '' };
    let titleCursor = 0;
    let titlePlayerCursor = 0;
    let titleScrollOffset = 0;
    let textInputCallback = null;

    function showTextInput(label, placeholder, maxLen, isPassword, initialValue, callback) {
        const overlay = document.getElementById('text-input-overlay');
        const field = document.getElementById('text-input-field');
        const lbl = document.getElementById('text-input-label');
        const err = document.getElementById('text-input-error');
        const btn = document.getElementById('text-input-submit');
        if (!overlay || !field) return;
        lbl.textContent = label;
        field.value = initialValue || '';
        field.maxLength = maxLen || 20;
        field.placeholder = placeholder || 'Type here...';
        field.type = isPassword ? 'password' : 'text';
        err.textContent = '';
        overlay.classList.add('active');
        textInputCallback = callback;
        setTimeout(() => field.focus(), 100);

        const submitFn = () => {
            const val = field.value;
            if (textInputCallback) {
                const result = textInputCallback(val);
                if (result && result.error) {
                    err.textContent = result.error;
                    return;
                }
            }
            hideTextInput();
        };

        btn.onclick = submitFn;
        field.onkeydown = (e) => {
            if (e.key === 'Enter') { e.preventDefault(); submitFn(); }
            else if (e.key === 'Escape') { e.preventDefault(); hideTextInput(); }
        };
    }

    function hideTextInput() {
        const overlay = document.getElementById('text-input-overlay');
        if (overlay) overlay.classList.remove('active');
        textInputCallback = null;
        const c = document.getElementById('game-canvas');
        if (c) c.focus();
    }

    const WORLDS = ['Modern', 'Industrial', 'Fantasy', 'Sci-Fi'];
    const INDUSTRIES = {
        'Modern': ['Restaurant', 'Tech Startup', 'Retail', 'Consulting'],
        'Industrial': ['Steel Mill', 'Automobile', 'Textiles', 'Mining'],
        'Fantasy': ['Potion Shop', 'Enchantment', 'Tavern', 'Smithy'],
        'Sci-Fi': ['Space Mining', 'Cybernetics', 'Terraforming', 'AI Services']
    };
    const CAREERS = ['entrepreneur', 'executive', 'consultant', 'investor'];

    function getCharacterOptions(world) {
        if (world === 'Industrial') return RPGSprites.IND_CHARACTER_KEYS;
        return ['hero', 'merchant', 'scholar', 'warrior'];
    }

    function getCharacterNames(world) {
        if (world === 'Industrial') return RPGSprites.IND_CHARACTER_NAMES;
        return ['Hero', 'Merchant', 'Scholar', 'Warrior'];
    }

    const C = RPGColors.C;

    let ui = {};
    let dpr = 1;
    let isMobile = false;

    function calcUI() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        const minDim = Math.min(w, h);
        const s = Math.max(0.45, Math.min(1.4, minDim / 700));
        isMobile = ('ontouchstart' in window) || window.innerWidth < 768;

        ui = {
            s: s,
            fs: (base) => Math.max(6, Math.round(base * s)),
            pad: Math.round(16 * s),
            titlePanelW: Math.min(Math.round(320 * s), w - 30),
            charPanelW: Math.min(Math.round(400 * s), w - 24),
            battleBarW: Math.min(Math.round(200 * s), (w / 2) - 50),
            resultBoxW: Math.min(Math.round(400 * s), w - 30),
            resultBoxH: Math.min(Math.round(250 * s), h - 60),
            loadBarW: Math.min(Math.round(300 * s), w - 40),
            loadBarH: Math.round(20 * s),
            titleY: Math.round(h * 0.12),
            subtitleY: Math.round(h * 0.12 + 35 * s),
            taglineY: Math.round(h * 0.12 + 70 * s),
            menuStartY: Math.round(h * 0.12 + 105 * s),
            menuBtnH: Math.round(50 * s),
            menuGap: Math.round(10 * s),
            listItemH: Math.round(40 * s),
            stepH: Math.round(22 * s),
            optionH: Math.round(34 * s),
            previewSize: Math.max(48, Math.min(Math.round(72 * s), Math.floor((w - 80) / 5))),
            previewSpacing: Math.round(12 * s),
            confirmPreview: Math.max(48, Math.round(72 * s)),
            pauseMenuW: Math.min(Math.round(240 * s), w - 30),
        };
        return ui;
    }

    function init(canvasId) {
        canvas = document.getElementById(canvasId);
        if (!canvas) return;
        ctx = canvas.getContext('2d');
        ctx.imageSmoothingEnabled = false;
        resize();
        window.addEventListener('resize', resize);
        window.addEventListener('keydown', onKeyDown);
        window.addEventListener('keyup', onKeyUp);
        canvas.addEventListener('click', onClick);
        setupTouch();
        updateTouchVisibility();
        fetchCSRF();
        fetchPlayers();
        setState('LOADING');
        running = true;
        lastTime = performance.now();
        requestAnimationFrame(loop);
    }

    function resize() {
        dpr = window.devicePixelRatio || 1;
        const cssW = window.innerWidth;
        const cssH = window.innerHeight;
        canvas.width = cssW * dpr;
        canvas.height = cssH * dpr;
        canvas.style.width = cssW + 'px';
        canvas.style.height = cssH + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.imageSmoothingEnabled = false;
        calcUI();
        updateTouchVisibility();
        _titleScene = null;
    }

    function updateTouchVisibility() {
        const dpad = document.getElementById('dpad');
        const btns = document.getElementById('action-buttons');
        const show = isMobile || ('ontouchstart' in window);
        if (dpad) dpad.style.display = show ? 'flex' : 'none';
        if (btns) btns.style.display = show ? 'flex' : 'none';
    }

    function loop(ts) {
        if (!running) return;
        const dt = Math.min(ts - lastTime, 50);
        lastTime = ts;
        gameTime += dt;
        update(dt);
        render();
        requestAnimationFrame(loop);
    }

    function update(dt) {
        if (currentState === 'LOADING') {
            updateLoading();
            return;
        }
        if (currentState === 'WORLD') {
            RPGEngine.setOnScreenControls(onScreenControls);
            RPGEngine.externalUpdate(dt, gameTime);
        } else if (currentState === 'TITLE') {
            charSelectState.cursorBlink += dt;
        } else if (currentState === 'CHAR_SELECT') {
            charSelectState.cursorBlink += dt;
        } else if (currentState === 'LOGIN') {
            charSelectState.cursorBlink += dt;
        } else if (currentState === 'BATTLE') {
            updateBattle(dt);
        }
    }

    function render() {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

        switch (currentState) {
            case 'LOADING': renderLoading(); break;
            case 'TITLE': renderTitle(); break;
            case 'CHAR_SELECT': renderCharSelect(); break;
            case 'LOGIN': renderLogin(); break;
            case 'WORLD': RPGEngine.externalRender(); break;
            case 'BATTLE': renderBattle(); break;
            case 'PAUSE_MENU': RPGEngine.externalRender(); renderPauseMenu(); break;
        }
    }

    function setState(s) {
        const prev = currentState;
        currentState = s;
        if (s === 'WORLD') {
            RPGEngine.init('game-canvas', {
                externalLoop: true,
                onInteract: onNPCInteract,
                onTransition: onMapTransition,
                hudData: playerData ? {
                    capital: playerData.cash || 10000,
                    morale: playerData.morale || 80,
                    brand: playerData.brand_equity || 100,
                    energy: playerData.energy || 100,
                    quarter: playerData.fiscal_quarter || 1
                } : {}
            });
            let mapName = 'hub';
            const pWorld = playerData ? (playerData.chosen_world || playerData.world || 'Modern') : 'Modern';
            if (pWorld === 'Industrial') {
                mapName = 'iron_basin';
            }
            RPGSprites.setActiveHero(pWorld, playerData ? (playerData.character_index || 0) : 0);
            const map = RPGMaps.getMap(mapName);
            RPGEngine.loadMap(map);
        }
        if (prev === 'WORLD' && s !== 'WORLD' && s !== 'PAUSE_MENU' && s !== 'BATTLE') {
            RPGEngine.stop();
        }
    }

    function isTextInputActive() {
        const overlay = document.getElementById('text-input-overlay');
        return overlay && overlay.classList.contains('active');
    }

    function onKeyDown(e) {
        if (isTextInputActive()) return;
        keys[e.key] = true;
        const prevented = ['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' ','Enter','w','a','s','d','Escape','Tab'];
        if (prevented.includes(e.key)) e.preventDefault();

        if (currentState === 'TITLE') handleTitleKey(e.key);
        else if (currentState === 'CHAR_SELECT') handleCharSelectKey(e.key);
        else if (currentState === 'LOGIN') handleLoginKey(e.key);
        else if (currentState === 'WORLD') {
            if (e.key === 'Escape') {
                if (!RPGEngine.isDialogueActive() && !RPGEngine.isOverlayActive()) {
                    setState('PAUSE_MENU');
                    return;
                }
            }
            RPGEngine.handleKeyDown(e.key);
        }
        else if (currentState === 'PAUSE_MENU') handlePauseKey(e.key);
        else if (currentState === 'BATTLE') handleBattleKey(e.key);
    }

    function onKeyUp(e) {
        keys[e.key] = false;
        if (currentState === 'WORLD') {
            RPGEngine.handleKeyUp(e.key);
        }
    }

    function onClick(e) {
        if (isTextInputActive()) return;
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        if (currentState === 'TITLE') handleTitleClick(mx, my);
        else if (currentState === 'CHAR_SELECT') handleCharSelectClick(mx, my);
        else if (currentState === 'BATTLE') handleBattleClick(mx, my);
        else if (currentState === 'PAUSE_MENU') handlePauseClick(mx, my);
    }

    function dpadToKey(d) {
        return d === 'up' ? 'ArrowUp' : d === 'down' ? 'ArrowDown' : d === 'left' ? 'ArrowLeft' : 'ArrowRight';
    }

    function setupTouch() {
        ['up','down','left','right'].forEach(d => {
            const b = document.getElementById('dpad-' + d);
            if (!b) return;
            const press = (e) => {
                if (e) e.preventDefault();
                onScreenControls[d] = true;
                b.classList.add('pressed');
                if (currentState === 'TITLE') handleTitleKey(dpadToKey(d));
                else if (currentState === 'CHAR_SELECT') handleCharSelectKey(dpadToKey(d));
                else if (currentState === 'LOGIN') handleLoginKey(dpadToKey(d));
                else if (currentState === 'PAUSE_MENU') handlePauseKey(dpadToKey(d));
                else if (currentState === 'BATTLE') handleBattleKey(dpadToKey(d));
            };
            const release = (e) => {
                if (e) e.preventDefault();
                onScreenControls[d] = false;
                b.classList.remove('pressed');
            };
            b.addEventListener('touchstart', press);
            b.addEventListener('touchend', release);
            b.addEventListener('touchcancel', release);
            b.addEventListener('mousedown', press);
            b.addEventListener('mouseup', release);
            b.addEventListener('mouseleave', release);
        });
        window.addEventListener('mouseup', () => {
            ['up','down','left','right'].forEach(d => {
                onScreenControls[d] = false;
                const b = document.getElementById('dpad-' + d);
                if (b) b.classList.remove('pressed');
            });
        });
        const ab = document.getElementById('btn-action');
        if (ab) {
            const act = () => {
                if (currentState === 'TITLE') handleTitleKey('Enter');
                else if (currentState === 'CHAR_SELECT') handleCharSelectKey('Enter');
                else if (currentState === 'WORLD') RPGEngine.handleKeyDown('Enter');
                else if (currentState === 'BATTLE') handleBattleKey('Enter');
                else if (currentState === 'PAUSE_MENU') handlePauseKey('Enter');
            };
            ab.addEventListener('touchstart', e => { e.preventDefault(); act(); });
            ab.addEventListener('click', act);
        }
        const cb = document.getElementById('btn-cancel');
        if (cb) {
            const cancel = () => {
                if (currentState === 'WORLD') {
                    if (!RPGEngine.isDialogueActive() && !RPGEngine.isOverlayActive()) {
                        setState('PAUSE_MENU');
                    }
                }
                else if (currentState === 'PAUSE_MENU') handlePauseKey('Escape');
                else if (currentState === 'BATTLE') handleBattleKey('Escape');
                else if (currentState === 'CHAR_SELECT') handleCharSelectKey('Escape');
            };
            cb.addEventListener('touchstart', e => { e.preventDefault(); cancel(); });
            cb.addEventListener('click', cancel);
        }
    }

    async function fetchCSRF() {
        try {
            const r = await fetch('/api/csrf');
            const d = await r.json();
            csrfToken = d.token || '';
        } catch(e) { console.warn('CSRF fetch failed'); }
    }

    async function fetchPlayers() {
        try {
            const r = await fetch('/api/players');
            const d = await r.json();
            allPlayers = d.players || [];
        } catch(e) { allPlayers = []; }
    }

    async function createPlayer(name, password, world, industry, career) {
        try {
            const charIdx = charSelectState.characterIndex || 0;
            const r = await fetch('/api/create_player', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ name, password, world, industry, career_path: career, character_index: charIdx })
            });
            const d = await r.json();
            if (d.success) {
                playerData = d.player;
                playerData.character_index = charIdx;
                playerData.chosen_world = world;
                setState('WORLD');
            } else {
                charSelectState.error = d.error || 'Failed to create character';
            }
        } catch(e) { charSelectState.error = 'Connection error'; }
    }

    async function loginPlayer(playerId) {
        try {
            const r = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ player_id: playerId })
            });
            const d = await r.json();
            if (d.success) {
                playerData = d.player;
                setState('WORLD');
            } else {
                loginState.error = d.error || 'Login failed';
            }
        } catch(e) { loginState.error = 'Connection error'; }
    }

    async function fetchPlayerStats() {
        try {
            const r = await fetch('/api/stats');
            const d = await r.json();
            if (d.stats) {
                playerData = { ...playerData, ...d.stats };
                if (d.energy) playerData.energy = d.energy.current_energy;
                if (d.resources) {
                    playerData.morale = d.resources.morale;
                    playerData.brand_equity = d.resources.brand_equity;
                    playerData.fiscal_quarter = d.resources.fiscal_quarter;
                }
                RPGEngine.updateHUD({
                    capital: playerData.cash || 10000,
                    morale: playerData.morale || 80,
                    brand: playerData.brand_equity || 100,
                    energy: playerData.energy || 100,
                    quarter: playerData.fiscal_quarter || 1
                });
            }
        } catch(e) {}
    }


    function drawFFBox(x, y, w, h) {
        const grd = ctx.createLinearGradient(x, y, x, y + h);
        grd.addColorStop(0, '#181888');
        grd.addColorStop(0.3, '#101060');
        grd.addColorStop(1, '#080840');
        ctx.fillStyle = grd;
        ctx.fillRect(x + 2, y + 2, w - 4, h - 4);
        ctx.strokeStyle = '#f0f0f8';
        ctx.lineWidth = 2;
        ctx.strokeRect(x + 1, y + 1, w - 2, h - 2);
        ctx.strokeStyle = '#9898c8';
        ctx.lineWidth = 1;
        ctx.strokeRect(x + 4, y + 4, w - 8, h - 8);
        ctx.fillStyle = '#f0f0f8';
        ctx.fillRect(x, y, 2, 2);
        ctx.fillRect(x + w - 2, y, 2, 2);
        ctx.fillRect(x, y + h - 2, 2, 2);
        ctx.fillRect(x + w - 2, y + h - 2, 2, 2);
    }

    function drawCursor(x, y) {
        const bob = Math.sin(gameTime / 200) * 2;
        ctx.fillStyle = '#f0f0f8';
        ctx.beginPath();
        ctx.moveTo(x + bob, y - 5);
        ctx.lineTo(x + 8 + bob, y);
        ctx.lineTo(x + bob, y + 5);
        ctx.closePath();
        ctx.fill();
    }

    function drawText(text, x, y, color, size, align) {
        ctx.fillStyle = color || '#fff';
        ctx.font = (size || 11) + 'px "Press Start 2P", monospace';
        ctx.textAlign = align || 'left';
        ctx.textBaseline = 'middle';
        ctx.shadowColor = '#000030';
        ctx.shadowOffsetX = 1;
        ctx.shadowOffsetY = 1;
        ctx.fillText(text, x, y);
        ctx.shadowColor = 'transparent';
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
    }

    function wrapText(text, x, y, maxW, lineH, color, size) {
        ctx.fillStyle = color || '#fff';
        ctx.font = (size || 11) + 'px "Press Start 2P", monospace';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'middle';
        const words = text.split(' ');
        let line = '', ty = y;
        for (let i = 0; i < words.length; i++) {
            const test = line + words[i] + ' ';
            if (ctx.measureText(test).width > maxW && i > 0) {
                ctx.fillText(line.trim(), x, ty);
                line = words[i] + ' ';
                ty += lineH;
            } else line = test;
        }
        ctx.fillText(line.trim(), x, ty);
        return ty;
    }


    function updateLoading() {
        const tilesReady = RPGTiles.isLoaded();
        const spritesReady = RPGSprites.isLoaded();
        if (tilesReady && spritesReady) {
            setState('TITLE');
        }
    }

    function renderLoading() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        const cx = w / 2;
        const cy = h / 2;

        drawText('BUSINESS TYCOON RPG', cx, cy - 60 * ui.s, '#f0d850', ui.fs(16), 'center');

        const tp = RPGTiles.getLoadProgress();
        const sp = RPGSprites.getLoadProgress();
        const loaded = tp.loaded + sp.loaded;
        const total = tp.total + sp.total;
        const pct = total > 0 ? loaded / total : 0;

        const barW = ui.loadBarW;
        const barH = ui.loadBarH;
        const barX = cx - barW / 2;
        const barY = cy - barH / 2;

        ctx.fillStyle = '#181840';
        ctx.fillRect(barX - 2, barY - 2, barW + 4, barH + 4);
        ctx.strokeStyle = '#6060a0';
        ctx.lineWidth = 1;
        ctx.strokeRect(barX - 2, barY - 2, barW + 4, barH + 4);

        const grd = ctx.createLinearGradient(barX, barY, barX + barW * pct, barY);
        grd.addColorStop(0, '#4080e0');
        grd.addColorStop(1, '#60c0f0');
        ctx.fillStyle = grd;
        ctx.fillRect(barX, barY, barW * pct, barH);

        drawText('Loading... ' + Math.floor(pct * 100) + '%', cx, barY + barH + 25, '#8080c0', ui.fs(9), 'center');
    }

    function renderTitle() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        const cx = w / 2;

        renderTitleBackground();

        drawText('BUSINESS TYCOON', cx, ui.titleY, '#f0d850', ui.fs(20), 'center');
        drawText('R P G', cx, ui.subtitleY, '#c0a030', ui.fs(16), 'center');

        drawText('Master Business Skills Through Adventure', cx, ui.taglineY, '#8080c0', ui.fs(9), 'center');

        const panelW = ui.titlePanelW;
        const panelX = cx - panelW / 2;
        const btnH = ui.menuBtnH;
        let panelY = ui.menuStartY;

        drawFFBox(panelX, panelY, panelW, btnH);
        if (titleCursor === 0) drawCursor(panelX + 14, panelY + btnH / 2);
        drawText('NEW ADVENTURE', panelX + 32, panelY + btnH / 2, titleCursor === 0 ? '#fff' : '#a0a0c0', ui.fs(12));

        panelY += btnH + ui.menuGap;
        drawFFBox(panelX, panelY, panelW, btnH);
        if (titleCursor === 1) drawCursor(panelX + 14, panelY + btnH / 2);
        drawText('CONTINUE QUEST', panelX + 32, panelY + btnH / 2, titleCursor === 1 ? '#fff' : '#a0a0c0', ui.fs(12));

        if (titleCursor === 1 && allPlayers.length > 0) {
            const listY = panelY + btnH + ui.menuGap;
            const itemH = ui.listItemH;
            const listH = Math.min(allPlayers.length * itemH + 20, h - listY - 40);
            drawFFBox(panelX, listY, panelW, listH);

            ctx.save();
            ctx.beginPath();
            ctx.rect(panelX + 4, listY + 4, panelW - 8, listH - 8);
            ctx.clip();

            const visibleCount = Math.floor((listH - 20) / itemH);
            if (titlePlayerCursor >= titleScrollOffset + visibleCount) titleScrollOffset = titlePlayerCursor - visibleCount + 1;
            if (titlePlayerCursor < titleScrollOffset) titleScrollOffset = titlePlayerCursor;

            for (let i = titleScrollOffset; i < allPlayers.length && i < titleScrollOffset + visibleCount; i++) {
                const p = allPlayers[i];
                const iy = listY + 14 + (i - titleScrollOffset) * itemH;
                if (i === titlePlayerCursor) {
                    ctx.fillStyle = 'rgba(80,80,160,0.3)';
                    ctx.fillRect(panelX + 8, iy - 8, panelW - 16, itemH - 4);
                    drawCursor(panelX + 14, iy + 10);
                }
                drawText(p.player_name || 'Player', panelX + 32, iy + 4, i === titlePlayerCursor ? '#fff' : '#c0c0e0', ui.fs(10));
                drawText((p.chosen_world || p.world || 'Modern') + ' / ' + (p.chosen_industry || p.industry || ''), panelX + 32, iy + 22, '#6868a0', ui.fs(8));
                drawText('$' + Number(p.total_cash || p.cash || 0).toLocaleString(), panelX + panelW - 24, iy + 4, '#e8c020', ui.fs(9), 'right');
                ctx.textAlign = 'left';
            }
            ctx.restore();

            if (allPlayers.length > visibleCount) {
                if (titleScrollOffset > 0) drawText('\u25B2', panelX + panelW - 20, listY + 10, '#8080c0', ui.fs(8));
                if (titleScrollOffset + visibleCount < allPlayers.length) drawText('\u25BC', panelX + panelW - 20, listY + listH - 12, '#8080c0', ui.fs(8));
            }
        } else if (titleCursor === 1 && allPlayers.length === 0) {
            const listY = panelY + btnH + ui.menuGap;
            drawFFBox(panelX, listY, panelW, btnH);
            drawText('No saved games found', panelX + 20, listY + btnH / 2, '#6868a0', ui.fs(9));
        }

        drawText(isMobile ? 'Tap to select' : 'Click or use \u25B2\u25BC + ENTER', cx, h - 30, '#4848a0', ui.fs(8), 'center');
    }

    let _titleScene = null;
    function buildTitleScene(cols, rows) {
        const scene = [];
        for (let r = 0; r < rows; r++) {
            scene[r] = [];
            for (let c = 0; c < cols; c++) {
                let t = 1;
                const rng = ((r * 137 + c * 241 + 73) % 100) / 100;
                if (r <= 1 || r >= rows - 2) { t = 9; }
                else if (c <= 1 || c >= cols - 2) { t = 9; }
                else if (r >= rows - 5 && r < rows - 2) {
                    t = 3;
                    if (r === rows - 5 && rng < 0.3) t = 27;
                }
                else if (r >= 3 && r <= 5 && c >= 4 && c <= 8) { t = 6; if (r === 5) t = 4; }
                else if (r === 6 && c >= 4 && c <= 8) { t = 4; if (c === 6) t = 7; }
                else if (r >= 3 && r <= 5 && c >= cols - 9 && c <= cols - 5) { t = 6; if (r === 5) t = 4; }
                else if (r === 6 && c >= cols - 9 && c <= cols - 5) { t = 4; if (c === cols - 7) t = 7; }
                else if (r >= Math.floor(rows/2) - 1 && r <= Math.floor(rows/2) + 1 && c >= Math.floor(cols/2) - 2 && c <= Math.floor(cols/2) + 2) { t = 14; if (r === Math.floor(rows/2) && c === Math.floor(cols/2)) t = 18; }
                else if (Math.abs(c - Math.floor(cols/2)) <= 1) { t = 2; }
                else if (Math.abs(r - Math.floor(rows/2)) <= 0) { t = 2; }
                else if (rng < 0.06) t = 9;
                else if (rng < 0.10) t = 10;
                else if (rng < 0.14) t = 30;
                else if (rng < 0.17) t = 31;
                else if (rng < 0.19) t = 29;

                if (r === 4 && (c === 3 || c === 9 || c === cols - 10 || c === cols - 4)) t = 19;
                if (r === Math.floor(rows/2) + 3 && (c === 5 || c === cols - 6)) t = 22;
                if (r === Math.floor(rows/2) - 3 && c >= Math.floor(cols/2) - 1 && c <= Math.floor(cols/2) + 1) t = 33;

                scene[r][c] = t;
            }
        }
        return scene;
    }

    function renderTitleBackground() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        const tileSize = 32;
        const cols = Math.ceil(w / tileSize) + 1;
        const rows = Math.ceil(h / tileSize) + 1;

        if (!_titleScene || _titleScene.length !== rows || _titleScene[0].length !== cols) {
            _titleScene = buildTitleScene(cols, rows);
        }

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                RPGTiles.drawTile(ctx, C, _titleScene[r][c], c * tileSize, r * tileSize, r, c, gameTime, tileSize);
            }
        }

        ctx.fillStyle = 'rgba(0,0,20,0.55)';
        ctx.fillRect(0, 0, w, h);

        const grd = ctx.createLinearGradient(0, 0, 0, 80);
        grd.addColorStop(0, 'rgba(0,0,30,0.85)');
        grd.addColorStop(1, 'transparent');
        ctx.fillStyle = grd;
        ctx.fillRect(0, 0, w, 80);

        const grd2 = ctx.createLinearGradient(0, h - 80, 0, h);
        grd2.addColorStop(0, 'transparent');
        grd2.addColorStop(1, 'rgba(0,0,30,0.85)');
        ctx.fillStyle = grd2;
        ctx.fillRect(0, h - 80, w, 80);
    }

    function handleTitleKey(key) {
        if (titleCursor === 1 && allPlayers.length > 0) {
            if (key === 'ArrowUp' || key === 'w') {
                titlePlayerCursor = Math.max(0, titlePlayerCursor - 1);
                return;
            }
            if (key === 'ArrowDown' || key === 's') {
                titlePlayerCursor = Math.min(allPlayers.length - 1, titlePlayerCursor + 1);
                return;
            }
            if (key === 'Enter' || key === ' ') {
                const p = allPlayers[titlePlayerCursor];
                loginPlayer(p.player_id);
                return;
            }
            if (key === 'Escape') {
                titleCursor = 0;
                return;
            }
        }
        if (key === 'ArrowUp' || key === 'w') titleCursor = 0;
        else if (key === 'ArrowDown' || key === 's') titleCursor = 1;
        else if (key === 'Enter' || key === ' ') {
            if (titleCursor === 0) {
                charSelectState.step = 0;
                charSelectState.name = '';
                charSelectState.worldIndex = 0;
                charSelectState.industryIndex = 0;
                charSelectState.careerIndex = 0;
                charSelectState.error = '';
                setState('CHAR_SELECT');
                promptForName();
            }
        }
    }

    function promptForName() {
        showTextInput('Enter your character name:', 'Your name...', 20, false, charSelectState.name, (val) => {
            if (!val || val.trim().length === 0) {
                return { error: 'Please enter a name' };
            }
            charSelectState.name = val.trim();
            charSelectState.step = 1;
            charSelectState.error = '';
            return null;
        });
    }

    function handleTitleClick(mx, my) {
        const w = window.innerWidth;
        const h = window.innerHeight;
        const cx = w / 2;
        const panelW = ui.titlePanelW;
        const panelX = cx - panelW / 2;
        const btnH = ui.menuBtnH;
        const firstPanelY = ui.menuStartY;
        const secondPanelY = firstPanelY + btnH + ui.menuGap;

        if (mx >= panelX && mx <= panelX + panelW) {
            if (my >= firstPanelY && my <= firstPanelY + btnH) {
                titleCursor = 0;
                handleTitleKey('Enter');
                return;
            } else if (my >= secondPanelY && my <= secondPanelY + btnH) {
                if (titleCursor !== 1) {
                    titleCursor = 1;
                    return;
                }
            }
        }

        if (titleCursor === 1 && allPlayers.length > 0) {
            const listY = secondPanelY + btnH + ui.menuGap;
            const itemH = ui.listItemH;
            const listH = Math.min(allPlayers.length * itemH + 20, h - listY - 40);
            const visibleCount = Math.floor((listH - 20) / itemH);
            for (let i = titleScrollOffset; i < allPlayers.length && i < titleScrollOffset + visibleCount; i++) {
                const iy = listY + 14 + (i - titleScrollOffset) * itemH;
                if (my >= iy - 8 && my <= iy + 28 && mx >= panelX && mx <= panelX + panelW) {
                    titlePlayerCursor = i;
                    loginPlayer(allPlayers[i].player_id);
                    return;
                }
            }
        }
    }


    function renderCharSelect() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        const cx = w / 2;

        renderTitleBackground();

        drawText('CREATE CHARACTER', cx, Math.round(h * 0.06), '#f0d850', ui.fs(16), 'center');

        const panelW = ui.charPanelW;
        const panelX = cx - panelW / 2;
        const panelY = Math.round(h * 0.1);
        const panelH = h - panelY - Math.round(40 * ui.s);
        drawFFBox(panelX, panelY, panelW, panelH);

        let y = panelY + Math.round(20 * ui.s);
        const stepFS = ui.fs(9);
        const stepGap = ui.stepH;
        const optFS = ui.fs(11);
        const optGap = ui.optionH;
        const labelFS = ui.fs(10);
        const inPad = Math.round(20 * ui.s);

        const steps = ['Name', 'World', 'Industry', 'Career', 'Character', 'Confirm'];
        for (let i = 0; i < steps.length; i++) {
            const active = i === charSelectState.step;
            const done = i < charSelectState.step;
            drawText((done ? '\u2713 ' : (i + 1) + '. ') + steps[i], panelX + inPad, y, active ? '#f0d850' : (done ? '#40a040' : '#5050a0'), stepFS);
            y += stepGap;
        }

        y += Math.round(8 * ui.s);
        ctx.fillStyle = '#484888';
        ctx.fillRect(panelX + 16, y, panelW - 32, 1);
        y += Math.round(12 * ui.s);

        if (charSelectState.step === 0) {
            drawText('Enter your name:', panelX + inPad, y, '#c0c0e0', labelFS);
            y += Math.round(26 * ui.s);
            drawFFBox(panelX + inPad, y - 10, panelW - inPad * 2, Math.round(36 * ui.s));
            if (charSelectState.name) {
                drawText(charSelectState.name, panelX + inPad + 12, y + 8, '#fff', ui.fs(12));
            } else {
                drawText('(tap to type)', panelX + inPad + 12, y + 8, '#5050a0', labelFS);
            }
            y += Math.round(50 * ui.s);
            drawText(isMobile ? 'Tap to enter your name' : 'Click anywhere to enter your name', panelX + inPad, y, '#5050a0', ui.fs(8));
        } else if (charSelectState.step === 1) {
            drawText('Choose your world:', panelX + inPad, y, '#c0c0e0', labelFS);
            y += Math.round(26 * ui.s);
            for (let i = 0; i < WORLDS.length; i++) {
                const sel = i === charSelectState.worldIndex;
                if (sel) {
                    ctx.fillStyle = 'rgba(80,80,160,0.3)';
                    ctx.fillRect(panelX + inPad, y - 10, panelW - inPad * 2, Math.round(28 * ui.s));
                    drawCursor(panelX + inPad + 4, y + 5);
                }
                drawText(WORLDS[i], panelX + inPad + 24, y + 5, sel ? '#fff' : '#8080c0', optFS);
                y += optGap;
            }
        } else if (charSelectState.step === 2) {
            const world = WORLDS[charSelectState.worldIndex];
            const industries = INDUSTRIES[world] || ['General'];
            drawText('Industry (' + world + '):', panelX + inPad, y, '#c0c0e0', labelFS);
            y += Math.round(26 * ui.s);
            for (let i = 0; i < industries.length; i++) {
                const sel = i === charSelectState.industryIndex;
                if (sel) {
                    ctx.fillStyle = 'rgba(80,80,160,0.3)';
                    ctx.fillRect(panelX + inPad, y - 10, panelW - inPad * 2, Math.round(28 * ui.s));
                    drawCursor(panelX + inPad + 4, y + 5);
                }
                drawText(industries[i], panelX + inPad + 24, y + 5, sel ? '#fff' : '#8080c0', optFS);
                y += optGap;
            }
        } else if (charSelectState.step === 3) {
            drawText('Choose career path:', panelX + inPad, y, '#c0c0e0', labelFS);
            y += Math.round(26 * ui.s);
            for (let i = 0; i < CAREERS.length; i++) {
                const sel = i === charSelectState.careerIndex;
                if (sel) {
                    ctx.fillStyle = 'rgba(80,80,160,0.3)';
                    ctx.fillRect(panelX + inPad, y - 10, panelW - inPad * 2, Math.round(28 * ui.s));
                    drawCursor(panelX + inPad + 4, y + 5);
                }
                drawText(CAREERS[i].charAt(0).toUpperCase() + CAREERS[i].slice(1), panelX + inPad + 24, y + 5, sel ? '#fff' : '#8080c0', optFS);
                y += optGap;
            }
        } else if (charSelectState.step === 4) {
            const world = WORLDS[charSelectState.worldIndex];
            const charKeys = getCharacterOptions(world);
            const charNames = getCharacterNames(world);
            drawText('Choose your character:', panelX + inPad, y, '#c0c0e0', labelFS);
            y += Math.round(22 * ui.s);

            const previewSize = ui.previewSize;
            const spacing = ui.previewSpacing;
            const totalW = charKeys.length * (previewSize + spacing) - spacing;
            const startX = cx - totalW / 2;

            for (let i = 0; i < charKeys.length; i++) {
                const sel = i === charSelectState.characterIndex;
                const px = startX + i * (previewSize + spacing);

                ctx.fillStyle = '#0a0a30';
                ctx.fillRect(px, y, previewSize, previewSize);

                if (sel) {
                    ctx.strokeStyle = '#f0d850';
                    ctx.lineWidth = 3;
                    ctx.strokeRect(px - 4, y - 4, previewSize + 8, previewSize + 8);
                    ctx.fillStyle = 'rgba(240,216,80,0.15)';
                    ctx.fillRect(px, y, previewSize, previewSize);
                } else {
                    ctx.strokeStyle = '#484888';
                    ctx.lineWidth = 1;
                    ctx.strokeRect(px - 2, y - 2, previewSize + 4, previewSize + 4);
                }

                RPGSprites.drawCharacterPreview(ctx, charKeys[i], px, y, previewSize, previewSize);
            }

            y += previewSize + Math.round(14 * ui.s);
            const selName = charNames[charSelectState.characterIndex] || 'Unknown';
            drawText(selName, cx, y, '#f0d850', ui.fs(12), 'center');
            y += Math.round(20 * ui.s);
            drawText(isMobile ? 'Swipe or tap to select' : 'Use LEFT/RIGHT to browse, ENTER to select', cx, y, '#5050a0', ui.fs(8), 'center');
        } else if (charSelectState.step === 5) {
            drawText('Confirm your character:', panelX + inPad, y, '#c0c0e0', labelFS);
            y += Math.round(24 * ui.s);
            const world = WORLDS[charSelectState.worldIndex];
            const industry = (INDUSTRIES[world] || ['General'])[charSelectState.industryIndex];
            const career = CAREERS[charSelectState.careerIndex];
            const charNames = getCharacterNames(world);
            const infoFS = ui.fs(10);
            const infoGap = Math.round(22 * ui.s);
            drawText('Name: ' + charSelectState.name, panelX + inPad + 10, y, '#fff', infoFS); y += infoGap;
            drawText('World: ' + world, panelX + inPad + 10, y, '#fff', infoFS); y += infoGap;
            drawText('Industry: ' + industry, panelX + inPad + 10, y, '#fff', infoFS); y += infoGap;
            drawText('Career: ' + career.charAt(0).toUpperCase() + career.slice(1), panelX + inPad + 10, y, '#fff', infoFS); y += infoGap;
            drawText('Character: ' + (charNames[charSelectState.characterIndex] || 'Hero'), panelX + inPad + 10, y, '#fff', infoFS); y += Math.round(14 * ui.s);

            const charKeys = getCharacterOptions(world);
            const previewKey = charKeys[charSelectState.characterIndex];
            const cpSize = ui.confirmPreview;
            const cpHalf = Math.round(cpSize / 2);
            ctx.fillStyle = '#0a0a30';
            ctx.fillRect(cx - cpHalf, y, cpSize, cpSize);
            ctx.strokeStyle = '#484888';
            ctx.lineWidth = 1;
            ctx.strokeRect(cx - cpHalf - 2, y - 2, cpSize + 4, cpSize + 4);
            RPGSprites.drawCharacterPreview(ctx, previewKey, cx - cpHalf, y, cpSize, cpSize);
            y += cpSize + Math.round(12 * ui.s);

            ctx.fillStyle = 'rgba(80,80,160,0.3)';
            ctx.fillRect(panelX + inPad, y - 10, panelW - inPad * 2, Math.round(30 * ui.s));
            drawCursor(panelX + inPad + 4, y + 5);
            drawText('START ADVENTURE', panelX + inPad + 24, y + 5, '#f0d850', ui.fs(12));
        }

        if (charSelectState.error) {
            drawText(charSelectState.error, cx, h - Math.round(50 * ui.s), '#e84040', ui.fs(9), 'center');
        }

        drawText(isMobile ? 'Tap to select' : 'Click to select   ESC to go back', cx, h - 20, '#4848a0', ui.fs(8), 'center');
    }

    function handleCharSelectKey(key) {
        if (charSelectState.step === 0) {
            if (key === 'Enter') {
                promptForName();
            } else if (key === 'Escape') {
                hideTextInput();
                setState('TITLE');
            }
        } else if (charSelectState.step === 1) {
            if (key === 'ArrowUp' || key === 'w') charSelectState.worldIndex = Math.max(0, charSelectState.worldIndex - 1);
            else if (key === 'ArrowDown' || key === 's') charSelectState.worldIndex = Math.min(WORLDS.length - 1, charSelectState.worldIndex + 1);
            else if (key === 'Enter' || key === ' ') { charSelectState.step = 2; charSelectState.industryIndex = 0; }
            else if (key === 'Escape') { charSelectState.step = 0; promptForName(); }
        } else if (charSelectState.step === 2) {
            const world = WORLDS[charSelectState.worldIndex];
            const industries = INDUSTRIES[world] || ['General'];
            if (key === 'ArrowUp' || key === 'w') charSelectState.industryIndex = Math.max(0, charSelectState.industryIndex - 1);
            else if (key === 'ArrowDown' || key === 's') charSelectState.industryIndex = Math.min(industries.length - 1, charSelectState.industryIndex + 1);
            else if (key === 'Enter' || key === ' ') { charSelectState.step = 3; charSelectState.careerIndex = 0; }
            else if (key === 'Escape') charSelectState.step = 1;
        } else if (charSelectState.step === 3) {
            if (key === 'ArrowUp' || key === 'w') charSelectState.careerIndex = Math.max(0, charSelectState.careerIndex - 1);
            else if (key === 'ArrowDown' || key === 's') charSelectState.careerIndex = Math.min(CAREERS.length - 1, charSelectState.careerIndex + 1);
            else if (key === 'Enter' || key === ' ') { charSelectState.step = 4; charSelectState.characterIndex = 0; }
            else if (key === 'Escape') charSelectState.step = 2;
        } else if (charSelectState.step === 4) {
            const world = WORLDS[charSelectState.worldIndex];
            const charKeys = getCharacterOptions(world);
            if (key === 'ArrowLeft' || key === 'a') charSelectState.characterIndex = Math.max(0, charSelectState.characterIndex - 1);
            else if (key === 'ArrowRight' || key === 'd') charSelectState.characterIndex = Math.min(charKeys.length - 1, charSelectState.characterIndex + 1);
            else if (key === 'ArrowUp' || key === 'w') charSelectState.characterIndex = Math.max(0, charSelectState.characterIndex - 1);
            else if (key === 'ArrowDown' || key === 's') charSelectState.characterIndex = Math.min(charKeys.length - 1, charSelectState.characterIndex + 1);
            else if (key === 'Enter' || key === ' ') charSelectState.step = 5;
            else if (key === 'Escape') charSelectState.step = 3;
        } else if (charSelectState.step === 5) {
            if (key === 'Enter' || key === ' ') {
                const world = WORLDS[charSelectState.worldIndex];
                const industry = (INDUSTRIES[world] || ['General'])[charSelectState.industryIndex];
                const career = CAREERS[charSelectState.careerIndex];
                createPlayer(charSelectState.name.trim(), 'pass', world, industry, career);
            } else if (key === 'Escape') charSelectState.step = 4;
        }
    }

    function handleCharSelectClick(mx, my) {
        const w = window.innerWidth;
        const h = window.innerHeight;
        const cx = w / 2;
        const panelW = ui.charPanelW;
        const panelX = cx - panelW / 2;
        const panelY = Math.round(h * 0.1);
        const inPad = Math.round(20 * ui.s);
        const optGap = ui.optionH;

        let y = panelY + Math.round(20 * ui.s);
        y += ui.stepH * 6 + Math.round(8 * ui.s) + 1 + Math.round(12 * ui.s);

        if (charSelectState.step === 0) {
            promptForName();
            return;
        } else if (charSelectState.step === 1) {
            y += Math.round(26 * ui.s);
            for (let i = 0; i < WORLDS.length; i++) {
                if (mx >= panelX + inPad && mx <= panelX + panelW - inPad && my >= y - 10 && my <= y + 20) {
                    charSelectState.worldIndex = i;
                    charSelectState.step = 2;
                    charSelectState.industryIndex = 0;
                    return;
                }
                y += optGap;
            }
        } else if (charSelectState.step === 2) {
            const world = WORLDS[charSelectState.worldIndex];
            const industries = INDUSTRIES[world] || ['General'];
            y += Math.round(26 * ui.s);
            for (let i = 0; i < industries.length; i++) {
                if (mx >= panelX + inPad && mx <= panelX + panelW - inPad && my >= y - 10 && my <= y + 20) {
                    charSelectState.industryIndex = i;
                    charSelectState.step = 3;
                    charSelectState.careerIndex = 0;
                    return;
                }
                y += optGap;
            }
        } else if (charSelectState.step === 3) {
            y += Math.round(26 * ui.s);
            for (let i = 0; i < CAREERS.length; i++) {
                if (mx >= panelX + inPad && mx <= panelX + panelW - inPad && my >= y - 10 && my <= y + 20) {
                    charSelectState.careerIndex = i;
                    charSelectState.step = 4;
                    charSelectState.characterIndex = 0;
                    return;
                }
                y += optGap;
            }
        } else if (charSelectState.step === 4) {
            const world = WORLDS[charSelectState.worldIndex];
            const charKeys = getCharacterOptions(world);
            y += Math.round(22 * ui.s);
            const previewSize = ui.previewSize;
            const spacing = ui.previewSpacing;
            const totalW = charKeys.length * (previewSize + spacing) - spacing;
            const startX = cx - totalW / 2;
            for (let i = 0; i < charKeys.length; i++) {
                const px = startX + i * (previewSize + spacing);
                if (mx >= px - 4 && mx <= px + previewSize + 4 && my >= y - 4 && my <= y + previewSize + 4) {
                    charSelectState.characterIndex = i;
                    charSelectState.step = 5;
                    return;
                }
            }
        } else if (charSelectState.step === 5) {
            const infoGap = Math.round(22 * ui.s);
            const cpSize = ui.confirmPreview;
            y += Math.round(24 * ui.s) + infoGap * 5 + Math.round(14 * ui.s) + cpSize + Math.round(12 * ui.s);
            if (mx >= panelX + inPad && mx <= panelX + panelW - inPad && my >= y - 10 && my <= y + 20) {
                const world = WORLDS[charSelectState.worldIndex];
                const industry = (INDUSTRIES[world] || ['General'])[charSelectState.industryIndex];
                const career = CAREERS[charSelectState.careerIndex];
                createPlayer(charSelectState.name.trim(), 'pass', world, industry, career);
            }
        }
    }


    function renderLogin() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        const cx = w / 2;

        renderTitleBackground();

        drawText('LOGIN', cx, Math.round(h * 0.12), '#f0d850', ui.fs(16), 'center');

        const panelW = Math.min(Math.round(360 * ui.s), w - 30);
        const panelX = cx - panelW / 2;
        const panelY = Math.round(h * 0.2);
        drawFFBox(panelX, panelY, panelW, Math.round(200 * ui.s));

        let y = panelY + Math.round(30 * ui.s);
        drawText('Welcome back, ' + loginState.playerName, panelX + 20, y, '#c0c0e0', ui.fs(10));
        y += Math.round(40 * ui.s);
        drawText('Enter password:', panelX + 20, y, '#c0c0e0', ui.fs(10));
        y += Math.round(30 * ui.s);
        drawFFBox(panelX + 20, y - 10, panelW - 40, Math.round(36 * ui.s));
        const passDisplay = '*'.repeat(loginState.password.length) + (Math.floor(charSelectState.cursorBlink / 400) % 2 === 0 ? '_' : '');
        drawText(passDisplay, panelX + 32, y + 8, '#fff', ui.fs(12));

        if (loginState.error) {
            drawText(loginState.error, cx, panelY + Math.round(170 * ui.s), '#e84040', ui.fs(9), 'center');
        }

        drawText('ENTER to login   ESC to go back', cx, h - 30, '#4848a0', ui.fs(8), 'center');
    }

    function handleLoginKey(key) {
        if (key === 'Escape') {
            hideTextInput();
            setState('TITLE');
        }
    }


    let pauseCursor = 0;
    const PAUSE_ITEMS = ['Status', 'Skills', 'Items', 'Resume', 'Save & Quit'];

    function renderPauseMenu() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        ctx.fillStyle = 'rgba(0,0,20,0.75)';
        ctx.fillRect(0, 0, w, h);

        const menuW = ui.pauseMenuW;
        const itemGap = Math.round(36 * ui.s);
        const menuH = PAUSE_ITEMS.length * itemGap + Math.round(30 * ui.s);
        const menuX = Math.round(20 * ui.s);
        const menuY = Math.round(40 * ui.s);
        drawFFBox(menuX, menuY, menuW, menuH);

        drawText('MENU', menuX + menuW / 2, menuY + Math.round(20 * ui.s), '#f0d850', ui.fs(14), 'center');
        ctx.textAlign = 'left';

        for (let i = 0; i < PAUSE_ITEMS.length; i++) {
            const iy = menuY + Math.round(46 * ui.s) + i * itemGap;
            if (i === pauseCursor) {
                ctx.fillStyle = 'rgba(80,80,160,0.3)';
                ctx.fillRect(menuX + 8, iy - 8, menuW - 16, Math.round(30 * ui.s));
                drawCursor(menuX + 16, iy + 7);
            }
            drawText(PAUSE_ITEMS[i], menuX + 36, iy + 7, i === pauseCursor ? '#fff' : '#a0a0c0', ui.fs(11));
        }

        const infoX = menuX + menuW + Math.round(16 * ui.s);
        const infoW = w - infoX - Math.round(20 * ui.s);
        if (infoW > Math.round(150 * ui.s)) {
            const infoH = menuH;
            drawFFBox(infoX, menuY, infoW, infoH);
            const infoFS = ui.fs(10);
            const infoSmFS = ui.fs(9);
            const infoGap = Math.round(24 * ui.s);

            if (pauseCursor === 0 && playerData) {
                let y = menuY + Math.round(30 * ui.s);
                drawText('Name: ' + (playerData.name || 'Hero'), infoX + 20, y, '#fff', infoFS); y += infoGap;
                drawText('Title: ' + (playerData.job_title || 'Apprentice'), infoX + 20, y, '#c0c0e0', infoSmFS); y += infoGap;
                drawText('Gold: ' + Number(playerData.cash || 0).toLocaleString(), infoX + 20, y, '#e8c020', infoFS); y += infoGap;
                drawText('Reputation: ' + (playerData.reputation || 0), infoX + 20, y, '#50a0f0', infoFS); y += infoGap;
            } else if (pauseCursor === 1 && playerData && playerData.disciplines) {
                let y = menuY + Math.round(30 * ui.s);
                drawText('Business Skills', infoX + 20, y, '#f0d850', infoFS); y += Math.round(30 * ui.s);
                for (const [name, d] of Object.entries(playerData.disciplines)) {
                    drawText(name, infoX + 20, y, '#c0c0e0', infoSmFS);
                    drawText('Lv.' + (d.level || 1), infoX + infoW - Math.round(60 * ui.s), y, '#50a0f0', infoSmFS);
                    y += Math.round(22 * ui.s);
                }
            } else {
                drawText('Select an option', infoX + 20, menuY + Math.round(50 * ui.s), '#5050a0', infoSmFS);
            }
        }
    }

    function handlePauseKey(key) {
        if (key === 'ArrowUp' || key === 'w') pauseCursor = Math.max(0, pauseCursor - 1);
        else if (key === 'ArrowDown' || key === 's') pauseCursor = Math.min(PAUSE_ITEMS.length - 1, pauseCursor + 1);
        else if (key === 'Enter' || key === ' ') {
            if (PAUSE_ITEMS[pauseCursor] === 'Resume') {
                setState('WORLD');
            } else if (PAUSE_ITEMS[pauseCursor] === 'Save & Quit') {
                RPGEngine.stop();
                playerData = null;
                fetchPlayers();
                setState('TITLE');
            } else if (PAUSE_ITEMS[pauseCursor] === 'Status') {
                fetchPlayerStats();
            }
        }
        else if (key === 'Escape') setState('WORLD');
    }

    function handlePauseClick(mx, my) {
        const menuX = Math.round(20 * ui.s);
        const menuW = ui.pauseMenuW;
        const menuY = Math.round(40 * ui.s);
        const itemGap = Math.round(36 * ui.s);
        for (let i = 0; i < PAUSE_ITEMS.length; i++) {
            const iy = menuY + Math.round(46 * ui.s) + i * itemGap;
            if (mx >= menuX && mx <= menuX + menuW && my >= iy - 8 && my <= iy + 28) {
                pauseCursor = i;
                handlePauseKey('Enter');
                return;
            }
        }
    }


    let battleState = null;

    function startBattle(discipline, scenarioData) {
        battleState = {
            phase: 'intro',
            discipline: discipline,
            scenario: scenarioData,
            question: scenarioData,
            playerHP: 100,
            playerMaxHP: 100,
            enemyHP: 100,
            enemyMaxHP: 100,
            enemyName: discipline + ' Challenge',
            choiceIndex: 0,
            choices: [],
            timer: 0,
            result: null,
            particles: [],
            shakeTimer: 0,
            flashTimer: 0
        };

        if (scenarioData && scenarioData.choices) {
            battleState.choices = Object.keys(scenarioData.choices);
        }
        battleState.phase = 'question';
        setState('BATTLE');
    }

    function updateBattle(dt) {
        if (!battleState) return;
        battleState.timer += dt;
        if (battleState.shakeTimer > 0) battleState.shakeTimer -= dt;
        if (battleState.flashTimer > 0) battleState.flashTimer -= dt;

        for (let i = battleState.particles.length - 1; i >= 0; i--) {
            const p = battleState.particles[i];
            p.x += p.vx * dt / 16;
            p.y += p.vy * dt / 16;
            p.life -= dt;
            if (p.life <= 0) battleState.particles.splice(i, 1);
        }
    }

    function renderBattle() {
        if (!battleState) return;
        const w = window.innerWidth;
        const h = window.innerHeight;
        const shake = battleState.shakeTimer > 0 ? (Math.random() - 0.5) * 6 : 0;

        ctx.save();
        ctx.translate(shake, shake);

        const grd = ctx.createLinearGradient(0, 0, 0, h);
        grd.addColorStop(0, '#181840');
        grd.addColorStop(0.5, '#101030');
        grd.addColorStop(1, '#080820');
        ctx.fillStyle = grd;
        ctx.fillRect(0, 0, w, h);

        for (let i = 0; i < 5; i++) {
            const gy = h * 0.4 + i * h * 0.12;
            ctx.fillStyle = `rgba(40,60,40,${0.15 + i * 0.05})`;
            ctx.fillRect(0, gy, w, h * 0.12);
        }

        if (battleState.flashTimer > 0) {
            ctx.fillStyle = '#fff';
            ctx.globalAlpha = battleState.flashTimer / 300;
            ctx.fillRect(0, 0, w, h);
            ctx.globalAlpha = 1;
        }

        const battleTS = Math.round(96 * ui.s);
        const battleYOFF = Math.round(64 * ui.s);
        const playerSpriteX = w * 0.18;
        const playerSpriteY = h * 0.28;
        RPGSprites.drawSprite(ctx, gameTime, 'hero', playerSpriteX, playerSpriteY, 'right', 0, false, undefined, undefined, battleTS, battleYOFF);

        const enemySpriteX = w * 0.68;
        const enemySpriteY = h * 0.24;
        RPGSprites.drawSprite(ctx, gameTime, 'npc', enemySpriteX, enemySpriteY, 'left', 0, false, '#cc4444', (battleState.discipline || '').length, battleTS, battleYOFF);

        const barW = ui.battleBarW;
        const barH = Math.round(16 * ui.s);
        const boxPad = Math.round(10 * ui.s);
        const boxH = Math.round(60 * ui.s);
        drawFFBox(boxPad, boxPad, barW + Math.round(40 * ui.s), boxH);
        drawText(playerData ? playerData.name || 'Hero' : 'Hero', boxPad + 10, boxPad + Math.round(16 * ui.s), '#fff', ui.fs(10));
        drawHealthBar(boxPad + 10, boxPad + Math.round(30 * ui.s), barW, barH, battleState.playerHP, battleState.playerMaxHP, '#40c040');

        const eBoxW = barW + Math.round(40 * ui.s);
        drawFFBox(w - eBoxW - boxPad, boxPad, eBoxW, boxH);
        drawText(battleState.enemyName, w - eBoxW - boxPad + 10, boxPad + Math.round(16 * ui.s), '#fff', ui.fs(10));
        drawHealthBar(w - eBoxW - boxPad + 10, boxPad + Math.round(30 * ui.s), barW, barH, battleState.enemyHP, battleState.enemyMaxHP, '#e04040');

        if (battleState.phase === 'question') {
            renderBattleQuestion();
        } else if (battleState.phase === 'result') {
            renderBattleResult();
        }

        for (const p of battleState.particles) {
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.life / p.maxLife;
            ctx.fillRect(p.x, p.y, p.size, p.size);
        }
        ctx.globalAlpha = 1;

        ctx.restore();
    }

    function drawHealthBar(x, y, w, h, hp, maxHp, color) {
        ctx.fillStyle = '#101040';
        ctx.fillRect(x, y, w, h);
        const pct = Math.max(0, hp / maxHp);
        ctx.fillStyle = color;
        ctx.fillRect(x, y, Math.round(w * pct), h);
        ctx.fillStyle = 'rgba(255,255,255,0.25)';
        ctx.fillRect(x, y, Math.round(w * pct), h / 2);
        ctx.strokeStyle = '#a0a0d0';
        ctx.lineWidth = 1;
        ctx.strokeRect(x, y, w, h);
        drawText(hp + '/' + maxHp, x + w / 2, y + h / 2, '#fff', ui.fs(8), 'center');
        ctx.textAlign = 'left';
    }

    function renderBattleQuestion() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        const qBoxH = Math.min(h * 0.45, Math.round(300 * ui.s));
        const qBoxY = h - qBoxH - 10;
        const qBoxW = w - 20;
        drawFFBox(10, qBoxY, qBoxW, qBoxH);

        let y = qBoxY + Math.round(20 * ui.s);
        if (battleState.question && battleState.question.scenario_text) {
            y = wrapText(battleState.question.scenario_text, 30, y, qBoxW - 60, Math.round(18 * ui.s), '#c0c0e0', ui.fs(9));
            y += Math.round(24 * ui.s);
        }

        if (battleState.choices.length > 0) {
            for (let i = 0; i < battleState.choices.length; i++) {
                const sel = i === battleState.choiceIndex;
                if (sel) {
                    ctx.fillStyle = 'rgba(80,80,160,0.3)';
                    ctx.fillRect(20, y - 8, qBoxW - 40, Math.round(26 * ui.s));
                    drawCursor(26, y + 5);
                }
                const choiceKey = battleState.choices[i];
                const choiceText = battleState.question.choices[choiceKey] || choiceKey;
                const displayText = choiceKey.toUpperCase() + ': ' + (typeof choiceText === 'string' ? choiceText : (choiceText.text || choiceKey));
                wrapText(displayText, 46, y + 5, qBoxW - 80, Math.round(18 * ui.s), sel ? '#fff' : '#8080c0', ui.fs(9));
                y += Math.round(30 * ui.s);
            }
        }
    }

    function renderBattleResult() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        const rBoxW = ui.resultBoxW;
        const rBoxH = ui.resultBoxH;
        const rBoxX = (w - rBoxW) / 2;
        const rBoxY = (h - rBoxH) / 2;
        drawFFBox(rBoxX, rBoxY, rBoxW, rBoxH);

        if (!battleState.result) return;
        const r = battleState.result;
        const isWin = r.success;

        let y = rBoxY + Math.round(30 * ui.s);
        drawText(isWin ? 'VICTORY!' : 'DEFEATED', rBoxX + rBoxW / 2, y, isWin ? '#f0d850' : '#e84040', ui.fs(16), 'center');
        y += Math.round(30 * ui.s);

        if (r.feedback) {
            y = wrapText(r.feedback, rBoxX + 20, y, rBoxW - 40, Math.round(18 * ui.s), '#c0c0e0', ui.fs(9));
            y += Math.round(30 * ui.s);
        }
        if (r.exp_gained) { drawText('+' + r.exp_gained + ' EXP', rBoxX + rBoxW / 2, y, '#40d840', ui.fs(11), 'center'); y += Math.round(24 * ui.s); }
        if (r.cash_change) { drawText((r.cash_change > 0 ? '+' : '') + r.cash_change + ' Gold', rBoxX + rBoxW / 2, y, '#e8c020', ui.fs(11), 'center'); y += Math.round(24 * ui.s); }

        drawText(isMobile ? 'Tap to continue' : 'Press ENTER to continue', rBoxX + rBoxW / 2, rBoxY + rBoxH - Math.round(24 * ui.s), '#5050a0', ui.fs(8), 'center');
        ctx.textAlign = 'left';
    }

    function handleBattleKey(key) {
        if (!battleState) return;
        if (battleState.phase === 'question') {
            if (key === 'ArrowUp' || key === 'w') battleState.choiceIndex = Math.max(0, battleState.choiceIndex - 1);
            else if (key === 'ArrowDown' || key === 's') battleState.choiceIndex = Math.min(battleState.choices.length - 1, battleState.choiceIndex + 1);
            else if (key === 'Enter' || key === ' ') {
                submitBattleChoice();
            }
        } else if (battleState.phase === 'result') {
            if (key === 'Enter' || key === ' ') {
                fetchPlayerStats();
                battleState = null;
                setState('WORLD');
            }
        }
    }

    function handleBattleClick(mx, my) {
        if (!battleState) return;
        if (battleState.phase === 'result') {
            handleBattleKey('Enter');
            return;
        }
        if (battleState.phase === 'question' && battleState.choices.length > 0) {
            const w = window.innerWidth;
            const h = window.innerHeight;
            const qBoxH = Math.min(h * 0.45, Math.round(300 * ui.s));
            const qBoxY = h - qBoxH - 10;
            const qBoxW = w - 20;

            let y = qBoxY + Math.round(20 * ui.s);
            if (battleState.question && battleState.question.scenario_text) {
                const charW = ui.fs(9) * 0.65;
                const charsPerLine = Math.max(1, Math.floor((qBoxW - 60) / charW));
                const textLines = Math.ceil(battleState.question.scenario_text.length / charsPerLine);
                y += textLines * Math.round(18 * ui.s) + Math.round(24 * ui.s);
            }

            const choiceGap = Math.round(30 * ui.s);
            for (let i = 0; i < battleState.choices.length; i++) {
                if (mx >= 20 && mx <= 20 + qBoxW - 40 && my >= y - 8 && my <= y + 22) {
                    battleState.choiceIndex = i;
                    submitBattleChoice();
                    return;
                }
                y += choiceGap;
            }
        }
    }

    async function submitBattleChoice() {
        if (!battleState || !battleState.question) return;
        const choiceKey = battleState.choices[battleState.choiceIndex];
        try {
            const r = await fetch('/api/choose/' + battleState.question.scenario_id + '/' + choiceKey, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken }
            });
            const d = await r.json();
            if (d.result) {
                battleState.result = d.result;
                if (d.result.success) {
                    battleState.enemyHP = 0;
                    battleState.flashTimer = 300;
                    spawnParticles(window.innerWidth * 0.7, window.innerHeight * 0.35, '#f0d850', 20);
                } else {
                    battleState.playerHP = Math.max(10, battleState.playerHP - 30);
                    battleState.shakeTimer = 300;
                    spawnParticles(window.innerWidth * 0.2, window.innerHeight * 0.4, '#e84040', 15);
                }
                battleState.phase = 'result';
                if (d.stats) playerData = { ...playerData, ...d.stats };
            }
        } catch(e) {
            battleState.result = { success: false, feedback: 'Connection error' };
            battleState.phase = 'result';
        }
    }

    function spawnParticles(x, y, color, count) {
        if (!battleState) return;
        for (let i = 0; i < count; i++) {
            battleState.particles.push({
                x, y,
                vx: (Math.random() - 0.5) * 5,
                vy: (Math.random() - 0.5) * 5 - 2,
                size: 2 + Math.random() * 4,
                color: color,
                life: 600 + Math.random() * 400,
                maxLife: 1000
            });
        }
    }


    function onNPCInteract(npc) {
        if (npc.action && npc.route) {
            const discipline = npc.route.replace('/scenarios/', '');
            loadAndStartBattle(discipline);
        }
    }

    async function loadAndStartBattle(discipline) {
        try {
            const r = await fetch('/api/scenarios/' + encodeURIComponent(discipline));
            const d = await r.json();
            const scenarios = d.scenarios || [];
            const available = scenarios.filter(s => !s.is_completed);
            if (available.length > 0) {
                const scenarioId = available[0].scenario_id;
                const pr = await fetch('/api/play/' + scenarioId);
                const pd = await pr.json();
                if (pd.scenario) {
                    startBattle(discipline, pd.scenario);
                } else {
                    RPGEngine.showDialogue(['No quests available right now. Come back later!'], 'System');
                }
            } else {
                RPGEngine.showDialogue(['All quests completed in this discipline! Great work!'], 'System');
            }
        } catch(e) {
            RPGEngine.showDialogue(['Connection error. Please try again.'], 'System');
        }
    }

    function onMapTransition(target, spawnX, spawnY) {
        const map = RPGMaps.getMap(target);
        RPGEngine.loadMap(map, spawnX, spawnY);
    }


    return { init, startBattle };
})();
