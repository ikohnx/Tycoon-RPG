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
        {h:'#3a2518',hHL:'#6a5040',hDk:'#1a0808',hMd:'#4a3020'},
        {h:'#e8d060',hHL:'#f8e888',hDk:'#b09830',hMd:'#d0c050'},
        {h:'#c03020',hHL:'#e05040',hDk:'#801810',hMd:'#a82818'},
        {h:'#101010',hHL:'#383838',hDk:'#000000',hMd:'#202020'},
        {h:'#f0f0f0',hHL:'#ffffff',hDk:'#c0c0c0',hMd:'#e0e0e0'},
        {h:'#ff6820',hHL:'#ff9050',hDk:'#c04010',hMd:'#e05018'},
        {h:'#604080',hHL:'#8060a0',hDk:'#402060',hMd:'#503070'},
        {h:'#2080c0',hHL:'#40a0e0',hDk:'#106090',hMd:'#1870a8'}
    ];

    const ARCHETYPES = {
        merchant: {hairStyle:1,build:'stocky',outfit:'vest',acc:'bag',hatType:'beret'},
        scholar:  {hairStyle:2,build:'slim',outfit:'robe',acc:'glasses',hatType:null},
        elder:    {hairStyle:3,build:'normal',outfit:'robe_long',acc:'staff',hatType:null},
        warrior:  {hairStyle:4,build:'broad',outfit:'armor',acc:'shield',hatType:null},
        scout:    {hairStyle:5,build:'slim',outfit:'cloak',acc:'quiver',hatType:'hood'},
        noble:    {hairStyle:6,build:'normal',outfit:'doublet',acc:'medallion',hatType:'crown'},
        artisan:  {hairStyle:7,build:'stocky',outfit:'apron_outfit',acc:'tools',hatType:'bandana'},
        mystic:   {hairStyle:0,build:'slim',outfit:'robe_fancy',acc:'orb',hatType:'wizard'}
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
            cloak: shade(c, -20), cloakHL: shade(c, 0), cloakDk: shade(c, -45),
            acc1: shade(c, 50), acc2: shade(c, -20),
            arch
        };
    }

    const _spriteCache = {};

    function drawSpriteCached(ctx, gt, type, x, y, facing, frame, moving, color, spriteId, TS, SPRITE_YOFF) {
        const key = type + '_' + (spriteId || 0) + '_' + (color || '') + '_' + facing + '_' + (frame || 0) + '_' + (moving ? 1 : 0);
        let cached = _spriteCache[key];
        if (!cached) {
            const W = TS;
            const H = TS + (SPRITE_YOFF || 0) + 16;
            const off = document.createElement('canvas');
            off.width = W;
            off.height = H;
            const oc = off.getContext('2d');
            oc.imageSmoothingEnabled = false;
            _drawSpriteRaw(oc, gt, type, 0, SPRITE_YOFF || 0, facing, frame, moving, color, spriteId, TS, SPRITE_YOFF);
            _spriteCache[key] = off;
            cached = off;
        }
        ctx.drawImage(cached, x, y - (SPRITE_YOFF || 0));
    }

    function _drawSpriteRaw(ctx, gt, type, x, y, facing, frame, moving, color, spriteId, TS, SPRITE_YOFF) {
        const cx = x + 24;
        const isHero = type === 'hero';
        const sid = spriteId || 0;
        const arch = isHero ? {hairStyle:0,build:'normal',outfit:'hero',acc:'sword',hatType:null} : getArchetype(sid);
        const pal = isHero ? {
            hair:'#c03020',hairHL:'#e85040',hairDk:'#801810',hairMd:'#a82818',
            skin:'#f4d0a0',skinHL:'#ffe8c8',skinSh:'#d8a870',skinDk:'#c09060',skinRim:'#e8c090',
            eyeW:'#f0f0ff',eye:'#1830a0',eyeHL:'#4060d0',pupil:'#080830',
            mouth:'#c07050',cheek:'#e8b090',nose:'#d8b080',
            tunic:'#2848c0',tunicHL:'#5878e8',tunicMd:'#3858d0',tunicDk:'#182878',tunicSh:'#101850',
            tunicTrim:'#c0b060',collar:'#e8e0d0',collarSh:'#c0b898',
            shoulder:'#3050d0',shoulderHL:'#5070e8',
            belt:'#d8a830',beltBk:'#b08020',beltHL:'#f0c848',
            pants:'#384898',pantsDk:'#283068',pantsHL:'#5060b0',
            boots:'#503020',bootsHL:'#785838',bootsDk:'#2a1408',bootsCuff:'#685030',bootsSole:'#201008',
            cape:'#c82828',capeMd:'#a82020',capeDk:'#681010',capeHL:'#e84848',capeEdge:'#500808',
            glove:'#e8d8b8',gloveSh:'#c8b890',
            outline:'#101020',
            weapon:'#a0a8b8',weaponHL:'#d0d8e0',weaponDk:'#606878',
            armor:'#3858d0',armorHL:'#5878e8',armorDk:'#182878',armorTrim:'#c0b060',
            vest:'#2848c0',vestHL:'#5878e8',vestDk:'#182878',
            robe:'#2848c0',robeHL:'#5878e8',robeDk:'#182878',robeTrim:'#c0b060',
            cloak:'#c82828',cloakHL:'#e84848',cloakDk:'#681010',
            acc1:'#c0b060',acc2:'#a09040',arch
        } : buildNPCPal(color, sid);

        const dir = facing === 'down' ? 0 : facing === 'right' ? 1 : facing === 'up' ? 2 : 3;
        const bob = moving ? Math.sin(frame * Math.PI / 2) * 2 : 0;
        const breathe = !moving ? Math.sin(gt / 700) * 0.5 : 0;
        const wc = moving ? frame % 4 : 0;
        const legL = wc === 1 ? 4 : wc === 3 ? -3 : 0;
        const legR = wc === 1 ? -3 : wc === 3 ? 4 : 0;
        const armSwing = moving ? Math.sin(frame * Math.PI / 2) * 2 : 0;
        const by = Math.round(-bob + breathe);
        const sy = y - SPRITE_YOFF;

        const ell = (ex,ey,rx,ry) => { ctx.beginPath(); ctx.ellipse(ex,ey,rx,ry,0,0,Math.PI*2); ctx.fill(); };
        const rect = (rx,ry,rw,rh) => { ctx.fillRect(rx,ry,rw,rh); };

        const headY = sy + 14 + by;
        const bodyY = sy + 44 + by;
        const legY = sy + 62 + by;
        const bw = arch.build === 'broad' ? 10 : arch.build === 'stocky' ? 9 : arch.build === 'slim' ? 7 : 8;
        const OL = pal.outline;

        const drawCape = () => {
            const of = arch.outfit;
            if (of === 'cloak' || (isHero && dir === 2)) {
                ctx.fillStyle = OL;
                rect(cx-bw-3, bodyY-3, bw*2+6, 24);
                ctx.fillStyle = pal.cape || pal.cloak || pal.tunicDk;
                rect(cx-bw-2, bodyY-2, bw*2+4, 22);
                ctx.fillStyle = pal.capeDk || pal.cloakDk || pal.tunicSh;
                rect(cx-bw-2, bodyY+18, bw*2+4, 2);
                ctx.fillStyle = pal.capeHL || pal.cloakHL || pal.tunicHL;
                rect(cx-bw, bodyY, bw, 16);
            }
        };

        const drawBody = () => {
            const of = arch.outfit;
            const tc = (of === 'armor' || of === 'hero') ? (pal.armor || pal.tunic) : (of === 'vest') ? pal.tunic :
                       (of === 'robe' || of === 'robe_long' || of === 'robe_fancy') ? (pal.robe || pal.tunic) :
                       (of === 'cloak') ? (pal.cloak || pal.tunic) : pal.tunic;
            const tcHL = (of === 'armor' || of === 'hero') ? (pal.armorHL || pal.tunicHL) :
                         (of === 'robe' || of === 'robe_long' || of === 'robe_fancy') ? (pal.robeHL || pal.tunicHL) : pal.tunicHL;
            const tcDk = (of === 'armor' || of === 'hero') ? (pal.armorDk || pal.tunicDk) :
                         (of === 'robe' || of === 'robe_long' || of === 'robe_fancy') ? (pal.robeDk || pal.tunicDk) : pal.tunicDk;

            ctx.fillStyle = OL;
            rect(cx-bw-2, bodyY-2, bw*2+4, 22);

            ctx.fillStyle = tc;
            const bh = (of === 'robe_long' || of === 'robe_fancy') ? 22 : 18;
            rect(cx-bw, bodyY, bw*2, bh);
            ctx.fillStyle = tcHL;
            rect(cx-bw+1, bodyY+1, bw-1, bh-4);
            ctx.fillStyle = tcDk;
            rect(cx-1, bodyY+2, 2, bh-4);

            if (of === 'vest') {
                ctx.fillStyle = pal.vest;
                rect(cx-bw, bodyY+1, 4, 16);
                rect(cx+bw-4, bodyY+1, 4, 16);
                ctx.fillStyle = '#c0a040';
                rect(cx-1, bodyY+4, 2, 2);
                rect(cx-1, bodyY+9, 2, 2);
            }
            if (of === 'armor' || of === 'hero') {
                ctx.fillStyle = pal.armorTrim || pal.tunicTrim;
                rect(cx-bw, bodyY+17, bw*2, 1);
                rect(cx-bw+1, bodyY, 1, 16);
                rect(cx+bw-2, bodyY, 1, 16);
            }
            if (of === 'doublet') {
                ctx.fillStyle = '#fff';
                rect(cx-2, bodyY+2, 4, 12);
                ctx.fillStyle = '#c0a040';
                rect(cx-1, bodyY+4, 2, 2);
                rect(cx-1, bodyY+8, 2, 2);
            }
            if (of === 'apron_outfit') {
                ctx.fillStyle = '#e0d8c8';
                rect(cx-bw+2, bodyY+6, bw*2-4, 12);
                ctx.fillStyle = '#c8c0b0';
                rect(cx-1, bodyY+4, 2, 3);
            }
            if (of === 'robe_fancy') {
                ctx.fillStyle = pal.robeTrim || '#f0e060';
                rect(cx-1, bodyY+2, 2, bh-4);
                ctx.fillStyle = '#f0e060';
                rect(cx-bw+1, bodyY+bh-2, bw*2-2, 1);
            }

            ctx.fillStyle = pal.collar || pal.tunicHL;
            rect(cx-bw+1, bodyY-1, bw*2-2, 3);

            ctx.fillStyle = pal.belt;
            rect(cx-bw, bodyY+15, bw*2, 2);
            ctx.fillStyle = pal.beltHL;
            rect(cx-1, bodyY+15, 2, 2);
        };

        const drawArms = () => {
            const la = Math.round(armSwing);
            const ra = Math.round(-armSwing);
            ctx.fillStyle = OL;
            rect(cx-bw-4, bodyY+la, 5, 12);
            rect(cx+bw-1, bodyY+ra, 5, 12);
            ctx.fillStyle = pal.shoulder || pal.tunic;
            rect(cx-bw-3, bodyY+1+la, 4, 10);
            rect(cx+bw, bodyY+1+ra, 4, 10);
            ctx.fillStyle = pal.shoulderHL || pal.tunicHL;
            rect(cx-bw-2, bodyY+2+la, 2, 6);
            rect(cx+bw+1, bodyY+2+ra, 2, 6);
            ctx.fillStyle = pal.skin;
            rect(cx-bw-2, bodyY+10+la, 3, 3);
            rect(cx+bw, bodyY+10+ra, 3, 3);
        };

        const drawLegs = () => {
            ctx.fillStyle = OL;
            rect(cx-6, legY-2, 5, 16+legL);
            rect(cx+1, legY-2, 5, 16+legR);

            ctx.fillStyle = pal.pants;
            rect(cx-5, legY, 4, 8+legL);
            rect(cx+1, legY, 4, 8+legR);
            ctx.fillStyle = pal.pantsHL;
            rect(cx-4, legY+1, 2, 5);
            rect(cx+2, legY+1, 2, 5);

            ctx.fillStyle = OL;
            rect(cx-6, legY+8+legL, 6, 6);
            rect(cx, legY+8+legR, 6, 6);
            ctx.fillStyle = pal.boots;
            rect(cx-5, legY+8+legL, 5, 5);
            rect(cx+1, legY+8+legR, 5, 5);
            ctx.fillStyle = pal.bootsHL;
            rect(cx-4, legY+9+legL, 2, 2);
            rect(cx+2, legY+9+legR, 2, 2);
            ctx.fillStyle = pal.bootsSole;
            rect(cx-5, legY+12+legL, 5, 1);
            rect(cx+1, legY+12+legR, 5, 1);
        };

        const drawHead = () => {
            const hcx = cx;
            const hcy = headY + 15;

            ctx.fillStyle = OL;
            ell(hcx, hcy, 14, 13);

            if (dir === 2) {
                ctx.fillStyle = pal.hairDk;
                ell(hcx, hcy-1, 13, 12);
                ctx.fillStyle = pal.hair;
                ell(hcx, hcy, 12, 11);
                ctx.fillStyle = pal.hairHL;
                ell(hcx-2, hcy-3, 6, 4);
                drawHairBack(hcx, hcy);
                return;
            }

            ctx.fillStyle = pal.hairDk;
            ell(hcx, hcy-2, 13, 12);
            ctx.fillStyle = pal.hair;
            ell(hcx, hcy-1, 12, 11);

            ctx.fillStyle = pal.skin;
            if (dir === 0) {
                ell(hcx, hcy+2, 10, 9);
            } else if (dir === 3) {
                ell(hcx-1, hcy+2, 10, 9);
            } else {
                ell(hcx+1, hcy+2, 10, 9);
            }
            ctx.fillStyle = pal.skinHL;
            ell(hcx + (dir===1?1:dir===3?-1:0), hcy, 6, 5);

            drawFace(hcx, hcy+2, dir);
            drawHairFront(hcx, hcy, dir);
            drawHairBack(hcx, hcy);
        };

        const drawFace = (fcx, fcy, dir) => {
            if (dir === 0) {
                ctx.fillStyle = OL;
                ell(fcx-5, fcy-1, 4, 3.5);
                ell(fcx+5, fcy-1, 4, 3.5);
                ctx.fillStyle = pal.eyeW;
                ell(fcx-5, fcy-1, 3.5, 3);
                ell(fcx+5, fcy-1, 3.5, 3);
                ctx.fillStyle = pal.eye;
                ell(fcx-5, fcy, 2.5, 2.5);
                ell(fcx+5, fcy, 2.5, 2.5);
                ctx.fillStyle = pal.pupil;
                rect(fcx-6, fcy, 2, 2);
                rect(fcx+4, fcy, 2, 2);
                ctx.fillStyle = '#fff';
                rect(fcx-4, fcy-2, 1, 1);
                rect(fcx+6, fcy-2, 1, 1);
                ctx.fillStyle = OL;
                rect(fcx-7, fcy-3, 5, 1);
                rect(fcx+3, fcy-3, 5, 1);

                ctx.fillStyle = pal.nose || pal.skinSh;
                rect(fcx-1, fcy+3, 2, 1);
                ctx.fillStyle = pal.mouth;
                rect(fcx-2, fcy+5, 4, 1);
                ctx.fillStyle = shade(pal.mouth, 30);
                rect(fcx-1, fcy+5, 2, 1);

                if (pal.cheek) {
                    ctx.fillStyle = pal.cheek;
                    ctx.globalAlpha = 0.3;
                    ell(fcx-8, fcy+2, 3, 2);
                    ell(fcx+8, fcy+2, 3, 2);
                    ctx.globalAlpha = 1;
                }
            } else if (dir === 3) {
                ctx.fillStyle = OL;
                ell(fcx-4, fcy-1, 4, 3.5);
                ctx.fillStyle = pal.eyeW;
                ell(fcx-4, fcy-1, 3.5, 3);
                ctx.fillStyle = pal.eye;
                ell(fcx-4, fcy, 2.5, 2.5);
                ctx.fillStyle = pal.pupil;
                rect(fcx-5, fcy, 2, 2);
                ctx.fillStyle = '#fff';
                rect(fcx-3, fcy-2, 1, 1);
                ctx.fillStyle = OL;
                rect(fcx-6, fcy-3, 5, 1);
                ctx.fillStyle = pal.nose || pal.skinSh;
                rect(fcx-9, fcy+2, 2, 1);
                ctx.fillStyle = pal.mouth;
                rect(fcx-6, fcy+5, 3, 1);
            } else if (dir === 1) {
                ctx.fillStyle = OL;
                ell(fcx+4, fcy-1, 4, 3.5);
                ctx.fillStyle = pal.eyeW;
                ell(fcx+4, fcy-1, 3.5, 3);
                ctx.fillStyle = pal.eye;
                ell(fcx+4, fcy, 2.5, 2.5);
                ctx.fillStyle = pal.pupil;
                rect(fcx+3, fcy, 2, 2);
                ctx.fillStyle = '#fff';
                rect(fcx+5, fcy-2, 1, 1);
                ctx.fillStyle = OL;
                rect(fcx+2, fcy-3, 5, 1);
                ctx.fillStyle = pal.nose || pal.skinSh;
                rect(fcx+7, fcy+2, 2, 1);
                ctx.fillStyle = pal.mouth;
                rect(fcx+3, fcy+5, 3, 1);
            }
        };

        const drawHairFront = (hcx, hcy, dir) => {
            const hs = arch.hairStyle;
            ctx.fillStyle = pal.hair;
            if (hs === 0) {
                ell(hcx, hcy-4, 12, 8);
                ctx.fillStyle = pal.hairHL;
                ell(hcx-2, hcy-6, 6, 4);
                if (isHero) {
                    ctx.fillStyle = pal.hair;
                    rect(hcx-5,hcy-12,3,7); rect(hcx-1,hcy-14,3,8); rect(hcx+3,hcy-13,3,7);
                    ctx.fillStyle = pal.hairHL;
                    rect(hcx-4,hcy-10,1,4); rect(hcx,hcy-12,1,4); rect(hcx+4,hcy-11,1,4);
                    ctx.fillStyle = pal.hairDk;
                    rect(hcx-5,hcy-12,1,7); rect(hcx-1,hcy-14,1,8); rect(hcx+3,hcy-13,1,7);
                }
            } else if (hs === 1) {
                ell(hcx, hcy-3, 12, 8);
                ctx.fillStyle = pal.hairHL;
                rect(hcx-7, hcy-7, 14, 3);
                ctx.fillStyle = pal.hairDk;
                rect(hcx-9, hcy-1, 18, 2);
            } else if (hs === 2) {
                ell(hcx, hcy-4, 12, 9);
                ctx.fillStyle = pal.hairHL;
                ell(hcx-2, hcy-6, 6, 4);
            } else if (hs === 3) {
                ell(hcx, hcy-3, 11, 7);
                ctx.fillStyle = pal.hairHL;
                ell(hcx, hcy-5, 6, 3);
            } else if (hs === 4) {
                ell(hcx, hcy-3, 11, 8);
                ctx.fillStyle = pal.hairHL;
                rect(hcx-2, hcy-8, 4, 4);
                ctx.fillStyle = pal.hairDk;
                rect(hcx-4, hcy-12, 8, 5);
                ctx.fillStyle = pal.hair;
                rect(hcx-2, hcy-13, 4, 4);
                ctx.fillStyle = pal.hairHL;
                rect(hcx-1, hcy-12, 2, 3);
            } else if (hs === 5) {
                ell(hcx, hcy-3, 12, 8);
                ctx.fillStyle = pal.hairHL;
                ell(hcx-1, hcy-5, 6, 4);
            } else if (hs === 6) {
                ell(hcx, hcy-4, 13, 9);
                ctx.fillStyle = pal.hairHL;
                for(let i=0;i<5;i++) rect(hcx-8+i*4,hcy-7+Math.abs(i-2),3,2);
                ctx.fillStyle = pal.hairDk;
                rect(hcx-11, hcy-1, 22, 2);
            } else {
                ell(hcx, hcy-3, 12, 8);
                ctx.fillStyle = pal.hairHL;
                ell(hcx, hcy-5, 6, 4);
                if (dir === 1) {
                    ctx.fillStyle = pal.hairDk;
                    ell(hcx+2, hcy-8, 4, 4);
                    ctx.fillStyle = pal.hair;
                    ell(hcx+2, hcy-7, 3, 3);
                }
            }
        };

        const drawHairBack = (hcx, hcy) => {
            const hs = arch.hairStyle;
            if (hs === 2) {
                ctx.fillStyle = pal.hair;
                if (dir === 0 || dir === 2) {
                    rect(hcx-11, hcy+5, 4, 14);
                    rect(hcx+7, hcy+5, 4, 14);
                } else if (dir === 3) {
                    rect(hcx-11, hcy+5, 4, 16);
                } else {
                    rect(hcx+7, hcy+5, 4, 16);
                }
                ctx.fillStyle = pal.hairDk;
                if (dir === 0 || dir === 2) {
                    rect(hcx-11, hcy+17, 4, 2);
                    rect(hcx+7, hcy+17, 4, 2);
                } else if (dir === 3) {
                    rect(hcx-11, hcy+19, 4, 2);
                } else {
                    rect(hcx+7, hcy+19, 4, 2);
                }
            }
            if (hs === 5 && (dir === 0 || dir === 1)) {
                ctx.fillStyle = pal.hair;
                rect(hcx+7, hcy+5, 3, 12);
                ctx.fillStyle = pal.hairHL;
                rect(hcx+8, hcy+6, 2, 5);
                ctx.fillStyle = pal.hairDk;
                ell(hcx+8, hcy+18, 3, 2);
            }
        };

        const drawHat = (hcx, hcy) => {
            const ht = arch.hatType;
            if (!ht) return;
            hcy = headY + 15;
            if (ht === 'beret') {
                ctx.fillStyle = OL;
                ell(hcx+1, hcy-9, 11, 6);
                ctx.fillStyle = pal.acc1;
                ell(hcx+1, hcy-9, 10, 5);
                ctx.fillStyle = pal.acc2;
                ell(hcx, hcy-10, 6, 3);
            } else if (ht === 'hood') {
                ctx.fillStyle = OL;
                ell(hcx, hcy-3, 15, 13);
                ctx.fillStyle = pal.cloak;
                ell(hcx, hcy-3, 14, 12);
                ctx.fillStyle = pal.cloakHL;
                ell(hcx-1, hcy-5, 8, 6);
                ctx.fillStyle = pal.cloakDk;
                rect(hcx-13, hcy+6, 26, 3);
            } else if (ht === 'crown') {
                ctx.fillStyle = OL;
                rect(hcx-9, hcy-10, 18, 6);
                ctx.fillStyle = '#c0a040';
                rect(hcx-8, hcy-9, 16, 5);
                ctx.fillStyle = '#e0c060';
                rect(hcx-6, hcy-14, 3, 5); rect(hcx-1, hcy-16, 2, 7); rect(hcx+4, hcy-14, 3, 5);
                ctx.fillStyle = '#e02020';
                rect(hcx-1, hcy-12, 2, 2);
                ctx.fillStyle = '#2020e0';
                rect(hcx-5, hcy-10, 2, 2); rect(hcx+4, hcy-10, 2, 2);
            } else if (ht === 'bandana') {
                ctx.fillStyle = pal.acc1;
                rect(hcx-11, hcy-3, 22, 3);
                ctx.fillStyle = pal.acc2;
                rect(hcx-11, hcy-2, 22, 1);
                ctx.fillStyle = pal.acc1;
                rect(hcx+8, hcy-2, 3, 6); rect(hcx+9, hcy+2, 2, 4);
            } else if (ht === 'wizard') {
                ctx.fillStyle = OL;
                ctx.beginPath(); ctx.moveTo(hcx-12,hcy-2); ctx.lineTo(hcx,hcy-24); ctx.lineTo(hcx+12,hcy-2); ctx.fill();
                ctx.fillStyle = pal.tunicDk;
                ctx.beginPath(); ctx.moveTo(hcx-11,hcy-3); ctx.lineTo(hcx,hcy-22); ctx.lineTo(hcx+11,hcy-3); ctx.fill();
                ctx.fillStyle = pal.tunic;
                ctx.beginPath(); ctx.moveTo(hcx-9,hcy-3); ctx.lineTo(hcx,hcy-20); ctx.lineTo(hcx+9,hcy-3); ctx.fill();
                ctx.fillStyle = pal.tunicHL;
                ctx.beginPath(); ctx.moveTo(hcx-5,hcy-4); ctx.lineTo(hcx-1,hcy-16); ctx.lineTo(hcx+3,hcy-4); ctx.fill();
                ctx.fillStyle = '#f0e060';
                ell(hcx, hcy-21, 2, 2);
                ctx.fillStyle = pal.tunicDk;
                rect(hcx-12, hcy-3, 24, 2);
            }
        };

        const drawAccessory = (acx, acy) => {
            const ac = arch.acc;
            if (!ac) return;
            if (ac === 'sword') {
                if (dir === 0 || dir === 1) {
                    ctx.fillStyle = OL;
                    rect(cx+bw+1, bodyY-5, 4, 22);
                    ctx.fillStyle = pal.weaponDk;
                    rect(cx+bw+2, bodyY-4, 2, 20);
                    ctx.fillStyle = pal.weapon;
                    rect(cx+bw+3, bodyY-4, 1, 18);
                    ctx.fillStyle = pal.weaponHL;
                    rect(cx+bw+3, bodyY-3, 1, 6);
                    ctx.fillStyle = '#c0a040';
                    rect(cx+bw+1, bodyY+14, 4, 2);
                }
            } else if (ac === 'shield') {
                if (dir === 0 || dir === 3) {
                    ctx.fillStyle = OL;
                    ell(cx-bw-5, bodyY+6, 6, 7);
                    ctx.fillStyle = pal.armorDk;
                    ell(cx-bw-5, bodyY+6, 5, 6);
                    ctx.fillStyle = pal.armor;
                    ell(cx-bw-5, bodyY+6, 4, 5);
                    ctx.fillStyle = pal.armorTrim;
                    rect(cx-bw-6, bodyY+5, 2, 2);
                }
            } else if (ac === 'staff') {
                ctx.fillStyle = OL;
                rect(cx+bw+1, bodyY-11, 4, 30);
                ctx.fillStyle = '#8B6914';
                rect(cx+bw+2, bodyY-10, 2, 28);
                ctx.fillStyle = '#a07828';
                rect(cx+bw+3, bodyY-10, 1, 26);
                ctx.fillStyle = '#60d0f0';
                ell(cx+bw+3, bodyY-12, 3, 3);
            } else if (ac === 'bag') {
                ctx.fillStyle = OL;
                rect(cx+bw, bodyY+7, 7, 8);
                ctx.fillStyle = '#a07040';
                rect(cx+bw+1, bodyY+8, 5, 6);
                ctx.fillStyle = '#b88050';
                rect(cx+bw+2, bodyY+9, 3, 3);
                ctx.fillStyle = '#806030';
                rect(cx+bw+1, bodyY+8, 5, 1);
            } else if (ac === 'glasses') {
                if (dir === 0) {
                    ctx.fillStyle = '#a0a8b8';
                    rect(cx-8, headY+14, 16, 1);
                    ctx.fillStyle = '#c0d0e8';
                    rect(cx-8, headY+13, 5, 3);
                    rect(cx+3, headY+13, 5, 3);
                }
            } else if (ac === 'quiver') {
                ctx.fillStyle = OL;
                rect(cx+bw+1, bodyY-6, 5, 22);
                ctx.fillStyle = '#8B6914';
                rect(cx+bw+2, bodyY-5, 3, 20);
                ctx.fillStyle = '#a07828';
                rect(cx+bw+3, bodyY-5, 1, 18);
                ctx.fillStyle = '#b8a080';
                rect(cx+bw+2, bodyY-8, 3, 3);
                rect(cx+bw+1, bodyY-7, 1, 1);
                rect(cx+bw+5, bodyY-7, 1, 1);
            } else if (ac === 'tools') {
                ctx.fillStyle = OL;
                rect(cx-bw-4, bodyY+6, 5, 12);
                ctx.fillStyle = '#8B6914';
                rect(cx-bw-3, bodyY+7, 3, 10);
                ctx.fillStyle = '#a0a8b8';
                rect(cx-bw-3, bodyY+3, 3, 4);
            } else if (ac === 'orb') {
                if (dir === 0 || dir === 1) {
                    ctx.fillStyle = OL;
                    ell(cx+bw+4, bodyY+8, 5, 5);
                    ctx.fillStyle = '#8040c0';
                    ell(cx+bw+4, bodyY+8, 4, 4);
                    ctx.fillStyle = '#a060e0';
                    ell(cx+bw+3, bodyY+7, 2, 2);
                }
            } else if (ac === 'medallion') {
                if (dir === 0) {
                    ctx.fillStyle = '#c0a040';
                    rect(cx-2, bodyY+4, 4, 4);
                    ctx.fillStyle = '#e0c060';
                    rect(cx-1, bodyY+5, 2, 2);
                }
            }
        };

        if (dir === 2) drawCape();
        drawLegs();
        if (dir !== 2) drawCape();
        drawBody();
        drawArms();
        drawHead();
        drawHat(cx, headY);
        drawAccessory(cx, bodyY);
    }

    return { drawSprite: drawSpriteCached, buildNPCPal, getArchetype, SKIN_TONES, EYE_COLORS, HAIR_PRESETS, ARCHETYPES };
})();
