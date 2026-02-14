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

    function _drawTileRaw(ctx, C, id, x, y, row, col, gt, TS) {
        _ctx = ctx;
        const s = TS;
        const D = 1;
        const sd = (row * 131 + col * 97) & 0xFF;
        const t = gt;

        switch(id) {
            case 0: break;

            case 1: {
                ctx.fillStyle = '#2d9b2d';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#3aaf3a';
                ctx.fillRect(x, y, s, 20);
                ctx.fillStyle = '#48c848';
                ctx.fillRect(x, y, s, 8);
                for (let i = 0; i < 6; i++) {
                    const dx = (sd * 7 + i * 31) % 44 + 2;
                    const dy = (sd * 11 + i * 23) % 40 + 4;
                    ctx.fillStyle = '#5de05d';
                    ctx.fillRect(x + dx, y + dy, D, D);
                }
                for (let i = 0; i < 3; i++) {
                    const dx = (sd * 3 + i * 41) % 42 + 3;
                    const dy = (sd * 13 + i * 29) % 38 + 6;
                    ctx.fillStyle = '#1a7a1a';
                    ctx.fillRect(x + dx, y + dy, D, D);
                }
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
                        const sc = ((si + sd) & 1) ? C.p1 : C.p4;
                        ctx.fillStyle = sc;
                        ctx.fillRect(x + cx2, y + by, sw, 11);
                        ctx.fillStyle = C.p6;
                        ctx.fillRect(x + cx2, y + by, sw, D);
                        ctx.fillStyle = C.pe;
                        ctx.fillRect(x + cx2, y + by + 11, sw, D);
                        cx2 += sw + 1;
                        si++;
                    }
                }
                break;
            }

            case 3: {
                const wt = t / 600;
                ctx.fillStyle = '#1848a0';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#2060c0';
                ctx.fillRect(x, y, s, 32);
                ctx.fillStyle = '#3078d8';
                ctx.fillRect(x, y, s, 16);
                for (let i = 0; i < 3; i++) {
                    const wx = Math.sin(wt + i * 2.0 + col * 0.5) * 8 + 6;
                    const wy = i * 16 + 4;
                    const ww = 24 + Math.sin(wt * 0.7 + i) * 4;
                    ctx.fillStyle = '#70b8f0';
                    ctx.fillRect(x + wx, y + wy, ww, D);
                    ctx.fillStyle = '#fff';
                    ctx.globalAlpha = 0.4;
                    ctx.fillRect(x + wx + 4, y + wy + 1, ww - 8, D);
                    ctx.globalAlpha = 1;
                }
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.2 + Math.sin(wt * 2 + sd) * 0.1;
                ctx.fillRect(x + ((sd * 7) % 30) + 8, y + ((sd * 3) % 20) + 10, 3, D);
                ctx.globalAlpha = 1;
                break;
            }

            case 4: {
                ctx.fillStyle = C.bk5;
                ctx.fillRect(x, y, s, s);
                for (let row2 = 0; row2 < 4; row2++) {
                    let cx2 = (row2 % 2) * 6;
                    const by = row2 * 12;
                    let si = (sd + row2 * 3) & 7;
                    while (cx2 < s) {
                        const bw = Math.min(11, s - cx2);
                        if (bw < 3) { cx2 += bw + 1; si++; continue; }
                        const bc = ((si + row2 + sd) & 1) ? C.bk1 : C.bk3;
                        ctx.fillStyle = bc;
                        ctx.fillRect(x + cx2, y + by, bw, 11);
                        ctx.fillStyle = C.bkh;
                        ctx.fillRect(x + cx2, y + by, bw, D);
                        ctx.fillStyle = C.bkl;
                        ctx.fillRect(x + cx2, y + by + 11, bw, D);
                        cx2 += bw + 1;
                        si++;
                    }
                }
                break;
            }

            case 5: {
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x, y, s, s);
                for (let i = 0; i < 4; i++) {
                    const bx = i * 12;
                    ctx.fillStyle = C.bk4;
                    ctx.fillRect(x + bx, y, 11, 16);
                    ctx.fillStyle = C.bkh;
                    ctx.fillRect(x + bx, y, 11, 2);
                    ctx.fillStyle = C.bkl;
                    ctx.fillRect(x + bx, y + 15, 11, D);
                }
                ctx.fillStyle = C.bk5;
                ctx.fillRect(x, y + 16, s, 2);
                let cx2 = 0;
                for (let i = 0; cx2 < s; i++) {
                    const bw = 11;
                    const bc = (i & 1) ? C.bk1 : C.bk3;
                    ctx.fillStyle = bc;
                    ctx.fillRect(x + cx2, y + 20, Math.min(bw, s - cx2), 12);
                    ctx.fillStyle = C.bkl;
                    ctx.fillRect(x + cx2, y + 32, Math.min(bw, s - cx2), D);
                    cx2 += bw + 1;
                }
                cx2 = 5;
                for (let i = 0; cx2 < s; i++) {
                    const bw = 11;
                    const bc = (i & 1) ? C.bk3 : C.bk1;
                    ctx.fillStyle = bc;
                    ctx.fillRect(x + cx2, y + 34, Math.min(bw, s - cx2), 12);
                    ctx.fillStyle = C.bkl;
                    ctx.fillRect(x + cx2, y + 46, Math.min(bw, s - cx2), D);
                    cx2 += bw + 1;
                }
                break;
            }

            case 6: {
                ctx.fillStyle = C.rf3;
                ctx.fillRect(x, y, s, s);
                for (let r2 = 0; r2 < 5; r2++) {
                    const rOff = (r2 % 2) * 5;
                    for (let c2 = -1; c2 < 6; c2++) {
                        const tx2 = c2 * 10 + rOff;
                        const ty2 = r2 * 10;
                        if (tx2 >= s) continue;
                        const sc = ((r2 + c2 + sd) & 1) ? C.rf1 : C.rf4;
                        const clx = Math.max(0, tx2);
                        const clw = Math.min(9, s - clx);
                        ctx.fillStyle = sc;
                        ctx.fillRect(x + clx, y + ty2, clw, 9);
                        ctx.fillStyle = C.rfh;
                        ctx.fillRect(x + clx, y + ty2, clw, D);
                        ctx.fillStyle = C.rfs;
                        ctx.fillRect(x + clx, y + ty2 + 9, clw, D);
                    }
                }
                break;
            }

            case 7: {
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.bkl;
                ctx.fillRect(x + 6, y + 2, 36, 44);
                ctx.fillStyle = C.dr3;
                ctx.fillRect(x + 8, y + 4, 32, 40);
                ctx.fillStyle = C.dr1;
                ctx.fillRect(x + 10, y + 6, 13, 17);
                ctx.fillRect(x + 25, y + 6, 13, 17);
                ctx.fillStyle = C.dr2;
                ctx.fillRect(x + 10, y + 25, 13, 17);
                ctx.fillRect(x + 25, y + 25, 13, 17);
                ctx.fillStyle = C.drf;
                ctx.fillRect(x + 23, y + 4, 2, 40);
                ctx.fillRect(x + 10, y + 23, 28, 2);
                ctx.fillStyle = C.drh;
                ctx.fillRect(x + 10, y + 6, 28, D);
                ctx.fillStyle = C.drk;
                ctx.fillRect(x + 32, y + 28, 4, 4);
                ctx.fillStyle = '#d4b030';
                ctx.fillRect(x + 33, y + 29, 2, 2);
                break;
            }

            case 8: {
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.bk6;
                ctx.fillRect(x + 5, y + 3, 38, 38);
                ctx.fillStyle = C.bkl;
                ctx.fillRect(x + 43, y + 3, D, 38);
                ctx.fillRect(x + 5, y + 41, 38, D);
                ctx.fillStyle = C.w1;
                ctx.fillRect(x + 7, y + 5, 16, 16);
                ctx.fillRect(x + 25, y + 5, 16, 16);
                ctx.fillRect(x + 7, y + 23, 16, 16);
                ctx.fillRect(x + 25, y + 23, 16, 16);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.25;
                ctx.fillRect(x + 9, y + 7, 6, D);
                ctx.fillRect(x + 27, y + 7, 6, D);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x + 23, y + 5, 2, 34);
                ctx.fillRect(x + 7, y + 21, 34, 2);
                ctx.fillStyle = C.bk4;
                ctx.fillRect(x + 5, y + 42, 38, 6);
                break;
            }

            case 9: {
                const tw = 6;
                const tl = x + (s - tw) / 2;
                ctx.fillStyle = C.tk3;
                ctx.fillRect(tl, y + 24, tw, 24);
                ctx.fillStyle = C.tk2;
                ctx.fillRect(tl + 1, y + 24, tw - 2, 24);
                ctx.fillStyle = C.tkh;
                ctx.fillRect(tl + 1, y + 24, D, 24);
                const cx2 = x + s / 2;
                const cy2 = y + 16;
                ctx.fillStyle = C.trs;
                ctx.beginPath();
                ctx.ellipse(cx2, cy2, 22, 16, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.tr1;
                ctx.beginPath();
                ctx.ellipse(cx2, cy2, 20, 14, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.tr2;
                ctx.beginPath();
                ctx.ellipse(cx2, cy2 - 2, 14, 10, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.tr4;
                ctx.beginPath();
                ctx.ellipse(cx2 - 3, cy2 - 4, 7, 5, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.trh;
                ctx.beginPath();
                ctx.ellipse(cx2 - 5, cy2 - 6, 4, 3, 0, 0, Math.PI * 2);
                ctx.fill();
                break;
            }

            case 10: {
                ctx.fillStyle = '#2d9b2d';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = '#3aaf3a';
                ctx.fillRect(x, y, s, 20);
                const flowerColors = [C.fr, C.fy, C.fp, C.fw, C.fo];
                for (let i = 0; i < 5; i++) {
                    const fx = (sd * 7 + i * 37) % 38 + 5;
                    const fy = (sd * 11 + i * 29) % 30 + 8;
                    ctx.fillStyle = '#1a7a1a';
                    ctx.fillRect(x + fx, y + fy + 3, D, 4);
                    ctx.fillStyle = flowerColors[(sd + i) % 5];
                    ctx.fillRect(x + fx - 1, y + fy, 3, 3);
                    ctx.fillStyle = '#fff';
                    ctx.fillRect(x + fx, y + fy, D, D);
                }
                break;
            }

            case 11: {
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x, y, s, s);
                for (let py = 0; py < s; py += 8) {
                    ctx.fillStyle = (py & 8) ? C.wd2 : C.wd1;
                    ctx.fillRect(x, y + py, s, 7);
                    ctx.fillStyle = C.wd3;
                    ctx.fillRect(x, y + py + 7, s, D);
                }
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.08;
                ctx.fillRect(x, y, s, 2);
                ctx.globalAlpha = 1;
                break;
            }

            case 12: {
                ctx.fillStyle = '#2d9b2d';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.tk3;
                ctx.fillRect(x + 22, y + 24, 4, 24);
                ctx.fillStyle = C.tk2;
                ctx.fillRect(x + 23, y + 24, 2, 24);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 10, y + 12, 28, 16);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 12, y + 14, 24, 12);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 12, y + 14, 24, D);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.15;
                ctx.fillRect(x + 14, y + 16, 20, 2);
                ctx.globalAlpha = 1;
                break;
            }

            case 13: {
                ctx.fillStyle = C.sa2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.sa1;
                ctx.fillRect(x, y, s, 24);
                for (let i = 0; i < 5; i++) {
                    const dx = (sd * 7 + i * 31) % 42 + 3;
                    const dy = (sd * 11 + i * 23) % 40 + 4;
                    ctx.fillStyle = C.sa4;
                    ctx.fillRect(x + dx, y + dy, D, D);
                }
                for (let i = 0; i < 3; i++) {
                    const dx = (sd * 3 + i * 43) % 40 + 4;
                    const dy = (sd * 13 + i * 37) % 38 + 6;
                    ctx.fillStyle = C.sa3;
                    ctx.fillRect(x + dx, y + dy, D, D);
                }
                break;
            }

            case 14: {
                ctx.fillStyle = C.st2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.stm;
                for (let py = 0; py < s; py += 16) {
                    ctx.fillRect(x, y + py, s, D);
                }
                for (let px = 0; px < s; px += 16) {
                    ctx.fillRect(x + px, y, D, s);
                }
                ctx.fillStyle = C.st4;
                ctx.globalAlpha = 0.15;
                ctx.fillRect(x, y, s, D);
                ctx.globalAlpha = 1;
                break;
            }

            case 15: {
                ctx.fillStyle = '#2d9b2d';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.hgs;
                ctx.fillRect(x + 4, y + 4, 40, 40);
                ctx.fillStyle = C.hg1;
                ctx.fillRect(x + 6, y + 6, 36, 36);
                ctx.fillStyle = C.hg2;
                ctx.fillRect(x + 8, y + 8, 32, 32);
                ctx.fillStyle = C.hg3;
                for (let i = 0; i < 6; i++) {
                    const lx = (sd * 7 + i * 29) % 28 + 10;
                    const ly = (sd * 11 + i * 23) % 28 + 10;
                    ctx.fillRect(x + lx, y + ly, 2, 2);
                }
                break;
            }

            case 16: {
                ctx.fillStyle = C.st2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 10, y + 20, 28, 20);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 12, y + 22, 24, 16);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 12, y + 22, 24, D);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 12, y + 30, 24, 2);
                ctx.fillStyle = C.ch1;
                ctx.fillRect(x + 22, y + 32, 4, 3);
                ctx.fillStyle = C.chl;
                ctx.fillRect(x + 23, y + 33, 2, D);
                break;
            }

            case 17: {
                const pt = t / 800;
                ctx.fillStyle = C.st2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.pt1;
                ctx.fillRect(x + 8, y + 8, 32, 32);
                ctx.fillStyle = C.pt2;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + 24, 14, 14, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.pt3;
                ctx.globalAlpha = 0.7 + Math.sin(pt * 3) * 0.3;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + 24, 10, 10, pt, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.pt4;
                ctx.globalAlpha = 0.6 + Math.sin(pt * 4) * 0.3;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + 24, 6, 6, -pt * 1.5, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.5 + Math.sin(pt * 5) * 0.3;
                ctx.fillRect(x + 22, y + 22, 4, 4);
                ctx.globalAlpha = 1;
                break;
            }

            case 18: {
                ctx.fillStyle = C.st2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.st3;
                ctx.fillRect(x + 6, y + 18, 36, 28);
                ctx.fillStyle = C.st7;
                ctx.fillRect(x + 6, y + 18, 36, 2);
                ctx.fillStyle = C.st1;
                ctx.fillRect(x + 8, y + 20, 32, 24);
                ctx.fillStyle = C.w1;
                ctx.fillRect(x + 12, y + 24, 24, 16);
                ctx.fillStyle = C.w2;
                ctx.fillRect(x + 16, y + 28, 16, 8);
                const ft = t / 400;
                ctx.fillStyle = C.wf;
                ctx.globalAlpha = 0.5 + Math.sin(ft * 2) * 0.3;
                ctx.fillRect(x + 18, y + 10, 12, 10);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wsp;
                ctx.globalAlpha = 0.4 + Math.sin(ft * 3) * 0.3;
                ctx.fillRect(x + 21, y + 7, 6, 4);
                ctx.globalAlpha = 1;
                break;
            }

            case 19: {
                ctx.fillStyle = C.st2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.mtl4;
                ctx.fillRect(x + 22, y + 12, 4, 36);
                ctx.fillStyle = C.mtl2;
                ctx.fillRect(x + 23, y + 13, 2, 34);
                ctx.fillStyle = C.mtl3;
                ctx.fillRect(x + 16, y + 8, 16, 6);
                ctx.fillStyle = C.mtl1;
                ctx.fillRect(x + 17, y + 9, 14, D);
                const lg = 0.5 + Math.sin(t / 800 + sd) * 0.3;
                ctx.fillStyle = C.lp;
                ctx.globalAlpha = lg;
                ctx.fillRect(x + 16, y + 2, 16, 8);
                ctx.fillStyle = C.lpg;
                ctx.fillRect(x + 18, y + 3, 12, 6);
                ctx.globalAlpha = lg * 0.15;
                ctx.fillStyle = C.lpw;
                ctx.beginPath();
                ctx.arc(x + 24, y + 6, 18, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
                break;
            }

            case 20: {
                ctx.fillStyle = C.st2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 2, y + 20, 4, 28);
                ctx.fillRect(x + 42, y + 20, 4, 28);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 2, y + 20, 44, 26);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 4, y + 22, 40, 22);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 4, y + 32, 40, D);
                ctx.fillStyle = C.mk;
                ctx.fillRect(x + 2, y + 2, 44, 18);
                ctx.fillStyle = C.mkd;
                ctx.fillRect(x + 2, y + 14, 44, 6);
                for (let i = 0; i < 7; i++) {
                    ctx.fillStyle = (i & 1) ? C.mk : C.mkd;
                    ctx.fillRect(x + 2 + i * 7, y + 18, 6, 2);
                }
                ctx.fillStyle = C.fy;
                ctx.fillRect(x + 8, y + 24, 6, 6);
                ctx.fillStyle = C.fr;
                ctx.fillRect(x + 20, y + 24, 6, 6);
                ctx.fillStyle = C.fo;
                ctx.fillRect(x + 32, y + 26, 6, 6);
                break;
            }

            case 21: {
                ctx.fillStyle = '#2d9b2d';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 8, y + 30, 4, 16);
                ctx.fillRect(x + 36, y + 30, 4, 16);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 6, y + 22, 36, 10);
                ctx.fillStyle = C.wd2;
                ctx.fillRect(x + 8, y + 24, 32, 6);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 6, y + 22, 36, D);
                ctx.fillRect(x + 6, y + 32, 36, D);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha = 0.1;
                ctx.fillRect(x + 8, y + 24, 32, D);
                ctx.globalAlpha = 1;
                break;
            }

            case 22: {
                ctx.fillStyle = '#2d9b2d';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.st3;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + 32, 16, 12, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.st1;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + 32, 14, 10, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.w1;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + 32, 10, 7, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.w2;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + 32, 6, 4, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 12, y + 6, 24, 4);
                ctx.fillRect(x + 22, y + 10, 4, 16);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 10, y + 6, 2, 10);
                ctx.fillRect(x + 36, y + 6, 2, 10);
                break;
            }

            case 23: {
                ctx.fillStyle = C.st2;
                ctx.fillRect(x, y, s, s);
                const drawCrate = (cx, cy, cw, ch) => {
                    ctx.fillStyle = C.wd3;
                    ctx.fillRect(x + cx, y + cy, cw, ch);
                    ctx.fillStyle = C.wd1;
                    ctx.fillRect(x + cx + 2, y + cy + 2, cw - 4, ch - 4);
                    ctx.fillStyle = C.wd2;
                    ctx.fillRect(x + cx + 2, y + cy + 2, cw - 4, D);
                    ctx.fillStyle = C.wd3;
                    ctx.fillRect(x + cx + Math.floor(cw/2) - 1, y + cy, 2, ch);
                    ctx.fillRect(x + cx, y + cy + Math.floor(ch/2) - 1, cw, 2);
                };
                drawCrate(2, 22, 22, 24);
                drawCrate(26, 14, 20, 32);
                drawCrate(8, 6, 16, 16);
                break;
            }

            case 24: {
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.fp2;
                ctx.fillRect(x + 4, y + 16, 40, 32);
                ctx.fillStyle = C.fp3;
                ctx.fillRect(x + 6, y + 18, 36, 28);
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x + 2, y + 12, 44, 4);
                ctx.fillRect(x + 2, y + 12, 4, 36);
                ctx.fillRect(x + 42, y + 12, 4, 36);
                ctx.fillStyle = C.bk3;
                ctx.fillRect(x + 14, y + 6, 20, 6);
                ctx.fillRect(x + 16, y + 2, 16, 4);
                const flk = 0.6 + Math.sin(t / 150 + sd * 3) * 0.35;
                ctx.fillStyle = C.fph;
                ctx.globalAlpha = flk;
                ctx.fillRect(x + 12, y + 28, 24, 14);
                ctx.fillStyle = C.fpf;
                ctx.globalAlpha = flk * 0.9;
                ctx.fillRect(x + 16, y + 24, 16, 12);
                ctx.fillStyle = C.fpb;
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
                ctx.fillStyle = C.bk2;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 4, y + 2, 40, 44);
                ctx.fillStyle = C.wd1;
                ctx.fillRect(x + 6, y + 4, 36, 40);
                ctx.fillStyle = C.wd3;
                ctx.fillRect(x + 4, y + 2, 2, 44);
                ctx.fillRect(x + 42, y + 2, 2, 44);
                const shelfYs = [4, 16, 28];
                const bookColors = ['#8b2020','#204080','#208040','#a06020','#602080','#c08020','#306050','#903030'];
                shelfYs.forEach((sy) => {
                    ctx.fillStyle = C.wd2;
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
                ctx.fillStyle = C.rk5;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.rk3;
                ctx.fillRect(x, y, s, 16);
                ctx.fillStyle = C.rkd;
                ctx.fillRect(x, y + 32, s, 16);
                for (let i = 0; i < 4; i++) {
                    const rx2 = (sd * 7 + i * 29) % 30 + 4;
                    const ry2 = i * 12 + 4;
                    const rw = 10 + (i * 3 + sd) % 6;
                    const rc = [C.rk1, C.rk2, C.rk7, C.rk8][i];
                    ctx.fillStyle = rc;
                    ctx.fillRect(x + rx2, y + ry2, rw, 8);
                    ctx.fillStyle = C.rkh;
                    ctx.fillRect(x + rx2, y + ry2, rw, D);
                    ctx.fillStyle = C.rkd;
                    ctx.fillRect(x + rx2, y + ry2 + 7, rw, D);
                }
                break;
            }

            case 27: {
                ctx.fillStyle = C.rk5;
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.rkd;
                ctx.fillRect(x, y + 16, s, 32);
                for (let i = 0; i < 4; i++) {
                    const rx2 = (sd * 5 + i * 23) % 28 + 6;
                    const ry2 = i * 12 + 6;
                    const rw = 10 + (i * 7 + sd) % 6;
                    ctx.fillStyle = [C.rk2, C.rk7, C.rk1, C.rk8][i];
                    ctx.fillRect(x + rx2, y + ry2, rw, 8);
                    ctx.fillStyle = C.rkh;
                    ctx.fillRect(x + rx2, y + ry2, rw, D);
                }
                ctx.fillStyle = '#2d9b2d';
                ctx.globalAlpha = 0.4;
                ctx.fillRect(x, y, s, 6);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.mv2;
                ctx.globalAlpha = 0.5;
                for (let i = 0; i < 4; i++) {
                    ctx.fillRect(x + (sd * 3 + i * 29) % 38 + 4, y + 1, D, 3 + (i & 1));
                }
                ctx.globalAlpha = 1;
                break;
            }

            case 28: {
                const wft = t / 500;
                ctx.fillStyle = C.rk2;
                ctx.fillRect(x, y, 10, s);
                ctx.fillRect(x + 38, y, 10, s);
                ctx.fillStyle = C.w1;
                ctx.fillRect(x + 10, y, 28, s);
                ctx.fillStyle = C.w2;
                ctx.fillRect(x + 14, y, 20, s);
                ctx.fillStyle = C.w4;
                ctx.fillRect(x + 18, y, 12, s);
                for (let wy = 0; wy < 48; wy += 6) {
                    const wx = Math.sin(wft * 2 + wy * 0.2 + sd) * 3;
                    ctx.fillStyle = C.wf;
                    ctx.globalAlpha = 0.5 + Math.sin(wft + wy * 0.3) * 0.3;
                    ctx.fillRect(x + 14 + wx, y + wy, 20, 2);
                    ctx.fillStyle = '#fff';
                    ctx.globalAlpha = 0.3 + Math.sin(wft * 1.5 + wy * 0.4) * 0.2;
                    ctx.fillRect(x + 18 + wx, y + wy, 12, D);
                }
                ctx.globalAlpha = 1;
                for (let i = 0; i < 4; i++) {
                    ctx.fillStyle = [C.rk1, C.rk7, C.rk8, C.rk2][i];
                    ctx.fillRect(x + 1, y + i * 13 + 2, 8, 8);
                    ctx.fillRect(x + 39, y + i * 13 + 6, 8, 8);
                }
                break;
            }

            case 29: {
                ctx.fillStyle = '#2d9b2d';
                ctx.fillRect(x, y, s, s);
                ctx.fillStyle = C.rkd;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + 28, 16, 12, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.rk5;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + 28, 14, 10, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.rk2;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + 26, 12, 8, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = C.rkh;
                ctx.globalAlpha = 0.3;
                ctx.fillRect(x + 14, y + 20, 16, 4);
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
