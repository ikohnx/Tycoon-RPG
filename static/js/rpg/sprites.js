window.RPGSprites = (function() {
    const shade = RPGColors.shade;

    const SKIN_TONES = [
        {skin:'#f4d0a0',skinHL:'#ffe8c8',skinSh:'#d8a870',skinDk:'#c09060',skinRim:'#e8c090',cheek:'#e8b090',nose:'#d8b080'},
        {skin:'#c68642',skinHL:'#dca060',skinSh:'#a06830',skinDk:'#885020',skinRim:'#b87838',cheek:'#c07838',nose:'#b07030'},
        {skin:'#8d5524',skinHL:'#a87040',skinSh:'#704018',skinDk:'#603010',skinRim:'#7a4820',cheek:'#8a4820',nose:'#7a4018'},
        {skin:'#ffdbac',skinHL:'#fff0d8',skinSh:'#e8c090',skinDk:'#d0a870',skinRim:'#f0d0a0',cheek:'#f0c0a0',nose:'#e8c090'},
        {skin:'#e0ac69',skinHL:'#f0c888',skinSh:'#c89050',skinDk:'#b07838',skinRim:'#d09858',cheek:'#d09050',nose:'#c88848'},
        {skin:'#503335',skinHL:'#684848',skinSh:'#402028',skinDk:'#301820',skinRim:'#583038',cheek:'#582830',nose:'#482028'}
    ];
    const EYE_COLORS = ['#1830a0','#206020','#804020','#602080','#208080','#303030','#a05020','#2060a0'];
    const HAIR_PRESETS = [
        {h:'#2888e0',hHL:'#50b0ff',hDk:'#1060a0',hMd:'#3898d0'},
        {h:'#e8d060',hHL:'#f8e888',hDk:'#b09830',hMd:'#d0c050'},
        {h:'#c03020',hHL:'#e05040',hDk:'#801810',hMd:'#a82818'},
        {h:'#101010',hHL:'#383838',hDk:'#000000',hMd:'#202020'},
        {h:'#f0f0f0',hHL:'#ffffff',hDk:'#c0c0c0',hMd:'#e0e0e0'},
        {h:'#e87028',hHL:'#ff9050',hDk:'#c04010',hMd:'#d86020'},
        {h:'#604080',hHL:'#8060a0',hDk:'#402060',hMd:'#503070'},
        {h:'#2080c0',hHL:'#40a0e0',hDk:'#106090',hMd:'#1870a8'}
    ];

    const ARCHETYPES = {
        merchant: {hairStyle:1,build:'stocky',outfit:'vest',acc:'bag',hatType:'beret',class:'trader'},
        scholar:  {hairStyle:2,build:'slim',outfit:'robe',acc:'glasses',hatType:null,class:'mage'},
        elder:    {hairStyle:3,build:'normal',outfit:'robe_long',acc:'staff',hatType:null,class:'sage'},
        warrior:  {hairStyle:4,build:'broad',outfit:'armor',acc:'shield',hatType:null,class:'knight'},
        scout:    {hairStyle:5,build:'slim',outfit:'cloak',acc:'quiver',hatType:'hood',class:'ranger'},
        noble:    {hairStyle:6,build:'normal',outfit:'doublet',acc:'medallion',hatType:'crown',class:'noble'},
        artisan:  {hairStyle:7,build:'stocky',outfit:'apron_outfit',acc:'tools',hatType:'bandana',class:'crafter'},
        mystic:   {hairStyle:0,build:'slim',outfit:'robe_fancy',acc:'orb',hatType:'wizard',class:'mystic'}
    };

    function getArchetype(spriteId) {
        const keys = Object.keys(ARCHETYPES);
        return ARCHETYPES[keys[(spriteId || 0) % keys.length]];
    }

    function buildNPCPal(color, spriteId) {
        const c = color || '#44aa44';
        const sid = spriteId || 0;
        const skinSet = SKIN_TONES[sid % SKIN_TONES.length];
        const hairSet = HAIR_PRESETS[sid % HAIR_PRESETS.length];
        const eyeC = EYE_COLORS[sid % EYE_COLORS.length];
        const arch = getArchetype(sid);
        return {
            hair: hairSet.h, hairHL: hairSet.hHL, hairDk: hairSet.hDk, hairMd: hairSet.hMd,
            ...skinSet,
            eyeW: '#f0f0ff', eye: eyeC, eyeHL: shade(eyeC, 30), pupil: '#080830', eyeLash: '#201018',
            mouth: '#c07050',
            tunic: c, tunicHL: shade(c, 30), tunicMd: shade(c, 15), tunicDk: shade(c, -30), tunicSh: shade(c, -45),
            tunicTrim: shade(c, 40), tunicTrimDk: shade(c, 10),
            collar: shade(c, 50), collarSh: shade(c, 30),
            shoulder: shade(c, 5), shoulderHL: shade(c, 25),
            belt: '#b09030', beltBk: '#806020', beltHL: '#d0b040',
            pants: shade(c, -35), pantsDk: shade(c, -50), pantsHL: shade(c, -20),
            boots: '#504030', bootsHL: '#685040', bootsDk: '#382818', bootsCuff: '#605038', bootsSole: '#201008',
            glove: '#e8d8b8', gloveSh: '#c8b890',
            cape: shade(c, -15), capeMd: shade(c, -25), capeDk: shade(c, -40), capeHL: shade(c, 5), capeEdge: shade(c, -50),
            outline: '#101020',
            weapon: '#a0a8b8', weaponHL: '#d0d8e0', weaponDk: '#606878',
            vest: shade(c, -10), vestHL: shade(c, 10), vestDk: shade(c, -35),
            robe: c, robeHL: shade(c, 25), robeDk: shade(c, -25), robeTrim: shade(c, 45),
            armor: '#808898', armorHL: '#b0b8c8', armorDk: '#505868', armorTrim: '#c0a040',
            armorMd: '#909ab0', armorEdge: '#404858', armorGlow: '#d0d8e8',
            cloak: shade(c, -20), cloakHL: shade(c, 0), cloakDk: shade(c, -45),
            acc1: shade(c, 50), acc2: shade(c, -20),
            scarf: '#c82828', scarfHL: '#e84848', scarfDk: '#901818', scarfMd: '#b02020',
            gold: '#d0a030', goldHL: '#f0c848', goldDk: '#906818', goldMd: '#c09028',
            arch
        };
    }

    const _spriteCache = {};

    function drawSpriteCached(ctx, gt, type, x, y, facing, frame, moving, color, spriteId, TS, SPRITE_YOFF) {
        const key = type + '_' + (spriteId || 0) + '_' + (color || '') + '_' + facing + '_' + (frame || 0) + '_' + (moving ? 1 : 0);
        let cached = _spriteCache[key];
        if (!cached) {
            const W = TS + 16;
            const H = TS + (SPRITE_YOFF || 0) + 24;
            const off = document.createElement('canvas');
            off.width = W;
            off.height = H;
            const oc = off.getContext('2d');
            oc.imageSmoothingEnabled = false;
            _drawSpriteRaw(oc, gt, type, 8, (SPRITE_YOFF || 0) + 4, facing, frame, moving, color, spriteId, TS, SPRITE_YOFF);
            _spriteCache[key] = off;
            cached = off;
        }
        ctx.drawImage(cached, x - 8, y - (SPRITE_YOFF || 0) - 4);
    }

    function _drawSpriteRaw(ctx, gt, type, x, y, facing, frame, moving, color, spriteId, TS, SPRITE_YOFF) {
        const cx = x + 24;
        const isHero = type === 'hero';
        const sid = spriteId || 0;
        const arch = isHero ? {hairStyle:0,build:'normal',outfit:'hero_armor',acc:'sword',hatType:null,class:'hero'} : getArchetype(sid);
        const pal = isHero ? buildHeroPal() : buildNPCPal(color, sid);

        const dir = facing === 'down' ? 0 : facing === 'right' ? 1 : facing === 'up' ? 2 : 3;
        const bob = moving ? Math.sin(frame * Math.PI / 2) * 2 : 0;
        const breathe = !moving ? Math.sin(gt / 700) * 0.5 : 0;
        const wc = moving ? frame % 4 : 0;
        const legL = wc === 1 ? 4 : wc === 3 ? -3 : 0;
        const legR = wc === 1 ? -3 : wc === 3 ? 4 : 0;
        const armSwing = moving ? Math.sin(frame * Math.PI / 2) * 2.5 : 0;
        const by = Math.round(-bob + breathe);
        const sy = y - SPRITE_YOFF;

        const ell = (ex,ey,rx,ry) => { ctx.beginPath(); ctx.ellipse(ex,ey,rx,ry,0,0,Math.PI*2); ctx.fill(); };
        const rect = (rx,ry,rw,rh) => { ctx.fillRect(rx,ry,rw,rh); };
        const tri = (x1,y1,x2,y2,x3,y3) => { ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.lineTo(x3,y3); ctx.fill(); };

        const headY = sy + 10 + by;
        const bodyY = sy + 42 + by;
        const legY = sy + 62 + by;
        const bw = arch.build === 'broad' ? 11 : arch.build === 'stocky' ? 10 : arch.build === 'slim' ? 7 : 9;
        const OL = pal.outline;

        const drawShadow = () => {
            ctx.fillStyle = 'rgba(0,0,0,0.2)';
            ell(cx, sy + 80, 14, 4);
        };

        const drawCape = () => {
            const capeFlow = moving ? Math.sin(frame * Math.PI / 2) * 3 : Math.sin(gt / 1000) * 1;
            if (isHero || arch.outfit === 'cloak') {
                ctx.fillStyle = OL;
                rect(cx-bw-4, bodyY-4, bw*2+8, 28 + Math.round(capeFlow));
                ctx.fillStyle = pal.cape || pal.cloak || pal.tunicDk;
                rect(cx-bw-3, bodyY-3, bw*2+6, 26 + Math.round(capeFlow));
                ctx.fillStyle = pal.capeMd || pal.cloakDk || pal.tunicSh;
                rect(cx-bw-3, bodyY+20, bw*2+6, 3 + Math.round(capeFlow));
                ctx.fillStyle = pal.capeHL || pal.cloakHL || pal.tunicHL;
                rect(cx-bw-1, bodyY-1, bw, 18);
                ctx.fillStyle = pal.capeDk || pal.cloakDk;
                rect(cx+2, bodyY+4, bw-2, 14);
                ctx.fillStyle = pal.capeEdge || pal.capeDk;
                rect(cx-bw-3, bodyY+22+Math.round(capeFlow), bw*2+6, 2);
            }
        };

        const drawBody = () => {
            const of = arch.outfit;
            const isArmored = of === 'armor' || of === 'hero_armor';
            const isRobed = of === 'robe' || of === 'robe_long' || of === 'robe_fancy';

            ctx.fillStyle = OL;
            rect(cx-bw-2, bodyY-3, bw*2+4, 23);

            if (isArmored) {
                ctx.fillStyle = pal.armorDk || '#505868';
                rect(cx-bw, bodyY-1, bw*2, 20);
                ctx.fillStyle = pal.armor || '#808898';
                rect(cx-bw+1, bodyY, bw*2-2, 18);
                ctx.fillStyle = pal.armorHL || '#b0b8c8';
                rect(cx-bw+2, bodyY+1, bw-3, 12);
                ctx.fillStyle = pal.armorMd || pal.armor;
                rect(cx+1, bodyY+2, bw-3, 10);
                ctx.fillStyle = pal.armorGlow || '#d0d8e8';
                rect(cx-bw+3, bodyY+2, 3, 6);
                ctx.fillStyle = pal.armorTrim || '#c0a040';
                rect(cx-bw+1, bodyY+17, bw*2-2, 2);
                rect(cx-1, bodyY+1, 2, 16);
                ctx.fillStyle = pal.goldHL || '#f0c848';
                rect(cx-1, bodyY+1, 1, 14);
                ctx.fillStyle = pal.armorDk;
                rect(cx-bw+1, bodyY+14, bw*2-2, 1);
                ctx.fillStyle = OL;
                rect(cx-bw, bodyY+16, bw*2, 1);
                ctx.fillStyle = pal.gold || '#d0a030';
                rect(cx-3, bodyY+8, 6, 3);
                ctx.fillStyle = pal.goldHL;
                rect(cx-2, bodyY+9, 4, 1);
            } else if (isRobed) {
                const bh = of === 'robe_long' || of === 'robe_fancy' ? 24 : 20;
                ctx.fillStyle = pal.robeDk || pal.tunicDk;
                rect(cx-bw, bodyY-1, bw*2, bh);
                ctx.fillStyle = pal.robe || pal.tunic;
                rect(cx-bw+1, bodyY, bw*2-2, bh-2);
                ctx.fillStyle = pal.robeHL || pal.tunicHL;
                rect(cx-bw+2, bodyY+1, bw-2, bh-6);
                if (of === 'robe_fancy') {
                    ctx.fillStyle = pal.robeTrim || '#f0e060';
                    rect(cx-1, bodyY+2, 2, bh-4);
                    for (let i = 0; i < 3; i++) {
                        rect(cx-bw+3, bodyY+4+i*6, bw*2-6, 1);
                    }
                    ctx.fillStyle = pal.goldHL || '#f0c848';
                    rect(cx-bw+1, bodyY+bh-3, bw*2-2, 2);
                }
            } else if (of === 'vest') {
                ctx.fillStyle = pal.tunic;
                rect(cx-bw, bodyY-1, bw*2, 20);
                ctx.fillStyle = pal.tunicHL;
                rect(cx-bw+1, bodyY, bw-2, 14);
                ctx.fillStyle = pal.vest;
                rect(cx-bw, bodyY, 5, 18);
                rect(cx+bw-5, bodyY, 5, 18);
                ctx.fillStyle = pal.vestHL;
                rect(cx-bw+1, bodyY+1, 3, 14);
                rect(cx+bw-4, bodyY+1, 3, 14);
                ctx.fillStyle = '#c0a040';
                rect(cx-1, bodyY+4, 2, 2);
                rect(cx-1, bodyY+9, 2, 2);
                rect(cx-1, bodyY+13, 2, 2);
            } else if (of === 'doublet') {
                ctx.fillStyle = pal.tunic;
                rect(cx-bw, bodyY-1, bw*2, 20);
                ctx.fillStyle = pal.tunicHL;
                rect(cx-bw+1, bodyY, bw-1, 16);
                ctx.fillStyle = '#fff';
                rect(cx-2, bodyY+2, 4, 14);
                ctx.fillStyle = '#e0e0e0';
                rect(cx-1, bodyY+3, 2, 12);
                ctx.fillStyle = '#c0a040';
                rect(cx-1, bodyY+4, 2, 2);
                rect(cx-1, bodyY+8, 2, 2);
                rect(cx-1, bodyY+12, 2, 2);
            } else if (of === 'apron_outfit') {
                ctx.fillStyle = pal.tunic;
                rect(cx-bw, bodyY-1, bw*2, 20);
                ctx.fillStyle = pal.tunicHL;
                rect(cx-bw+1, bodyY, bw-1, 14);
                ctx.fillStyle = '#e8e0d0';
                rect(cx-bw+2, bodyY+5, bw*2-4, 14);
                ctx.fillStyle = '#d8d0c0';
                rect(cx-bw+3, bodyY+6, bw*2-6, 12);
                ctx.fillStyle = '#c8c0b0';
                rect(cx-1, bodyY+3, 2, 3);
            } else {
                ctx.fillStyle = pal.tunicDk;
                rect(cx-bw, bodyY-1, bw*2, 20);
                ctx.fillStyle = pal.tunic;
                rect(cx-bw+1, bodyY, bw*2-2, 18);
                ctx.fillStyle = pal.tunicHL;
                rect(cx-bw+2, bodyY+1, bw-2, 12);
                ctx.fillStyle = pal.tunicDk;
                rect(cx-1, bodyY+2, 2, 14);
            }

            ctx.fillStyle = pal.collar || pal.tunicHL;
            rect(cx-bw+1, bodyY-2, bw*2-2, 3);
            ctx.fillStyle = shade(pal.collar || pal.tunicHL, 15);
            rect(cx-bw+2, bodyY-2, bw*2-4, 1);

            if (!isRobed) {
                ctx.fillStyle = pal.belt;
                rect(cx-bw, bodyY+16, bw*2, 3);
                ctx.fillStyle = pal.beltHL;
                rect(cx-2, bodyY+16, 4, 3);
                ctx.fillStyle = pal.beltBk;
                rect(cx-bw, bodyY+18, bw*2, 1);
                ctx.fillStyle = pal.goldHL || '#f0c848';
                rect(cx-1, bodyY+17, 2, 1);
            }

            if (isHero) {
                drawScarf(dir);
            }
        };

        const drawScarf = (dir) => {
            const scarfFlow = moving ? Math.sin(frame * Math.PI / 2) * 2 : Math.sin(gt / 800) * 1;
            ctx.fillStyle = OL;
            if (dir === 0 || dir === 1) {
                rect(cx+bw-2, bodyY-3, 6, 4);
                rect(cx+bw, bodyY+1, 5, 10 + Math.round(scarfFlow));
                ctx.fillStyle = pal.scarf;
                rect(cx+bw-1, bodyY-2, 5, 3);
                rect(cx+bw+1, bodyY+2, 3, 8 + Math.round(scarfFlow));
                ctx.fillStyle = pal.scarfHL;
                rect(cx+bw, bodyY-2, 3, 2);
                rect(cx+bw+1, bodyY+3, 2, 4);
                ctx.fillStyle = pal.scarfDk;
                rect(cx+bw+1, bodyY+8+Math.round(scarfFlow), 3, 2);
            } else if (dir === 3) {
                rect(cx-bw-4, bodyY-3, 6, 4);
                rect(cx-bw-5, bodyY+1, 5, 10 + Math.round(scarfFlow));
                ctx.fillStyle = pal.scarf;
                rect(cx-bw-3, bodyY-2, 5, 3);
                rect(cx-bw-4, bodyY+2, 3, 8 + Math.round(scarfFlow));
                ctx.fillStyle = pal.scarfHL;
                rect(cx-bw-2, bodyY-2, 3, 2);
                ctx.fillStyle = pal.scarfDk;
                rect(cx-bw-4, bodyY+8+Math.round(scarfFlow), 3, 2);
            } else {
                rect(cx-3, bodyY-4, 6, 3);
                ctx.fillStyle = pal.scarf;
                rect(cx-2, bodyY-3, 4, 2);
                ctx.fillStyle = pal.scarfHL;
                rect(cx-1, bodyY-3, 2, 1);
            }
        };

        const drawShoulderArmor = (sx, sy, isLeft) => {
            const isArmored = arch.outfit === 'armor' || arch.outfit === 'hero_armor';
            if (!isArmored) return;
            ctx.fillStyle = OL;
            ell(sx, sy+2, 6, 5);
            ctx.fillStyle = pal.armorDk;
            ell(sx, sy+2, 5, 4);
            ctx.fillStyle = pal.armor;
            ell(sx, sy+1, 4, 3);
            ctx.fillStyle = pal.armorHL;
            ell(sx + (isLeft ? -1 : 1), sy, 2, 2);
            ctx.fillStyle = pal.armorTrim;
            rect(sx-4, sy+4, 8, 1);
        };

        const drawArms = () => {
            const la = Math.round(armSwing);
            const ra = Math.round(-armSwing);
            const isArmored = arch.outfit === 'armor' || arch.outfit === 'hero_armor';

            ctx.fillStyle = OL;
            rect(cx-bw-5, bodyY-1+la, 6, 14);
            rect(cx+bw-1, bodyY-1+ra, 6, 14);

            const armC = isArmored ? (pal.armor || pal.tunic) : (pal.shoulder || pal.tunic);
            const armHL = isArmored ? (pal.armorHL || pal.tunicHL) : (pal.shoulderHL || pal.tunicHL);

            ctx.fillStyle = armC;
            rect(cx-bw-4, bodyY+la, 5, 12);
            rect(cx+bw, bodyY+ra, 5, 12);
            ctx.fillStyle = armHL;
            rect(cx-bw-3, bodyY+1+la, 3, 8);
            rect(cx+bw+1, bodyY+1+ra, 3, 8);

            if (isArmored) {
                ctx.fillStyle = pal.armorDk;
                rect(cx-bw-4, bodyY+5+la, 5, 1);
                rect(cx+bw, bodyY+5+ra, 5, 1);
                ctx.fillStyle = pal.armorTrim;
                rect(cx-bw-4, bodyY+la, 5, 1);
                rect(cx+bw, bodyY+ra, 5, 1);
            }

            drawShoulderArmor(cx-bw-2, bodyY-3+la, true);
            drawShoulderArmor(cx+bw+2, bodyY-3+ra, false);

            ctx.fillStyle = OL;
            rect(cx-bw-4, bodyY+10+la, 4, 4);
            rect(cx+bw+1, bodyY+10+ra, 4, 4);
            ctx.fillStyle = pal.glove || pal.skin;
            rect(cx-bw-3, bodyY+11+la, 3, 3);
            rect(cx+bw+1, bodyY+11+ra, 3, 3);
            ctx.fillStyle = pal.gloveSh || pal.skinSh;
            rect(cx-bw-3, bodyY+13+la, 3, 1);
            rect(cx+bw+1, bodyY+13+ra, 3, 1);
        };

        const drawLegs = () => {
            const isRobed = arch.outfit === 'robe_long' || arch.outfit === 'robe_fancy';

            ctx.fillStyle = OL;
            rect(cx-7, legY-2, 6, 16+legL);
            rect(cx+1, legY-2, 6, 16+legR);

            if (isRobed) {
                ctx.fillStyle = pal.robeDk || pal.pantsDk;
                rect(cx-6, legY, 5, 8+legL);
                rect(cx+1, legY, 5, 8+legR);
            } else {
                ctx.fillStyle = pal.pants;
                rect(cx-6, legY, 5, 8+legL);
                rect(cx+1, legY, 5, 8+legR);
                ctx.fillStyle = pal.pantsHL;
                rect(cx-5, legY+1, 3, 5);
                rect(cx+2, legY+1, 3, 5);
                ctx.fillStyle = pal.pantsDk;
                rect(cx-6, legY+6+legL, 5, 2);
                rect(cx+1, legY+6+legR, 5, 2);
            }

            ctx.fillStyle = OL;
            rect(cx-7, legY+8+legL, 7, 7);
            rect(cx, legY+8+legR, 7, 7);
            ctx.fillStyle = pal.boots;
            rect(cx-6, legY+8+legL, 6, 6);
            rect(cx+1, legY+8+legR, 6, 6);
            ctx.fillStyle = pal.bootsHL;
            rect(cx-5, legY+9+legL, 3, 3);
            rect(cx+2, legY+9+legR, 3, 3);
            ctx.fillStyle = pal.bootsDk;
            rect(cx-6, legY+13+legL, 6, 1);
            rect(cx+1, legY+13+legR, 6, 1);
            ctx.fillStyle = pal.bootsCuff;
            rect(cx-6, legY+8+legL, 6, 2);
            rect(cx+1, legY+8+legR, 6, 2);
            ctx.fillStyle = pal.bootsSole;
            rect(cx-7, legY+14+legL, 7, 1);
            rect(cx, legY+14+legR, 7, 1);
        };

        const drawHead = () => {
            const hcx = cx;
            const hcy = headY + 16;

            ctx.fillStyle = OL;
            ell(hcx, hcy, 15, 14);

            if (dir === 2) {
                ctx.fillStyle = pal.hairDk;
                ell(hcx, hcy-1, 14, 13);
                ctx.fillStyle = pal.hair;
                ell(hcx, hcy, 13, 12);
                ctx.fillStyle = pal.hairHL;
                ell(hcx-2, hcy-3, 7, 5);
                ctx.fillStyle = pal.hairMd;
                ell(hcx+3, hcy-1, 5, 4);
                drawHairBack(hcx, hcy);
                drawHat(hcx, hcy);
                return;
            }

            ctx.fillStyle = pal.hairDk;
            ell(hcx, hcy-2, 14, 13);
            ctx.fillStyle = pal.hair;
            ell(hcx, hcy-1, 13, 12);

            ctx.fillStyle = pal.skin;
            if (dir === 0) {
                ell(hcx, hcy+2, 11, 10);
            } else if (dir === 3) {
                ell(hcx-1, hcy+2, 11, 10);
            } else {
                ell(hcx+1, hcy+2, 11, 10);
            }
            ctx.fillStyle = pal.skinHL;
            ell(hcx + (dir===1?2:dir===3?-2:0), hcy, 7, 5);
            ctx.fillStyle = pal.skinRim;
            if (dir === 0) {
                ell(hcx, hcy+8, 8, 3);
            }

            drawFace(hcx, hcy+2, dir);
            drawHairFront(hcx, hcy, dir);
            drawHairBack(hcx, hcy);
            drawHat(hcx, hcy);
        };

        const drawFace = (fcx, fcy, dir) => {
            if (dir === 0) {
                ctx.fillStyle = OL;
                ell(fcx-5, fcy-1, 4.5, 4);
                ell(fcx+5, fcy-1, 4.5, 4);
                ctx.fillStyle = pal.eyeW;
                ell(fcx-5, fcy-1, 4, 3.5);
                ell(fcx+5, fcy-1, 4, 3.5);
                ctx.fillStyle = pal.eye;
                ell(fcx-5, fcy, 3, 3);
                ell(fcx+5, fcy, 3, 3);
                ctx.fillStyle = pal.eyeHL;
                ell(fcx-5, fcy+0.5, 2, 2);
                ell(fcx+5, fcy+0.5, 2, 2);
                ctx.fillStyle = pal.pupil;
                rect(fcx-6, fcy-1, 2, 3);
                rect(fcx+4, fcy-1, 2, 3);
                ctx.fillStyle = '#fff';
                rect(fcx-4, fcy-2, 2, 2);
                rect(fcx+6, fcy-2, 2, 2);
                ctx.fillStyle = OL;
                rect(fcx-8, fcy-4, 6, 1);
                rect(fcx+2, fcy-4, 6, 1);
                ctx.fillStyle = pal.eyeLash || OL;
                rect(fcx-8, fcy-4, 2, 1);
                rect(fcx+6, fcy-4, 2, 1);

                ctx.fillStyle = pal.nose || pal.skinSh;
                rect(fcx-1, fcy+4, 2, 2);
                ctx.fillStyle = pal.skinDk;
                rect(fcx-1, fcy+5, 2, 1);
                ctx.fillStyle = pal.mouth;
                rect(fcx-3, fcy+7, 6, 2);
                ctx.fillStyle = shade(pal.mouth, 30);
                rect(fcx-2, fcy+7, 4, 1);
                ctx.fillStyle = shade(pal.mouth, -20);
                rect(fcx-2, fcy+8, 4, 1);

                if (pal.cheek) {
                    ctx.fillStyle = pal.cheek;
                    ctx.globalAlpha = 0.25;
                    ell(fcx-9, fcy+3, 3, 2);
                    ell(fcx+9, fcy+3, 3, 2);
                    ctx.globalAlpha = 1;
                }
            } else if (dir === 3) {
                ctx.fillStyle = OL;
                ell(fcx-5, fcy-1, 4.5, 4);
                ctx.fillStyle = pal.eyeW;
                ell(fcx-5, fcy-1, 4, 3.5);
                ctx.fillStyle = pal.eye;
                ell(fcx-5, fcy, 3, 3);
                ctx.fillStyle = pal.pupil;
                rect(fcx-7, fcy-1, 2, 3);
                ctx.fillStyle = '#fff';
                rect(fcx-4, fcy-2, 2, 2);
                ctx.fillStyle = OL;
                rect(fcx-8, fcy-4, 6, 1);
                ctx.fillStyle = pal.nose || pal.skinSh;
                rect(fcx-10, fcy+3, 2, 2);
                ctx.fillStyle = pal.mouth;
                rect(fcx-7, fcy+7, 4, 1);
            } else if (dir === 1) {
                ctx.fillStyle = OL;
                ell(fcx+5, fcy-1, 4.5, 4);
                ctx.fillStyle = pal.eyeW;
                ell(fcx+5, fcy-1, 4, 3.5);
                ctx.fillStyle = pal.eye;
                ell(fcx+5, fcy, 3, 3);
                ctx.fillStyle = pal.pupil;
                rect(fcx+5, fcy-1, 2, 3);
                ctx.fillStyle = '#fff';
                rect(fcx+6, fcy-2, 2, 2);
                ctx.fillStyle = OL;
                rect(fcx+2, fcy-4, 6, 1);
                ctx.fillStyle = pal.nose || pal.skinSh;
                rect(fcx+8, fcy+3, 2, 2);
                ctx.fillStyle = pal.mouth;
                rect(fcx+3, fcy+7, 4, 1);
            }
        };

        const drawHairFront = (hcx, hcy, dir) => {
            const hs = arch.hairStyle;
            ctx.fillStyle = pal.hair;

            if (hs === 0 && isHero) {
                ell(hcx, hcy-4, 13, 9);
                ctx.fillStyle = pal.hairHL;
                ell(hcx-2, hcy-6, 7, 5);
                ctx.fillStyle = pal.hair;
                const spikes = [
                    [-8,-14,4,10], [-4,-18,4,12], [0,-20,4,14], [4,-17,4,11], [8,-14,3,9], [-10,-10,3,6]
                ];
                for (const [sx,sy,sw,sh] of spikes) {
                    ctx.fillStyle = pal.hair;
                    rect(hcx+sx, hcy+sy, sw, sh);
                    ctx.fillStyle = pal.hairHL;
                    rect(hcx+sx+1, hcy+sy+1, sw-2, sh-3);
                    ctx.fillStyle = pal.hairDk;
                    rect(hcx+sx, hcy+sy, 1, sh);
                }
                ctx.fillStyle = pal.hairMd;
                ell(hcx, hcy-6, 8, 4);
                ctx.fillStyle = pal.hairHL;
                rect(hcx-2, hcy-8, 2, 3);
                rect(hcx+1, hcy-9, 2, 3);
            } else if (hs === 0) {
                ell(hcx, hcy-4, 13, 9);
                ctx.fillStyle = pal.hairHL;
                ell(hcx-2, hcy-6, 7, 5);
                ctx.fillStyle = pal.hairDk;
                rect(hcx-6, hcy-12, 3, 6);
                rect(hcx-1, hcy-14, 3, 8);
                rect(hcx+4, hcy-12, 3, 6);
                ctx.fillStyle = pal.hair;
                rect(hcx-5, hcy-11, 2, 5);
                rect(hcx, hcy-13, 2, 7);
                rect(hcx+5, hcy-11, 2, 5);
                ctx.fillStyle = pal.hairHL;
                rect(hcx-4, hcy-10, 1, 3);
                rect(hcx+1, hcy-12, 1, 4);
            } else if (hs === 1) {
                ell(hcx, hcy-3, 13, 9);
                ctx.fillStyle = pal.hairHL;
                rect(hcx-8, hcy-8, 16, 3);
                ctx.fillStyle = pal.hairMd;
                ell(hcx, hcy-5, 10, 5);
                ctx.fillStyle = pal.hairDk;
                rect(hcx-10, hcy-1, 20, 2);
            } else if (hs === 2) {
                ell(hcx, hcy-4, 13, 10);
                ctx.fillStyle = pal.hairHL;
                ell(hcx-2, hcy-6, 7, 5);
                ctx.fillStyle = pal.hairMd;
                ell(hcx+3, hcy-3, 5, 4);
            } else if (hs === 3) {
                ell(hcx, hcy-3, 12, 8);
                ctx.fillStyle = pal.hairHL;
                ell(hcx, hcy-5, 7, 4);
            } else if (hs === 4) {
                ell(hcx, hcy-3, 12, 9);
                ctx.fillStyle = pal.hairHL;
                rect(hcx-3, hcy-9, 6, 5);
                ctx.fillStyle = pal.hairDk;
                rect(hcx-5, hcy-14, 10, 6);
                ctx.fillStyle = pal.hair;
                rect(hcx-3, hcy-15, 6, 5);
                ctx.fillStyle = pal.hairHL;
                rect(hcx-2, hcy-14, 4, 3);
                ctx.fillStyle = pal.hairMd;
                rect(hcx-1, hcy-12, 2, 2);
            } else if (hs === 5) {
                ell(hcx, hcy-3, 13, 9);
                ctx.fillStyle = pal.hairHL;
                ell(hcx-1, hcy-5, 7, 5);
                ctx.fillStyle = pal.hairMd;
                ell(hcx+2, hcy-2, 5, 4);
                if (dir === 0) {
                    ctx.fillStyle = pal.hair;
                    rect(hcx-12, hcy-2, 4, 20);
                    rect(hcx+8, hcy-2, 4, 20);
                    ctx.fillStyle = pal.hairHL;
                    rect(hcx-11, hcy, 2, 12);
                    rect(hcx+9, hcy, 2, 12);
                    ctx.fillStyle = pal.hairDk;
                    rect(hcx-12, hcy+16, 4, 3);
                    rect(hcx+8, hcy+16, 4, 3);
                }
            } else if (hs === 6) {
                ell(hcx, hcy-4, 14, 10);
                ctx.fillStyle = pal.hairHL;
                for (let i=0; i<5; i++) rect(hcx-9+i*4, hcy-8+Math.abs(i-2), 3, 3);
                ctx.fillStyle = pal.hairDk;
                rect(hcx-12, hcy-1, 24, 2);
                ctx.fillStyle = pal.hairMd;
                ell(hcx, hcy-6, 9, 4);
            } else {
                ell(hcx, hcy-3, 13, 9);
                ctx.fillStyle = pal.hairHL;
                ell(hcx, hcy-5, 7, 5);
                ctx.fillStyle = pal.hairMd;
                ell(hcx-3, hcy-2, 4, 3);
                if (dir === 1) {
                    ctx.fillStyle = pal.hairDk;
                    ell(hcx+3, hcy-9, 5, 5);
                    ctx.fillStyle = pal.hair;
                    ell(hcx+3, hcy-8, 4, 4);
                    ctx.fillStyle = pal.hairHL;
                    ell(hcx+2, hcy-9, 2, 2);
                }
            }
        };

        const drawHairBack = (hcx, hcy) => {
            const hs = arch.hairStyle;
            if (hs === 2) {
                ctx.fillStyle = pal.hair;
                if (dir === 0 || dir === 2) {
                    rect(hcx-12, hcy+5, 4, 16);
                    rect(hcx+8, hcy+5, 4, 16);
                    ctx.fillStyle = pal.hairHL;
                    rect(hcx-11, hcy+6, 2, 8);
                    rect(hcx+9, hcy+6, 2, 8);
                } else if (dir === 3) {
                    rect(hcx-12, hcy+5, 4, 18);
                    ctx.fillStyle = pal.hairHL;
                    rect(hcx-11, hcy+6, 2, 10);
                } else {
                    rect(hcx+8, hcy+5, 4, 18);
                    ctx.fillStyle = pal.hairHL;
                    rect(hcx+9, hcy+6, 2, 10);
                }
                ctx.fillStyle = pal.hairDk;
                if (dir === 0 || dir === 2) {
                    rect(hcx-12, hcy+19, 4, 2);
                    rect(hcx+8, hcy+19, 4, 2);
                } else if (dir === 3) {
                    rect(hcx-12, hcy+21, 4, 2);
                } else {
                    rect(hcx+8, hcy+21, 4, 2);
                }
            }
            if (hs === 5 && (dir === 1 || dir === 3)) {
                const sx = dir === 1 ? 8 : -12;
                ctx.fillStyle = pal.hair;
                rect(hcx+sx, hcy+5, 4, 18);
                ctx.fillStyle = pal.hairHL;
                rect(hcx+sx+1, hcy+6, 2, 10);
                ctx.fillStyle = pal.hairDk;
                ell(hcx+sx+2, hcy+24, 3, 2);
            }
        };

        const drawHat = (hcx, hcy) => {
            const ht = arch.hatType;
            if (!ht) return;
            hcy = headY + 16;
            if (ht === 'beret') {
                ctx.fillStyle = OL;
                ell(hcx+1, hcy-10, 12, 7);
                ctx.fillStyle = pal.acc1;
                ell(hcx+1, hcy-10, 11, 6);
                ctx.fillStyle = pal.acc2;
                ell(hcx, hcy-11, 7, 4);
                ctx.fillStyle = shade(pal.acc1, 20);
                ell(hcx-2, hcy-12, 4, 2);
            } else if (ht === 'hood') {
                ctx.fillStyle = OL;
                ell(hcx, hcy-3, 16, 14);
                ctx.fillStyle = pal.cloak;
                ell(hcx, hcy-3, 15, 13);
                ctx.fillStyle = pal.cloakHL;
                ell(hcx-1, hcy-5, 9, 7);
                ctx.fillStyle = pal.cloakDk;
                rect(hcx-14, hcy+7, 28, 3);
                ctx.fillStyle = shade(pal.cloak, 10);
                ell(hcx, hcy-8, 6, 3);
            } else if (ht === 'crown') {
                ctx.fillStyle = OL;
                rect(hcx-10, hcy-11, 20, 7);
                ctx.fillStyle = '#c0a040';
                rect(hcx-9, hcy-10, 18, 6);
                ctx.fillStyle = '#e0c060';
                rect(hcx-7, hcy-16, 3, 6); rect(hcx-1, hcy-18, 3, 8); rect(hcx+5, hcy-16, 3, 6);
                ctx.fillStyle = '#f0d878';
                rect(hcx-6, hcy-14, 2, 3); rect(hcx, hcy-16, 2, 4); rect(hcx+6, hcy-14, 2, 3);
                ctx.fillStyle = '#e02020';
                rect(hcx, hcy-13, 2, 2);
                ctx.fillStyle = '#2020e0';
                rect(hcx-6, hcy-11, 2, 2); rect(hcx+5, hcy-11, 2, 2);
            } else if (ht === 'bandana') {
                ctx.fillStyle = pal.acc1;
                rect(hcx-12, hcy-3, 24, 4);
                ctx.fillStyle = pal.acc2;
                rect(hcx-12, hcy-2, 24, 1);
                ctx.fillStyle = shade(pal.acc1, 15);
                rect(hcx-12, hcy-3, 24, 1);
                ctx.fillStyle = pal.acc1;
                rect(hcx+9, hcy-2, 4, 7); rect(hcx+10, hcy+3, 3, 5);
                ctx.fillStyle = pal.acc2;
                rect(hcx+11, hcy+6, 2, 2);
            } else if (ht === 'wizard') {
                ctx.fillStyle = OL;
                tri(hcx-14, hcy-2, hcx, hcy-28, hcx+14, hcy-2);
                ctx.fillStyle = pal.tunicDk;
                tri(hcx-13, hcy-3, hcx, hcy-26, hcx+13, hcy-3);
                ctx.fillStyle = pal.tunic;
                tri(hcx-11, hcy-3, hcx, hcy-24, hcx+11, hcy-3);
                ctx.fillStyle = pal.tunicHL;
                tri(hcx-7, hcy-4, hcx-1, hcy-20, hcx+5, hcy-4);
                ctx.fillStyle = pal.tunicMd || pal.tunic;
                tri(hcx-3, hcy-5, hcx, hcy-18, hcx+3, hcy-5);
                ctx.fillStyle = '#f0e060';
                ell(hcx, hcy-25, 3, 3);
                ctx.fillStyle = '#f8f080';
                ell(hcx-1, hcy-26, 2, 2);
                ctx.fillStyle = pal.tunicDk;
                rect(hcx-14, hcy-3, 28, 3);
                ctx.fillStyle = pal.robeTrim || '#f0e060';
                rect(hcx-14, hcy-4, 28, 1);
                rect(hcx-14, hcy, 28, 1);
            }
        };

        const drawAccessory = () => {
            const ac = arch.acc;
            if (!ac) return;
            if (ac === 'sword') {
                if (dir === 0 || dir === 1) {
                    ctx.fillStyle = OL;
                    rect(cx+bw+2, bodyY-8, 5, 26);
                    ctx.fillStyle = pal.weaponDk;
                    rect(cx+bw+3, bodyY-7, 3, 24);
                    ctx.fillStyle = pal.weapon;
                    rect(cx+bw+4, bodyY-7, 2, 22);
                    ctx.fillStyle = pal.weaponHL;
                    rect(cx+bw+5, bodyY-6, 1, 14);
                    ctx.fillStyle = '#c0a040';
                    rect(cx+bw+1, bodyY+16, 7, 3);
                    ctx.fillStyle = '#e0c060';
                    rect(cx+bw+2, bodyY+17, 5, 1);
                    ctx.fillStyle = '#8B6914';
                    rect(cx+bw+3, bodyY+19, 3, 4);
                    ctx.fillStyle = '#a08020';
                    rect(cx+bw+4, bodyY+19, 1, 4);
                }
            } else if (ac === 'shield') {
                if (dir === 0 || dir === 3) {
                    ctx.fillStyle = OL;
                    ell(cx-bw-6, bodyY+6, 7, 8);
                    ctx.fillStyle = pal.armorDk;
                    ell(cx-bw-6, bodyY+6, 6, 7);
                    ctx.fillStyle = pal.armor;
                    ell(cx-bw-6, bodyY+6, 5, 6);
                    ctx.fillStyle = pal.armorHL;
                    ell(cx-bw-7, bodyY+5, 3, 3);
                    ctx.fillStyle = pal.armorTrim;
                    rect(cx-bw-7, bodyY+5, 2, 3);
                    ctx.fillStyle = pal.goldHL || '#f0c848';
                    ell(cx-bw-6, bodyY+6, 2, 2);
                }
            } else if (ac === 'staff') {
                ctx.fillStyle = OL;
                rect(cx+bw+2, bodyY-14, 4, 34);
                ctx.fillStyle = '#8B6914';
                rect(cx+bw+3, bodyY-13, 2, 32);
                ctx.fillStyle = '#a07828';
                rect(cx+bw+4, bodyY-13, 1, 30);
                ctx.fillStyle = '#60d0f0';
                ell(cx+bw+4, bodyY-16, 4, 4);
                ctx.fillStyle = '#90e8ff';
                ell(cx+bw+3, bodyY-17, 2, 2);
                ctx.fillStyle = OL;
                ell(cx+bw+4, bodyY-16, 5, 5);
                ctx.fillStyle = '#60d0f0';
                ell(cx+bw+4, bodyY-16, 4, 4);
                ctx.fillStyle = '#a0f0ff';
                ell(cx+bw+3, bodyY-17, 2, 2);
            } else if (ac === 'bag') {
                ctx.fillStyle = OL;
                rect(cx+bw+1, bodyY+6, 8, 10);
                ctx.fillStyle = '#a07040';
                rect(cx+bw+2, bodyY+7, 6, 8);
                ctx.fillStyle = '#b88050';
                rect(cx+bw+3, bodyY+8, 4, 4);
                ctx.fillStyle = '#c89060';
                rect(cx+bw+4, bodyY+9, 2, 2);
                ctx.fillStyle = '#806030';
                rect(cx+bw+2, bodyY+7, 6, 2);
            } else if (ac === 'glasses') {
                if (dir === 0) {
                    ctx.fillStyle = '#a0a8b8';
                    rect(cx-9, headY+15, 18, 1);
                    ctx.fillStyle = '#d0d8e8';
                    rect(cx-9, headY+14, 6, 4);
                    rect(cx+3, headY+14, 6, 4);
                    ctx.fillStyle = '#c0c8d8';
                    rect(cx-8, headY+15, 4, 2);
                    rect(cx+4, headY+15, 4, 2);
                }
            } else if (ac === 'quiver') {
                ctx.fillStyle = OL;
                rect(cx+bw+2, bodyY-8, 6, 26);
                ctx.fillStyle = '#8B6914';
                rect(cx+bw+3, bodyY-7, 4, 24);
                ctx.fillStyle = '#a07828';
                rect(cx+bw+4, bodyY-7, 2, 22);
                ctx.fillStyle = '#b8a080';
                rect(cx+bw+3, bodyY-10, 4, 3);
                rect(cx+bw+2, bodyY-9, 1, 2);
                rect(cx+bw+7, bodyY-9, 1, 2);
                ctx.fillStyle = '#c0c8d0';
                rect(cx+bw+4, bodyY-12, 1, 3);
                rect(cx+bw+6, bodyY-11, 1, 2);
            } else if (ac === 'tools') {
                ctx.fillStyle = OL;
                rect(cx-bw-5, bodyY+4, 6, 14);
                ctx.fillStyle = '#8B6914';
                rect(cx-bw-4, bodyY+5, 4, 12);
                ctx.fillStyle = '#a0a8b8';
                rect(cx-bw-4, bodyY+1, 4, 5);
                ctx.fillStyle = '#c0c8d8';
                rect(cx-bw-3, bodyY+2, 2, 3);
            } else if (ac === 'orb') {
                if (dir === 0 || dir === 1) {
                    ctx.fillStyle = OL;
                    ell(cx+bw+5, bodyY+8, 6, 6);
                    ctx.fillStyle = '#6030a0';
                    ell(cx+bw+5, bodyY+8, 5, 5);
                    ctx.fillStyle = '#8040c0';
                    ell(cx+bw+4, bodyY+7, 3, 3);
                    ctx.fillStyle = '#b070e0';
                    ell(cx+bw+3, bodyY+6, 2, 2);
                    ctx.fillStyle = '#e0c0ff';
                    rect(cx+bw+3, bodyY+6, 1, 1);
                }
            } else if (ac === 'medallion') {
                if (dir === 0) {
                    ctx.fillStyle = OL;
                    ell(cx, bodyY+5, 4, 4);
                    ctx.fillStyle = '#c0a040';
                    ell(cx, bodyY+5, 3, 3);
                    ctx.fillStyle = '#e0c060';
                    ell(cx-1, bodyY+4, 2, 2);
                    ctx.fillStyle = '#f0d878';
                    rect(cx-1, bodyY+4, 1, 1);
                }
            }
        };

        drawShadow();
        if (dir === 2) drawCape();
        drawLegs();
        if (dir !== 2) drawCape();
        drawBody();
        drawArms();
        drawHead();
        drawAccessory();
    }

    function buildHeroPal() {
        return {
            hair:'#2888e0',hairHL:'#50b0ff',hairDk:'#1060a0',hairMd:'#3898d0',
            skin:'#f4d0a0',skinHL:'#ffe8c8',skinSh:'#d8a870',skinDk:'#c09060',skinRim:'#e8c090',
            eyeW:'#f0f0ff',eye:'#1830a0',eyeHL:'#4060d0',pupil:'#080830',eyeLash:'#201018',
            mouth:'#c07050',cheek:'#e8b090',nose:'#d8b080',
            tunic:'#1c3078',tunicHL:'#3050a8',tunicMd:'#2840a0',tunicDk:'#101850',tunicSh:'#080830',
            tunicTrim:'#c0b060',tunicTrimDk:'#a09040',
            collar:'#e8e0d0',collarSh:'#c0b898',
            shoulder:'#3050d0',shoulderHL:'#5070e8',
            belt:'#d8a830',beltBk:'#b08020',beltHL:'#f0c848',
            pants:'#1c2858',pantsDk:'#101840',pantsHL:'#283870',
            boots:'#503020',bootsHL:'#785838',bootsDk:'#2a1408',bootsCuff:'#685030',bootsSole:'#201008',
            cape:'#c82828',capeMd:'#a82020',capeDk:'#681010',capeHL:'#e84848',capeEdge:'#500808',
            glove:'#e8d8b8',gloveSh:'#c8b890',
            outline:'#101020',
            weapon:'#a0a8b8',weaponHL:'#d0d8e0',weaponDk:'#606878',
            armor:'#4060c8',armorHL:'#6888e8',armorDk:'#283878',armorTrim:'#d0a030',
            armorMd:'#5070d0',armorEdge:'#182858',armorGlow:'#88a8f0',
            vest:'#1c3078',vestHL:'#3050a8',vestDk:'#101850',
            robe:'#1c3078',robeHL:'#3050a8',robeDk:'#101850',robeTrim:'#c0b060',
            cloak:'#c82828',cloakHL:'#e84848',cloakDk:'#681010',
            acc1:'#c0b060',acc2:'#a09040',
            scarf:'#c82828',scarfHL:'#e84848',scarfDk:'#901818',scarfMd:'#b02020',
            gold:'#d0a030',goldHL:'#f0c848',goldDk:'#906818',goldMd:'#c09028',
            arch:{hairStyle:0,build:'normal',outfit:'hero_armor',acc:'sword',hatType:null,class:'hero'}
        };
    }

    return { drawSprite: drawSpriteCached, buildNPCPal, getArchetype, SKIN_TONES, EYE_COLORS, HAIR_PRESETS, ARCHETYPES };
})();
