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
            outline: '#181020',
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
        const D = 1;
        const cx = x + 24;
        const isHero = type === 'hero';
        const sid = spriteId || 0;
        const arch = isHero ? {hairStyle:0,build:'normal',outfit:'hero',acc:'sword',hatType:null} : getArchetype(sid);
        const pal = isHero ? {
            hair:'#3a2518',hairHL:'#6a5040',hairDk:'#1a0808',hairMd:'#4a3020',
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
            outline:'#100818',
            weapon:'#a0a8b8',weaponHL:'#d0d8e0',weaponDk:'#606878',
            armor:'#3858d0',armorHL:'#5878e8',armorDk:'#182878',armorTrim:'#c0b060',
            vest:'#2848c0',vestHL:'#5878e8',vestDk:'#182878',
            robe:'#2848c0',robeHL:'#5878e8',robeDk:'#182878',robeTrim:'#c0b060',
            cloak:'#c82828',cloakHL:'#e84848',cloakDk:'#681010',
            acc1:'#c0b060',acc2:'#a09040',arch
        } : buildNPCPal(color, sid);

        const bob = moving ? Math.sin(frame * Math.PI / 2) * 1.5 : 0;
        const breathe = !moving ? Math.sin(gt / 700) * 0.6 : 0;
        const wc = moving ? frame % 4 : 0;
        const legL = wc === 1 ? 3 : wc === 3 ? -2 : 0;
        const legR = wc === 1 ? -2 : wc === 3 ? 3 : 0;
        const armSwing = moving ? Math.sin(frame * Math.PI / 2) * 3 : 0;
        const by = Math.round(-bob + breathe);
        const sy = y - SPRITE_YOFF;
        const ell = (ex,ey,rx,ry) => { ctx.beginPath(); ctx.ellipse(ex,ey,rx,ry,0,0,Math.PI*2); ctx.fill(); };
        const bw = arch.build === 'broad' ? 10 : arch.build === 'stocky' ? 9 : arch.build === 'slim' ? 7 : 8;
        const sw = Math.round(bw * 1.1);

        const drawHair = (hcx, hcy, dir) => {
            const hs = arch.hairStyle;
            ctx.fillStyle = pal.hairDk;
            if (hs === 0) {
                ell(hcx, hcy, 9, 8);
                ctx.fillStyle = pal.hair;
                ell(hcx, hcy+1, 8, 7);
                ctx.fillStyle = pal.hairHL;
                ell(hcx-2, hcy-2, 4, 3);
                if (isHero && dir === 0) {
                    ctx.fillStyle = pal.hairDk;
                    ctx.fillRect(hcx-4,hcy-7,2,5);ctx.fillRect(hcx-1,hcy-9,2,6);ctx.fillRect(hcx+3,hcy-8,2,5);
                    ctx.fillStyle = pal.hairHL;
                    ctx.fillRect(hcx-3,hcy-6,D,3);ctx.fillRect(hcx+1,hcy-8,D,3);
                }
            } else if (hs === 1) {
                ell(hcx, hcy, 9, 8);
                ctx.fillStyle = pal.hair;
                ell(hcx, hcy, 8, 7);
                ctx.fillStyle = pal.hairHL;
                ctx.fillRect(hcx-6,hcy-3,12,3);
                ctx.fillStyle = pal.hairDk;
                ctx.fillRect(hcx-7,hcy+2,14,2);
            } else if (hs === 2) {
                ell(hcx, hcy-1, 9, 9);
                ctx.fillStyle = pal.hair;
                ell(hcx, hcy, 8, 8);
                ctx.fillStyle = pal.hairHL;
                ell(hcx-2, hcy-3, 5, 3);
                if (dir === 0 || dir === 2) {
                    ctx.fillStyle = pal.hair;
                    ctx.fillRect(hcx-8,hcy+2,4,10);
                    ctx.fillRect(hcx+4,hcy+2,4,10);
                    ctx.fillStyle = pal.hairDk;
                    ctx.fillRect(hcx-8,hcy+10,4,3);
                    ctx.fillRect(hcx+4,hcy+10,4,3);
                } else if (dir === 3) {
                    ctx.fillStyle = pal.hair;
                    ctx.fillRect(hcx-8,hcy+2,4,12);
                    ctx.fillStyle = pal.hairDk;
                    ctx.fillRect(hcx-8,hcy+12,4,3);
                } else {
                    ctx.fillStyle = pal.hair;
                    ctx.fillRect(hcx+4,hcy+2,4,12);
                    ctx.fillStyle = pal.hairDk;
                    ctx.fillRect(hcx+4,hcy+12,4,3);
                }
            } else if (hs === 3) {
                ell(hcx, hcy, 8, 7);
                ctx.fillStyle = pal.hair;
                ell(hcx, hcy+1, 7, 6);
                ctx.fillStyle = pal.hairHL;
                ell(hcx, hcy-1, 5, 3);
            } else if (hs === 4) {
                ell(hcx, hcy, 8, 7);
                ctx.fillStyle = pal.hair;
                ell(hcx, hcy+1, 7, 6);
                ctx.fillStyle = pal.hairHL;
                ctx.fillRect(hcx-2,hcy-6,4,5);
                ctx.fillStyle = pal.hair;
                ctx.fillRect(hcx-3,hcy-8,6,4);
                ctx.fillStyle = pal.hairDk;
                ctx.fillRect(hcx-1,hcy-9,2,3);
            } else if (hs === 5) {
                ell(hcx, hcy, 9, 8);
                ctx.fillStyle = pal.hair;
                ell(hcx, hcy+1, 8, 7);
                ctx.fillStyle = pal.hairHL;
                ell(hcx-1, hcy-2, 5, 3);
                if (dir === 1 || dir === 0) {
                    ctx.fillStyle = pal.hair;
                    ctx.fillRect(hcx+4,hcy+3,3,8);
                    ctx.fillStyle = pal.hairHL;
                    ctx.fillRect(hcx+5,hcy+4,2,3);
                    ctx.fillStyle = pal.hairDk;
                    ell(hcx+5,hcy+12,3,2);
                }
            } else if (hs === 6) {
                ell(hcx, hcy-1, 10, 9);
                ctx.fillStyle = pal.hair;
                ell(hcx, hcy, 9, 8);
                ctx.fillStyle = pal.hairHL;
                for(let i=0;i<5;i++){ctx.fillRect(hcx-8+i*4,hcy-5+Math.abs(i-2),3,2);}
                ctx.fillStyle = pal.hairDk;
                ctx.fillRect(hcx-9,hcy+3,18,3);
            } else {
                ell(hcx, hcy, 9, 8);
                ctx.fillStyle = pal.hair;
                ell(hcx, hcy, 8, 7);
                if (dir === 1) {
                    ctx.fillStyle = pal.hairDk;
                    ell(hcx, hcy-6, 4, 5);
                    ctx.fillStyle = pal.hair;
                    ell(hcx, hcy-5, 3, 4);
                    ctx.fillStyle = pal.hairHL;
                    ell(hcx, hcy-7, 2, 2);
                }
            }
        };

        const drawHat = (hcx, hcy) => {
            const ht = arch.hatType;
            if (!ht) return;
            if (ht === 'beret') {
                ctx.fillStyle = pal.acc1;
                ell(hcx+1, hcy-2, 9, 5);
                ctx.fillStyle = pal.acc2;
                ell(hcx, hcy-3, 6, 3);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha=0.3;ctx.fillRect(hcx-2,hcy-5,3,D);ctx.globalAlpha=1;
            } else if (ht === 'hood') {
                ctx.fillStyle = pal.cloak;
                ell(hcx, hcy-1, 11, 10);
                ctx.fillStyle = pal.cloakHL;
                ell(hcx-1, hcy-3, 7, 5);
                ctx.fillStyle = pal.cloakDk;
                ctx.fillRect(hcx-10,hcy+5,20,3);
            } else if (ht === 'crown') {
                ctx.fillStyle = '#c0a040';
                ctx.fillRect(hcx-7,hcy-3,14,5);
                ctx.fillStyle = '#e0c060';
                ctx.fillRect(hcx-5,hcy-6,3,4);ctx.fillRect(hcx-1,hcy-8,2,6);ctx.fillRect(hcx+3,hcy-6,3,4);
                ctx.fillStyle = '#e02020';
                ctx.fillRect(hcx-1,hcy-5,2,2);
                ctx.fillStyle = '#2020e0';
                ctx.fillRect(hcx-5,hcy-3,2,2);ctx.fillRect(hcx+4,hcy-3,2,2);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha=0.4;ctx.fillRect(hcx-4,hcy-3,8,D);ctx.globalAlpha=1;
            } else if (ht === 'bandana') {
                ctx.fillStyle = pal.acc1;
                ctx.fillRect(hcx-8,hcy+1,16,3);
                ctx.fillStyle = pal.acc2;
                ctx.fillRect(hcx-8,hcy+2,16,D);
                ctx.fillStyle = pal.acc1;
                ctx.fillRect(hcx+5,hcy+2,3,5);ctx.fillRect(hcx+6,hcy+5,2,4);
            } else if (ht === 'wizard') {
                ctx.fillStyle = pal.tunicDk;
                ctx.beginPath();ctx.moveTo(hcx-9,hcy+4);ctx.lineTo(hcx,hcy-16);ctx.lineTo(hcx+9,hcy+4);ctx.fill();
                ctx.fillStyle = pal.tunic;
                ctx.beginPath();ctx.moveTo(hcx-7,hcy+3);ctx.lineTo(hcx,hcy-14);ctx.lineTo(hcx+7,hcy+3);ctx.fill();
                ctx.fillStyle = pal.tunicHL;
                ctx.beginPath();ctx.moveTo(hcx-4,hcy+2);ctx.lineTo(hcx-1,hcy-10);ctx.lineTo(hcx+2,hcy+2);ctx.fill();
                ctx.fillStyle = '#f0e060';
                ell(hcx,hcy-14,2,2);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(hcx-9,hcy+3,18,2);
            }
        };

        const drawFace = (fcx, fcy, dir) => {
            ctx.fillStyle = pal.skin;
            ell(fcx, fcy, 7, 6);
            ctx.fillStyle = pal.skinHL;
            ell(fcx-(dir===1?1:dir===3?-1:1), fcy-2, 4, 3);
            ctx.fillStyle = pal.skinSh;
            ctx.fillRect(fcx-5, fcy+4, 10, D);
            if (dir === 0) {
                ctx.fillStyle = pal.eyeW;
                ctx.fillRect(fcx-5,fcy-2,3,3);ctx.fillRect(fcx+2,fcy-2,3,3);
                ctx.fillStyle = pal.eye;
                ctx.fillRect(fcx-4,fcy-2,2,2);ctx.fillRect(fcx+3,fcy-2,2,2);
                ctx.fillStyle = pal.pupil;
                ctx.fillRect(fcx-4,fcy-1,D,D);ctx.fillRect(fcx+3,fcy-1,D,D);
                ctx.fillStyle = '#fff';
                ctx.fillRect(fcx-3,fcy-2,D,D);ctx.fillRect(fcx+4,fcy-2,D,D);
                ctx.fillStyle = pal.outline;
                ctx.fillRect(fcx-5,fcy-3,3,D);ctx.fillRect(fcx+2,fcy-3,3,D);
                ctx.fillStyle = pal.nose || pal.skinSh;
                ctx.fillRect(fcx-1,fcy+1,2,D);
                ctx.fillStyle = pal.mouth || pal.skinSh;
                ctx.fillRect(fcx-1,fcy+3,3,D);
                if (pal.cheek) {
                    ctx.fillStyle = pal.cheek; ctx.globalAlpha=0.2;
                    ctx.fillRect(fcx-6,fcy+1,2,2);ctx.fillRect(fcx+4,fcy+1,2,2);
                    ctx.globalAlpha=1;
                }
            } else if (dir === 2) {
                ctx.fillStyle = pal.outline;
                ctx.fillRect(fcx-5,fcy-3,3,D);
            } else if (dir === 3) {
                ctx.fillStyle = pal.skin;
                ctx.fillRect(fcx-8,fcy,2,3);
                ctx.fillStyle = pal.eyeW;
                ctx.fillRect(fcx-5,fcy-2,4,3);
                ctx.fillStyle = pal.eye;
                ctx.fillRect(fcx-4,fcy-2,2,2);
                ctx.fillStyle = pal.pupil;
                ctx.fillRect(fcx-5,fcy-1,D,D);
                ctx.fillStyle = '#fff';
                ctx.fillRect(fcx-3,fcy-2,D,D);
                ctx.fillStyle = pal.outline;
                ctx.fillRect(fcx-5,fcy-3,4,D);
                ctx.fillStyle = pal.nose || pal.skinSh;
                ctx.fillRect(fcx-7,fcy+1,2,D);
                ctx.fillStyle = pal.mouth;
                ctx.fillRect(fcx-4,fcy+3,4,D);
            } else {
                ctx.fillStyle = pal.skin;
                ctx.fillRect(fcx+6,fcy,2,3);
                ctx.fillStyle = pal.eyeW;
                ctx.fillRect(fcx+1,fcy-2,4,3);
                ctx.fillStyle = pal.eye;
                ctx.fillRect(fcx+2,fcy-2,2,2);
                ctx.fillStyle = pal.pupil;
                ctx.fillRect(fcx+4,fcy-1,D,D);
                ctx.fillStyle = '#fff';
                ctx.fillRect(fcx+2,fcy-2,D,D);
                ctx.fillStyle = pal.outline;
                ctx.fillRect(fcx+1,fcy-3,4,D);
                ctx.fillStyle = pal.nose || pal.skinSh;
                ctx.fillRect(fcx+5,fcy+1,2,D);
                ctx.fillStyle = pal.mouth;
                ctx.fillRect(fcx,fcy+3,4,D);
            }
        };

        const drawNeck = (ncx, ncy) => {
            ctx.fillStyle = pal.skin;
            ctx.fillRect(ncx-3, ncy, 6, 3);
            ctx.fillStyle = pal.skinSh;
            ctx.fillRect(ncx-3, ncy+1, 6, D);
        };

        const drawOutfit = (ocx, ocy, dir) => {
            const of = arch.outfit;
            const la = Math.round(armSwing);
            const ra = Math.round(-armSwing);
            if (of === 'hero' || of === 'armor') {
                ctx.fillStyle = pal.armor || pal.tunic;
                ctx.fillRect(ocx-bw, ocy, bw*2, 16);
                ctx.fillStyle = pal.armorHL || pal.tunicHL;
                ctx.fillRect(ocx-bw+2, ocy, bw-2, 12);
                ctx.fillStyle = pal.armorDk || pal.tunicDk;
                ctx.fillRect(ocx, ocy, D, 16);
                ctx.fillRect(ocx-bw, ocy+14, bw*2, 2);
                ctx.fillStyle = pal.armorTrim || pal.tunicTrim;
                ctx.fillRect(ocx-bw, ocy+15, bw*2, D);
                ctx.fillRect(ocx-bw+1, ocy, D, 14);
                ctx.fillRect(ocx+bw-2, ocy, D, 14);
                ctx.fillStyle = pal.shoulder || pal.tunic;
                ell(ocx-bw-2, ocy+3, 4, 4);
                ell(ocx+bw+2, ocy+3, 4, 4);
                ctx.fillStyle = pal.shoulderHL || pal.tunicHL;
                ctx.fillRect(ocx-bw-4, ocy+1, 3, D);
                ctx.fillRect(ocx+bw+1, ocy+1, 3, D);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(ocx-bw+1, ocy-1, bw*2-2, 2);
            } else if (of === 'vest') {
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(ocx-bw, ocy, bw*2, 16);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(ocx-bw+2, ocy, bw-2, 12);
                ctx.fillStyle = pal.vest;
                ctx.fillRect(ocx-bw+1, ocy+1, 4, 14);
                ctx.fillRect(ocx+bw-5, ocy+1, 4, 14);
                ctx.fillStyle = pal.vestHL;
                ctx.fillRect(ocx-bw+2, ocy+2, 2, 8);
                ctx.fillRect(ocx+bw-4, ocy+2, 2, 8);
                ctx.fillStyle = pal.vestDk;
                ctx.fillRect(ocx-bw+1, ocy+14, 4, D);
                ctx.fillRect(ocx+bw-5, ocy+14, 4, D);
                ctx.fillStyle = '#c0a040';
                ctx.fillRect(ocx-1, ocy+3, 2, 2);ctx.fillRect(ocx-1, ocy+7, 2, 2);ctx.fillRect(ocx-1, ocy+11, 2, 2);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(ocx-bw+1, ocy-1, bw*2-2, 2);
                ctx.fillStyle = pal.shoulder || pal.tunic;
                ell(ocx-bw-1, ocy+3, 3, 3);ell(ocx+bw+1, ocy+3, 3, 3);
            } else if (of === 'robe' || of === 'robe_long' || of === 'robe_fancy') {
                ctx.fillStyle = pal.robe || pal.tunic;
                const rlen = of === 'robe_long' ? 20 : of === 'robe_fancy' ? 18 : 16;
                ctx.fillRect(ocx-bw, ocy, bw*2, rlen);
                ctx.fillStyle = pal.robeHL || pal.tunicHL;
                ctx.fillRect(ocx-bw+2, ocy, bw-3, rlen-4);
                ctx.fillStyle = pal.robeDk || pal.tunicDk;
                ctx.fillRect(ocx, ocy, D, rlen);
                ctx.fillRect(ocx-bw, ocy+rlen-2, bw*2, 2);
                ctx.fillStyle = pal.robeTrim || pal.tunicTrim;
                ctx.fillRect(ocx-bw, ocy+rlen-1, bw*2, D);
                if (of === 'robe_fancy') {
                    ctx.fillStyle = '#f0e060';
                    for(let i=0;i<3;i++){ctx.fillRect(ocx-bw+2+i*5,ocy+rlen-3,2,D);}
                    ctx.fillStyle = pal.robeTrim;
                    ctx.fillRect(ocx-1,ocy+2,2,rlen-6);
                }
                if (of === 'robe_long') {
                    ctx.fillStyle = pal.robeDk;
                    ctx.fillRect(ocx-2,ocy+4,D,12);ctx.fillRect(ocx+2,ocy+6,D,10);
                }
                ctx.fillStyle = pal.shoulder || pal.tunic;
                ell(ocx-bw-1, ocy+3, 3, 3);ell(ocx+bw+1, ocy+3, 3, 3);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(ocx-bw+1, ocy-1, bw*2-2, 2);
            } else if (of === 'cloak') {
                ctx.fillStyle = pal.cloak;
                ctx.fillRect(ocx-bw-1, ocy-1, bw*2+2, 18);
                ctx.fillStyle = pal.cloakHL;
                ctx.fillRect(ocx-bw+1, ocy, bw-2, 14);
                ctx.fillStyle = pal.cloakDk;
                ctx.fillRect(ocx-bw-1, ocy+15, bw*2+2, 2);
                ctx.fillRect(ocx, ocy, D, 16);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(ocx-3, ocy-1, 6, 2);
                ctx.fillStyle = pal.shoulder || pal.tunic;
                ell(ocx-bw-1, ocy+3, 3, 3);ell(ocx+bw+1, ocy+3, 3, 3);
            } else if (of === 'doublet') {
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(ocx-bw, ocy, bw*2, 16);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(ocx-bw+2, ocy, bw-2, 12);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(ocx-bw, ocy+14, bw*2, 2);
                ctx.fillStyle = '#fff';
                ctx.fillRect(ocx-2, ocy+1, 4, 10);
                ctx.fillStyle = '#e0e0e0';
                ctx.fillRect(ocx-2, ocy+9, 4, 2);
                ctx.fillStyle = pal.tunicTrim;
                ctx.fillRect(ocx-bw, ocy, D, 16);ctx.fillRect(ocx+bw-1, ocy, D, 16);
                ctx.fillStyle = '#c0a040';
                ctx.fillRect(ocx-1, ocy+2, 2, 2);ctx.fillRect(ocx-1, ocy+6, 2, 2);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(ocx-bw+1, ocy-1, bw*2-2, 2);
                ctx.fillStyle = pal.shoulder || pal.tunic;
                ell(ocx-bw-1, ocy+3, 3, 3);ell(ocx+bw+1, ocy+3, 3, 3);
            } else if (of === 'apron_outfit') {
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(ocx-bw, ocy, bw*2, 16);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(ocx-bw+2, ocy, bw-2, 12);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(ocx-bw, ocy+14, bw*2, 2);
                ctx.fillStyle = '#e0d8c8';
                ctx.fillRect(ocx-bw+2, ocy+6, bw*2-4, 10);
                ctx.fillStyle = '#c8c0b0';
                ctx.fillRect(ocx-bw+2, ocy+14, bw*2-4, 2);
                ctx.fillStyle = '#d0c8b8';
                ctx.fillRect(ocx-1, ocy+3, 2, 4);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(ocx-bw+1, ocy-1, bw*2-2, 2);
                ctx.fillStyle = pal.shoulder || pal.tunic;
                ell(ocx-bw-1, ocy+3, 3, 3);ell(ocx+bw+1, ocy+3, 3, 3);
            } else {
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(ocx-bw, ocy, bw*2, 16);
                ctx.fillStyle = pal.tunicHL;
                ctx.fillRect(ocx-bw+2, ocy, bw-2, 12);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(ocx, ocy, D, 16);
                ctx.fillRect(ocx-bw, ocy+14, bw*2, 2);
                ctx.fillStyle = pal.tunicTrim || pal.tunicHL;
                ctx.fillRect(ocx-bw, ocy+15, bw*2, D);
                ctx.fillStyle = pal.collar || pal.tunicHL;
                ctx.fillRect(ocx-bw+1, ocy-1, bw*2-2, 2);
                ctx.fillStyle = pal.shoulder || pal.tunic;
                ell(ocx-bw-1, ocy+3, 3, 3);ell(ocx+bw+1, ocy+3, 3, 3);
            }

            ctx.fillStyle = pal.belt;
            ctx.fillRect(ocx-bw, ocy+16, bw*2, 3);
            ctx.fillStyle = pal.beltHL;
            ctx.fillRect(ocx-bw+2, ocy+16, bw-2, D);
            ctx.fillStyle = pal.beltBk;
            ctx.fillRect(ocx-1, ocy+16, 3, 3);
            ctx.fillStyle = '#fff';ctx.globalAlpha=0.4;ctx.fillRect(ocx,ocy+16,D,D);ctx.globalAlpha=1;

            if (dir === 0 || dir === 2) {
                ctx.fillStyle = of === 'armor' || of === 'hero' ? (pal.armorDk || pal.tunicDk) : pal.tunic;
                ctx.fillRect(ocx-bw-3+la, ocy, 4, 8);
                ctx.fillRect(ocx+bw-1+ra, ocy, 4, 8);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(ocx-bw-3+la, ocy+7, 4, D);
                ctx.fillRect(ocx+bw-1+ra, ocy+7, 4, D);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(ocx-bw-2+la, ocy+8, 3, 4);
                ctx.fillRect(ocx+bw+ra, ocy+8, 3, 4);
                ctx.fillStyle = pal.glove || pal.skinSh;
                ctx.fillRect(ocx-bw-2+la, ocy+12, 3, 3);
                ctx.fillRect(ocx+bw+ra, ocy+12, 3, 3);
            } else if (dir === 3) {
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(ocx-bw-3+la, ocy, 4, 8);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(ocx-bw-3+la, ocy+7, 4, D);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(ocx-bw-2+la, ocy+8, 3, 4);
                ctx.fillStyle = pal.glove || pal.skinSh;
                ctx.fillRect(ocx-bw-2+la, ocy+12, 3, 3);
            } else {
                ctx.fillStyle = pal.tunic;
                ctx.fillRect(ocx+bw-1+ra, ocy, 4, 8);
                ctx.fillStyle = pal.tunicDk;
                ctx.fillRect(ocx+bw-1+ra, ocy+7, 4, D);
                ctx.fillStyle = pal.skin;
                ctx.fillRect(ocx+bw+ra, ocy+8, 3, 4);
                ctx.fillStyle = pal.glove || pal.skinSh;
                ctx.fillRect(ocx+bw+ra, ocy+12, 3, 3);
            }
        };

        const drawAcc = (acx, acy, dir) => {
            const a = arch.acc;
            if (a === 'sword' || a === 'shield') {
                const wx = dir===3 ? acx+bw+3 : dir===1 ? acx-bw-5 : acx-bw-5+Math.round(armSwing);
                if (a === 'sword' || isHero) {
                    ctx.fillStyle = pal.weapon;
                    ctx.fillRect(wx, acy+4, 2, 14);
                    ctx.fillStyle = pal.weaponHL;
                    ctx.fillRect(wx, acy+4, D, 12);
                    ctx.fillStyle = '#c0a040';
                    ctx.fillRect(wx-1, acy+4, 4, 2);
                }
                if (a === 'shield') {
                    const sx = dir===1 ? acx+bw+1 : acx-bw-5;
                    ctx.fillStyle = pal.armorDk;
                    ctx.fillRect(sx, acy+2, 5, 8);
                    ctx.fillStyle = pal.armor;
                    ctx.fillRect(sx+1, acy+3, 3, 6);
                    ctx.fillStyle = pal.armorTrim;
                    ctx.fillRect(sx+2, acy+4, D, 4);
                }
            } else if (a === 'staff') {
                const sx2 = dir===1 ? acx+bw+2 : acx-bw-4;
                ctx.fillStyle = '#8b6914';
                ctx.fillRect(sx2, acy-8, 2, 28);
                ctx.fillStyle = '#a88020';
                ctx.fillRect(sx2, acy-8, D, 26);
                ctx.fillStyle = '#60d0f0';
                ell(sx2+1, acy-10, 3, 3);
                ctx.fillStyle = '#80e0ff';
                ctx.globalAlpha=0.5;ell(sx2+1, acy-11, 2, 2);ctx.globalAlpha=1;
            } else if (a === 'bag') {
                const bx = dir===1 ? acx+bw : acx-bw-4;
                ctx.fillStyle = '#8b6030';
                ctx.fillRect(bx, acy+10, 5, 6);
                ctx.fillStyle = '#a07838';
                ctx.fillRect(bx+1, acy+11, 3, 4);
                ctx.fillStyle = '#c09048';
                ctx.fillRect(bx+1, acy+10, 3, D);
            } else if (a === 'glasses' && dir === 0) {
                ctx.fillStyle = '#404040';
                ctx.fillRect(acx-6, acy-3, 12, D);
                ctx.fillStyle = '#606060';
                ctx.strokeStyle = '#404040';
                ctx.lineWidth = 0.5;
                ctx.strokeRect(acx-6, acy-3, 5, 4);
                ctx.strokeRect(acx+1, acy-3, 5, 4);
                ctx.lineWidth = 1;
            } else if (a === 'quiver') {
                const qx = dir===3 ? acx-bw-3 : acx+bw;
                ctx.fillStyle = '#6b4020';
                ctx.fillRect(qx, acy-2, 3, 14);
                ctx.fillStyle = '#8b5830';
                ctx.fillRect(qx+1, acy-1, D, 12);
                ctx.fillStyle = '#808080';
                ctx.fillRect(qx, acy-6, D, 5);ctx.fillRect(qx+2, acy-5, D, 4);
                ctx.fillStyle = '#c0c0c0';
                ctx.fillRect(qx, acy-7, D, 2);ctx.fillRect(qx+2, acy-6, D, 2);
            } else if (a === 'medallion' && dir === 0) {
                ctx.fillStyle = '#c0a040';
                ctx.fillRect(acx-1, acy-1, 2, 3);
                ctx.fillStyle = '#e0c060';
                ell(acx, acy+3, 3, 3);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha=0.3;ctx.fillRect(acx-1, acy+2, D, D);ctx.globalAlpha=1;
            } else if (a === 'tools') {
                const tx = dir===1 ? acx+bw+1 : acx-bw-4;
                ctx.fillStyle = '#808080';
                ctx.fillRect(tx, acy+6, 2, 8);
                ctx.fillStyle = '#a0a0a0';
                ctx.fillRect(tx, acy+6, D, 6);
                ctx.fillStyle = '#8b6914';
                ctx.fillRect(tx, acy+3, 2, 4);
            } else if (a === 'orb') {
                const ox = dir===1 ? acx+bw+2 : acx-bw-5;
                ctx.fillStyle = '#4040c0';
                ell(ox+2, acy+12, 4, 4);
                ctx.fillStyle = '#6060e0';
                ell(ox+1, acy+11, 2, 2);
                ctx.fillStyle = '#fff';
                ctx.globalAlpha=0.4;ctx.fillRect(ox, acy+10, D, D);ctx.globalAlpha=1;
            }
        };

        const drawLegs = (lcx, lcy) => {
            ctx.fillStyle = pal.pants;
            ctx.fillRect(lcx-6, lcy, 5, 12);
            ctx.fillRect(lcx+1, lcy, 5, 12);
            ctx.fillStyle = pal.pantsHL;
            ctx.fillRect(lcx-5, lcy, 3, 8);
            ctx.fillRect(lcx+2, lcy, 3, 8);
            ctx.fillStyle = pal.pantsDk;
            ctx.fillRect(lcx-1, lcy, 2, 12);
            ctx.fillRect(lcx-6, lcy+8, 5, 2);
            ctx.fillRect(lcx+1, lcy+8, 5, 2);
            ctx.fillStyle = pal.boots;
            ctx.fillRect(lcx-7, lcy+12+legL, 6, 18);
            ctx.fillRect(lcx+1, lcy+12+legR, 6, 18);
            ctx.fillStyle = pal.bootsCuff;
            ctx.fillRect(lcx-7, lcy+12+legL, 6, 2);
            ctx.fillRect(lcx+1, lcy+12+legR, 6, 2);
            ctx.fillStyle = pal.bootsHL;
            ctx.fillRect(lcx-5, lcy+14+legL, 2, D);
            ctx.fillRect(lcx+3, lcy+14+legR, 2, D);
            ctx.fillStyle = pal.bootsDk;
            ctx.fillRect(lcx-7, lcy+26+legL, 6, D);
            ctx.fillRect(lcx+1, lcy+26+legR, 6, D);
            ctx.fillStyle = pal.bootsSole;
            ctx.fillRect(lcx-8, lcy+30+legL, 8, 6);
            ctx.fillRect(lcx, lcy+30+legR, 8, 6);
            ctx.fillStyle = pal.bootsDk;
            ctx.fillRect(lcx-8, lcy+34+legL, 8, 2);
            ctx.fillRect(lcx, lcy+34+legR, 8, 2);
        };

        const drawSideLegs = (lcx, lcy) => {
            ctx.fillStyle = pal.pants;
            ctx.fillRect(lcx-5, lcy, 10, 12);
            ctx.fillStyle = pal.pantsDk;
            ctx.fillRect(lcx-5, lcy+8, 10, 2);
            ctx.fillStyle = pal.pantsHL;
            ctx.fillRect(lcx-3, lcy, 4, 8);
            ctx.fillStyle = pal.boots;
            ctx.fillRect(lcx-6, lcy+12+legL, 6, 18);
            ctx.fillRect(lcx+1, lcy+12+legR, 6, 18);
            ctx.fillStyle = pal.bootsCuff;
            ctx.fillRect(lcx-6, lcy+12+legL, 6, 2);
            ctx.fillRect(lcx+1, lcy+12+legR, 6, 2);
            ctx.fillStyle = pal.bootsDk;
            ctx.fillRect(lcx-6, lcy+26+legL, 6, D);
            ctx.fillRect(lcx+1, lcy+26+legR, 6, D);
            ctx.fillStyle = pal.bootsSole;
            ctx.fillRect(lcx-7, lcy+30+legL, 8, 6);
            ctx.fillRect(lcx, lcy+30+legR, 8, 6);
            ctx.fillStyle = pal.bootsDk;
            ctx.fillRect(lcx-7, lcy+34+legL, 8, 2);
            ctx.fillRect(lcx, lcy+34+legR, 8, 2);
        };

        const drawCapeBack = (ccx, ccy) => {
            if (!isHero) return;
            ctx.fillStyle = pal.cape;
            ctx.fillRect(ccx-bw-1, ccy, bw*2+2, 22);
            ctx.fillStyle = pal.capeHL;
            ctx.fillRect(ccx-bw+1, ccy, bw-2, 18);
            ctx.fillStyle = pal.capeDk;
            ctx.fillRect(ccx, ccy, 2, 22);
            ctx.fillRect(ccx+2, ccy+1, bw-2, 21);
            ctx.fillStyle = pal.capeEdge;
            ctx.fillRect(ccx-bw-1, ccy+20, bw*2+2, 2);
            const cw = moving ? Math.sin(frame*Math.PI/2)*2 : Math.sin(gt/1200)*0.5;
            ctx.fillStyle = pal.capeDk;
            ctx.fillRect(ccx-bw+2, ccy+20+Math.round(cw), bw*2-4, 2);
            ctx.fillStyle = pal.cape;
            for(let i=0;i<4;i++) ctx.fillRect(ccx-bw+2+i*Math.round(bw/2), ccy+6, D, 12);
        };

        const dir = facing === 'down' ? 0 : facing === 'up' ? 2 : facing === 'left' ? 3 : 1;
        const headY = sy + by + 12;
        const hairY = sy + by + 5;
        const neckY = sy + by + 17;
        const bodyY = sy + by + 21;
        const legY = y + 2;

        if (dir === 2 && isHero) drawCapeBack(cx, bodyY-1);

        if (arch.hatType) {
            drawHat(cx, hairY);
        } else {
            drawHair(cx, hairY, dir);
        }
        drawFace(cx, headY, dir);
        drawNeck(cx, neckY);
        drawOutfit(cx, bodyY, dir);
        drawAcc(cx, bodyY, dir);
        drawLegs(cx, legY);
    }

    return { drawSprite: drawSpriteCached, buildNPCPal, getArchetype, SKIN_TONES, EYE_COLORS, HAIR_PRESETS, ARCHETYPES };
})();
