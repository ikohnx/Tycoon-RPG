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
    const charSelectState = { step: 0, name: '', nameActive: false, cursorBlink: 0, worldIndex: 0, industryIndex: 0, careerIndex: 0 };
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

    const C = RPGColors.C;

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
        fetchCSRF();
        fetchPlayers();
        setState('TITLE');
        running = true;
        lastTime = performance.now();
        requestAnimationFrame(loop);
    }

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        ctx.imageSmoothingEnabled = false;
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
        ctx.fillRect(0, 0, canvas.width, canvas.height);

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
            const map = RPGMaps.getMap('hub');
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
            const r = await fetch('/api/create_player', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ name, password, world, industry, career_path: career })
            });
            const d = await r.json();
            if (d.success) {
                playerData = d.player;
                setState('WORLD');
            } else {
                charSelectState.error = d.error || 'Failed to create character';
            }
        } catch(e) { charSelectState.error = 'Connection error'; }
    }

    async function loginPlayer(playerId, password) {
        try {
            const r = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ player_id: playerId, password: password })
            });
            const d = await r.json();
            if (d.success) {
                playerData = d.player;
                setState('WORLD');
            } else {
                if (d.needs_password) {
                    loginState.playerId = playerId;
                    loginState.playerName = allPlayers.find(p => p.player_id === playerId)?.player_name || 'Player';
                    loginState.password = '';
                    loginState.error = '';
                    loginState.active = true;
                    setState('LOGIN');
                    showTextInput('Enter password for ' + loginState.playerName + ':', 'Password...', 32, true, '', (val) => {
                        loginState.password = val;
                        loginPlayer(loginState.playerId, val);
                        return null;
                    });
                } else {
                    loginState.error = d.error || 'Login failed';
                }
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


    function renderLoading() {
        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        drawText('LOADING...', cx, cy, '#f0d850', 14, 'center');
    }

    function renderTitle() {
        const cx = canvas.width / 2;
        const w = canvas.width;
        const h = canvas.height;

        renderTitleBackground();

        drawText('BUSINESS TYCOON', cx, 80, '#f0d850', 20, 'center');
        drawText('R P G', cx, 115, '#c0a030', 16, 'center');

        ctx.fillStyle = '#8080c0';
        ctx.font = '9px "Press Start 2P", monospace';
        ctx.textAlign = 'center';
        ctx.fillText('Master Business Skills Through Adventure', cx, 150);
        ctx.textAlign = 'left';

        const panelW = 320;
        const panelX = cx - panelW / 2;
        let panelY = 185;

        drawFFBox(panelX, panelY, panelW, 50);
        if (titleCursor === 0) drawCursor(panelX + 14, panelY + 25);
        drawText('NEW ADVENTURE', panelX + 32, panelY + 25, titleCursor === 0 ? '#fff' : '#a0a0c0', 12);

        panelY += 60;
        drawFFBox(panelX, panelY, panelW, 50);
        if (titleCursor === 1) drawCursor(panelX + 14, panelY + 25);
        drawText('CONTINUE QUEST', panelX + 32, panelY + 25, titleCursor === 1 ? '#fff' : '#a0a0c0', 12);

        if (titleCursor === 1 && allPlayers.length > 0) {
            const listY = panelY + 60;
            const listH = Math.min(allPlayers.length * 40 + 20, h - listY - 40);
            drawFFBox(panelX, listY, panelW, listH);

            ctx.save();
            ctx.beginPath();
            ctx.rect(panelX + 4, listY + 4, panelW - 8, listH - 8);
            ctx.clip();

            const visibleCount = Math.floor((listH - 20) / 40);
            if (titlePlayerCursor >= titleScrollOffset + visibleCount) titleScrollOffset = titlePlayerCursor - visibleCount + 1;
            if (titlePlayerCursor < titleScrollOffset) titleScrollOffset = titlePlayerCursor;

            for (let i = titleScrollOffset; i < allPlayers.length && i < titleScrollOffset + visibleCount; i++) {
                const p = allPlayers[i];
                const iy = listY + 14 + (i - titleScrollOffset) * 40;
                if (i === titlePlayerCursor) {
                    ctx.fillStyle = 'rgba(80,80,160,0.3)';
                    ctx.fillRect(panelX + 8, iy - 8, panelW - 16, 36);
                    drawCursor(panelX + 14, iy + 10);
                }
                drawText(p.player_name || 'Player', panelX + 32, iy + 4, i === titlePlayerCursor ? '#fff' : '#c0c0e0', 10);
                drawText((p.chosen_world || p.world || 'Modern') + ' / ' + (p.chosen_industry || p.industry || ''), panelX + 32, iy + 22, '#6868a0', 8);
                drawText('$' + Number(p.total_cash || p.cash || 0).toLocaleString(), panelX + panelW - 24, iy + 4, '#e8c020', 9, 'right');
                ctx.textAlign = 'left';
            }
            ctx.restore();

            if (allPlayers.length > visibleCount) {
                if (titleScrollOffset > 0) drawText('\u25B2', panelX + panelW - 20, listY + 10, '#8080c0', 8);
                if (titleScrollOffset + visibleCount < allPlayers.length) drawText('\u25BC', panelX + panelW - 20, listY + listH - 12, '#8080c0', 8);
            }
        } else if (titleCursor === 1 && allPlayers.length === 0) {
            const listY = panelY + 60;
            drawFFBox(panelX, listY, panelW, 50);
            drawText('No saved games found', panelX + 20, listY + 25, '#6868a0', 9);
        }

        drawText('Click or use \u25B2\u25BC + ENTER', cx, h - 30, '#4848a0', 8, 'center');
    }

    function renderTitleBackground() {
        const w = canvas.width;
        const h = canvas.height;

        for (let r = 0; r < Math.ceil(h / 48) + 1; r++) {
            for (let c = 0; c < Math.ceil(w / 48) + 1; c++) {
                const tileId = (r < 2 || r > Math.ceil(h/48) - 2) ? 9 : ((r + c) % 7 === 0 ? 10 : 1);
                RPGTiles.drawTile(ctx, C, tileId, c * 48, r * 48, r, c, gameTime, 48);
            }
        }

        ctx.fillStyle = 'rgba(0,0,20,0.75)';
        ctx.fillRect(0, 0, w, h);

        const grd = ctx.createLinearGradient(0, 0, 0, 60);
        grd.addColorStop(0, 'rgba(0,0,30,0.9)');
        grd.addColorStop(1, 'transparent');
        ctx.fillStyle = grd;
        ctx.fillRect(0, 0, w, 60);

        const grd2 = ctx.createLinearGradient(0, h - 60, 0, h);
        grd2.addColorStop(0, 'transparent');
        grd2.addColorStop(1, 'rgba(0,0,30,0.9)');
        ctx.fillStyle = grd2;
        ctx.fillRect(0, h - 60, w, 60);
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
                loginPlayer(p.player_id, null);
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
        const cx = canvas.width / 2;
        const panelW = 320;
        const panelX = cx - panelW / 2;
        const firstPanelY = 185;
        const secondPanelY = firstPanelY + 60;

        if (mx >= panelX && mx <= panelX + panelW) {
            if (my >= firstPanelY && my <= firstPanelY + 50) {
                titleCursor = 0;
                handleTitleKey('Enter');
                return;
            } else if (my >= secondPanelY && my <= secondPanelY + 50) {
                if (titleCursor !== 1) {
                    titleCursor = 1;
                    return;
                }
            }
        }

        if (titleCursor === 1 && allPlayers.length > 0) {
            const listY = secondPanelY + 60;
            const listH = Math.min(allPlayers.length * 40 + 20, canvas.height - listY - 40);
            const visibleCount = Math.floor((listH - 20) / 40);
            for (let i = titleScrollOffset; i < allPlayers.length && i < titleScrollOffset + visibleCount; i++) {
                const iy = listY + 14 + (i - titleScrollOffset) * 40;
                if (my >= iy - 8 && my <= iy + 28 && mx >= panelX && mx <= panelX + panelW) {
                    titlePlayerCursor = i;
                    loginPlayer(allPlayers[i].player_id, null);
                    return;
                }
            }
        }
    }


    function renderCharSelect() {
        const cx = canvas.width / 2;
        const h = canvas.height;

        renderTitleBackground();

        drawText('CREATE CHARACTER', cx, 50, '#f0d850', 16, 'center');

        const panelW = 400;
        const panelX = cx - panelW / 2;
        const panelY = 80;
        const panelH = h - 120;
        drawFFBox(panelX, panelY, panelW, panelH);

        let y = panelY + 30;

        const steps = ['Name', 'World', 'Industry', 'Career', 'Confirm'];
        for (let i = 0; i < steps.length; i++) {
            const active = i === charSelectState.step;
            const done = i < charSelectState.step;
            drawText((done ? '\u2713 ' : (i + 1) + '. ') + steps[i], panelX + 20, y, active ? '#f0d850' : (done ? '#40a040' : '#5050a0'), 9);
            y += 22;
        }

        y += 10;
        ctx.fillStyle = '#484888';
        ctx.fillRect(panelX + 16, y, panelW - 32, 1);
        y += 16;

        if (charSelectState.step === 0) {
            drawText('Enter your name:', panelX + 20, y, '#c0c0e0', 10);
            y += 30;
            drawFFBox(panelX + 20, y - 10, panelW - 40, 36);
            if (charSelectState.name) {
                drawText(charSelectState.name, panelX + 32, y + 8, '#fff', 12);
            } else {
                drawText('(click to type)', panelX + 32, y + 8, '#5050a0', 10);
            }
            y += 50;
            drawText('Click anywhere to enter your name', panelX + 20, y, '#5050a0', 8);
        } else if (charSelectState.step === 1) {
            drawText('Choose your world:', panelX + 20, y, '#c0c0e0', 10);
            y += 30;
            for (let i = 0; i < WORLDS.length; i++) {
                const sel = i === charSelectState.worldIndex;
                if (sel) {
                    ctx.fillStyle = 'rgba(80,80,160,0.3)';
                    ctx.fillRect(panelX + 20, y - 10, panelW - 40, 30);
                    drawCursor(panelX + 24, y + 5);
                }
                drawText(WORLDS[i], panelX + 44, y + 5, sel ? '#fff' : '#8080c0', 11);
                y += 34;
            }
        } else if (charSelectState.step === 2) {
            const world = WORLDS[charSelectState.worldIndex];
            const industries = INDUSTRIES[world] || ['General'];
            drawText('Choose industry (' + world + '):', panelX + 20, y, '#c0c0e0', 10);
            y += 30;
            for (let i = 0; i < industries.length; i++) {
                const sel = i === charSelectState.industryIndex;
                if (sel) {
                    ctx.fillStyle = 'rgba(80,80,160,0.3)';
                    ctx.fillRect(panelX + 20, y - 10, panelW - 40, 30);
                    drawCursor(panelX + 24, y + 5);
                }
                drawText(industries[i], panelX + 44, y + 5, sel ? '#fff' : '#8080c0', 11);
                y += 34;
            }
        } else if (charSelectState.step === 3) {
            drawText('Choose career path:', panelX + 20, y, '#c0c0e0', 10);
            y += 30;
            for (let i = 0; i < CAREERS.length; i++) {
                const sel = i === charSelectState.careerIndex;
                if (sel) {
                    ctx.fillStyle = 'rgba(80,80,160,0.3)';
                    ctx.fillRect(panelX + 20, y - 10, panelW - 40, 30);
                    drawCursor(panelX + 24, y + 5);
                }
                drawText(CAREERS[i].charAt(0).toUpperCase() + CAREERS[i].slice(1), panelX + 44, y + 5, sel ? '#fff' : '#8080c0', 11);
                y += 34;
            }
        } else if (charSelectState.step === 4) {
            drawText('Confirm your character:', panelX + 20, y, '#c0c0e0', 10);
            y += 30;
            const world = WORLDS[charSelectState.worldIndex];
            const industry = (INDUSTRIES[world] || ['General'])[charSelectState.industryIndex];
            const career = CAREERS[charSelectState.careerIndex];
            drawText('Name: ' + charSelectState.name, panelX + 30, y, '#fff', 10); y += 24;
            drawText('World: ' + world, panelX + 30, y, '#fff', 10); y += 24;
            drawText('Industry: ' + industry, panelX + 30, y, '#fff', 10); y += 24;
            drawText('Career: ' + career.charAt(0).toUpperCase() + career.slice(1), panelX + 30, y, '#fff', 10); y += 40;

            ctx.fillStyle = 'rgba(80,80,160,0.3)';
            ctx.fillRect(panelX + 20, y - 10, panelW - 40, 30);
            drawCursor(panelX + 24, y + 5);
            drawText('START ADVENTURE', panelX + 44, y + 5, '#f0d850', 12);
        }

        if (charSelectState.error) {
            drawText(charSelectState.error, cx, h - 50, '#e84040', 9, 'center');
        }

        drawText('Click to select   ESC to go back', cx, h - 20, '#4848a0', 8, 'center');
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
            else if (key === 'Enter' || key === ' ') charSelectState.step = 4;
            else if (key === 'Escape') charSelectState.step = 2;
        } else if (charSelectState.step === 4) {
            if (key === 'Enter' || key === ' ') {
                const world = WORLDS[charSelectState.worldIndex];
                const industry = (INDUSTRIES[world] || ['General'])[charSelectState.industryIndex];
                const career = CAREERS[charSelectState.careerIndex];
                createPlayer(charSelectState.name.trim(), 'pass', world, industry, career);
            } else if (key === 'Escape') charSelectState.step = 3;
        }
    }

    function handleCharSelectClick(mx, my) {
        const cx = canvas.width / 2;
        const h = canvas.height;
        const panelW = 400;
        const panelX = cx - panelW / 2;
        const panelY = 80;

        let y = panelY + 30;
        y += 22 * 5 + 10 + 1 + 16;

        if (charSelectState.step === 0) {
            promptForName();
            return;
        } else if (charSelectState.step === 1) {
            y += 30;
            for (let i = 0; i < WORLDS.length; i++) {
                if (mx >= panelX + 20 && mx <= panelX + panelW - 20 && my >= y - 10 && my <= y + 20) {
                    charSelectState.worldIndex = i;
                    charSelectState.step = 2;
                    charSelectState.industryIndex = 0;
                    return;
                }
                y += 34;
            }
        } else if (charSelectState.step === 2) {
            const world = WORLDS[charSelectState.worldIndex];
            const industries = INDUSTRIES[world] || ['General'];
            y += 30;
            for (let i = 0; i < industries.length; i++) {
                if (mx >= panelX + 20 && mx <= panelX + panelW - 20 && my >= y - 10 && my <= y + 20) {
                    charSelectState.industryIndex = i;
                    charSelectState.step = 3;
                    charSelectState.careerIndex = 0;
                    return;
                }
                y += 34;
            }
        } else if (charSelectState.step === 3) {
            y += 30;
            for (let i = 0; i < CAREERS.length; i++) {
                if (mx >= panelX + 20 && mx <= panelX + panelW - 20 && my >= y - 10 && my <= y + 20) {
                    charSelectState.careerIndex = i;
                    charSelectState.step = 4;
                    return;
                }
                y += 34;
            }
        } else if (charSelectState.step === 4) {
            y += 30 + 24 * 4 + 16;
            if (mx >= panelX + 20 && mx <= panelX + panelW - 20 && my >= y - 10 && my <= y + 20) {
                const world = WORLDS[charSelectState.worldIndex];
                const industry = (INDUSTRIES[world] || ['General'])[charSelectState.industryIndex];
                const career = CAREERS[charSelectState.careerIndex];
                createPlayer(charSelectState.name.trim(), 'pass', world, industry, career);
            }
        }
    }


    function renderLogin() {
        const cx = canvas.width / 2;
        const h = canvas.height;

        renderTitleBackground();

        drawText('LOGIN', cx, 80, '#f0d850', 16, 'center');

        const panelW = 360;
        const panelX = cx - panelW / 2;
        const panelY = 120;
        drawFFBox(panelX, panelY, panelW, 200);

        let y = panelY + 30;
        drawText('Welcome back, ' + loginState.playerName, panelX + 20, y, '#c0c0e0', 10);
        y += 40;
        drawText('Enter password:', panelX + 20, y, '#c0c0e0', 10);
        y += 30;
        drawFFBox(panelX + 20, y - 10, panelW - 40, 36);
        const passDisplay = '*'.repeat(loginState.password.length) + (Math.floor(charSelectState.cursorBlink / 400) % 2 === 0 ? '_' : '');
        drawText(passDisplay, panelX + 32, y + 8, '#fff', 12);

        if (loginState.error) {
            drawText(loginState.error, cx, panelY + 170, '#e84040', 9, 'center');
        }

        drawText('ENTER to login   ESC to go back', cx, h - 30, '#4848a0', 8, 'center');
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
        ctx.fillStyle = 'rgba(0,0,20,0.75)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const menuW = 240;
        const menuH = PAUSE_ITEMS.length * 36 + 30;
        const menuX = 40;
        const menuY = 60;
        drawFFBox(menuX, menuY, menuW, menuH);

        drawText('MENU', menuX + menuW / 2, menuY + 20, '#f0d850', 14, 'center');
        ctx.textAlign = 'left';

        for (let i = 0; i < PAUSE_ITEMS.length; i++) {
            const iy = menuY + 46 + i * 36;
            if (i === pauseCursor) {
                ctx.fillStyle = 'rgba(80,80,160,0.3)';
                ctx.fillRect(menuX + 8, iy - 8, menuW - 16, 30);
                drawCursor(menuX + 16, iy + 7);
            }
            drawText(PAUSE_ITEMS[i], menuX + 36, iy + 7, i === pauseCursor ? '#fff' : '#a0a0c0', 11);
        }

        const infoX = menuX + menuW + 20;
        const infoW = canvas.width - infoX - 40;
        if (infoW > 200) {
            const infoH = menuH;
            drawFFBox(infoX, menuY, infoW, infoH);

            if (pauseCursor === 0 && playerData) {
                let y = menuY + 30;
                drawText('Name: ' + (playerData.name || 'Hero'), infoX + 20, y, '#fff', 10); y += 24;
                drawText('Title: ' + (playerData.job_title || 'Apprentice'), infoX + 20, y, '#c0c0e0', 9); y += 24;
                drawText('Gold: ' + Number(playerData.cash || 0).toLocaleString(), infoX + 20, y, '#e8c020', 10); y += 24;
                drawText('Reputation: ' + (playerData.reputation || 0), infoX + 20, y, '#50a0f0', 10); y += 24;
            } else if (pauseCursor === 1 && playerData && playerData.disciplines) {
                let y = menuY + 30;
                drawText('Business Skills', infoX + 20, y, '#f0d850', 10); y += 30;
                for (const [name, d] of Object.entries(playerData.disciplines)) {
                    drawText(name, infoX + 20, y, '#c0c0e0', 9);
                    drawText('Lv.' + (d.level || 1), infoX + infoW - 60, y, '#50a0f0', 9);
                    y += 22;
                }
            } else {
                drawText('Select an option', infoX + 20, menuY + 50, '#5050a0', 9);
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
        const menuX = 40;
        const menuW = 240;
        const menuY = 60;
        for (let i = 0; i < PAUSE_ITEMS.length; i++) {
            const iy = menuY + 46 + i * 36;
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
        const w = canvas.width;
        const h = canvas.height;
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

        const battleTS = 96;
        const battleYOFF = 64;
        const playerSpriteX = w * 0.18;
        const playerSpriteY = h * 0.28;
        RPGSprites.drawSprite(ctx, gameTime, 'hero', playerSpriteX, playerSpriteY, 'right', 0, false, undefined, undefined, battleTS, battleYOFF);

        const enemySpriteX = w * 0.68;
        const enemySpriteY = h * 0.24;
        RPGSprites.drawSprite(ctx, gameTime, 'npc', enemySpriteX, enemySpriteY, 'left', 0, false, '#cc4444', (battleState.discipline || '').length, battleTS, battleYOFF);

        const barW = 200;
        const barH = 16;
        drawFFBox(20, 20, barW + 40, 60);
        drawText(playerData ? playerData.name || 'Hero' : 'Hero', 30, 36, '#fff', 10);
        drawHealthBar(30, 50, barW, barH, battleState.playerHP, battleState.playerMaxHP, '#40c040');

        drawFFBox(w - barW - 60, 20, barW + 40, 60);
        drawText(battleState.enemyName, w - barW - 50, 36, '#fff', 10);
        drawHealthBar(w - barW - 50, 50, barW, barH, battleState.enemyHP, battleState.enemyMaxHP, '#e04040');

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
        drawText(hp + '/' + maxHp, x + w / 2, y + h / 2, '#fff', 8, 'center');
        ctx.textAlign = 'left';
    }

    function renderBattleQuestion() {
        const w = canvas.width;
        const h = canvas.height;
        const qBoxH = Math.min(h * 0.45, 300);
        const qBoxY = h - qBoxH - 10;
        const qBoxW = w - 20;
        drawFFBox(10, qBoxY, qBoxW, qBoxH);

        let y = qBoxY + 24;
        if (battleState.question && battleState.question.scenario_text) {
            y = wrapText(battleState.question.scenario_text, 30, y, qBoxW - 60, 20, '#c0c0e0', 9);
            y += 30;
        }

        if (battleState.choices.length > 0) {
            for (let i = 0; i < battleState.choices.length; i++) {
                const sel = i === battleState.choiceIndex;
                if (sel) {
                    ctx.fillStyle = 'rgba(80,80,160,0.3)';
                    ctx.fillRect(20, y - 8, qBoxW - 40, 26);
                    drawCursor(26, y + 5);
                }
                const choiceKey = battleState.choices[i];
                const choiceText = battleState.question.choices[choiceKey] || choiceKey;
                const displayText = choiceKey.toUpperCase() + ': ' + (typeof choiceText === 'string' ? choiceText : (choiceText.text || choiceKey));
                wrapText(displayText, 46, y + 5, qBoxW - 80, 18, sel ? '#fff' : '#8080c0', 9);
                y += 30;
            }
        }
    }

    function renderBattleResult() {
        const w = canvas.width;
        const h = canvas.height;
        const rBoxW = 400;
        const rBoxH = 250;
        const rBoxX = (w - rBoxW) / 2;
        const rBoxY = (h - rBoxH) / 2;
        drawFFBox(rBoxX, rBoxY, rBoxW, rBoxH);

        if (!battleState.result) return;
        const r = battleState.result;
        const isWin = r.success;

        let y = rBoxY + 30;
        drawText(isWin ? 'VICTORY!' : 'DEFEATED', rBoxX + rBoxW / 2, y, isWin ? '#f0d850' : '#e84040', 16, 'center');
        y += 30;

        if (r.feedback) {
            y = wrapText(r.feedback, rBoxX + 20, y, rBoxW - 40, 18, '#c0c0e0', 9);
            y += 30;
        }
        if (r.exp_gained) { drawText('+' + r.exp_gained + ' EXP', rBoxX + rBoxW / 2, y, '#40d840', 11, 'center'); y += 24; }
        if (r.cash_change) { drawText((r.cash_change > 0 ? '+' : '') + r.cash_change + ' Gold', rBoxX + rBoxW / 2, y, '#e8c020', 11, 'center'); y += 24; }

        drawText('Press ENTER to continue', rBoxX + rBoxW / 2, rBoxY + rBoxH - 24, '#5050a0', 8, 'center');
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
            const w = canvas.width;
            const h = canvas.height;
            const qBoxH = Math.min(h * 0.45, 300);
            const qBoxY = h - qBoxH - 10;
            const qBoxW = w - 20;

            let y = qBoxY + 24;
            if (battleState.question && battleState.question.scenario_text) {
                const textLines = Math.ceil(battleState.question.scenario_text.length / Math.floor((qBoxW - 60) / 8));
                y += textLines * 20 + 30;
            }

            for (let i = 0; i < battleState.choices.length; i++) {
                if (mx >= 20 && mx <= 20 + qBoxW - 40 && my >= y - 8 && my <= y + 22) {
                    battleState.choiceIndex = i;
                    submitBattleChoice();
                    return;
                }
                y += 30;
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
                    spawnParticles(canvas.width * 0.7, canvas.height * 0.35, '#f0d850', 20);
                } else {
                    battleState.playerHP = Math.max(10, battleState.playerHP - 30);
                    battleState.shakeTimer = 300;
                    spawnParticles(canvas.width * 0.2, canvas.height * 0.4, '#e84040', 15);
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
