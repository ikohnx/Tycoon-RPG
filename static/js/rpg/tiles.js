window.RPGTiles = (function() {
    const TILE_IMAGES = {};
    let imagesLoaded = 0;
    let totalImages = 0;
    let allLoaded = false;

    const TILE_NAMES = {
        1: 'grass',
        2: 'path',
        3: 'water',
        4: 'wall',
        5: 'wall_top',
        6: 'roof',
        7: 'door',
        8: 'window',
        9: 'tree',
        10: 'flowers',
        11: 'wood_floor',
        12: 'sign',
        13: 'sand',
        14: 'stone_floor',
        15: 'hedge',
        16: 'chest',
        17: 'portal',
        18: 'fountain',
        19: 'lamp',
        20: 'stall',
        21: 'bench',
        22: 'well',
        23: 'crates',
        24: 'fireplace',
        25: 'bookshelf',
        26: 'cliff',
        27: 'cliff_top',
        28: 'waterfall',
        29: 'rock'
    };

    const ANIMATED_TILES = {3: true, 17: true, 18: true, 19: true, 24: true, 28: true};

    function loadAllTiles() {
        const names = Object.values(TILE_NAMES);
        const unique = [...new Set(names)];
        totalImages = unique.length;

        unique.forEach(name => {
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
            TILE_IMAGES[name] = img;
        });
    }

    loadAllTiles();

    const _cache = {};

    function drawTile(ctx, C, id, x, y, row, col, gt, TS) {
        if (id === 0) return;

        const tileName = TILE_NAMES[id];
        if (!tileName) return;

        const img = TILE_IMAGES[tileName];

        if (img && img.complete && img.naturalWidth > 0) {
            ctx.drawImage(img, x, y, TS, TS);

            if (ANIMATED_TILES[id]) {
                drawAnimOverlay(ctx, id, x, y, gt, TS, row, col);
            }
        } else {
            drawFallbackTile(ctx, C, id, x, y, TS);
        }
    }

    function drawAnimOverlay(ctx, id, x, y, gt, TS, row, col) {
        const t = gt / 1000;

        if (id === 3) {
            ctx.fillStyle = 'rgba(160,220,255,0.12)';
            const waveX = Math.sin(t * 2 + col * 0.8) * TS * 0.3;
            const waveW = TS * 0.4;
            ctx.fillRect(x + waveX + TS * 0.3, y, waveW, TS);

            ctx.fillStyle = 'rgba(255,255,255,0.08)';
            const shimX = Math.sin(t * 3 + row * 1.2) * TS * 0.2;
            ctx.fillRect(x + shimX + TS * 0.4, y + TS * 0.2, TS * 0.2, TS * 0.15);
        }

        if (id === 17) {
            const pulse = Math.sin(t * 4) * 0.15 + 0.15;
            ctx.fillStyle = 'rgba(120,80,255,' + pulse + ')';
            ctx.beginPath();
            ctx.arc(x + TS / 2, y + TS / 2, TS * 0.35, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = 'rgba(200,180,255,' + (pulse * 0.5) + ')';
            ctx.beginPath();
            ctx.arc(x + TS / 2, y + TS / 2, TS * 0.2, 0, Math.PI * 2);
            ctx.fill();
        }

        if (id === 18) {
            ctx.fillStyle = 'rgba(180,220,255,0.1)';
            const splashR = Math.sin(t * 3) * 2 + TS * 0.25;
            ctx.beginPath();
            ctx.arc(x + TS / 2, y + TS / 2, splashR, 0, Math.PI * 2);
            ctx.fill();
        }

        if (id === 19) {
            const flicker = Math.sin(t * 8 + col) * 0.08 + 0.15;
            ctx.fillStyle = 'rgba(255,220,100,' + flicker + ')';
            ctx.beginPath();
            ctx.arc(x + TS / 2, y + TS * 0.25, TS * 0.3, 0, Math.PI * 2);
            ctx.fill();
        }

        if (id === 24) {
            const flicker = Math.random() * 0.1 + 0.08;
            ctx.fillStyle = 'rgba(255,150,50,' + flicker + ')';
            ctx.fillRect(x, y, TS, TS);

            ctx.fillStyle = 'rgba(255,200,80,' + (flicker * 0.6) + ')';
            ctx.fillRect(x + TS * 0.2, y + TS * 0.3, TS * 0.6, TS * 0.4);
        }

        if (id === 28) {
            const flowY = (gt / 100) % TS;
            ctx.fillStyle = 'rgba(200,230,255,0.12)';
            ctx.fillRect(x + TS * 0.2, y + flowY - TS, TS * 0.2, TS);
            ctx.fillRect(x + TS * 0.55, y + ((flowY + TS / 2) % TS) - TS, TS * 0.15, TS);

            ctx.fillStyle = 'rgba(255,255,255,0.08)';
            ctx.fillRect(x + TS * 0.3, y + ((flowY + TS / 3) % TS), TS * 0.1, TS * 0.2);
        }
    }

    function drawFallbackTile(ctx, C, id, x, y, TS) {
        const colors = {
            1: '#2a8a28', 2: '#c8a878', 3: '#2060a0', 4: '#907050',
            5: '#806040', 6: '#a05030', 7: '#705030', 8: '#607090',
            9: '#1e7828', 10: '#50a850', 11: '#a08050', 12: '#907040',
            13: '#d8c890', 14: '#808890', 15: '#2a7a28', 16: '#a08030',
            17: '#5030a0', 18: '#4080b0', 19: '#c0a040', 20: '#a07040',
            21: '#806030', 22: '#708090', 23: '#906830', 24: '#c06020',
            25: '#604020', 26: '#687080', 27: '#507040', 28: '#3878b0',
            29: '#687070'
        };
        ctx.fillStyle = colors[id] || '#444';
        ctx.fillRect(x, y, TS, TS);
    }

    return {
        drawTile: drawTile,
        dither: function() {},
        ditherFast: function() {},
        isLoaded: function() { return allLoaded; },
        getLoadProgress: function() { return { loaded: imagesLoaded, total: totalImages }; }
    };
})();
