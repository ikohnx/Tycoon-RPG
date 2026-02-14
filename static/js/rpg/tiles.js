window.RPGTiles = (function() {
    let _ctx;
    const _cache = {};
    const ANIMATED_TILES = {3: true, 17: true, 18: true, 19: true, 24: true, 28: true};
    const ANIM_BUCKET_MS = 120;

    function dither(x, y, w, h, c1, c2) {
        _ctx.fillStyle = c1;
        _ctx.fillRect(x, y, w, h);
        _ctx.fillStyle = c2;
        for (let py = 0; py < h; py++) {
            for (let px = (py & 1); px < w; px += 2) {
                _ctx.fillRect(x + px, y + py, 1, 1);
            }
        }
    }

    function ditherFast(x, y, w, h, c1, c2) {
        _ctx.fillStyle = c1;
        _ctx.fillRect(x, y, w, h);
        _ctx.fillStyle = c2;
        for (let py = 0; py < h; py += 2) {
            for (let px = 0; px < w; px += 2) {
                _ctx.fillRect(x + px, y + py, 1, 1);
                _ctx.fillRect(x + px + 1, y + py + 1, 1, 1);
            }
        }
    }

    function drawTileCached(ctx, C, id, x, y, row, col, gt, TS) {
        if (id === 0) return;
        const sd = (row * 131 + col * 97) & 0xFF;
        let key;
        if (ANIMATED_TILES[id]) {
            const tb = Math.floor(gt / ANIM_BUCKET_MS);
            key = id + '_' + sd + '_' + col + '_' + tb;
        } else {
            key = id + '_' + sd;
        }
        let cached = _cache[key];
        if (!cached) {
            const off = document.createElement('canvas');
            off.width = TS;
            off.height = TS;
            const oc = off.getContext('2d');
            oc.imageSmoothingEnabled = false;
            _ctx = oc;
            _drawTileRaw(oc, C, id, 0, 0, row, col, gt, TS);
            _cache[key] = off;
            cached = off;
            if (ANIMATED_TILES[id]) {
                const oldKey = id + '_' + sd + '_' + col + '_' + (Math.floor(gt / ANIM_BUCKET_MS) - 2);
                delete _cache[oldKey];
            }
        }
        ctx.drawImage(cached, x, y);
    }

    const ell = (cx, cy, rx, ry) => { _ctx.beginPath(); _ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2); _ctx.fill(); };

    function _drawGrassBase(ctx, x, y, s, sd) {
        ctx.fillStyle = '#2a8a28';
        ctx.fillRect(x, y, s, s);
        ctx.fillStyle = '#329632';
        ctx.fillRect(x, y, s, s/2);
        ctx.fillStyle = '#3aa838';
        ctx.fillRect(x, y, s, s/4);
        const patches = [
            {c:'#248a22',w:14,h:10}, {c:'#36a834',w:12,h:8}, {c:'#2e9a2c',w:16,h:12},
            {c:'#40b040',w:10,h:8}, {c:'#228820',w:13,h:9}
        ];
        for (let i = 0; i < patches.length; i++) {
            const p = patches[i];
            const px = (sd * 7 + i * 41) % (s - p.w);
            const py = (sd * 13 + i * 31) % (s - p.h);
            ctx.fillStyle = p.c;
            ell(x + px + p.w/2, y + py + p.h/2, p.w/2, p.h/2);
        }
        const bladeColors = ['#50c850','#48b848','#5ad05a','#42b042','#58c858','#3ea03e'];
        for (let i = 0; i < 18; i++) {
            const bx = (sd * 11 + i * 29) % (s - 2) + 1;
            const by = (sd * 7 + i * 37) % (s - 6) + 2;
            ctx.fillStyle = bladeColors[(sd + i) % bladeColors.length];
            ctx.fillRect(x + bx, y + by, 1, 3);
            ctx.fillRect(x + bx, y + by, 1, 1);
        }
        for (let i = 0; i < 12; i++) {
            const bx = (sd * 3 + i * 43) % (s - 2) + 1;
            const by = (sd * 17 + i * 23) % (s - 4) + 2;
            ctx.fillStyle = '#1e7a1e';
            ctx.fillRect(x + bx, y + by, 1, 2);
        }
        for (let i = 0; i < 8; i++) {
            const bx = (sd * 19 + i * 31) % (s - 4) + 2;
            const by = (sd * 23 + i * 17) % (s - 4) + 2;
            ctx.fillStyle = '#60d860';
            ctx.fillRect(x + bx, y + by, 1, 1);
        }
        for (let i = 0; i < 5; i++) {
            const bx = (sd * 29 + i * 47) % (s - 6) + 3;
            const by = (sd * 31 + i * 19) % (s - 6) + 3;
            ctx.fillStyle = '#2e9830';
            ctx.fillRect(x + bx, y + by, 2, 1);
            ctx.fillRect(x + bx + 1, y + by - 1, 1, 1);
        }
    }

    function _drawTreeCanopy(ctx, C, x, y, cx2, cy2, sd) {
        const leafClusters = [
            {dx:0, dy:0, r:18, c:'#1e7828'},
            {dx:-8, dy:-4, r:12, c:'#288830'},
            {dx:8, dy:-3, r:11, c:'#248228'},
            {dx:-4, dy:6, r:10, c:'#1a7020'},
            {dx:5, dy:5, r:10, c:'#207828'},
            {dx:0, dy:-8, r:10, c:'#2a8a32'},
            {dx:-10, dy:2, r:9, c:'#1e7428'},
            {dx:10, dy:1, r:9, c:'#227a2a'},
        ];
        for (const lc of leafClusters) {
            ctx.fillStyle = lc.c;
            ell(cx2 + lc.dx, cy2 + lc.dy, lc.r, lc.r * 0.7);
        }
        const hlClusters = [
            {dx:-6, dy:-6, r:7, c:'#38a840'},
            {dx:4, dy:-8, r:6, c:'#40b048'},
            {dx:-2, dy:-3, r:8, c:'#30a038'},
            {dx:8, dy:-4, r:5, c:'#48b850'},
            {dx:-10, dy:-2, r:5, c:'#3aaa42'},
        ];
        for (const hc of hlClusters) {
            ctx.fillStyle = hc.c;
            ell(cx2 + hc.dx, cy2 + hc.dy, hc.r, hc.r * 0.65);
        }
        const brightSpots = ['#58c860','#50c058','#60d068','#4cb854'];
        for (let i = 0; i < 14; i++) {
            const dx = (sd * 7 + i * 23) % 28 - 14;
            const dy = (sd * 11 + i * 19) % 20 - 12;
            if (dx*dx + dy*dy > 16*16) continue;
            ctx.fillStyle = brightSpots[i % brightSpots.length];
            ctx.fillRect(cx2 + dx, cy2 + dy, 2, 1);
            ctx.fillRect(cx2 + dx, cy2 + dy - 1, 1, 1);
        }
        const darkSpots = ['#146018','#185e20','#106014'];
        for (let i = 0; i < 10; i++) {
            const dx = (sd * 13 + i * 31) % 26 - 13;
            const dy = (sd * 17 + i * 29) % 18 - 6;
            if (dx*dx + dy*dy > 15*15) continue;
            ctx.fillStyle = darkSpots[i % darkSpots.length];
            ctx.fillRect(cx2 + dx, cy2 + dy, 2, 2);
        }
        ctx.fillStyle = '#0c4810';
        ctx.globalAlpha = 0.3;
        ell(cx2, cy2 + 4, 16, 8);
        ctx.globalAlpha = 1;
    }

    function _drawTileRaw(ctx, C, id, x, y, row, col, gt, TS) {
        _ctx = ctx;
        const s = TS;
        const D = 1;
        const sd = (row * 131 + col * 97) & 0xFF;
        const t = gt;

        switch(id) {
            case 0: break;

            case 1: {
                _drawGrassBase(ctx, x, y, s, sd);
                break;
            }

            case 2: {
                ctx.fillStyle = C.pm;
                ctx.fillRect(x, y, s, s);
                const stoneW = [11, 10, 12, 11, 10, 13, 11, 10];
                for (let row2 = 0; row2 < 4; row2++) {
                    let cx2 = (row2 % 2) * 5;
                    const by = row2 * 12;
                    let si = (sd + row2) & 7;
                    while (cx2 < s) {
                        const sw = Math.min(stoneW[si & 7], s - cx2);
                        if (sw < 3) { cx2 += sw + 1; si++; continue; }
                        const baseC = ((si + sd) & 1) ? '#d0b888' : '#c8a878';
                        ctx.fillStyle = baseC;
                        ctx.fillRect(x + cx2, y + by, sw, 11);
                        ctx.fillStyle = '#e0c898';
                        ctx.fillRect(x + cx2 + 1, y + by + 1, sw - 2, 4);
                        ctx.fillStyle = '#b89868';
                        ctx.fillRect(x + cx2 + 1, y + by + 8, sw - 2, 2);
                        ctx.fillStyle = '#e8d8b0';
                        ctx.fillRect(x + cx2, y + by, sw, D);
                        ctx.fillStyle = '#a08850';
                        ctx.fillRect(x + cx2, y + by + 11, sw, D);
                        ctx.fillStyle = '#9a8048';
                        ctx.fillRect(x + cx2, y + by, D, 11);
                        ctx.fillRect(x + cx2 + sw - 1, y + by, D, 11);
                        cx2 += sw + 1;
                        si++;
                    }
                }
                break;
            }

            case 3: {
                const wt = t / 600;
                ctx.fillStyle = '#103878';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#184898';
                ctx.fillRect(x, y, s, 36);
                ctx.fillStyle = '#2058a8';
                ctx.fillRect(x, y, s, 24);
                ctx.fillStyle = '#2868b8';
                ctx.fillRect(x, y, s, 12);
                for (let i = 0; i < 5; i++) {
                    const wx = Math.sin(wt + i * 1.5 + col * 0.7) * 6 + 4;
                    const wy = i * 10 + 2;
                    const ww = 20 + Math.sin(wt * 0.6 + i * 0.8) * 6;
                    ctx.fillStyle = '#4890d0';
                    ctx.fillRect(x + wx, y + wy, ww, 2);
                    ctx.fillStyle = '#68b0e8';
                    ctx.fillRect(x + wx + 2, y + wy, ww - 4, 1);
                    ctx.fillStyle = '#88c8f0';
                    ctx.globalAlpha = 0.5;
                    ctx.fillRect(x + wx + 4, y + wy + 1, ww - 8, D);
                    ctx.globalAlpha = 1;
                }
                ctx.fillStyle = '#fff';
                for (let i = 0; i < 4; i++) {
                    const sx = (sd * 7 + i * 31) % 34 + 6;
                    const sy2 = (sd * 11 + i * 23) % 30 + 8;
                    ctx.globalAlpha = 0.15 + Math.sin(wt * 2 + i * 1.2 + sd) * 0.1;
                    ctx.fillRect(x + sx, y + sy2, 4, D);
                    ctx.fillRect(x + sx + 1, y + sy2 + 1, 2, D);
                }
                ctx.globalAlpha = 1;
                for (let i = 0; i < 6; i++) {
                    const dx = (sd * 3 + i * 37) % 40 + 4;
                    const dy = (sd * 19 + i * 29) % 38 + 5;
                    ctx.fillStyle = '#2060a8';
                    ctx.fillRect(x + dx, y + dy, 2, 1);
                }
                break;
            }

            case 4: {
                ctx.fillStyle = '#808898';
                ctx.fillRect(x, y, s, s);
                for (let row2 = 0; row2 < 4; row2++) {
                    let cx2 = (row2 % 2) * 6;
                    const by = row2 * 12;
                    let si = (sd + row2 * 3) & 7;
                    while (cx2 < s) {
                        const bw = Math.min(11, s - cx2);
                        if (bw < 3) { cx2 += bw + 1; si++; continue; }
                        const bc = ((si + row2 + sd) & 1) ? '#a0a8c0' : '#909ab0';
                        ctx.fillStyle = bc;
                        ctx.fillRect(x + cx2, y + by, bw, 11);
                        ctx.fillStyle = '#b8c0d0';
                        ctx.fillRect(x + cx2 + 1, y + by + 1, bw - 2, 4);
                        ctx.fillStyle = '#787888';
                        ctx.fillRect(x + cx2 + 1, y + by + 8, bw - 2, 2);
                        ctx.fillStyle = '#c8d0e0';
                        ctx.fillRect(x + cx2, y + by, bw, D);
                        ctx.fillStyle = '#606878';
                        ctx.fillRect(x + cx2, y + by + 11, bw, D);
                        cx2 += bw + 1;
                        si++;
                    }
                }
                break;
            }

            case 5: {
                ctx.fillStyle = '#889098';
                ctx.fillRect(x, y, s, s);
                for (let i = 0; i < 4; i++) {
                    const bx = i * 12;
                    ctx.fillStyle = '#a0a8b8';
                    ctx.fillRect(x + bx, y, 11, 16);
                    ctx.fillStyle = '#c0c8d8';
                    ctx.fillRect(x + bx + 1, y + 1, 9, 6);
                    ctx.fillStyle = '#707880';
                    ctx.fillRect(x + bx, y + 14, 11, 2);
                }
                ctx.fillStyle = '#606870';
                ctx.fillRect(x, y + 16, s, 2);
                let cx2 = 0;
                for (let i = 0; cx2 < s; i++) {
                    const bw = 11;
                    const bc = (i & 1) ? '#a0a8c0' : '#909ab0';
                    ctx.fillStyle = bc;
                    ctx.fillRect(x + cx2, y + 20, Math.min(bw, s - cx2), 12);
                    ctx.fillStyle = '#b8c0d0';
                    ctx.fillRect(x + cx2 + 1, y + 21, Math.min(bw - 2, s - cx2 - 2), 4);
                    ctx.fillStyle = '#606878';
                    ctx.fillRect(x + cx2, y + 32, Math.min(bw, s - cx2), D);
                    cx2 += bw + 1;
                }
                cx2 = 5;
                for (let i = 0; cx2 < s; i++) {
                    const bw = 11;
                    const bc = (i & 1) ? '#909ab0' : '#a0a8c0';
                    ctx.fillStyle = bc;
                    ctx.fillRect(x + cx2, y + 34, Math.min(bw, s - cx2), 12);
                    ctx.fillStyle = '#606878';
                    ctx.fillRect(x + cx2, y + 46, Math.min(bw, s - cx2), D);
                    cx2 += bw + 1;
                }
                break;
            }

            case 6: {
                ctx.fillStyle = '#c03828';
                ctx.fillRect(x, y, s, s);
                for (let r2 = 0; r2 < 5; r2++) {
                    const rOff = (r2 % 2) * 5;
                    for (let c2 = -1; c2 < 6; c2++) {
                        const tx2 = c2 * 10 + rOff;
                        const ty2 = r2 * 10;
                        if (tx2 >= s) continue;
                        const sc = ((r2 + c2 + sd) & 1) ? '#d84838' : '#c84030';
                        const clx = Math.max(0, tx2);
                        const clw = Math.min(9, s - clx);
                        ctx.fillStyle = sc;
                        ctx.fillRect(x + clx, y + ty2, clw, 9);
                        ctx.fillStyle = '#e86858';
                        ctx.fillRect(x + clx + 1, y + ty2 + 1, clw - 2, 3);
                        ctx.fillStyle = '#f89888';
                        ctx.fillRect(x + clx, y + ty2, clw, D);
                        ctx.fillStyle = '#a02818';
                        ctx.fillRect(x + clx, y + ty2 + 9, clw, D);
                    }
                }
                break;
            }

            case 7: {
                ctx.fillStyle = '#8890a8';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#606878';
                ctx.fillRect(x + 6, y + 2, 36, 44);
                ctx.fillStyle = '#705028';
                ctx.fillRect(x + 8, y + 4, 32, 40);
                ctx.fillStyle = '#886838';
                ctx.fillRect(x + 9, y + 5, 30, 38);
                ctx.fillStyle = '#604020';
                ctx.fillRect(x + 10, y + 6, 13, 17);
                ctx.fillRect(x + 25, y + 6, 13, 17);
                ctx.fillStyle = '#705830';
                ctx.fillRect(x + 10, y + 25, 13, 17);
                ctx.fillRect(x + 25, y + 25, 13, 17);
                ctx.fillStyle = '#503018';
                ctx.fillRect(x + 23, y + 4, 2, 40);
                ctx.fillRect(x + 10, y + 23, 28, 2);
                ctx.fillStyle = '#a08848';
                ctx.fillRect(x + 10, y + 6, 28, D);
                ctx.fillStyle = '#3a2010';
                ctx.fillRect(x + 32, y + 28, 4, 4);
                ctx.fillStyle = '#d4b030';
                ctx.fillRect(x + 33, y + 29, 2, 2);
                break;
            }

            case 8: {
                ctx.fillStyle = '#8890a8';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#a0a8b8';
                ctx.fillRect(x + 5, y + 3, 38, 38);
                ctx.fillStyle = '#606878';
                ctx.fillRect(x + 43, y + 3, D, 38);
                ctx.fillRect(x + 5, y + 41, 38, D);
                ctx.fillStyle = '#80b8e8';
                ctx.fillRect(x + 7, y + 5, 16, 16);
                ctx.fillRect(x + 25, y + 5, 16, 16);
                ctx.fillRect(x + 7, y + 23, 16, 16);
                ctx.fillRect(x + 25, y + 23, 16, 16);
                ctx.fillStyle = '#a0d0f0';
                ctx.fillRect(x + 8, y + 6, 6, 6);
                ctx.fillRect(x + 26, y + 6, 6, 6);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.3;
                ctx.fillRect(x + 9, y + 7, 4, 3);
                ctx.fillRect(x + 27, y + 7, 4, 3);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#707888';
                ctx.fillRect(x + 23, y + 5, 2, 34);
                ctx.fillRect(x + 7, y + 21, 34, 2);
                ctx.fillStyle = '#909ab0';
                ctx.fillRect(x + 5, y + 42, 38, 6);
                break;
            }

            case 9: {
                _drawGrassBase(ctx, x, y, s, sd);
                const tw = 6;
                const tl = x + (s - tw) / 2;
                ctx.fillStyle = '#3a2010';
                ctx.fillRect(tl - 1, y + 26, tw + 2, 22);
                ctx.fillStyle = '#583818';
                ctx.fillRect(tl, y + 26, tw, 22);
                ctx.fillStyle = '#6a4828';
                ctx.fillRect(tl + 1, y + 26, 2, 22);
                ctx.fillStyle = '#4a3018';
                ctx.fillRect(tl + tw - 1, y + 28, 1, 18);
                const tcx = x + s / 2;
                const tcy = y + 18;
                _drawTreeCanopy(ctx, C, x, y, tcx, tcy, sd);
                break;
            }

            case 10: {
                _drawGrassBase(ctx, x, y, s, sd);
                const flowerColors = ['#f04858','#f8e030','#d050f0','#f8f0f8','#f8a040'];
                for (let i = 0; i < 7; i++) {
                    const fx = (sd * 7 + i * 31) % 36 + 6;
                    const fy = (sd * 11 + i * 23) % 30 + 8;
                    ctx.fillStyle = '#1a7a1a';
                    ctx.fillRect(x + fx, y + fy + 3, 1, 5);
                    ctx.fillStyle = '#228822';
                    ctx.fillRect(x + fx - 1, y + fy + 5, 1, 2);
                    const fc = flowerColors[(sd + i) % 5];
                    ctx.fillStyle = fc;
                    ctx.fillRect(x + fx - 1, y + fy - 1, 3, 3);
                    ctx.fillRect(x + fx, y + fy - 2, 1, 1);
                    ctx.fillRect(x + fx - 2, y + fy, 1, 1);
                    ctx.fillRect(x + fx + 2, y + fy, 1, 1);
                    ctx.fillRect(x + fx, y + fy + 2, 1, 1);
                    ctx.fillStyle = '#fff';
                    ctx.fillRect(x + fx, y + fy, 1, 1);
                }
                break;
            }

            case 11: {
                ctx.fillStyle = '#a07848';
                ctx.fillRect(x, y, s, s);
                for (let py = 0; py < s; py += 8) {
                    ctx.fillStyle = (py & 8) ? '#b89058' : '#a07848';
                    ctx.fillRect(x, y + py, s, 7);
                    ctx.fillStyle = '#c8a068';
                    ctx.fillRect(x, y + py, s, 2);
                    ctx.fillStyle = '#886038';
                    ctx.fillRect(x, y + py + 7, s, D);
                }
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.08;
                ctx.fillRect(x, y, s, 2);
                ctx.globalAlpha = 1;
                break;
            }

            case 12: {
                _drawGrassBase(ctx, x, y, s, sd);
                ctx.fillStyle = '#3a2010';
                ctx.fillRect(x + 22, y + 24, 4, 24);
                ctx.fillStyle = '#583818';
                ctx.fillRect(x + 23, y + 24, 2, 24);
                ctx.fillStyle = '#886038';
                ctx.fillRect(x + 10, y + 12, 28, 16);
                ctx.fillStyle = '#a07848';
                ctx.fillRect(x + 12, y + 14, 24, 12);
                ctx.fillStyle = '#b89058';
                ctx.fillRect(x + 12, y + 14, 24, 3);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.15;
                ctx.fillRect(x + 14, y + 16, 20, 2);
                ctx.globalAlpha = 1;
                break;
            }

            case 13: {
                ctx.fillStyle = '#d0b868';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#d8c078';
                ctx.fillRect(x, y, s, 24);
                ctx.fillStyle = '#e0c888';
                ctx.fillRect(x, y, s, 12);
                for (let i = 0; i < 8; i++) {
                    const dx = (sd * 7 + i * 31) % 42 + 3;
                    const dy = (sd * 11 + i * 23) % 40 + 4;
                    ctx.fillStyle = '#e8d898';
                    ctx.fillRect(x + dx, y + dy, 2, 1);
                }
                for (let i = 0; i < 6; i++) {
                    const dx = (sd * 3 + i * 43) % 40 + 4;
                    const dy = (sd * 13 + i * 37) % 38 + 6;
                    ctx.fillStyle = '#c0a858';
                    ctx.fillRect(x + dx, y + dy, 1, 1);
                }
                for (let i = 0; i < 4; i++) {
                    const dx = (sd * 17 + i * 29) % 36 + 6;
                    const dy = (sd * 19 + i * 41) % 34 + 8;
                    ctx.fillStyle = '#b8a050';
                    ctx.fillRect(x + dx, y + dy, 3, 2);
                }
                break;
            }

            case 14: {
                ctx.fillStyle = '#98a8b0';
                ctx.fillRect(x, y, s, s);
                for (let py = 0; py < s; py += 16) {
                    for (let px = 0; px < s; px += 16) {
                        ctx.fillStyle = ((py + px) & 16) ? '#90a0a8' : '#a0b0b8';
                        ctx.fillRect(x + px, y + py, 16, 16);
                        ctx.fillStyle = '#b0c0c8';
                        ctx.fillRect(x + px, y + py, 16, 2);
                        ctx.fillRect(x + px, y + py, 2, 16);
                        ctx.fillStyle = '#788890';
                        ctx.fillRect(x + px + 14, y + py, 2, 16);
                        ctx.fillRect(x + px, y + py + 14, 16, 2);
                    }
                }
                break;
            }

            case 15: {
                _drawGrassBase(ctx, x, y, s, sd);
                ctx.fillStyle = '#105018';
                ctx.fillRect(x + 4, y + 4, 40, 40);
                ctx.fillStyle = '#1a6820';
                ctx.fillRect(x + 6, y + 6, 36, 36);
                ctx.fillStyle = '#228828';
                ctx.fillRect(x + 8, y + 8, 32, 32);
                ctx.fillStyle = '#2aa032';
                ctx.fillRect(x + 10, y + 10, 28, 28);
                for (let i = 0; i < 10; i++) {
                    const lx = (sd * 7 + i * 29) % 26 + 11;
                    const ly = (sd * 11 + i * 23) % 26 + 11;
                    ctx.fillStyle = '#38b040';
                    ctx.fillRect(x + lx, y + ly, 2, 2);
                }
                for (let i = 0; i < 6; i++) {
                    const lx = (sd * 13 + i * 37) % 24 + 12;
                    const ly = (sd * 17 + i * 31) % 24 + 12;
                    ctx.fillStyle = '#48c050';
                    ctx.fillRect(x + lx, y + ly, 1, 1);
                }
                break;
            }

            case 16: {
                ctx.fillStyle = '#98a8b0';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#886038';
                ctx.fillRect(x + 10, y + 20, 28, 20);
                ctx.fillStyle = '#a07848';
                ctx.fillRect(x + 12, y + 22, 24, 16);
                ctx.fillStyle = '#b89058';
                ctx.fillRect(x + 12, y + 22, 24, 3);
                ctx.fillStyle = '#886038';
                ctx.fillRect(x + 12, y + 30, 24, 2);
                ctx.fillStyle = '#e0a838';
                ctx.fillRect(x + 22, y + 32, 4, 3);
                ctx.fillStyle = '#f8e068';
                ctx.fillRect(x + 23, y + 33, 2, D);
                break;
            }

            case 17: {
                const pt = t / 800;
                ctx.fillStyle = '#98a8b0';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#5830b0';
                ctx.fillRect(x + 8, y + 8, 32, 32);
                ctx.fillStyle = '#6838d0';
                ell(x + 24, y + 24, 14, 14);
                ctx.fillStyle = '#8048e8';
                ctx.globalAlpha = 0.7 + Math.sin(pt * 3) * 0.3;
                ell(x + 24, y + 24, 10, 10);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#a068f8';
                ctx.globalAlpha = 0.6 + Math.sin(pt * 4) * 0.3;
                ell(x + 24, y + 24, 6, 6);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#d0a0ff';
                ctx.globalAlpha = 0.5 + Math.sin(pt * 5) * 0.3;
                ctx.fillRect(x + 22, y + 22, 4, 4);
                ctx.globalAlpha = 1;
                break;
            }

            case 18: {
                ctx.fillStyle = '#98a8b0';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#788890';
                ctx.fillRect(x + 6, y + 18, 36, 28);
                ctx.fillStyle = '#b0c0c8';
                ctx.fillRect(x + 6, y + 18, 36, 2);
                ctx.fillStyle = '#8898a0';
                ctx.fillRect(x + 8, y + 20, 32, 24);
                ctx.fillStyle = '#2860c0';
                ctx.fillRect(x + 12, y + 24, 24, 16);
                ctx.fillStyle = '#3878d8';
                ctx.fillRect(x + 16, y + 28, 16, 8);
                const ft = t / 400;
                ctx.fillStyle = '#a0d0ff';
                ctx.globalAlpha = 0.5 + Math.sin(ft * 2) * 0.3;
                ctx.fillRect(x + 18, y + 10, 12, 10);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#d0e8ff';
                ctx.globalAlpha = 0.4 + Math.sin(ft * 3) * 0.3;
                ctx.fillRect(x + 21, y + 7, 6, 4);
                ctx.globalAlpha = 1;
                break;
            }

            case 19: {
                ctx.fillStyle = '#98a8b0';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#586070';
                ctx.fillRect(x + 22, y + 12, 4, 36);
                ctx.fillStyle = '#a0a8b8';
                ctx.fillRect(x + 23, y + 13, 2, 34);
                ctx.fillStyle = '#707888';
                ctx.fillRect(x + 16, y + 8, 16, 6);
                ctx.fillStyle = '#c8d0d8';
                ctx.fillRect(x + 17, y + 9, 14, D);
                const lg = 0.5 + Math.sin(t / 800 + sd) * 0.3;
                ctx.fillStyle = '#f8d848';
                ctx.globalAlpha = lg;
                ctx.fillRect(x + 16, y + 2, 16, 8);
                ctx.fillStyle = '#fff8d8';
                ctx.fillRect(x + 18, y + 3, 12, 6);
                ctx.globalAlpha = lg * 0.15;
                ctx.fillStyle = '#ffe8b0';
                ell(x + 24, y + 6, 18, 18);
                ctx.globalAlpha = 1;
                break;
            }

            case 20: {
                ctx.fillStyle = '#98a8b0';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#886038';
                ctx.fillRect(x + 2, y + 20, 4, 28);
                ctx.fillRect(x + 42, y + 20, 4, 28);
                ctx.fillStyle = '#a07848';
                ctx.fillRect(x + 2, y + 20, 44, 26);
                ctx.fillStyle = '#b89058';
                ctx.fillRect(x + 4, y + 22, 40, 22);
                ctx.fillStyle = '#886038';
                ctx.fillRect(x + 4, y + 32, 40, D);
                ctx.fillStyle = '#e03838';
                ctx.fillRect(x + 2, y + 2, 44, 18);
                ctx.fillStyle = '#b82828';
                ctx.fillRect(x + 2, y + 14, 44, 6);
                for (let i = 0; i < 7; i++) {
                    ctx.fillStyle = (i & 1) ? '#e03838' : '#b82828';
                    ctx.fillRect(x + 2 + i * 7, y + 18, 6, 2);
                }
                ctx.fillStyle = '#f8e030';
                ctx.fillRect(x + 8, y + 24, 6, 6);
                ctx.fillStyle = '#f04858';
                ctx.fillRect(x + 20, y + 24, 6, 6);
                ctx.fillStyle = '#f8a040';
                ctx.fillRect(x + 32, y + 26, 6, 6);
                break;
            }

            case 21: {
                _drawGrassBase(ctx, x, y, s, sd);
                ctx.fillStyle = '#886038';
                ctx.fillRect(x + 8, y + 30, 4, 16);
                ctx.fillRect(x + 36, y + 30, 4, 16);
                ctx.fillStyle = '#a07848';
                ctx.fillRect(x + 6, y + 22, 36, 10);
                ctx.fillStyle = '#b89058';
                ctx.fillRect(x + 8, y + 24, 32, 6);
                ctx.fillStyle = '#886038';
                ctx.fillRect(x + 6, y + 22, 36, D);
                ctx.fillRect(x + 6, y + 32, 36, D);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.1;
                ctx.fillRect(x + 8, y + 24, 32, D);
                ctx.globalAlpha = 1;
                break;
            }

            case 22: {
                _drawGrassBase(ctx, x, y, s, sd);
                ctx.fillStyle = '#687880';
                ell(x + 24, y + 32, 16, 12);
                ctx.fillStyle = '#8898a0';
                ell(x + 24, y + 32, 14, 10);
                ctx.fillStyle = '#2860c0';
                ell(x + 24, y + 32, 10, 7);
                ctx.fillStyle = '#3878d8';
                ell(x + 24, y + 32, 6, 4);
                ctx.fillStyle = '#a07848';
                ctx.fillRect(x + 12, y + 6, 24, 4);
                ctx.fillRect(x + 22, y + 10, 4, 16);
                ctx.fillStyle = '#886038';
                ctx.fillRect(x + 10, y + 6, 2, 10);
                ctx.fillRect(x + 36, y + 6, 2, 10);
                break;
            }

            case 23: {
                ctx.fillStyle = '#98a8b0';
                ctx.fillRect(x, y, s, s);
                const drawCrate = (cx, cy, cw, ch) => {
                    ctx.fillStyle = '#886038';
                    ctx.fillRect(x + cx, y + cy, cw, ch);
                    ctx.fillStyle = '#a07848';
                    ctx.fillRect(x + cx + 2, y + cy + 2, cw - 4, ch - 4);
                    ctx.fillStyle = '#b89058';
                    ctx.fillRect(x + cx + 2, y + cy + 2, cw - 4, 3);
                    ctx.fillStyle = '#886038';
                    ctx.fillRect(x + cx + Math.floor(cw/2) - 1, y + cy, 2, ch);
                    ctx.fillRect(x + cx, y + cy + Math.floor(ch/2) - 1, cw, 2);
                };
                drawCrate(2, 22, 22, 24);
                drawCrate(26, 14, 20, 32);
                drawCrate(8, 6, 16, 16);
                break;
            }

            case 24: {
                ctx.fillStyle = '#8890a8';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#505860';
                ctx.fillRect(x + 4, y + 16, 40, 32);
                ctx.fillStyle = '#404850';
                ctx.fillRect(x + 6, y + 18, 36, 28);
                ctx.fillStyle = '#a0a8c0';
                ctx.fillRect(x + 2, y + 12, 44, 4);
                ctx.fillRect(x + 2, y + 12, 4, 36);
                ctx.fillRect(x + 42, y + 12, 4, 36);
                ctx.fillStyle = '#b0b8d0';
                ctx.fillRect(x + 14, y + 6, 20, 6);
                ctx.fillRect(x + 16, y + 2, 16, 4);
                const flk = 0.6 + Math.sin(t / 150 + sd * 3) * 0.35;
                ctx.fillStyle = '#e04818';
                ctx.globalAlpha = flk;
                ctx.fillRect(x + 12, y + 28, 24, 14);
                ctx.fillStyle = '#f89038';
                ctx.globalAlpha = flk * 0.9;
                ctx.fillRect(x + 16, y + 24, 16, 12);
                ctx.fillStyle = '#f8c848';
                ctx.globalAlpha = flk * 0.8;
                ctx.fillRect(x + 18, y + 22, 12, 6);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = flk * 0.4;
                ctx.fillRect(x + 22, y + 24, 4, 2);
                ctx.globalAlpha = 1;
                break;
            }

            case 25: {
                ctx.fillStyle = '#8890a8';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#886038';
                ctx.fillRect(x + 4, y + 2, 40, 44);
                ctx.fillStyle = '#a07848';
                ctx.fillRect(x + 6, y + 4, 36, 40);
                ctx.fillStyle = '#886038';
                ctx.fillRect(x + 4, y + 2, 2, 44);
                ctx.fillRect(x + 42, y + 2, 2, 44);
                const shelfYs = [4, 16, 28];
                const bookColors = ['#8b2020','#204080','#208040','#a06020','#602080','#c08020','#306050','#903030'];
                shelfYs.forEach((sy) => {
                    ctx.fillStyle = '#b89058';
                    ctx.fillRect(x + 6, y + sy + 10, 36, 2);
                    let bx = 6;
                    for (let bi = 0; bi < 7 && bx < 42; bi++) {
                        const bw = 4 + ((sd + bi) & 1);
                        const bh = 8 + ((sd + bi) & 1) * 2;
                        ctx.fillStyle = bookColors[(sd + bi + sy) & 7];
                        ctx.fillRect(x + bx, y + sy + (10 - bh), bw, bh);
                        ctx.fillStyle = '#fff';
                        ctx.globalAlpha = 0.15;
                        ctx.fillRect(x + bx, y + sy + (10 - bh), bw, D);
                        ctx.globalAlpha = 1;
                        bx += bw + 1;
                    }
                });
                break;
            }

            case 26: {
                ctx.fillStyle = '#887048';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#a08868';
                ctx.fillRect(x, y, s, 16);
                ctx.fillStyle = '#685840';
                ctx.fillRect(x, y + 32, s, 16);
                for (let i = 0; i < 5; i++) {
                    const rx2 = (sd * 7 + i * 23) % 28 + 4;
                    const ry2 = i * 10 + 2;
                    const rw = 10 + (i * 3 + sd) % 6;
                    const rh = 7 + (i & 1);
                    const rc = ['#b8a078','#a89068','#c0a880','#a08060','#d0b890'][i];
                    ctx.fillStyle = rc;
                    ell(x + rx2 + rw/2, y + ry2 + rh/2, rw/2, rh/2);
                    ctx.fillStyle = '#e0d0b0';
                    ctx.globalAlpha = 0.3;
                    ell(x + rx2 + rw/2 - 2, y + ry2 + 2, rw/3, rh/3);
                    ctx.globalAlpha = 1;
                    ctx.fillStyle = '#685038';
                    ctx.globalAlpha = 0.3;
                    ell(x + rx2 + rw/2 + 2, y + ry2 + rh - 2, rw/3, rh/4);
                    ctx.globalAlpha = 1;
                }
                break;
            }

            case 27: {
                ctx.fillStyle = '#887048';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#685840';
                ctx.fillRect(x, y + 16, s, 32);
                for (let i = 0; i < 4; i++) {
                    const rx2 = (sd * 5 + i * 23) % 28 + 6;
                    const ry2 = i * 12 + 6;
                    const rw = 10 + (i * 7 + sd) % 6;
                    ctx.fillStyle = ['#b8a078','#c0a880','#a89068','#d0b890'][i];
                    ell(x + rx2 + rw/2, y + ry2 + 4, rw/2, 4);
                    ctx.fillStyle = '#e0d0b0';
                    ctx.globalAlpha = 0.25;
                    ell(x + rx2 + rw/2 - 1, y + ry2 + 2, rw/3, 2);
                    ctx.globalAlpha = 1;
                }
                _drawGrassBase(ctx, x, y, 48, sd);
                ctx.fillStyle = '#000';
                ctx.globalAlpha = 0.7;
                ctx.fillRect(x, y + 6, s, s - 6);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#685840';
                ctx.fillRect(x, y + 6, s, s - 6);
                for (let i = 0; i < 4; i++) {
                    const rx2 = (sd * 5 + i * 23) % 28 + 6;
                    const ry2 = i * 12 + 6;
                    const rw = 10 + (i * 7 + sd) % 6;
                    ctx.fillStyle = ['#b8a078','#c0a880','#a89068','#d0b890'][i];
                    ell(x + rx2 + rw/2, y + ry2 + 4, rw/2, 4);
                }
                ctx.fillStyle = '#2a8a28';
                ctx.globalAlpha = 0.5;
                ctx.fillRect(x, y, s, 6);
                ctx.globalAlpha = 1;
                for (let i = 0; i < 6; i++) {
                    ctx.fillStyle = '#3aa838';
                    ctx.fillRect(x + (sd * 3 + i * 29) % 38 + 4, y + 1, 1, 3 + (i & 1));
                    ctx.fillStyle = '#50c850';
                    ctx.fillRect(x + (sd * 7 + i * 23) % 36 + 6, y, 1, 2);
                }
                break;
            }

            case 28: {
                const wft = t / 500;
                ctx.fillStyle = '#a08868';
                ctx.fillRect(x, y, 10, s);
                ctx.fillRect(x + 38, y, 10, s);
                for (let i = 0; i < 4; i++) {
                    ctx.fillStyle = ['#b8a078','#c0a880','#a89068','#d0b890'][i];
                    ell(x + 5, y + i * 13 + 6, 5, 5);
                    ell(x + 43, y + i * 13 + 10, 5, 5);
                }
                ctx.fillStyle = '#1848a0';
                ctx.fillRect(x + 10, y, 28, s);
                ctx.fillStyle = '#2060b8';
                ctx.fillRect(x + 14, y, 20, s);
                ctx.fillStyle = '#2870c8';
                ctx.fillRect(x + 18, y, 12, s);
                for (let wy = 0; wy < 48; wy += 4) {
                    const wx = Math.sin(wft * 2 + wy * 0.2 + sd) * 3;
                    ctx.fillStyle = '#4898e0';
                    ctx.globalAlpha = 0.6;
                    ctx.fillRect(x + 14 + wx, y + wy, 20, 2);
                    ctx.fillStyle = '#88c8f0';
                    ctx.globalAlpha = 0.4 + Math.sin(wft + wy * 0.3) * 0.2;
                    ctx.fillRect(x + 18 + wx, y + wy, 12, D);
                    ctx.fillStyle = '#fff';
                    ctx.globalAlpha = 0.2 + Math.sin(wft * 1.5 + wy * 0.4) * 0.15;
                    ctx.fillRect(x + 20 + wx, y + wy, 8, D);
                }
                ctx.globalAlpha = 1;
                break;
            }

            case 29: {
                _drawGrassBase(ctx, x, y, s, sd);
                ctx.fillStyle = '#685840';
                ell(x + 24, y + 30, 16, 11);
                ctx.fillStyle = '#887048';
                ell(x + 24, y + 29, 14, 9);
                ctx.fillStyle = '#a08868';
                ell(x + 24, y + 28, 12, 7);
                ctx.fillStyle = '#b8a078';
                ell(x + 22, y + 26, 8, 5);
                ctx.fillStyle = '#d0b890';
                ctx.globalAlpha = 0.4;
                ell(x + 20, y + 24, 5, 3);
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#685038';
                ctx.globalAlpha = 0.3;
                ell(x + 28, y + 32, 6, 3);
                ctx.globalAlpha = 1;
                break;
            }

            default:
                ctx.fillStyle = '#ff00ff';
                ctx.fillRect(x, y, s, s);
        }
    }

    return {
        drawTile: drawTileCached,
        dither: function(ctx, x, y, w, h, c1, c2) { _ctx = ctx; dither(x, y, w, h, c1, c2); },
        ditherFast: function(ctx, x, y, w, h, c1, c2) { _ctx = ctx; ditherFast(x, y, w, h, c1, c2); }
    };
})();
