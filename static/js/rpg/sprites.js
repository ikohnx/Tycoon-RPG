window.RPGSprites = (function() {
    const ARCHETYPE_KEYS = ['merchant','scholar','elder','warrior','scout','noble','artisan','mystic'];

    const IND_CHARACTER_KEYS = ['ind_accountant','ind_foreman','ind_engineer','ind_inventor'];
    const IND_CHARACTER_NAMES = ['Accountant', 'Foreman', 'Engineer', 'Inventor'];

    const SPRITE_IMAGES = {};
    const SPRITE_NAMES = ['hero','merchant','scholar','elder','warrior','scout','noble','artisan','mystic',
        'ind_accountant','ind_foreman','ind_engineer','ind_inventor'];
    let imagesLoaded = 0;
    let totalImages = SPRITE_NAMES.length;
    let allLoaded = false;

    function loadAllSprites() {
        SPRITE_NAMES.forEach(name => {
            const img = new Image();
            img.onload = function() {
                imagesLoaded++;
                if (imagesLoaded >= totalImages) allLoaded = true;
            };
            img.onerror = function() {
                console.warn('Failed to load sprite:', name);
                imagesLoaded++;
                if (imagesLoaded >= totalImages) allLoaded = true;
            };
            img.src = '/static/images/sprites/' + name + '.png';
            SPRITE_IMAGES[name] = img;
        });
    }

    loadAllSprites();

    function getArchetypeName(spriteId) {
        return ARCHETYPE_KEYS[(spriteId || 0) % ARCHETYPE_KEYS.length];
    }

    function getHeroSpriteName(world, characterIndex) {
        if (world === 'Industrial' && characterIndex >= 0 && characterIndex < IND_CHARACTER_KEYS.length) {
            return IND_CHARACTER_KEYS[characterIndex];
        }
        return 'hero';
    }

    let activeHeroSprite = 'hero';

    function setActiveHero(world, characterIndex) {
        activeHeroSprite = getHeroSpriteName(world, characterIndex);
    }

    function drawSprite(ctx, gt, type, x, y, facing, frame, moving, color, spriteId, TS, SPRITE_YOFF) {
        const isHero = type === 'hero';
        const spriteName = isHero ? activeHeroSprite : getArchetypeName(spriteId);
        const img = SPRITE_IMAGES[spriteName];

        const spriteW = TS + 16;
        const spriteH = TS + (SPRITE_YOFF || 0) + 24;

        const bob = moving ? Math.sin((frame || 0) * Math.PI / 2) * 2 : 0;
        const breathe = !moving ? Math.sin(gt / 700) * 0.5 : 0;
        const by = Math.round(-bob + breathe);

        ctx.fillStyle = 'rgba(0,0,0,0.2)';
        ctx.beginPath();
        ctx.ellipse(x + TS / 2, y + TS - 2, 14, 4, 0, 0, Math.PI * 2);
        ctx.fill();

        if (img && img.complete && img.naturalWidth > 0) {
            const drawW = spriteW;
            const drawH = spriteH;
            const drawX = x + TS / 2 - drawW / 2;
            const drawY = y - (SPRITE_YOFF || 0) - 4 + by;

            ctx.save();
            ctx.imageSmoothingEnabled = false;

            if (facing === 'left') {
                ctx.translate(drawX + drawW, drawY);
                ctx.scale(-1, 1);
                ctx.drawImage(img, 0, 0, drawW, drawH);
            } else {
                ctx.drawImage(img, drawX, drawY, drawW, drawH);
            }

            ctx.restore();
        } else {
            drawFallbackSprite(ctx, gt, type, x, y, facing, frame, moving, color, spriteId, TS, SPRITE_YOFF);
        }
    }

    function drawFallbackSprite(ctx, gt, type, x, y, facing, frame, moving, color, spriteId, TS, SPRITE_YOFF) {
        const isHero = type === 'hero';
        const cx = x + TS / 2;
        const bob = moving ? Math.sin((frame || 0) * Math.PI / 2) * 2 : 0;
        const breathe = !moving ? Math.sin(gt / 700) * 0.5 : 0;
        const by = Math.round(-bob + breathe);
        const sy = y - (SPRITE_YOFF || 0) + by;

        const bodyColor = isHero ? '#1c3078' : (color || '#44aa44');
        const skinColor = '#f4d0a0';
        const hairColor = isHero ? '#2888e0' : '#604020';

        ctx.fillStyle = '#101020';
        ctx.fillRect(cx - 9, sy + 42, 18, 20);
        ctx.fillStyle = bodyColor;
        ctx.fillRect(cx - 8, sy + 43, 16, 18);

        ctx.fillStyle = '#101020';
        ctx.beginPath();
        ctx.ellipse(cx, sy + 26, 12, 12, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = skinColor;
        ctx.beginPath();
        ctx.ellipse(cx, sy + 28, 10, 10, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = hairColor;
        ctx.beginPath();
        ctx.ellipse(cx, sy + 22, 11, 8, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#101020';
        ctx.fillRect(cx - 6, sy + 62, 5, 12);
        ctx.fillRect(cx + 1, sy + 62, 5, 12);
        ctx.fillStyle = '#503020';
        ctx.fillRect(cx - 5, sy + 63, 4, 10);
        ctx.fillRect(cx + 2, sy + 63, 4, 10);
    }

    function drawCharacterPreview(ctx, spriteName, x, y, w, h) {
        const img = SPRITE_IMAGES[spriteName];
        if (img && img.complete && img.naturalWidth > 0) {
            ctx.save();
            ctx.imageSmoothingEnabled = false;
            ctx.drawImage(img, x, y, w, h);
            ctx.restore();
        } else {
            ctx.fillStyle = '#303060';
            ctx.fillRect(x, y, w, h);
            ctx.fillStyle = '#8080c0';
            ctx.font = '10px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('?', x + w / 2, y + h / 2 + 4);
        }
    }

    function buildNPCPal(color, spriteId) {
        return { archName: getArchetypeName(spriteId) };
    }

    function getArchetype(spriteId) {
        return { class: getArchetypeName(spriteId) };
    }

    return {
        drawSprite: drawSprite,
        drawCharacterPreview: drawCharacterPreview,
        setActiveHero: setActiveHero,
        buildNPCPal: buildNPCPal,
        getArchetype: getArchetype,
        ARCHETYPE_KEYS: ARCHETYPE_KEYS,
        IND_CHARACTER_KEYS: IND_CHARACTER_KEYS,
        IND_CHARACTER_NAMES: IND_CHARACTER_NAMES,
        isLoaded: function() { return allLoaded; },
        getLoadProgress: function() { return { loaded: imagesLoaded, total: totalImages }; }
    };
})();
