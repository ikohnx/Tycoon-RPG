window.RPGTiles = (function() {
    const _cache = {};
    let _ctx;
    const ANIMATED_TILES = {3: true, 17: true, 18: true, 19: true, 24: true, 28: true};

    function seed(r, c) { return ((r * 7919 + c * 104729 + 13) % 256) / 256; }

    function drawGrassBase(x, y, S, row, col) {
        const s = seed(row, col);
        const g1 = s < 0.5 ? '#2d8c2d' : '#2a842a';
        const g2 = s < 0.5 ? '#258025' : '#237a23';
        _ctx.fillStyle = g1;
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        for (let i = 0; i < 8; i++) {
            for (let j = 0; j < 8; j++) {
                const v = seed(row * 8 + i, col * 8 + j);
                if (v < 0.3) {
                    _ctx.fillStyle = g2;
                    _ctx.fillRect(x + j * p, y + i * p, p, p);
                } else if (v > 0.85) {
                    _ctx.fillStyle = '#35a035';
                    _ctx.fillRect(x + j * p, y + i * p, p, p);
                }
            }
        }
        if (s > 0.7) {
            _ctx.fillStyle = '#3aaa3a';
            const bx = Math.floor(s * 5) * p + p;
            _ctx.fillRect(x + bx, y + p * 3, p, p * 2);
        }
    }

    function drawGrass(x, y, S, row, col) { drawGrassBase(x, y, S, row, col); }

    function drawGrass2(x, y, S, row, col) {
        drawGrassBase(x, y, S, row, col);
        const p = S / 8;
        const s = seed(row, col);
        _ctx.fillStyle = '#7a7a72';
        _ctx.fillRect(x + Math.floor(s * 6) * p, y + p * 2, p, p);
        _ctx.fillRect(x + Math.floor(s * 4 + 2) * p, y + p * 5, p, p);
    }

    function drawGrass3(x, y, S, row, col) {
        const s = seed(row, col);
        _ctx.fillStyle = '#1e6e1e';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        for (let i = 0; i < 8; i++)
            for (let j = 0; j < 8; j++) {
                const v = seed(row * 8 + i + 100, col * 8 + j + 100);
                if (v < 0.25) { _ctx.fillStyle = '#1a621a'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
                else if (v > 0.8) { _ctx.fillStyle = '#267826'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
            }
        _ctx.fillStyle = '#8a6a30';
        if (s > 0.3) _ctx.fillRect(x + p * 2, y + p * 6, p, p);
        if (s > 0.5) _ctx.fillRect(x + p * 5, y + p * 3, p, p);
    }

    function drawPath(x, y, S, row, col) {
        _ctx.fillStyle = '#c8a868';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        for (let i = 0; i < 8; i++)
            for (let j = 0; j < 8; j++) {
                const v = seed(row * 8 + i + 50, col * 8 + j + 50);
                if (v < 0.2) { _ctx.fillStyle = '#b89858'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
                else if (v > 0.85) { _ctx.fillStyle = '#d8b878'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
                else if (v > 0.78) { _ctx.fillStyle = '#c0a060'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
            }
        _ctx.fillStyle = '#a08848';
        _ctx.fillRect(x, y, S, p);
        _ctx.fillRect(x, y + S - p, S, p);
    }

    function drawWater(x, y, S, row, col, gt) {
        const t = (gt || 0) / 1000;
        _ctx.fillStyle = '#1858a0';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        for (let i = 0; i < 8; i++)
            for (let j = 0; j < 8; j++) {
                const wave = Math.sin(t * 2 + i * 0.8 + j * 0.5 + row + col) * 0.5 + 0.5;
                if (wave > 0.7) { _ctx.fillStyle = '#2070b8'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
                else if (wave < 0.2) { _ctx.fillStyle = '#104888'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
            }
        _ctx.fillStyle = 'rgba(180,220,255,0.15)';
        const wx = Math.sin(t * 1.5 + row) * S * 0.2;
        _ctx.fillRect(x + S * 0.2 + wx, y + p * 2, S * 0.3, p);
        _ctx.fillRect(x + S * 0.4 - wx, y + p * 5, S * 0.25, p);
    }

    function drawWall(x, y, S) {
        _ctx.fillStyle = '#8a7058';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#786048';
        for (let i = 0; i < 4; i++) {
            const off = (i % 2) * 4;
            for (let j = 0; j < 8; j += 4) {
                _ctx.strokeStyle = '#685040';
                _ctx.lineWidth = 1;
                _ctx.strokeRect(x + (j + off) % 8 * p, y + i * p * 2, p * 4, p * 2);
            }
        }
        _ctx.fillStyle = '#9a8068';
        _ctx.fillRect(x + p, y + p, p, p);
        _ctx.fillRect(x + p * 5, y + p * 3, p, p);
        _ctx.fillRect(x + p * 3, y + p * 5, p, p);
    }

    function drawWallTop(x, y, S) {
        _ctx.fillStyle = '#706050';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#605040';
        _ctx.fillRect(x, y, S, p * 2);
        _ctx.fillStyle = '#807060';
        _ctx.fillRect(x + p * 2, y + p, p, p);
        _ctx.fillRect(x + p * 5, y + p, p, p);
        _ctx.fillStyle = '#685848';
        for (let j = 0; j < 8; j += 2) _ctx.fillRect(x + j * p, y + p * 3, p * 2, p);
    }

    function drawRoof(x, y, S) {
        _ctx.fillStyle = '#b04828';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        for (let i = 0; i < 8; i++) {
            const shade = i % 2 === 0 ? '#a04020' : '#c05830';
            _ctx.fillStyle = shade;
            _ctx.fillRect(x, y + i * p, S, p);
        }
        _ctx.fillStyle = '#983818';
        _ctx.fillRect(x, y, p, S);
        _ctx.fillRect(x + S - p, y, p, S);
        _ctx.fillStyle = '#d06838';
        _ctx.fillRect(x + p * 3, y + p, p * 2, p);
        _ctx.fillRect(x + p * 2, y + p * 4, p * 2, p);
    }

    function drawDoor(x, y, S) {
        drawWall(x, y, S);
        const p = S / 8;
        _ctx.fillStyle = '#604020';
        _ctx.fillRect(x + p, y + p, p * 6, p * 7);
        _ctx.fillStyle = '#503018';
        _ctx.fillRect(x + p * 2, y + p * 2, p * 4, p * 5);
        _ctx.fillStyle = '#805030';
        _ctx.fillRect(x + p * 2, y + p * 2, p * 4, p);
        _ctx.fillStyle = '#c0a030';
        _ctx.fillRect(x + p * 5, y + p * 4, p, p);
    }

    function drawWindow(x, y, S) {
        drawWall(x, y, S);
        const p = S / 8;
        _ctx.fillStyle = '#405880';
        _ctx.fillRect(x + p, y + p, p * 6, p * 5);
        _ctx.fillStyle = '#5878a8';
        _ctx.fillRect(x + p * 2, y + p * 2, p * 2, p);
        _ctx.fillStyle = '#6888b8';
        _ctx.fillRect(x + p * 4, y + p * 2, p * 2, p);
        _ctx.fillStyle = '#384868';
        _ctx.fillRect(x + p * 3 + 1, y + p, 1, p * 5);
        _ctx.fillRect(x + p, y + p * 3, p * 6, 1);
        _ctx.fillStyle = '#786858';
        _ctx.fillRect(x + p, y + p * 6, p * 6, p);
    }

    function drawTree(x, y, S, row, col) {
        const p = S / 8;
        const s = seed(row, col);
        _ctx.fillStyle = '#1a5c1a';
        _ctx.fillRect(x, y, S, S);
        _ctx.fillStyle = '#0e4a0e';
        _ctx.beginPath();
        _ctx.arc(x + S / 2, y + S / 2, S * 0.48, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = '#1a6a1a';
        _ctx.beginPath();
        _ctx.arc(x + S * 0.4, y + S * 0.4, S * 0.32, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = '#228a22';
        _ctx.beginPath();
        _ctx.arc(x + S * 0.55, y + S * 0.35, S * 0.22, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = '#2a9a2a';
        _ctx.fillRect(x + p * 2, y + p * 2, p * 2, p);
        _ctx.fillRect(x + p * 4, y + p * 3, p, p);
        if (s > 0.5) {
            _ctx.fillStyle = '#30a830';
            _ctx.fillRect(x + p * 3, y + p, p, p);
        }
        _ctx.fillStyle = '#0a3a0a';
        _ctx.fillRect(x + p * 5, y + p * 5, p * 2, p * 2);
        _ctx.fillRect(x + p, y + p * 6, p * 2, p);
    }

    function drawFlowers(x, y, S, row, col) {
        drawGrassBase(x, y, S, row, col);
        const p = S / 8;
        const s = seed(row, col);
        const colors = ['#e04040', '#e0d040', '#d050a0', '#4080e0', '#e08030'];
        for (let i = 0; i < 5; i++) {
            const fx = Math.floor(seed(row + i, col + i * 3) * 6 + 1);
            const fy = Math.floor(seed(row + i * 2, col + i) * 6 + 1);
            _ctx.fillStyle = colors[(i + Math.floor(s * 5)) % 5];
            _ctx.fillRect(x + fx * p, y + fy * p, p, p);
            _ctx.fillStyle = '#2a7a2a';
            _ctx.fillRect(x + fx * p, y + (fy + 1) * p, p, Math.min(p, S - (fy + 1) * p));
        }
    }

    function drawWoodFloor(x, y, S) {
        _ctx.fillStyle = '#906838';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        for (let i = 0; i < 8; i++) {
            _ctx.fillStyle = i % 2 === 0 ? '#886030' : '#987040';
            _ctx.fillRect(x, y + i * p, S, p);
        }
        _ctx.fillStyle = '#785828';
        _ctx.fillRect(x + p * 3, y, 1, S);
        _ctx.fillRect(x + p * 6, y, 1, S);
        _ctx.fillStyle = '#a07840';
        _ctx.fillRect(x + p * 2, y + p * 3, p, p);
    }

    function drawSign(x, y, S, row, col) {
        drawGrassBase(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#705028';
        _ctx.fillRect(x + p * 3, y + p * 3, p * 2, p * 5);
        _ctx.fillStyle = '#906838';
        _ctx.fillRect(x + p, y + p, p * 6, p * 3);
        _ctx.fillStyle = '#a07840';
        _ctx.fillRect(x + p * 2, y + p + 1, p * 4, p);
        _ctx.fillStyle = '#604018';
        _ctx.fillRect(x + p, y + p, p * 6, 1);
        _ctx.fillRect(x + p, y + p * 4 - 1, p * 6, 1);
    }

    function drawSand(x, y, S, row, col) {
        _ctx.fillStyle = '#d8c078';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        for (let i = 0; i < 8; i++)
            for (let j = 0; j < 8; j++) {
                const v = seed(row * 8 + i + 200, col * 8 + j + 200);
                if (v < 0.15) { _ctx.fillStyle = '#c8b068'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
                else if (v > 0.9) { _ctx.fillStyle = '#e8d088'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
            }
    }

    function drawStoneFloor(x, y, S) {
        _ctx.fillStyle = '#888890';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#787880';
        for (let i = 0; i < 4; i++) {
            const off = (i % 2) * 2;
            for (let j = off; j < 8; j += 4) {
                _ctx.fillRect(x + j * p, y + i * 2 * p, p * 4, 1);
            }
            _ctx.fillRect(x + (off + 2) * p, y + i * 2 * p, 1, p * 2);
        }
        _ctx.fillStyle = '#989898';
        _ctx.fillRect(x + p * 2, y + p * 2, p, p);
        _ctx.fillRect(x + p * 5, y + p * 5, p, p);
    }

    function drawHedge(x, y, S) {
        _ctx.fillStyle = '#1a5818';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#2a7828';
        _ctx.fillRect(x + p, y + p, p * 6, p * 5);
        _ctx.fillStyle = '#3a8838';
        _ctx.fillRect(x + p * 2, y + p * 2, p * 2, p * 2);
        _ctx.fillRect(x + p * 4, y + p, p * 2, p * 2);
        _ctx.fillStyle = '#124a10';
        _ctx.fillRect(x, y + S - p, S, p);
        _ctx.fillRect(x, y, S, p);
    }

    function drawChest(x, y, S, row, col) {
        drawGrassBase(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#805020';
        _ctx.fillRect(x + p, y + p * 3, p * 6, p * 4);
        _ctx.fillStyle = '#906030';
        _ctx.fillRect(x + p * 2, y + p * 4, p * 4, p * 2);
        _ctx.fillStyle = '#c8a030';
        _ctx.fillRect(x + p * 3, y + p * 5, p * 2, p);
        _ctx.fillStyle = '#604018';
        _ctx.fillRect(x + p, y + p * 3, p * 6, 1);
        _ctx.fillRect(x + p, y + p * 5, p * 6, 1);
        _ctx.fillStyle = '#d8b838';
        _ctx.fillRect(x + p * 3, y + p * 3, p * 2, 1);
    }

    function drawPortal(x, y, S, row, col, gt) {
        const t = (gt || 0) / 1000;
        _ctx.fillStyle = '#181028';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        for (let ring = 3; ring >= 1; ring--) {
            const pulse = Math.sin(t * 3 + ring) * 0.2 + 0.8;
            const r = ring * S * 0.12 * pulse;
            const hue = 260 + ring * 20 + Math.sin(t * 2) * 10;
            _ctx.fillStyle = 'hsl(' + hue + ',70%,' + (40 + ring * 10) + '%)';
            _ctx.beginPath();
            _ctx.arc(x + S / 2, y + S / 2, r, 0, Math.PI * 2);
            _ctx.fill();
        }
        _ctx.fillStyle = 'rgba(200,180,255,' + (Math.sin(t * 4) * 0.2 + 0.4) + ')';
        _ctx.beginPath();
        _ctx.arc(x + S / 2, y + S / 2, S * 0.08, 0, Math.PI * 2);
        _ctx.fill();
    }

    function drawFountain(x, y, S, row, col, gt) {
        drawStoneFloor(x, y, S);
        const t = (gt || 0) / 1000;
        const p = S / 8;
        _ctx.fillStyle = '#607080';
        _ctx.fillRect(x + p, y + p * 2, p * 6, p * 5);
        _ctx.fillStyle = '#2868a0';
        _ctx.fillRect(x + p * 2, y + p * 3, p * 4, p * 3);
        _ctx.fillStyle = '#3878b0';
        const wy = Math.sin(t * 3) * p * 0.3;
        _ctx.fillRect(x + p * 3, y + p * 3 + wy, p * 2, p * 2);
        _ctx.fillStyle = 'rgba(180,220,255,0.5)';
        const sy = Math.sin(t * 4) * p;
        _ctx.fillRect(x + p * 3.5, y + p * 2 + sy, p, p);
        _ctx.fillStyle = '#506878';
        _ctx.fillRect(x + p, y + p * 2, p * 6, p);
    }

    function drawLamp(x, y, S, row, col, gt) {
        drawGrassBase(x, y, S, row, col);
        const p = S / 8;
        const t = (gt || 0) / 1000;
        _ctx.fillStyle = '#484848';
        _ctx.fillRect(x + p * 3, y + p * 3, p * 2, p * 5);
        _ctx.fillStyle = '#585858';
        _ctx.fillRect(x + p * 2, y + p * 7, p * 4, p);
        _ctx.fillStyle = '#404040';
        _ctx.fillRect(x + p * 2, y + p * 2, p * 4, p * 2);
        const flicker = Math.sin(t * 8 + col) * 0.15 + 0.85;
        _ctx.fillStyle = 'rgba(255,200,80,' + (0.7 * flicker) + ')';
        _ctx.beginPath();
        _ctx.arc(x + p * 4, y + p * 2, p * 1.5, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = 'rgba(255,240,150,' + (0.5 * flicker) + ')';
        _ctx.beginPath();
        _ctx.arc(x + p * 4, y + p * 2, p, 0, Math.PI * 2);
        _ctx.fill();
    }

    function drawStall(x, y, S, row, col) {
        drawGrassBase(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#705028';
        _ctx.fillRect(x + p, y + p * 4, p * 6, p * 4);
        _ctx.fillStyle = '#c83030';
        _ctx.fillRect(x, y + p, S, p * 2);
        _ctx.fillStyle = '#e8e8d0';
        _ctx.fillRect(x + p, y + p + 1, p * 2, p);
        _ctx.fillRect(x + p * 4, y + p + 1, p * 2, p);
        _ctx.fillStyle = '#806038';
        _ctx.fillRect(x + p, y + p * 3, p * 6, p);
        _ctx.fillStyle = '#c8a838';
        _ctx.fillRect(x + p * 2, y + p * 5, p, p);
        _ctx.fillRect(x + p * 4, y + p * 5, p, p);
        _ctx.fillStyle = '#40a040';
        _ctx.fillRect(x + p * 3, y + p * 5, p, p);
    }

    function drawBench(x, y, S, row, col) {
        drawGrassBase(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#705028';
        _ctx.fillRect(x + p, y + p * 5, p, p * 2);
        _ctx.fillRect(x + p * 6, y + p * 5, p, p * 2);
        _ctx.fillStyle = '#906838';
        _ctx.fillRect(x + p, y + p * 4, p * 6, p);
        _ctx.fillStyle = '#805830';
        _ctx.fillRect(x + p, y + p * 2, p * 6, p);
        _ctx.fillStyle = '#a07840';
        _ctx.fillRect(x + p * 2, y + p * 4, p * 4, p);
    }

    function drawWell(x, y, S, row, col) {
        drawGrassBase(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#707880';
        _ctx.beginPath();
        _ctx.arc(x + S / 2, y + S * 0.55, S * 0.35, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = '#1858a0';
        _ctx.beginPath();
        _ctx.arc(x + S / 2, y + S * 0.55, S * 0.22, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = '#604828';
        _ctx.fillRect(x + p * 2, y, p, p * 4);
        _ctx.fillRect(x + p * 5, y, p, p * 4);
        _ctx.fillRect(x + p * 2, y, p * 4, p);
        _ctx.fillStyle = '#808888';
        _ctx.fillRect(x + p * 3, y + p, p * 2, p);
    }

    function drawCrates(x, y, S, row, col) {
        drawGrassBase(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#806028';
        _ctx.fillRect(x + p, y + p * 3, p * 4, p * 4);
        _ctx.fillStyle = '#705020';
        _ctx.fillRect(x + p, y + p * 3, p * 4, 1);
        _ctx.fillRect(x + p * 3, y + p * 3, 1, p * 4);
        _ctx.fillStyle = '#906830';
        _ctx.fillRect(x + p * 3, y + p, p * 4, p * 4);
        _ctx.fillStyle = '#805828';
        _ctx.fillRect(x + p * 3, y + p, p * 4, 1);
        _ctx.fillRect(x + p * 5, y + p, 1, p * 4);
        _ctx.fillStyle = '#604018';
        _ctx.fillRect(x + p * 5, y + p * 5, p * 2, p * 2);
        _ctx.fillStyle = '#c0a038';
        _ctx.fillRect(x + p * 2, y + p * 5, p, p);
        _ctx.fillRect(x + p * 5, y + p * 2, p, p);
    }

    function drawFireplace(x, y, S, row, col, gt) {
        drawWall(x, y, S);
        const p = S / 8;
        const t = (gt || 0) / 1000;
        _ctx.fillStyle = '#484040';
        _ctx.fillRect(x + p, y + p * 3, p * 6, p * 5);
        _ctx.fillStyle = '#c04010';
        const fh = Math.sin(t * 6) * p + p * 2;
        _ctx.fillRect(x + p * 2, y + p * 8 - fh, p * 4, fh);
        _ctx.fillStyle = '#e88020';
        _ctx.fillRect(x + p * 3, y + p * 8 - fh + p, p * 2, fh - p);
        _ctx.fillStyle = '#ffe060';
        _ctx.fillRect(x + p * 3, y + p * 6, p * 2, p);
        _ctx.fillStyle = '#585050';
        _ctx.fillRect(x + p, y + p * 2, p * 6, p);
    }

    function drawBookshelf(x, y, S) {
        drawWall(x, y, S);
        const p = S / 8;
        _ctx.fillStyle = '#503820';
        _ctx.fillRect(x + p, y + p, p * 6, p * 6);
        const bookColors = ['#c03030', '#3060c0', '#30a030', '#c0a030', '#8030a0', '#c06020'];
        for (let row = 0; row < 3; row++)
            for (let col = 0; col < 6; col++) {
                _ctx.fillStyle = bookColors[(row * 6 + col) % bookColors.length];
                _ctx.fillRect(x + (col + 1) * p, y + (row * 2 + 1) * p, p, p * 1.5);
            }
        _ctx.fillStyle = '#604828';
        _ctx.fillRect(x + p, y + p * 3, p * 6, 1);
        _ctx.fillRect(x + p, y + p * 5, p * 6, 1);
    }

    function drawCliff(x, y, S) {
        _ctx.fillStyle = '#687078';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#586068';
        _ctx.fillRect(x + p, y + p * 2, p * 3, p * 2);
        _ctx.fillRect(x + p * 5, y + p * 4, p * 2, p * 2);
        _ctx.fillStyle = '#788088';
        _ctx.fillRect(x + p * 4, y + p, p * 3, p);
        _ctx.fillRect(x + p, y + p * 5, p * 2, p);
        _ctx.fillStyle = '#4a5258';
        _ctx.fillRect(x, y + S - p, S, p);
        _ctx.fillRect(x + p * 3, y + p * 3, 1, p * 3);
    }

    function drawCliffTop(x, y, S) {
        _ctx.fillStyle = '#506840';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#607850';
        _ctx.fillRect(x, y, S, p * 3);
        _ctx.fillStyle = '#687078';
        _ctx.fillRect(x, y + p * 5, S, p * 3);
        _ctx.fillStyle = '#588050';
        _ctx.fillRect(x + p * 2, y + p, p * 2, p);
        _ctx.fillRect(x + p * 5, y, p * 2, p);
    }

    function drawWaterfall(x, y, S, row, col, gt) {
        drawCliff(x, y, S);
        const t = (gt || 0) / 1000;
        const p = S / 8;
        const flowY = (t * 80) % S;
        _ctx.fillStyle = '#4090d0';
        _ctx.fillRect(x + p * 2, y, p * 4, S);
        _ctx.fillStyle = '#60b0e0';
        _ctx.fillRect(x + p * 3, y + ((flowY) % S), p * 2, p * 2);
        _ctx.fillRect(x + p * 2, y + ((flowY + S / 2) % S), p * 2, p);
        _ctx.fillStyle = 'rgba(200,230,255,0.4)';
        _ctx.fillRect(x + p * 3, y + ((flowY + S / 3) % S), p, p);
        _ctx.fillStyle = 'rgba(255,255,255,0.3)';
        _ctx.fillRect(x + p * 4, y + ((flowY + S * 0.7) % S), p, p);
    }

    function drawRock(x, y, S, row, col) {
        drawGrassBase(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#686868';
        _ctx.beginPath();
        _ctx.arc(x + S * 0.5, y + S * 0.55, S * 0.3, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = '#787878';
        _ctx.beginPath();
        _ctx.arc(x + S * 0.45, y + S * 0.5, S * 0.2, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = '#585858';
        _ctx.fillRect(x + p * 4, y + p * 5, p * 2, p);
    }

    function drawBridge(x, y, S) {
        _ctx.fillStyle = '#1858a0';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#806030';
        _ctx.fillRect(x, y + p, S, p * 6);
        _ctx.fillStyle = '#906838';
        for (let j = 0; j < 8; j += 2) _ctx.fillRect(x + j * p, y + p * 2, p * 2, p * 4);
        _ctx.fillStyle = '#705028';
        _ctx.fillRect(x, y + p, S, 1);
        _ctx.fillRect(x, y + p * 7 - 1, S, 1);
        _ctx.fillStyle = '#604820';
        for (let j = 1; j < 8; j += 2) _ctx.fillRect(x + j * p, y + p * 3, 1, p * 2);
    }

    function drawCobble(x, y, S) {
        _ctx.fillStyle = '#707880';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#606870';
        for (let i = 0; i < 4; i++) {
            const off = (i % 2) * 3;
            _ctx.fillRect(x + off * p, y + i * p * 2, p * 3, 1);
            _ctx.fillRect(x + (off + 3) * p, y + i * p * 2, 1, p * 2);
        }
        _ctx.fillStyle = '#808890';
        _ctx.fillRect(x + p * 2, y + p, p, p);
        _ctx.fillRect(x + p * 5, y + p * 4, p, p);
        _ctx.fillRect(x + p, y + p * 6, p, p);
    }

    function drawStatue(x, y, S, row, col) {
        drawStoneFloor(x, y, S);
        const p = S / 8;
        _ctx.fillStyle = '#909898';
        _ctx.fillRect(x + p * 2, y + p * 5, p * 4, p * 3);
        _ctx.fillStyle = '#a0a8b0';
        _ctx.fillRect(x + p * 3, y + p, p * 2, p * 5);
        _ctx.fillStyle = '#b0b8c0';
        _ctx.beginPath();
        _ctx.arc(x + p * 4, y + p * 1.5, p * 1.2, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = '#808890';
        _ctx.fillRect(x + p * 2, y + p * 3, p, p * 2);
        _ctx.fillRect(x + p * 5, y + p * 3, p, p * 2);
    }

    function drawFence(x, y, S, row, col) {
        drawGrassBase(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#705028';
        _ctx.fillRect(x + p, y + p * 2, p, p * 5);
        _ctx.fillRect(x + p * 4, y + p * 2, p, p * 5);
        _ctx.fillRect(x + p * 7, y + p * 2, p, p * 5);
        _ctx.fillStyle = '#906838';
        _ctx.fillRect(x, y + p * 3, S, p);
        _ctx.fillRect(x, y + p * 5, S, p);
        _ctx.fillStyle = '#805828';
        _ctx.fillRect(x + p, y + p * 2, p, p);
        _ctx.fillRect(x + p * 4, y + p * 2, p, p);
        _ctx.fillRect(x + p * 7, y + p * 2, p, p);
    }

    function drawDirtGround(x, y, S, row, col) {
        const s = seed(row, col);
        _ctx.fillStyle = '#7a6842';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        for (let i = 0; i < 8; i++)
            for (let j = 0; j < 8; j++) {
                const v = seed(row * 8 + i + 300, col * 8 + j + 300);
                if (v < 0.2) { _ctx.fillStyle = '#6a5832'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
                else if (v > 0.85) { _ctx.fillStyle = '#8a7852'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
            }
        if (s > 0.7) { _ctx.fillStyle = '#5a4828'; _ctx.fillRect(x + p * 3, y + p * 5, p * 2, p); }
    }

    function drawFactoryWall(x, y, S) {
        _ctx.fillStyle = '#3a3030';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#2a2020';
        for (let i = 0; i < 4; i++) {
            const off = (i % 2) * 4;
            for (let j = 0; j < 8; j += 4) {
                _ctx.strokeStyle = '#1a1818';
                _ctx.lineWidth = 1;
                _ctx.strokeRect(x + (j + off) % 8 * p, y + i * p * 2, p * 4, p * 2);
            }
        }
        _ctx.fillStyle = '#484040';
        _ctx.fillRect(x + p * 2, y + p, p, p);
        _ctx.fillRect(x + p * 5, y + p * 4, p, p);
    }

    function drawFactoryRoof(x, y, S) {
        _ctx.fillStyle = '#484048';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        for (let i = 0; i < 8; i++) {
            _ctx.fillStyle = i % 2 === 0 ? '#404038' : '#504848';
            _ctx.fillRect(x, y + i * p, S, p);
        }
        _ctx.fillStyle = '#383030';
        _ctx.fillRect(x, y, p, S);
        _ctx.fillRect(x + S - p, y, p, S);
        _ctx.fillStyle = '#585050';
        _ctx.fillRect(x + p * 3, y + p, p * 2, p);
    }

    function drawFactoryDoor(x, y, S) {
        drawFactoryWall(x, y, S);
        const p = S / 8;
        _ctx.fillStyle = '#282020';
        _ctx.fillRect(x + p, y + p, p * 6, p * 7);
        _ctx.fillStyle = '#201818';
        _ctx.fillRect(x + p * 2, y + p * 2, p * 4, p * 5);
        _ctx.fillStyle = '#c8a030';
        _ctx.fillRect(x + p * 5, y + p * 4, p, p);
        _ctx.fillStyle = '#383030';
        _ctx.fillRect(x + p * 3.5, y + p, 1, p * 7);
    }

    function drawFactoryWindow(x, y, S) {
        drawFactoryWall(x, y, S);
        const p = S / 8;
        _ctx.fillStyle = '#c89030';
        _ctx.fillRect(x + p, y + p, p * 6, p * 5);
        _ctx.fillStyle = '#e8b050';
        _ctx.fillRect(x + p * 2, y + p * 2, p * 2, p);
        _ctx.fillStyle = '#d8a040';
        _ctx.fillRect(x + p * 4, y + p * 2, p * 2, p);
        _ctx.fillStyle = '#282020';
        _ctx.fillRect(x + p * 3.5, y + p, 1, p * 5);
        _ctx.fillRect(x + p, y + p * 3, p * 6, 1);
        _ctx.fillStyle = '#2a2020';
        _ctx.fillRect(x + p, y + p * 6, p * 6, p);
    }

    function drawSmokestack(x, y, S, row, col, gt) {
        drawFactoryRoof(x, y, S);
        const p = S / 8;
        const t = (gt || 0) / 1000;
        _ctx.fillStyle = '#505050';
        _ctx.fillRect(x + p * 2, y, p * 4, S);
        _ctx.fillStyle = '#585858';
        _ctx.fillRect(x + p * 3, y, p * 2, S);
        _ctx.fillStyle = '#404040';
        _ctx.fillRect(x + p * 2, y, p * 4, p);
        _ctx.fillStyle = '#c83020';
        _ctx.fillRect(x + p * 2, y + p * 3, p * 4, p);
        for (let i = 0; i < 3; i++) {
            const sy = -p * (2 + i * 2) - Math.sin(t * 2 + i) * p;
            const sx = Math.sin(t * 1.5 + i * 2) * p;
            const a = 0.4 - i * 0.12;
            _ctx.fillStyle = 'rgba(180,180,180,' + a + ')';
            _ctx.beginPath();
            _ctx.arc(x + p * 4 + sx, y + sy, p * (1.5 + i * 0.5), 0, Math.PI * 2);
            _ctx.fill();
        }
    }

    function drawRailH(x, y, S, row, col) {
        drawDirtGround(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#484048';
        _ctx.fillRect(x, y + p * 2, S, p);
        _ctx.fillRect(x, y + p * 5, S, p);
        _ctx.fillStyle = '#606060';
        _ctx.fillRect(x, y + p * 2, S, 1);
        _ctx.fillRect(x, y + p * 6 - 1, S, 1);
        _ctx.fillStyle = '#604828';
        for (let j = 0; j < 8; j += 2) {
            _ctx.fillRect(x + j * p + p * 0.3, y + p, p * 0.4, p * 6);
        }
    }

    function drawRailV(x, y, S, row, col) {
        drawDirtGround(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#484048';
        _ctx.fillRect(x + p * 2, y, p, S);
        _ctx.fillRect(x + p * 5, y, p, S);
        _ctx.fillStyle = '#606060';
        _ctx.fillRect(x + p * 2, y, 1, S);
        _ctx.fillRect(x + p * 6 - 1, y, 1, S);
        _ctx.fillStyle = '#604828';
        for (let i = 0; i < 8; i += 2) {
            _ctx.fillRect(x + p, y + i * p + p * 0.3, p * 6, p * 0.4);
        }
    }

    function drawRailCross(x, y, S, row, col) {
        drawDirtGround(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#604828';
        for (let j = 0; j < 8; j += 2) _ctx.fillRect(x + j * p + p * 0.3, y + p, p * 0.4, p * 6);
        for (let i = 0; i < 8; i += 2) _ctx.fillRect(x + p, y + i * p + p * 0.3, p * 6, p * 0.4);
        _ctx.fillStyle = '#484048';
        _ctx.fillRect(x, y + p * 2, S, p);
        _ctx.fillRect(x, y + p * 5, S, p);
        _ctx.fillRect(x + p * 2, y, p, S);
        _ctx.fillRect(x + p * 5, y, p, S);
    }

    function drawDock(x, y, S) {
        _ctx.fillStyle = '#1858a0';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#705028';
        _ctx.fillRect(x, y, S, p * 6);
        _ctx.fillStyle = '#806030';
        for (let j = 0; j < 8; j += 2) _ctx.fillRect(x + j * p, y, p * 2, p * 6);
        _ctx.fillStyle = '#604018';
        for (let j = 1; j < 8; j += 2) _ctx.fillRect(x + j * p, y + p, 1, p * 4);
        _ctx.fillStyle = '#504020';
        _ctx.fillRect(x, y + p * 5, S, p);
    }

    function drawPineTree(x, y, S, row, col) {
        const p = S / 8;
        const s = seed(row, col);
        _ctx.fillStyle = '#1a3a1a';
        _ctx.fillRect(x, y, S, S);
        _ctx.fillStyle = '#483020';
        _ctx.fillRect(x + p * 3, y + p * 5, p * 2, p * 3);
        _ctx.fillStyle = '#1a4a1a';
        _ctx.beginPath();
        _ctx.moveTo(x + S / 2, y + p);
        _ctx.lineTo(x + p * 7, y + p * 5);
        _ctx.lineTo(x + p, y + p * 5);
        _ctx.closePath();
        _ctx.fill();
        _ctx.fillStyle = '#1a5818';
        _ctx.beginPath();
        _ctx.moveTo(x + S / 2, y + p * 2);
        _ctx.lineTo(x + p * 6.5, y + p * 6);
        _ctx.lineTo(x + p * 1.5, y + p * 6);
        _ctx.closePath();
        _ctx.fill();
        if (s > 0.5) {
            _ctx.fillStyle = '#205820';
            _ctx.fillRect(x + p * 2, y + p * 4, p, p);
        }
        _ctx.fillStyle = '#0a2a0a';
        _ctx.fillRect(x + p * 5, y + p * 5, p * 2, p * 2);
        _ctx.fillRect(x + p, y + p * 6, p * 2, p);
    }

    function drawMountain(x, y, S, row, col) {
        _ctx.fillStyle = '#505860';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#404850';
        _ctx.beginPath();
        _ctx.moveTo(x + S / 2, y);
        _ctx.lineTo(x + S, y + S);
        _ctx.lineTo(x, y + S);
        _ctx.closePath();
        _ctx.fill();
        _ctx.fillStyle = '#606870';
        _ctx.beginPath();
        _ctx.moveTo(x + S / 2, y);
        _ctx.lineTo(x + S * 0.65, y + S * 0.4);
        _ctx.lineTo(x + S * 0.35, y + S * 0.4);
        _ctx.closePath();
        _ctx.fill();
        _ctx.fillStyle = '#e0e8f0';
        _ctx.beginPath();
        _ctx.moveTo(x + S / 2, y);
        _ctx.lineTo(x + S * 0.58, y + p * 2);
        _ctx.lineTo(x + S * 0.42, y + p * 2);
        _ctx.closePath();
        _ctx.fill();
        _ctx.fillStyle = '#384048';
        _ctx.fillRect(x + p * 2, y + p * 5, p, p);
        _ctx.fillRect(x + p * 5, y + p * 6, p, p);
    }

    function drawMountainBase(x, y, S, row, col) {
        _ctx.fillStyle = '#485050';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#404848';
        for (let i = 0; i < 8; i++)
            for (let j = 0; j < 8; j++) {
                const v = seed(row * 8 + i + 400, col * 8 + j + 400);
                if (v < 0.2) { _ctx.fillStyle = '#384040'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
                else if (v > 0.8) { _ctx.fillStyle = '#586060'; _ctx.fillRect(x + j * p, y + i * p, p, p); }
            }
        _ctx.fillStyle = '#354040';
        _ctx.fillRect(x + p * 2, y + p * 3, p * 3, p);
    }

    function drawGear(x, y, S, row, col, gt) {
        drawFactoryWall(x, y, S);
        const p = S / 8;
        const t = (gt || 0) / 1000;
        const cx = x + S / 2, cy = y + S / 2;
        const r = S * 0.32;
        _ctx.save();
        _ctx.translate(cx, cy);
        _ctx.rotate(t * 0.5);
        _ctx.fillStyle = '#c89030';
        for (let i = 0; i < 8; i++) {
            const a = (i / 8) * Math.PI * 2;
            _ctx.fillRect(-p * 0.4, -r - p, p * 0.8, p);
            _ctx.save();
            _ctx.rotate(a);
            _ctx.fillRect(-p * 0.4, -r - p, p * 0.8, p);
            _ctx.restore();
        }
        _ctx.beginPath();
        _ctx.arc(0, 0, r, 0, Math.PI * 2);
        _ctx.fillStyle = '#b08020';
        _ctx.fill();
        _ctx.beginPath();
        _ctx.arc(0, 0, r * 0.5, 0, Math.PI * 2);
        _ctx.fillStyle = '#3a3030';
        _ctx.fill();
        _ctx.beginPath();
        _ctx.arc(0, 0, r * 0.2, 0, Math.PI * 2);
        _ctx.fillStyle = '#c89030';
        _ctx.fill();
        _ctx.restore();
    }

    function drawCoalPile(x, y, S, row, col) {
        drawDirtGround(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#181818';
        _ctx.beginPath();
        _ctx.arc(x + S / 2, y + S * 0.55, S * 0.35, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = '#282828';
        _ctx.beginPath();
        _ctx.arc(x + S * 0.45, y + S * 0.5, S * 0.2, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = '#101010';
        _ctx.fillRect(x + p * 4, y + p * 5, p * 2, p);
        _ctx.fillStyle = '#383838';
        _ctx.fillRect(x + p * 2, y + p * 3, p, p);
    }

    function drawIronFence(x, y, S, row, col) {
        drawDirtGround(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#303030';
        _ctx.fillRect(x, y + p * 3, S, p * 0.5);
        _ctx.fillRect(x, y + p * 5, S, p * 0.5);
        for (let j = 1; j < 8; j += 2) {
            _ctx.fillStyle = '#383838';
            _ctx.fillRect(x + j * p, y + p * 2, p * 0.6, p * 5);
            _ctx.fillStyle = '#404040';
            _ctx.fillRect(x + j * p, y + p * 2, p * 0.6, p * 0.6);
        }
    }

    function drawIndustrialLamp(x, y, S, row, col, gt) {
        drawDirtGround(x, y, S, row, col);
        const p = S / 8;
        const t = (gt || 0) / 1000;
        _ctx.fillStyle = '#303030';
        _ctx.fillRect(x + p * 3, y + p * 3, p * 2, p * 5);
        _ctx.fillStyle = '#383838';
        _ctx.fillRect(x + p * 2, y + p * 7, p * 4, p);
        _ctx.fillStyle = '#282828';
        _ctx.fillRect(x + p * 2, y + p * 2, p * 4, p * 2);
        const flicker = Math.sin(t * 8 + col) * 0.15 + 0.85;
        _ctx.fillStyle = 'rgba(255,180,50,' + (0.7 * flicker) + ')';
        _ctx.beginPath();
        _ctx.arc(x + p * 4, y + p * 2, p * 1.5, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = 'rgba(255,220,100,' + (0.5 * flicker) + ')';
        _ctx.beginPath();
        _ctx.arc(x + p * 4, y + p * 2, p, 0, Math.PI * 2);
        _ctx.fill();
    }

    function drawWarehouse(x, y, S) {
        _ctx.fillStyle = '#4a3828';
        _ctx.fillRect(x, y, S, S);
        const p = S / 8;
        _ctx.fillStyle = '#3a2818';
        for (let i = 0; i < 8; i++) {
            _ctx.fillStyle = i % 2 === 0 ? '#3a2818' : '#4a3828';
            _ctx.fillRect(x, y + i * p, S, p);
        }
        _ctx.fillStyle = '#302010';
        _ctx.fillRect(x + p * 3, y + p, 1, p * 6);
        _ctx.fillRect(x + p * 6, y + p, 1, p * 6);
        _ctx.fillStyle = '#c8a030';
        _ctx.fillRect(x + p * 2, y + p * 3, p, p);
        _ctx.fillRect(x + p * 5, y + p * 5, p, p);
    }

    function drawSteamPipe(x, y, S, row, col) {
        drawFactoryWall(x, y, S);
        const p = S / 8;
        _ctx.fillStyle = '#606868';
        _ctx.fillRect(x, y + p * 2, S, p * 2);
        _ctx.fillStyle = '#707878';
        _ctx.fillRect(x, y + p * 2, S, p * 0.5);
        _ctx.fillStyle = '#505858';
        _ctx.fillRect(x, y + p * 4 - p * 0.5, S, p * 0.5);
        _ctx.fillStyle = '#808888';
        for (let j = 2; j < 8; j += 3) {
            _ctx.fillRect(x + j * p, y + p * 1.5, p, p * 3);
        }
    }

    function drawAnvil(x, y, S, row, col) {
        drawDirtGround(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#404040';
        _ctx.fillRect(x + p * 2, y + p * 5, p * 4, p * 2);
        _ctx.fillStyle = '#505050';
        _ctx.fillRect(x + p * 1, y + p * 3, p * 6, p * 2);
        _ctx.fillStyle = '#585858';
        _ctx.fillRect(x + p * 1, y + p * 3, p * 6, p);
        _ctx.fillStyle = '#606060';
        _ctx.fillRect(x + p * 0, y + p * 3, p * 2, p);
        _ctx.fillRect(x + p * 5, y + p * 3, p * 3, p);
        _ctx.fillStyle = '#383838';
        _ctx.fillRect(x + p * 3, y + p * 6, p * 2, p);
    }

    function drawBarrel(x, y, S, row, col) {
        drawDirtGround(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#604020';
        _ctx.beginPath();
        _ctx.ellipse(x + S / 2, y + S / 2, p * 2.5, p * 3, 0, 0, Math.PI * 2);
        _ctx.fill();
        _ctx.fillStyle = '#503018';
        _ctx.fillRect(x + p * 2, y + p * 2, p * 4, p * 4);
        _ctx.fillStyle = '#808080';
        _ctx.fillRect(x + p * 2, y + p * 2.5, p * 4, p * 0.4);
        _ctx.fillRect(x + p * 2, y + p * 5, p * 4, p * 0.4);
        _ctx.fillStyle = '#705028';
        _ctx.fillRect(x + p * 3, y + p * 3, p * 2, p * 2);
    }

    function drawCrane(x, y, S, row, col) {
        drawDirtGround(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#505050';
        _ctx.fillRect(x + p * 3, y + p * 2, p * 2, p * 6);
        _ctx.fillStyle = '#606060';
        _ctx.fillRect(x + p * 2, y + p * 7, p * 4, p);
        _ctx.fillStyle = '#585858';
        _ctx.fillRect(x + p, y + p, p * 6, p);
        _ctx.fillRect(x + p, y + p, p, p * 2);
        _ctx.fillStyle = '#c89030';
        _ctx.fillRect(x + p, y + p * 3, p * 0.5, p * 4);
        _ctx.fillStyle = '#b08020';
        _ctx.fillRect(x + p * 0.5, y + p * 6, p * 1.5, p);
    }

    function drawRailCurveNE(x, y, S, row, col) {
        drawDirtGround(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#604828';
        for (let i = 0; i < 6; i++) {
            const angle = (i / 5) * Math.PI / 2;
            const cx = x + Math.cos(angle) * p * 3 + p * 4;
            const cy = y + S - Math.sin(angle) * p * 3 - p * 4;
            _ctx.fillRect(cx - p * 0.2, cy - p * 0.2, p * 0.4, p * 0.4);
        }
        _ctx.fillStyle = '#484048';
        _ctx.beginPath();
        _ctx.arc(x, y + S, p * 6, -Math.PI / 2, 0);
        _ctx.lineWidth = p;
        _ctx.strokeStyle = '#484048';
        _ctx.stroke();
        _ctx.beginPath();
        _ctx.arc(x, y + S, p * 3, -Math.PI / 2, 0);
        _ctx.stroke();
    }

    function drawRailCurveSE(x, y, S, row, col) {
        drawDirtGround(x, y, S, row, col);
        const p = S / 8;
        _ctx.fillStyle = '#484048';
        _ctx.beginPath();
        _ctx.arc(x, y, p * 6, 0, Math.PI / 2);
        _ctx.lineWidth = p;
        _ctx.strokeStyle = '#484048';
        _ctx.stroke();
        _ctx.beginPath();
        _ctx.arc(x, y, p * 3, 0, Math.PI / 2);
        _ctx.stroke();
    }

    const ANIMATED_IND = {41: true, 47: true, 52: true};

    const DRAW_FN = {
        1: drawGrass, 2: drawPath, 3: drawWater, 4: drawWall,
        5: drawWallTop, 6: drawRoof, 7: drawDoor, 8: drawWindow,
        9: drawTree, 10: drawFlowers, 11: drawWoodFloor, 12: drawSign,
        13: drawSand, 14: drawStoneFloor, 15: drawHedge, 16: drawChest,
        17: drawPortal, 18: drawFountain, 19: drawLamp, 20: drawStall,
        21: drawBench, 22: drawWell, 23: drawCrates, 24: drawFireplace,
        25: drawBookshelf, 26: drawCliff, 27: drawCliffTop, 28: drawWaterfall,
        29: drawRock, 30: drawGrass2, 31: drawGrass3, 32: drawBridge,
        33: drawCobble, 34: drawStatue, 35: drawFence,
        36: drawDirtGround, 37: drawFactoryWall, 38: drawFactoryRoof,
        39: drawFactoryDoor, 40: drawFactoryWindow, 41: drawSmokestack,
        42: drawRailH, 43: drawRailV, 44: drawRailCross,
        45: drawDock, 46: drawPineTree, 47: drawMountain,
        48: drawMountainBase, 49: drawGear, 50: drawCoalPile,
        51: drawIronFence, 52: drawIndustrialLamp, 53: drawWarehouse,
        54: drawSteamPipe, 55: drawAnvil, 56: drawBarrel,
        57: drawCrane, 58: drawRailCurveNE, 59: drawRailCurveSE
    };

    function drawTile(ctx, C, id, x, y, row, col, gt, TS) {
        if (id === 0) return;
        _ctx = ctx;
        const fn = DRAW_FN[id];
        if (fn) {
            ctx.save();
            ctx.beginPath();
            ctx.rect(x, y, TS, TS);
            ctx.clip();
            fn(x, y, TS, row, col, gt);
            ctx.restore();
        }
    }

    return {
        drawTile: drawTile,
        dither: function() {},
        ditherFast: function() {},
        isLoaded: function() { return true; },
        getLoadProgress: function() { return { loaded: 1, total: 1 }; }
    };
})();
