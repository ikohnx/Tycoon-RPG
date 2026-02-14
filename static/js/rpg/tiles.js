window.RPGTiles = (function() {
    let _ctx;
    const _cache = {};
    const ANIMATED_TILES = {3: true};
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

            case 26: {
                ctx.fillStyle = C.rk5;
                ctx.fillRect(x, y, s, s);
                ditherFast(x, y, s, 20, C.rk3, C.rk5);
                ditherFast(x, y + 16, s, 20, C.rk5, C.rkd);
                ditherFast(x, y + 32, s, 16, C.rkd, C.rk5);
                for (let i = 0; i < 6; i++) {
                    const rx2 = (sd * 7 + i * 31) % 30 + 4;
                    const ry2 = (sd * 11 + i * 19) % 34 + 4;
                    const rw = 8 + (i * 3 + sd) % 8;
                    const rh = 6 + (i * 5 + sd) % 6;
                    const rc = [C.rk1, C.rk2, C.rk7, C.rk8, C.rk4, C.rk9][i];
                    ctx.fillStyle = rc;
                    ctx.beginPath();
                    ctx.ellipse(rx2 + x + rw/2, ry2 + y + rh/2, rw/2, rh/2, (i * 0.3), 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = C.rkh;
                    ctx.globalAlpha = 0.25;
                    ctx.fillRect(x + rx2 + 1, y + ry2, rw - 2, 2);
                    ctx.globalAlpha = 1;
                    ctx.fillStyle = C.rkd;
                    ctx.globalAlpha = 0.3;
                    ctx.fillRect(x + rx2 + 1, y + ry2 + rh - 2, rw - 2, 2);
                    ctx.globalAlpha = 1;
                }
                ctx.fillStyle = C.mv1;
                ctx.globalAlpha = 0.4;
                for (let i = 0; i < 3; i++) {
                    const mx = (sd * 3 + i * 37) % 34 + 6;
                    const my = (sd * 7 + i * 23) % 30 + 8;
                    ctx.fillRect(x + mx, y + my, 3, D);
                    ctx.fillRect(x + mx + 1, y + my + 1, 2, D);
                }
                ctx.globalAlpha = 1;
                ctx.fillStyle = 'rgba(0,0,0,0.15)';
                ctx.fillRect(x, y + 44, s, 4);
                ctx.fillStyle = 'rgba(255,255,255,0.08)';
                ctx.fillRect(x, y, s, 4);
                break;
            }

            case 27: {
                ctx.fillStyle = C.rk5;
                ctx.fillRect(x, y, s, s);
                ditherFast(x, y, s, s, C.rkd, C.rk5);
                for (let i = 0; i < 5; i++) {
                    const rx2 = (sd * 5 + i * 23) % 28 + 6;
                    const ry2 = i * 10 + 2;
                    const rw = 10 + (i * 7 + sd) % 6;
                    const rc2 = [C.rk2, C.rk7, C.rk1, C.rk8, C.rk4][i];
                    ctx.fillStyle = rc2;
                    ctx.beginPath();
                    ctx.ellipse(x + rx2 + rw/2, y + ry2 + 4, rw/2, 4, 0.2 * i, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = C.rkh;
                    ctx.globalAlpha = 0.2;
                    ctx.fillRect(x + rx2 + 1, y + ry2, rw - 2, D);
                    ctx.globalAlpha = 1;
                }
                ctx.fillStyle = C.g2;
                ctx.globalAlpha = 0.2;
                ctx.beginPath();
                ctx.ellipse(x + 24, y + 2, 22, 5, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.mv2;
                ctx.globalAlpha = 0.5;
                for (let i = 0; i < 4; i++) {
                    ctx.fillRect(x + (sd * 3 + i * 29) % 38 + 4, y + 1, D, 3 + (i & 1));
                    ctx.fillRect(x + (sd * 7 + i * 17) % 38 + 4, y + 2, D, 2);
                }
                ctx.globalAlpha = 1;
                ctx.fillStyle = 'rgba(0,0,0,0.2)';
                ctx.fillRect(x, y + 44, s, 4);
                break;
            }

            case 28: {
                const wft = t / 500;
                ctx.fillStyle = C.rk5;
                ctx.fillRect(x, y, s, s);
                ditherFast(x, y, s, s, C.rkd, C.rk5);
                ctx.fillStyle = C.w1;
                ctx.fillRect(x + 8, y, 32, s);
                ctx.fillStyle = C.w2;
                ctx.fillRect(x + 12, y, 24, s);
                ctx.fillStyle = C.w4;
                ctx.fillRect(x + 16, y, 16, s);
                for (let wy = 0; wy < 48; wy += 3) {
                    const wx = Math.sin(wft * 2 + wy * 0.2 + sd) * 3;
                    ctx.fillStyle = C.wf;
                    ctx.globalAlpha = 0.5 + Math.sin(wft + wy * 0.3) * 0.3;
                    ctx.fillRect(x + 14 + wx, y + wy, 20, 2);
                    ctx.fillStyle = '#fff';
                    ctx.globalAlpha = 0.3 + Math.sin(wft * 1.5 + wy * 0.4) * 0.2;
                    ctx.fillRect(x + 18 + wx, y + wy, 12, D);
                }
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.wsp;
                for (let i = 0; i < 8; i++) {
                    const spx = 10 + Math.sin(wft * 3 + i * 1.2) * 6;
                    const spy = (i * 7 + Math.floor(wft * 20) * 3) % 48;
                    ctx.globalAlpha = 0.4 + Math.sin(wft * 4 + i) * 0.3;
                    ctx.fillRect(x + spx + 8, y + spy, 2, D);
                }
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.rk2;
                ctx.fillRect(x, y, 10, s);
                ctx.fillRect(x + 38, y, 10, s);
                for (let i = 0; i < 4; i++) {
                    ctx.fillStyle = [C.rk1, C.rk7, C.rk8, C.rk2][i];
                    ctx.beginPath();
                    ctx.ellipse(x + 5, y + i * 13 + 6, 6, 5, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.beginPath();
                    ctx.ellipse(x + 43, y + i * 13 + 10, 6, 5, 0, 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.fillStyle = C.wms;
                ctx.globalAlpha = 0.15 + Math.sin(wft) * 0.1;
                ctx.fillRect(x + 6, y, 6, s);
                ctx.fillRect(x + 36, y, 6, s);
                ctx.globalAlpha = 1;
                break;
            }

            case 29: {
                ctx.fillStyle = C.rk5;
                ctx.fillRect(x, y, s, s);
                ditherFast(x, y, s, 24, C.rk3, C.rk5);
                ditherFast(x, y + 20, s, 28, C.rk5, C.rkd);
                for (let i = 0; i < 4; i++) {
                    const rx2 = (sd * 7 + i * 23) % 26 + 8;
                    const ry2 = (sd * 3 + i * 17) % 20 + 14;
                    ctx.fillStyle = [C.rk1, C.rk7, C.rk2, C.rk8][i];
                    ctx.beginPath();
                    ctx.ellipse(x + rx2, y + ry2, 7, 5, i * 0.4, 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.fillStyle = C.rkh;
                ctx.globalAlpha = 0.12;
                ctx.fillRect(x, y, s, 6);
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.mv1;
                ctx.globalAlpha = 0.35;
                for (let i = 0; i < 5; i++) {
                    const vx = (sd * 5 + i * 19) % 38 + 4;
                    const vy = (sd * 11 + i * 13) % 30 + 4;
                    ctx.fillRect(x + vx, y + vy, D, 4 + (i & 1) * 2);
                    ctx.fillRect(x + vx + 1, y + vy + 1, D, 3);
                }
                ctx.globalAlpha = 1;
                ctx.fillStyle = C.mv2;
                ctx.globalAlpha = 0.3;
                for (let i = 0; i < 3; i++) {
                    ctx.beginPath();
                    ctx.ellipse(x + (sd * 7 + i * 31) % 30 + 8, y + (sd * 3 + i * 17) % 24 + 12, 3, 2, 0, 0, Math.PI * 2);
                    ctx.fill();
                }
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
