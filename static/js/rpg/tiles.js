window.RPGTiles = (function() {
    const TILE_IMAGES = {};
    let imagesLoaded = 0;
    let totalImages = 0;
    let allLoaded = false;

    const ANIMATED_TILES = {3: true, 17: true, 18: true, 19: true, 24: true, 28: true, 41: true, 49: true, 52: true};

    const TILE_NAMES = {
        1: 'grass', 2: 'path', 3: 'water', 4: 'wall',
        5: 'wall_top', 6: 'roof', 7: 'door', 8: 'window',
        9: 'tree', 10: 'flowers', 11: 'wood_floor', 12: 'sign',
        13: 'sand', 14: 'stone_floor', 15: 'hedge', 16: 'chest',
        17: 'portal', 18: 'fountain', 19: 'lamp', 20: 'stall',
        21: 'bench', 22: 'well', 23: 'crates', 24: 'fireplace',
        25: 'bookshelf', 26: 'cliff', 27: 'cliff_top', 28: 'waterfall',
        29: 'rock', 30: 'grass2', 31: 'grass3', 32: 'bridge',
        33: 'cobble', 34: 'statue', 35: 'fence',
        36: 'dirt', 37: 'factory_wall', 38: 'factory_roof',
        39: 'factory_door', 40: 'factory_window', 41: 'smokestack',
        42: 'rail_h', 43: 'rail_v', 44: 'rail_cross',
        45: 'dock', 46: 'pine_tree', 47: 'mountain',
        48: 'mountain_base', 49: 'gear', 50: 'coal_pile',
        51: 'iron_fence', 52: 'ind_lamp', 53: 'warehouse',
        54: 'steam_pipe', 55: 'anvil', 56: 'barrel',
        57: 'crane', 58: 'rail_curve_ne', 59: 'rail_curve_se'
    };

    function loadAllTiles() {
        const ids = Object.keys(TILE_NAMES);
        totalImages = ids.length;
        ids.forEach(id => {
            const name = TILE_NAMES[id];
            const img = new Image();
            img.onload = function() {
                imagesLoaded++;
                if (imagesLoaded >= totalImages) allLoaded = true;
            };
            img.onerror = function() {
                console.warn('Failed to load tile:', name);
                imagesLoaded++;
                if (imagesLoaded >= totalImages) allLoaded = true;
            };
            img.src = '/static/images/tiles/' + name + '.png';
            TILE_IMAGES[id] = img;
        });
    }

    loadAllTiles();

    function seed(r, c) { return ((r * 7919 + c * 104729 + 13) % 256) / 256; }

    function drawAnimOverlay(ctx, id, x, y, TS, gt) {
        const t = (gt || 0) / 1000;
        if (id === 3) {
            const a = Math.sin(t * 1.5) * 0.12 + 0.15;
            ctx.fillStyle = 'rgba(180,220,255,' + a + ')';
            ctx.fillRect(x, y, TS, TS);
            const waveX = Math.sin(t * 2) * 3;
            ctx.fillStyle = 'rgba(255,255,255,0.08)';
            ctx.fillRect(x + waveX + TS * 0.2, y + TS * 0.3, TS * 0.3, 2);
            ctx.fillRect(x - waveX + TS * 0.5, y + TS * 0.7, TS * 0.25, 2);
        } else if (id === 17) {
            const a = Math.sin(t * 3) * 0.2 + 0.4;
            const r = TS * 0.3 + Math.sin(t * 2) * TS * 0.05;
            ctx.fillStyle = 'rgba(160,80,255,' + a + ')';
            ctx.beginPath();
            ctx.arc(x + TS / 2, y + TS / 2, r, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = 'rgba(200,140,255,' + (a * 0.5) + ')';
            ctx.beginPath();
            ctx.arc(x + TS / 2, y + TS / 2, r * 0.5, 0, Math.PI * 2);
            ctx.fill();
        } else if (id === 18) {
            for (let i = 0; i < 3; i++) {
                const angle = t * 1.5 + i * 2.1;
                const dx = Math.cos(angle) * TS * 0.15;
                const dy = Math.sin(angle) * TS * 0.15 - Math.abs(Math.sin(t * 3 + i)) * TS * 0.1;
                ctx.fillStyle = 'rgba(140,200,255,0.25)';
                ctx.beginPath();
                ctx.arc(x + TS / 2 + dx, y + TS * 0.4 + dy, 2, 0, Math.PI * 2);
                ctx.fill();
            }
            const sa = Math.sin(t * 2) * 0.1 + 0.15;
            ctx.fillStyle = 'rgba(100,180,255,' + sa + ')';
            ctx.beginPath();
            ctx.arc(x + TS / 2, y + TS / 2, TS * 0.25, 0, Math.PI * 2);
            ctx.fill();
        } else if (id === 19 || id === 52) {
            const flicker = Math.sin(t * 8 + x) * 0.15 + 0.85;
            ctx.fillStyle = 'rgba(255,200,80,' + (0.2 * flicker) + ')';
            ctx.beginPath();
            ctx.arc(x + TS / 2, y + TS * 0.3, TS * 0.35, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = 'rgba(255,240,150,' + (0.15 * flicker) + ')';
            ctx.beginPath();
            ctx.arc(x + TS / 2, y + TS * 0.3, TS * 0.2, 0, Math.PI * 2);
            ctx.fill();
        } else if (id === 24) {
            const flicker = Math.sin(t * 10 + 3) * 0.2 + 0.8;
            ctx.fillStyle = 'rgba(255,120,20,' + (0.25 * flicker) + ')';
            ctx.beginPath();
            ctx.arc(x + TS / 2, y + TS * 0.4, TS * 0.3, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = 'rgba(255,200,50,' + (0.15 * flicker) + ')';
            ctx.beginPath();
            ctx.arc(x + TS / 2, y + TS * 0.35, TS * 0.15, 0, Math.PI * 2);
            ctx.fill();
        } else if (id === 28) {
            const a = Math.sin(t * 4) * 0.1 + 0.2;
            ctx.fillStyle = 'rgba(180,220,255,' + a + ')';
            ctx.fillRect(x + TS * 0.3, y, TS * 0.4, TS);
            for (let i = 0; i < 4; i++) {
                const fy = ((t * 60 + i * TS * 0.25) % TS);
                ctx.fillStyle = 'rgba(255,255,255,0.15)';
                ctx.fillRect(x + TS * 0.35 + Math.sin(t + i) * 2, y + fy, TS * 0.1, 3);
            }
        } else if (id === 41) {
            for (let i = 0; i < 3; i++) {
                const sy = -TS * (0.3 + i * 0.25) - Math.sin(t * 2 + i) * TS * 0.1;
                const sx = Math.sin(t * 1.5 + i * 2) * TS * 0.1;
                const sa = 0.3 - i * 0.08;
                ctx.fillStyle = 'rgba(180,180,180,' + sa + ')';
                ctx.beginPath();
                ctx.arc(x + TS / 2 + sx, y + sy, TS * (0.15 + i * 0.05), 0, Math.PI * 2);
                ctx.fill();
            }
        } else if (id === 49) {
            const ga = Math.sin(t * 0.5) * 0.1 + 0.15;
            ctx.fillStyle = 'rgba(200,144,48,' + ga + ')';
            ctx.beginPath();
            ctx.arc(x + TS / 2, y + TS / 2, TS * 0.35, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function drawFallbackTile(ctx, id, x, y, TS, row, col) {
        const colors = {
            1: '#2d8c2d', 2: '#c8a870', 3: '#1858a0', 4: '#8b4513',
            5: '#6b3010', 6: '#b83020', 7: '#604020', 8: '#87CEEB',
            9: '#1a5a1a', 10: '#2d8c2d', 11: '#a08060', 12: '#c8a870',
            13: '#d2b48c', 14: '#808080', 15: '#2d6b2d', 16: '#c8a030',
            17: '#6030a0', 18: '#4080c0', 19: '#c8a030', 20: '#a08060',
            21: '#8b6040', 22: '#808080', 23: '#8b6040', 24: '#8b4513',
            25: '#6b3010', 26: '#606060', 27: '#505050', 28: '#3070c0',
            29: '#808080', 30: '#348c34', 31: '#3a903a', 32: '#a08060',
            33: '#909090', 34: '#c0c0c0', 35: '#604020',
            36: '#7a6842', 37: '#3a3030', 38: '#484048', 39: '#282020',
            40: '#3a3030', 41: '#505050', 42: '#7a6842', 43: '#7a6842',
            44: '#7a6842', 45: '#705028', 46: '#1a4a1a', 47: '#505860',
            48: '#485050', 49: '#3a3030', 50: '#181818', 51: '#303030',
            52: '#7a6842', 53: '#4a3828', 54: '#3a3030', 55: '#404040',
            56: '#604020', 57: '#505050', 58: '#7a6842', 59: '#7a6842'
        };
        ctx.fillStyle = colors[id] || '#ff00ff';
        ctx.fillRect(x, y, TS, TS);
    }

    function drawTile(ctx, C, id, x, y, row, col, gt, TS) {
        if (id === 0) return;

        const img = TILE_IMAGES[id];
        if (img && img.complete && img.naturalWidth > 0) {
            ctx.save();
            ctx.imageSmoothingEnabled = false;
            ctx.drawImage(img, x, y, TS, TS);
            ctx.restore();

            if (ANIMATED_TILES[id]) {
                drawAnimOverlay(ctx, id, x, y, TS, gt);
            }
        } else {
            drawFallbackTile(ctx, id, x, y, TS, row, col);
        }
    }

    return {
        drawTile: drawTile,
        dither: function() {},
        ditherFast: function() {},
        isLoaded: function() { return allLoaded; },
        getLoadProgress: function() { return { loaded: imagesLoaded, total: totalImages }; }
    };
})();
