const RPGMaps = (function() {

    const T = {
        EMPTY: 0, GRASS: 1, PATH: 2, WATER: 3,
        WALL: 4, WALL_TOP: 5, ROOF: 6, DOOR: 7,
        WINDOW: 8, TREE: 9, FLOWERS: 10, WOOD_FLOOR: 11,
        SIGN: 12, SAND: 13, STONE_FLOOR: 14, HEDGE: 15,
        CHEST: 16, PORTAL: 17, FOUNTAIN: 18, LAMP: 19,
        STALL: 20, BENCH: 21, WELL: 22, CRATES: 23,
        FIREPLACE: 24, BOOKSHELF: 25,
        CLIFF: 26, CLIFF_TOP: 27, WATERFALL: 28, ROCK: 29,
        GRASS2: 30, GRASS3: 31, BRIDGE: 32,
        COBBLE: 33, STATUE: 34, FENCE: 35,
        DIRT: 36, FACTORY_WALL: 37, FACTORY_ROOF: 38,
        FACTORY_DOOR: 39, FACTORY_WINDOW: 40, SMOKESTACK: 41,
        RAIL_H: 42, RAIL_V: 43, RAIL_CROSS: 44,
        DOCK: 45, PINE_TREE: 46, MOUNTAIN: 47,
        MOUNTAIN_BASE: 48, GEAR: 49, COAL_PILE: 50,
        IRON_FENCE: 51, IND_LAMP: 52, WAREHOUSE: 53,
        STEAM_PIPE: 54, ANVIL: 55, BARREL: 56,
        CRANE: 57, RAIL_CURVE_NE: 58, RAIL_CURVE_SE: 59
    };

    const SOLID = [T.TREE, T.WALL, T.WALL_TOP, T.ROOF, T.WINDOW, T.WATER, T.HEDGE,
        T.CHEST, T.SIGN, T.FOUNTAIN, T.STALL, T.WELL, T.LAMP, T.BENCH, T.CRATES,
        T.FIREPLACE, T.BOOKSHELF, T.CLIFF, T.CLIFF_TOP, T.WATERFALL, T.ROCK,
        T.STATUE, T.FENCE,
        T.FACTORY_WALL, T.FACTORY_ROOF, T.FACTORY_WINDOW, T.SMOKESTACK,
        T.PINE_TREE, T.MOUNTAIN, T.MOUNTAIN_BASE, T.GEAR, T.COAL_PILE,
        T.IRON_FENCE, T.IND_LAMP, T.WAREHOUSE, T.STEAM_PIPE, T.ANVIL,
        T.BARREL, T.CRANE];

    function fill(tiles, r1, c1, r2, c2, t) {
        for (let r = r1; r <= r2; r++)
            for (let c = c1; c <= c2; c++)
                tiles[r][c] = t;
    }

    function scatter(tiles, r1, c1, r2, c2, t, chance) {
        for (let r = r1; r <= r2; r++)
            for (let c = c1; c <= c2; c++)
                if (tiles[r][c] === T.GRASS && Math.random() < chance) tiles[r][c] = t;
    }

    function scatterVariant(tiles, W, H) {
        for (let r = 0; r < H; r++)
            for (let c = 0; c < W; c++)
                if (tiles[r][c] === T.GRASS) {
                    const rng = Math.random();
                    if (rng < 0.12) tiles[r][c] = T.GRASS2;
                    else if (rng < 0.18) tiles[r][c] = T.GRASS3;
                }
    }

    function makeCollision(tiles, W, H) {
        const collision = [];
        for (let r = 0; r < H; r++) {
            collision[r] = [];
            for (let c = 0; c < W; c++)
                collision[r][c] = SOLID.includes(tiles[r][c]) ? 1 : 0;
        }
        return collision;
    }

    function hPath(tiles, r, c1, c2, w) {
        w = w || 2;
        for (let dr = 0; dr < w; dr++)
            for (let c = c1; c <= c2; c++)
                tiles[r + dr][c] = T.PATH;
    }

    function vPath(tiles, c, r1, r2, w) {
        w = w || 2;
        for (let dc = 0; dc < w; dc++)
            for (let r = r1; r <= r2; r++)
                tiles[r][c + dc] = T.PATH;
    }

    function placeBuilding(tiles, sr, sc, w, h, extraWindows) {
        for (let c = sc; c < sc + w; c++) {
            tiles[sr][c] = T.ROOF;
            tiles[sr + 1][c] = T.ROOF;
        }
        for (let r = sr + 2; r < sr + h; r++)
            for (let c = sc; c < sc + w; c++) tiles[r][c] = T.WALL;
        const dc = sc + Math.floor(w / 2);
        tiles[sr + h - 1][dc] = T.DOOR;
        if (w >= 5) {
            tiles[sr + 2][sc + 1] = T.WINDOW;
            tiles[sr + 2][sc + w - 2] = T.WINDOW;
        }
        if (extraWindows && w >= 7) {
            tiles[sr + 3][sc + 1] = T.WINDOW;
            tiles[sr + 3][sc + w - 2] = T.WINDOW;
        }
    }

    function placeRiver(tiles, W, startCol, startRow, endRow, width) {
        for (let r = startRow; r <= endRow; r++) {
            const bend = Math.round(Math.sin(r * 0.15) * 3);
            for (let dc = 0; dc < width; dc++) {
                const c = startCol + bend + dc;
                if (c >= 0 && c < W) tiles[r][c] = T.WATER;
            }
        }
    }

    function placeBridgeH(tiles, r, c, len) {
        for (let i = 0; i < len; i++) tiles[r][c + i] = T.BRIDGE;
    }

    function placeBridgeV(tiles, r, c, len) {
        for (let i = 0; i < len; i++) tiles[r + i][c] = T.BRIDGE;
    }

    function placeTreeCluster(tiles, r, c, w, h) {
        for (let dr = 0; dr < h; dr++)
            for (let dc = 0; dc < w; dc++)
                tiles[r + dr][c + dc] = T.TREE;
    }

    function placeLake(tiles, cr, cc, rx, ry) {
        for (let r = cr - ry; r <= cr + ry; r++)
            for (let c = cc - rx; c <= cc + rx; c++) {
                const dx = (c - cc) / rx, dy = (r - cr) / ry;
                if (dx * dx + dy * dy <= 1) tiles[r][c] = T.WATER;
            }
    }

    function placeGarden(tiles, r, c, w, h) {
        fill(tiles, r, c, r + h - 1, c + w - 1, T.GRASS);
        for (let dr = 0; dr < h; dr++) {
            tiles[r + dr][c] = T.HEDGE;
            tiles[r + dr][c + w - 1] = T.HEDGE;
        }
        for (let dc = 0; dc < w; dc++) {
            tiles[r][c + dc] = T.HEDGE;
            tiles[r + h - 1][c + dc] = T.HEDGE;
        }
        tiles[r + Math.floor(h / 2)][c] = T.GRASS;
        scatter(tiles, r + 1, c + 1, r + h - 2, c + w - 2, T.FLOWERS, 0.4);
    }

    function createHubTown() {
        const W = 80;
        const H = 65;
        const tiles = [];
        for (let r = 0; r < H; r++) {
            tiles[r] = [];
            for (let c = 0; c < W; c++) tiles[r][c] = T.GRASS;
        }

        for (let c = 0; c < W; c++) { tiles[0][c] = T.TREE; tiles[1][c] = T.TREE; tiles[H-1][c] = T.TREE; tiles[H-2][c] = T.TREE; }
        for (let r = 0; r < H; r++) { tiles[r][0] = T.TREE; tiles[r][1] = T.TREE; tiles[r][W-1] = T.TREE; tiles[r][W-2] = T.TREE; }

        placeRiver(tiles, W, 60, 2, 45, 4);
        for (let r = 44; r <= 50; r++)
            for (let dc = 0; dc < 4; dc++) {
                const c = 60 + Math.round(Math.sin(r * 0.15) * 3) + dc;
                if (c >= 0 && c < W) tiles[r][c] = T.WATER;
            }
        for (let c = 57; c <= 73; c++) { tiles[48][c] = T.WATER; tiles[49][c] = T.WATER; tiles[50][c] = T.WATER; }

        placeBridgeH(tiles, 20, 58, 8);
        placeBridgeH(tiles, 21, 58, 8);
        placeBridgeH(tiles, 35, 57, 9);
        placeBridgeH(tiles, 36, 57, 9);

        placeTreeCluster(tiles, 3, 3, 5, 4);
        placeTreeCluster(tiles, 3, 10, 3, 3);
        placeTreeCluster(tiles, 50, 3, 6, 5);
        placeTreeCluster(tiles, 55, 10, 4, 3);
        placeTreeCluster(tiles, 3, 68, 5, 4);
        placeTreeCluster(tiles, 45, 68, 4, 5);
        placeTreeCluster(tiles, 8, 45, 3, 4);
        placeTreeCluster(tiles, 40, 3, 3, 4);

        scatter(tiles, 2, 2, 7, 18, T.TREE, 0.08);
        scatter(tiles, 55, 20, 62, 55, T.TREE, 0.06);
        scatter(tiles, 2, 50, 8, 56, T.TREE, 0.07);

        vPath(tiles, 38, 2, 62, 3);
        hPath(tiles, 30, 2, 77, 3);
        vPath(tiles, 20, 2, 28, 2);
        vPath(tiles, 55, 2, 28, 2);
        hPath(tiles, 15, 15, 60, 2);
        hPath(tiles, 45, 10, 55, 2);
        vPath(tiles, 20, 33, 62, 2);
        vPath(tiles, 55, 33, 62, 2);
        hPath(tiles, 55, 15, 55, 2);

        vPath(tiles, 38, 8, 14, 2);
        vPath(tiles, 38, 47, 55, 2);
        hPath(tiles, 10, 20, 55, 2);

        fill(tiles, 27, 33, 36, 44, T.COBBLE);
        fill(tiles, 28, 34, 35, 43, T.STONE_FLOOR);
        tiles[31][38] = T.FOUNTAIN; tiles[31][39] = T.FOUNTAIN;
        tiles[32][38] = T.FOUNTAIN; tiles[32][39] = T.FOUNTAIN;
        tiles[28][34] = T.LAMP; tiles[28][43] = T.LAMP;
        tiles[35][34] = T.LAMP; tiles[35][43] = T.LAMP;
        tiles[29][36] = T.BENCH; tiles[29][41] = T.BENCH;
        tiles[34][36] = T.BENCH; tiles[34][41] = T.BENCH;
        tiles[30][35] = T.FLOWERS; tiles[30][42] = T.FLOWERS;
        tiles[33][35] = T.FLOWERS; tiles[33][42] = T.FLOWERS;
        tiles[29][38] = T.STATUE; tiles[29][39] = T.STATUE;

        placeBuilding(tiles, 4, 20, 7, 5, true);
        tiles[3][22] = T.SIGN; tiles[3][25] = T.SIGN;
        tiles[9][20] = T.CRATES; tiles[9][26] = T.CRATES;
        tiles[9][21] = T.LAMP; tiles[9][25] = T.LAMP;

        placeBuilding(tiles, 4, 30, 6, 5);
        tiles[3][31] = T.FLOWERS; tiles[3][34] = T.FLOWERS;

        placeBuilding(tiles, 4, 44, 6, 5);
        tiles[3][45] = T.FLOWERS; tiles[3][48] = T.FLOWERS;
        tiles[9][44] = T.CRATES;

        placeBuilding(tiles, 4, 53, 7, 5, true);
        tiles[3][54] = T.SIGN; tiles[3][58] = T.SIGN;
        tiles[9][53] = T.CRATES; tiles[9][59] = T.CRATES;

        placeBuilding(tiles, 18, 15, 6, 5);
        tiles[23][15] = T.CRATES; tiles[23][20] = T.CRATES;

        placeBuilding(tiles, 18, 25, 5, 4);
        tiles[17][26] = T.SIGN;

        placeBuilding(tiles, 18, 50, 5, 4);
        tiles[17][51] = T.SIGN;

        placeBuilding(tiles, 18, 58, 6, 5);
        tiles[23][58] = T.CRATES;

        fill(tiles, 34, 15, 40, 22, T.STONE_FLOOR);
        placeBuilding(tiles, 34, 15, 8, 5);
        tiles[33][17] = T.SIGN; tiles[33][20] = T.SIGN;
        tiles[39][15] = T.LAMP; tiles[39][22] = T.LAMP;
        tiles[40][17] = T.STALL; tiles[40][19] = T.STALL;
        tiles[40][21] = T.STALL;

        fill(tiles, 34, 50, 40, 57, T.STONE_FLOOR);
        placeBuilding(tiles, 34, 50, 8, 5);
        tiles[33][52] = T.SIGN; tiles[33][55] = T.SIGN;
        tiles[39][50] = T.LAMP; tiles[39][57] = T.LAMP;
        tiles[40][52] = T.STALL; tiles[40][54] = T.STALL;
        tiles[40][56] = T.STALL;

        placeBuilding(tiles, 47, 20, 6, 5);
        tiles[52][20] = T.CRATES; tiles[52][25] = T.CRATES;

        placeBuilding(tiles, 47, 30, 5, 4);
        placeBuilding(tiles, 47, 42, 5, 4);

        placeBuilding(tiles, 47, 50, 6, 5);
        tiles[52][50] = T.CRATES; tiles[52][55] = T.CRATES;

        placeGarden(tiles, 13, 33, 6, 5);
        placeGarden(tiles, 37, 24, 5, 5);
        placeGarden(tiles, 37, 46, 5, 5);
        placeGarden(tiles, 54, 33, 6, 5);

        placeLake(tiles, 58, 45, 5, 3);
        tiles[55][44] = T.CLIFF_TOP; tiles[55][45] = T.CLIFF_TOP; tiles[55][46] = T.CLIFF_TOP;
        tiles[56][43] = T.ROCK; tiles[56][47] = T.ROCK;

        tiles[42][10] = T.WELL; tiles[42][65] = T.WELL;
        tiles[12][65] = T.WELL;

        tiles[10][38] = T.LAMP; tiles[10][40] = T.LAMP;
        tiles[15][33] = T.LAMP; tiles[15][44] = T.LAMP;
        tiles[45][33] = T.LAMP; tiles[45][44] = T.LAMP;
        tiles[55][20] = T.LAMP; tiles[55][55] = T.LAMP;

        for (let c = 14; c <= 23; c++) { tiles[43][c] = T.FENCE; }
        for (let c = 49; c <= 58; c++) { tiles[43][c] = T.FENCE; }

        scatter(tiles, 2, 2, 12, 18, T.FLOWERS, 0.08);
        scatter(tiles, 55, 2, 62, 18, T.FLOWERS, 0.06);
        scatter(tiles, 2, 62, 12, 77, T.FLOWERS, 0.07);
        scatter(tiles, 42, 25, 45, 32, T.FLOWERS, 0.1);
        scatter(tiles, 42, 43, 45, 49, T.FLOWERS, 0.1);
        scatter(tiles, 22, 38, 26, 44, T.FLOWERS, 0.06);
        scatter(tiles, 10, 12, 14, 18, T.ROCK, 0.03);
        scatter(tiles, 50, 60, 58, 70, T.ROCK, 0.03);

        tiles[0][39] = T.GRASS; tiles[0][40] = T.GRASS;
        tiles[1][39] = T.GRASS; tiles[1][40] = T.GRASS;

        tiles[H-2][39] = T.PORTAL; tiles[H-2][40] = T.PORTAL;
        tiles[H-1][39] = T.PORTAL; tiles[H-1][40] = T.PORTAL;

        scatterVariant(tiles, W, H);

        const collision = makeCollision(tiles, W, H);

        const npcs = [
            {
                x: 23, y: 9, name: 'Marketing Maven',
                spriteType: 'npc', color: '#cc4488', facing: 'down', spriteId: 5,
                dialogue: ["Welcome to the Marketing Guild!", "I specialize in branding, campaigns, and customer acquisition.", "Let me show you how to boost your company's reach."],
                action: 'marketing', route: '/scenarios/Marketing'
            },
            {
                x: 32, y: 9, name: 'Finance Director',
                spriteType: 'npc', color: '#44aa44', facing: 'down', spriteId: 1,
                dialogue: ["The Treasury is just behind me.", "Budgets, investments, financial forecasting... I manage it all.", "Let's make sure your books are balanced!"],
                action: 'finance', route: '/scenarios/Finance'
            },
            {
                x: 39, y: 12, name: 'Town Elder',
                spriteType: 'npc', color: '#8866aa', facing: 'down', stationary: true, spriteId: 2,
                dialogue: ["Welcome to Business Town, young entrepreneur!", "Each building here represents a different business discipline.", "Speak with the guild masters to learn and grow your empire.", "Use the arrow keys to move and press Enter or Space to talk."],
                action: 'tutorial', route: '/tutorial'
            },
            {
                x: 46, y: 9, name: 'Operations Chief',
                spriteType: 'npc', color: '#dd8833', facing: 'down', spriteId: 3,
                dialogue: ["I oversee the operations and logistics.", "Supply chains, inventory, scheduling...", "Come learn how to streamline your business!"],
                action: 'operations', route: '/scenarios/Operations'
            },
            {
                x: 56, y: 9, name: 'HR Manager',
                spriteType: 'npc', color: '#33aadd', facing: 'down', spriteId: 4,
                dialogue: ["People are any company's greatest asset!", "Hiring, training, team dynamics...", "Let me teach you to build an amazing team."],
                action: 'hr', route: '/scenarios/Human Resources'
            },
            {
                x: 17, y: 23, name: 'Legal Counsel',
                spriteType: 'npc', color: '#aa6633', facing: 'up', spriteId: 7,
                dialogue: ["Contracts, compliance, intellectual property...", "The law can be complex, but I'll guide you.", "Protect your business from legal pitfalls!"],
                action: 'legal', route: '/scenarios/Legal'
            },
            {
                x: 27, y: 22, name: 'Strategy Advisor',
                spriteType: 'npc', color: '#8844cc', facing: 'up', spriteId: 6,
                dialogue: ["Strategy is the art of seeing the big picture.", "Market analysis, competitive positioning, long-term planning...", "Let me sharpen your strategic thinking!"],
                action: 'strategy', route: '/scenarios/Strategy'
            },
            {
                x: 52, y: 22, name: 'Merchant',
                spriteType: 'npc', color: '#ccaa33', facing: 'up', spriteId: 0,
                dialogue: ["Looking to buy or sell? You've come to the right place!", "I have equipment, items, and special offers!", "Step into my shop to browse the inventory."],
                action: 'shop', route: '/inventory'
            },
            {
                x: 60, y: 23, name: 'Guild Master',
                spriteType: 'npc', color: '#cc3355', facing: 'up', spriteId: 11,
                dialogue: ["The Business Guild offers challenges and competitions.", "Prove your skills against other entrepreneurs!", "Are you ready for the next challenge?"],
                action: 'guild', route: '/dashboard'
            },
            {
                x: 38, y: 29, name: 'Mayor',
                spriteType: 'npc', color: '#dddd44', facing: 'down', stationary: true, spriteId: 13,
                dialogue: ["I am the Mayor of Business Town.", "This plaza is the heart of our community.", "All paths lead here. Visit the guilds to learn!", "Your progress is tracked in the Command Center."],
                action: 'hub', route: '/hub'
            },
            {
                x: 18, y: 40, name: 'Wandering Trader',
                spriteType: 'npc', color: '#55bb88', facing: 'right', spriteId: 8,
                dialogue: ["I travel between worlds collecting rare goods.", "Sometimes the market stalls have special deals!", "Check back often for new stock."]
            },
            {
                x: 55, y: 40, name: 'Courier',
                spriteType: 'npc', color: '#bb5555', facing: 'left', spriteId: 12,
                dialogue: ["I deliver messages and daily missions.", "Check your mission board regularly!", "There are always new opportunities."]
            },
            {
                x: 22, y: 52, name: 'Apprentice',
                spriteType: 'npc', color: '#66aa88', facing: 'down', spriteId: 9,
                dialogue: ["I'm just starting my business journey too!", "Have you tried the training grounds?", "Practice makes perfect!"],
                action: 'training', route: '/scenarios'
            },
            {
                x: 52, y: 52, name: 'Investor',
                spriteType: 'npc', color: '#aabb44', facing: 'down', spriteId: 14,
                dialogue: ["I'm always looking for the next big opportunity.", "Show me your business plan and I might invest!", "Success requires both vision and execution."],
                action: 'finance', route: '/scenarios/Finance'
            },
            {
                x: 65, y: 20, name: 'Fisher',
                spriteType: 'npc', color: '#5599bb', facing: 'left', spriteId: 10,
                dialogue: ["The river is peaceful today.", "Sometimes the best ideas come from quiet reflection.", "Take a break and enjoy the view!"]
            },
            {
                x: 45, y: 58, name: 'Gardener',
                spriteType: 'npc', color: '#44aa66', facing: 'down', spriteId: 15,
                dialogue: ["I tend the gardens of Business Town.", "A thriving town needs green spaces!", "Nature reminds us that growth takes patience."]
            }
        ];

        return {
            name: 'Business Town',
            width: W, height: H,
            tiles, collision,
            spawnX: 39, spawnY: 25,
            npcs,
            transitions: [
                { x: 39, y: 0, target: 'world_map' },
                { x: 40, y: 0, target: 'world_map' },
                { x: 39, y: H - 1, target: 'market_district', spawnX: 30, spawnY: 2 },
                { x: 40, y: H - 1, target: 'market_district', spawnX: 31, spawnY: 2 }
            ],
            interactables: [
                { x: 22, y: 3, name: 'Town Notice', dialogue: ["Business Town Notice Board", "Visit each guild master to learn business skills.", "Complete challenges to earn gold and reputation!"] },
                { x: 25, y: 3, name: 'Town Crest', dialogue: ["The crest of Business Town.", "Founded by entrepreneurs, for entrepreneurs."] }
            ]
        };
    }

    function createMarketDistrict() {
        const W = 60;
        const H = 50;
        const tiles = [];
        for (let r = 0; r < H; r++) {
            tiles[r] = [];
            for (let c = 0; c < W; c++) tiles[r][c] = T.GRASS;
        }

        for (let c = 0; c < W; c++) { tiles[0][c] = T.TREE; tiles[H-1][c] = T.TREE; tiles[H-2][c] = T.TREE; }
        for (let r = 0; r < H; r++) { tiles[r][0] = T.TREE; tiles[r][1] = T.TREE; tiles[r][W-1] = T.TREE; tiles[r][W-2] = T.TREE; }

        vPath(tiles, 29, 1, 48, 2);
        hPath(tiles, 24, 2, 57, 2);
        hPath(tiles, 12, 10, 49, 2);
        hPath(tiles, 36, 10, 49, 2);
        vPath(tiles, 15, 5, 44, 2);
        vPath(tiles, 44, 5, 44, 2);

        tiles[0][29] = T.GRASS; tiles[0][30] = T.GRASS;
        tiles[1][29] = T.PATH; tiles[1][30] = T.PATH;

        fill(tiles, 20, 24, 28, 36, T.COBBLE);
        fill(tiles, 21, 25, 27, 35, T.STONE_FLOOR);
        tiles[24][29] = T.FOUNTAIN; tiles[24][30] = T.FOUNTAIN;
        tiles[25][29] = T.FOUNTAIN; tiles[25][30] = T.FOUNTAIN;
        tiles[21][25] = T.LAMP; tiles[21][35] = T.LAMP;
        tiles[27][25] = T.LAMP; tiles[27][35] = T.LAMP;
        tiles[22][27] = T.BENCH; tiles[22][32] = T.BENCH;
        tiles[26][27] = T.BENCH; tiles[26][32] = T.BENCH;
        tiles[23][26] = T.STATUE;

        fill(tiles, 5, 5, 11, 14, T.STONE_FLOOR);
        tiles[6][6] = T.STALL; tiles[6][8] = T.STALL; tiles[6][10] = T.STALL; tiles[6][12] = T.STALL;
        tiles[8][6] = T.STALL; tiles[8][8] = T.STALL; tiles[8][10] = T.STALL; tiles[8][12] = T.STALL;
        tiles[10][6] = T.STALL; tiles[10][8] = T.STALL; tiles[10][10] = T.STALL; tiles[10][12] = T.STALL;
        tiles[7][7] = T.LAMP; tiles[7][11] = T.LAMP;
        tiles[9][7] = T.LAMP; tiles[9][11] = T.LAMP;
        tiles[5][5] = T.SIGN; tiles[5][14] = T.SIGN;

        fill(tiles, 5, 45, 11, 54, T.STONE_FLOOR);
        tiles[6][46] = T.STALL; tiles[6][48] = T.STALL; tiles[6][50] = T.STALL; tiles[6][52] = T.STALL;
        tiles[8][46] = T.STALL; tiles[8][48] = T.STALL; tiles[8][50] = T.STALL; tiles[8][52] = T.STALL;
        tiles[10][46] = T.STALL; tiles[10][48] = T.STALL; tiles[10][50] = T.STALL; tiles[10][52] = T.STALL;
        tiles[7][47] = T.LAMP; tiles[7][51] = T.LAMP;
        tiles[9][47] = T.LAMP; tiles[9][51] = T.LAMP;
        tiles[5][45] = T.SIGN; tiles[5][54] = T.SIGN;

        fill(tiles, 30, 5, 36, 14, T.STONE_FLOOR);
        tiles[31][6] = T.STALL; tiles[31][8] = T.STALL; tiles[31][10] = T.STALL; tiles[31][12] = T.STALL;
        tiles[33][6] = T.STALL; tiles[33][8] = T.STALL; tiles[33][10] = T.STALL; tiles[33][12] = T.STALL;
        tiles[35][6] = T.STALL; tiles[35][8] = T.STALL;
        tiles[32][7] = T.LAMP; tiles[32][11] = T.LAMP;
        tiles[34][7] = T.LAMP; tiles[34][11] = T.LAMP;

        fill(tiles, 30, 45, 36, 54, T.STONE_FLOOR);
        tiles[31][46] = T.STALL; tiles[31][48] = T.STALL; tiles[31][50] = T.STALL; tiles[31][52] = T.STALL;
        tiles[33][46] = T.STALL; tiles[33][48] = T.STALL; tiles[33][50] = T.STALL; tiles[33][52] = T.STALL;
        tiles[35][46] = T.STALL; tiles[35][48] = T.STALL;
        tiles[32][47] = T.LAMP; tiles[32][51] = T.LAMP;
        tiles[34][47] = T.LAMP; tiles[34][51] = T.LAMP;

        placeBuilding(tiles, 14, 20, 7, 5, true);
        tiles[13][22] = T.SIGN;

        placeBuilding(tiles, 14, 33, 7, 5, true);
        tiles[13][35] = T.SIGN;

        placeBuilding(tiles, 38, 20, 6, 4);
        placeBuilding(tiles, 38, 33, 6, 4);

        tiles[19][22] = T.CRATES; tiles[19][26] = T.CRATES;
        tiles[19][35] = T.CRATES; tiles[19][39] = T.CRATES;
        tiles[42][22] = T.CRATES; tiles[42][25] = T.CRATES;
        tiles[42][35] = T.CRATES; tiles[42][38] = T.CRATES;

        for (let c = 18; c <= 25; c++) tiles[43][c] = T.FENCE;
        for (let c = 34; c <= 41; c++) tiles[43][c] = T.FENCE;

        placeGarden(tiles, 14, 5, 5, 5);
        placeGarden(tiles, 14, 50, 5, 5);

        tiles[40][10] = T.WELL; tiles[40][49] = T.WELL;

        placeTreeCluster(tiles, 2, 25, 3, 2);
        placeTreeCluster(tiles, 2, 32, 3, 2);
        placeTreeCluster(tiles, 44, 3, 3, 3);
        placeTreeCluster(tiles, 44, 54, 3, 3);
        scatter(tiles, 2, 3, 4, 12, T.FLOWERS, 0.1);
        scatter(tiles, 2, 47, 4, 56, T.FLOWERS, 0.1);
        scatter(tiles, 44, 15, 47, 28, T.FLOWERS, 0.06);
        scatter(tiles, 44, 32, 47, 45, T.FLOWERS, 0.06);

        for (let c = 20; c <= 40; c++) { tiles[H-2][c] = T.WATER; tiles[H-1][c] = T.WATER; }
        tiles[H-3][22] = T.CLIFF_TOP; tiles[H-3][23] = T.CLIFF_TOP;
        tiles[H-3][37] = T.CLIFF_TOP; tiles[H-3][38] = T.CLIFF_TOP;
        placeBridgeH(tiles, H-2, 28, 5);
        placeBridgeH(tiles, H-1, 28, 5);

        scatterVariant(tiles, W, H);
        const collision = makeCollision(tiles, W, H);

        return {
            name: 'Market District',
            width: W, height: H,
            tiles, collision,
            spawnX: 30, spawnY: 2,
            npcs: [
                { x: 9, y: 7, name: 'Item Merchant', spriteType: 'npc', color: '#ddaa33', facing: 'down', stationary: true, spriteId: 9,
                  dialogue: ["Welcome to my stall!", "I sell potions, scrolls, and more.", "Browse my wares!"], action: 'shop', route: '/inventory' },
                { x: 49, y: 7, name: 'Equipment Smith', spriteType: 'npc', color: '#887766', facing: 'down', stationary: true, spriteId: 14,
                  dialogue: ["Need better gear?", "I forge the finest business tools!", "Let me show you my crafts."], action: 'equipment', route: '/inventory' },
                { x: 9, y: 32, name: 'Fortune Teller', spriteType: 'npc', color: '#9933cc', facing: 'down', stationary: true, spriteId: 15,
                  dialogue: ["The stars foretell great success...", "But only if you make the right decisions!", "Shall I read your business fortune?"] },
                { x: 49, y: 32, name: 'Recruiter', spriteType: 'npc', color: '#3388aa', facing: 'down', stationary: true, spriteId: 10,
                  dialogue: ["Looking to expand your team?", "I can help you find the best talent!", "Visit the HR Guild for more."], action: 'hr', route: '/scenarios/Human Resources' },
                { x: 23, y: 18, name: 'Potion Brewer', spriteType: 'npc', color: '#44bb77', facing: 'down', spriteId: 8,
                  dialogue: ["My potions boost your business abilities!", "Try an Energy Elixir for longer study sessions.", "Or a Focus Potion for sharper decisions."] },
                { x: 36, y: 18, name: 'Scroll Keeper', spriteType: 'npc', color: '#bb8844', facing: 'down', spriteId: 6,
                  dialogue: ["Ancient business scrolls for sale!", "Each scroll contains wisdom from past tycoons.", "Knowledge is the greatest investment."] },
                { x: 29, y: 42, name: 'Street Performer', spriteType: 'npc', color: '#cc55aa', facing: 'up', spriteId: 12,
                  dialogue: ["Step right up! Step right up!", "I entertain the market crowds.", "A happy customer is a spending customer!"] },
                { x: 15, y: 40, name: 'Guard', spriteType: 'npc', color: '#7788aa', facing: 'right', spriteId: 3,
                  dialogue: ["I keep the peace in the market.", "Trade fairly and prosper.", "No shady deals on my watch!"] }
            ],
            transitions: [
                { x: 29, y: 0, target: 'hub', spawnX: 39, spawnY: 62 },
                { x: 30, y: 0, target: 'hub', spawnX: 40, spawnY: 62 }
            ]
        };
    }

    function placeFactory(tiles, sr, sc, w, h, hasSmoke) {
        for (let c = sc; c < sc + w; c++) {
            tiles[sr][c] = T.FACTORY_ROOF;
            tiles[sr + 1][c] = T.FACTORY_ROOF;
        }
        if (hasSmoke) {
            tiles[sr][sc + Math.floor(w / 2)] = T.SMOKESTACK;
            if (w >= 7) tiles[sr][sc + w - 2] = T.SMOKESTACK;
        }
        for (let r = sr + 2; r < sr + h; r++)
            for (let c = sc; c < sc + w; c++) tiles[r][c] = T.FACTORY_WALL;
        const dc = sc + Math.floor(w / 2);
        tiles[sr + h - 1][dc] = T.FACTORY_DOOR;
        if (w >= 5) {
            tiles[sr + 2][sc + 1] = T.FACTORY_WINDOW;
            tiles[sr + 2][sc + w - 2] = T.FACTORY_WINDOW;
        }
        if (w >= 7) {
            tiles[sr + 3][sc + 1] = T.FACTORY_WINDOW;
            tiles[sr + 3][sc + w - 2] = T.FACTORY_WINDOW;
        }
    }

    function placeRailH(tiles, r, c1, c2) {
        for (let c = c1; c <= c2; c++) tiles[r][c] = T.RAIL_H;
    }

    function placeRailV(tiles, c, r1, r2) {
        for (let r = r1; r <= r2; r++) tiles[r][c] = T.RAIL_V;
    }

    function scatterIndustrial(tiles, r1, c1, r2, c2, t, chance) {
        for (let r = r1; r <= r2; r++)
            for (let c = c1; c <= c2; c++)
                if (tiles[r][c] === T.DIRT && Math.random() < chance) tiles[r][c] = t;
    }

    function createIronBasin() {
        const W = 80;
        const H = 70;
        const tiles = [];
        for (let r = 0; r < H; r++) {
            tiles[r] = [];
            for (let c = 0; c < W; c++) tiles[r][c] = T.DIRT;
        }

        for (let c = 0; c < W; c++) { tiles[0][c] = T.MOUNTAIN; tiles[1][c] = T.MOUNTAIN; tiles[2][c] = T.MOUNTAIN_BASE; }
        for (let c = 0; c < W; c++) { tiles[3][c] = T.MOUNTAIN_BASE; }
        for (let c = 0; c < 8; c++) { tiles[3][c] = T.MOUNTAIN; tiles[4][c] = T.MOUNTAIN_BASE; }
        for (let c = W - 8; c < W; c++) { tiles[3][c] = T.MOUNTAIN; tiles[4][c] = T.MOUNTAIN_BASE; }
        for (let r = 0; r < 6; r++) { tiles[r][0] = T.MOUNTAIN; tiles[r][1] = T.MOUNTAIN; }
        for (let r = 0; r < 6; r++) { tiles[r][W-1] = T.MOUNTAIN; tiles[r][W-2] = T.MOUNTAIN; }

        for (let r = 4; r < 12; r++) { tiles[r][0] = T.PINE_TREE; tiles[r][1] = T.PINE_TREE; tiles[r][2] = T.PINE_TREE; }
        for (let r = 4; r < 12; r++) { tiles[r][W-1] = T.PINE_TREE; tiles[r][W-2] = T.PINE_TREE; tiles[r][W-3] = T.PINE_TREE; }
        for (let r = 12; r < 25; r++) { tiles[r][0] = T.PINE_TREE; tiles[r][1] = T.PINE_TREE; }
        for (let r = 12; r < 25; r++) { tiles[r][W-1] = T.PINE_TREE; tiles[r][W-2] = T.PINE_TREE; }

        placeTreeCluster(tiles, 5, 3, 4, 6);
        placeTreeCluster(tiles, 5, W - 7, 4, 6);
        placeTreeCluster(tiles, 14, 3, 3, 4);
        placeTreeCluster(tiles, 14, W - 6, 3, 4);
        for (let r = 5; r < 12; r++)
            for (let c = 3; c < 8; c++)
                if (tiles[r][c] === T.DIRT && Math.random() < 0.3) tiles[r][c] = T.PINE_TREE;
        for (let r = 5; r < 12; r++)
            for (let c = W - 8; c < W - 3; c++)
                if (tiles[r][c] === T.DIRT && Math.random() < 0.3) tiles[r][c] = T.PINE_TREE;

        for (let c = 0; c < W; c++) {
            for (let r = H - 6; r < H; r++) tiles[r][c] = T.WATER;
        }
        for (let c = 15; c < 65; c++) tiles[H - 7][c] = T.WATER;
        fill(tiles, H - 8, 10, H - 7, 14, T.DOCK);
        fill(tiles, H - 8, 20, H - 7, 30, T.DOCK);
        fill(tiles, H - 8, 35, H - 7, 45, T.DOCK);
        fill(tiles, H - 8, 50, H - 7, 60, T.DOCK);
        fill(tiles, H - 8, 65, H - 7, 70, T.DOCK);

        tiles[H - 9][12] = T.CRANE;
        tiles[H - 9][25] = T.CRANE;
        tiles[H - 9][40] = T.CRANE;
        tiles[H - 9][55] = T.CRANE;
        tiles[H - 9][68] = T.CRANE;

        fill(tiles, H - 12, 8, H - 9, 13, T.COBBLE);
        fill(tiles, H - 12, 18, H - 9, 32, T.COBBLE);
        fill(tiles, H - 12, 48, H - 9, 62, T.COBBLE);
        fill(tiles, H - 12, 67, H - 9, 72, T.COBBLE);

        placeBuilding(tiles, H - 14, 8, 6, 4);
        placeBuilding(tiles, H - 14, 18, 7, 4, true);
        placeBuilding(tiles, H - 14, 28, 5, 4);
        placeBuilding(tiles, H - 14, 48, 7, 4, true);
        placeBuilding(tiles, H - 14, 58, 6, 4);
        placeBuilding(tiles, H - 14, 67, 6, 4);

        placeFactory(tiles, 6, 12, 8, 5, true);
        placeFactory(tiles, 6, 30, 7, 5, true);
        placeFactory(tiles, 6, 45, 9, 5, true);
        placeFactory(tiles, 6, 62, 7, 5, true);

        placeFactory(tiles, 14, 20, 6, 4, false);
        placeFactory(tiles, 14, 42, 8, 5, true);

        placeFactory(tiles, 24, 8, 7, 5, true);
        placeFactory(tiles, 24, 20, 9, 6, true);
        placeFactory(tiles, 24, 44, 8, 5, true);
        placeFactory(tiles, 24, 63, 7, 5, true);

        placeFactory(tiles, 32, 18, 6, 4, false);
        placeFactory(tiles, 32, 42, 7, 4, true);
        placeFactory(tiles, 32, 63, 6, 4, false);

        placeFactory(tiles, 40, 8, 8, 5, true);
        placeFactory(tiles, 40, 20, 7, 4, false);
        placeFactory(tiles, 40, 44, 9, 5, true);
        placeFactory(tiles, 40, 63, 7, 5, true);

        placeFactory(tiles, 47, 18, 7, 5, true);
        placeFactory(tiles, 47, 44, 6, 4, false);
        placeFactory(tiles, 47, 63, 7, 5, true);

        hPath(tiles, 20, 8, 72, 3);
        hPath(tiles, 35, 8, 72, 3);
        hPath(tiles, 50, 8, 72, 3);
        vPath(tiles, 15, 6, 55, 3);
        vPath(tiles, 38, 6, 55, 3);
        vPath(tiles, 60, 6, 55, 3);

        placeRailH(tiles, 12, 8, 72);
        placeRailH(tiles, 13, 8, 72);
        placeRailH(tiles, 31, 10, 70);
        placeRailH(tiles, 46, 10, 70);

        placeRailV(tiles, 25, 13, 46);
        placeRailV(tiles, 55, 13, 46);

        tiles[13][25] = T.RAIL_CROSS; tiles[12][25] = T.RAIL_CROSS;
        tiles[13][55] = T.RAIL_CROSS; tiles[12][55] = T.RAIL_CROSS;
        tiles[31][25] = T.RAIL_CROSS; tiles[31][55] = T.RAIL_CROSS;
        tiles[46][25] = T.RAIL_CROSS; tiles[46][55] = T.RAIL_CROSS;

        fill(tiles, 25, 33, 30, 44, T.COBBLE);
        fill(tiles, 26, 34, 29, 43, T.STONE_FLOOR);
        tiles[27][38] = T.FOUNTAIN; tiles[27][39] = T.FOUNTAIN;
        tiles[28][38] = T.FOUNTAIN; tiles[28][39] = T.FOUNTAIN;
        tiles[26][34] = T.IND_LAMP; tiles[26][43] = T.IND_LAMP;
        tiles[29][34] = T.IND_LAMP; tiles[29][43] = T.IND_LAMP;
        tiles[26][36] = T.BENCH; tiles[26][41] = T.BENCH;
        tiles[29][36] = T.BENCH; tiles[29][41] = T.BENCH;

        tiles[14][15] = T.COAL_PILE; tiles[14][17] = T.COAL_PILE;
        tiles[14][63] = T.COAL_PILE; tiles[14][65] = T.COAL_PILE;
        tiles[31][10] = T.COAL_PILE; tiles[31][12] = T.COAL_PILE;
        tiles[31][68] = T.COAL_PILE; tiles[31][70] = T.COAL_PILE;
        tiles[46][10] = T.COAL_PILE; tiles[46][12] = T.COAL_PILE;

        tiles[22][10] = T.BARREL; tiles[22][12] = T.BARREL;
        tiles[22][68] = T.BARREL; tiles[22][70] = T.BARREL;
        tiles[37][15] = T.BARREL; tiles[37][17] = T.BARREL;
        tiles[37][63] = T.BARREL; tiles[37][65] = T.BARREL;

        tiles[22][30] = T.ANVIL; tiles[22][50] = T.ANVIL;
        tiles[37][30] = T.ANVIL; tiles[37][50] = T.ANVIL;

        tiles[7][20] = T.GEAR; tiles[7][40] = T.GEAR; tiles[7][60] = T.GEAR;
        tiles[25][15] = T.GEAR; tiles[25][65] = T.GEAR;
        tiles[40][20] = T.GEAR; tiles[40][60] = T.GEAR;

        for (let c = 8; c <= 13; c++) tiles[18][c] = T.IRON_FENCE;
        for (let c = 67; c <= 72; c++) tiles[18][c] = T.IRON_FENCE;
        for (let c = 8; c <= 13; c++) tiles[44][c] = T.IRON_FENCE;
        for (let c = 67; c <= 72; c++) tiles[44][c] = T.IRON_FENCE;

        tiles[12][15] = T.IND_LAMP; tiles[12][38] = T.IND_LAMP; tiles[12][60] = T.IND_LAMP;
        tiles[23][15] = T.IND_LAMP; tiles[23][65] = T.IND_LAMP;
        tiles[38][15] = T.IND_LAMP; tiles[38][38] = T.IND_LAMP; tiles[38][65] = T.IND_LAMP;
        tiles[53][15] = T.IND_LAMP; tiles[53][38] = T.IND_LAMP; tiles[53][65] = T.IND_LAMP;

        tiles[H - 10][15] = T.IND_LAMP; tiles[H - 10][25] = T.IND_LAMP;
        tiles[H - 10][40] = T.IND_LAMP; tiles[H - 10][55] = T.IND_LAMP;
        tiles[H - 10][68] = T.IND_LAMP;

        tiles[H - 11][20] = T.CRATES; tiles[H - 11][22] = T.CRATES;
        tiles[H - 11][50] = T.CRATES; tiles[H - 11][52] = T.CRATES;
        tiles[H - 11][58] = T.CRATES; tiles[H - 11][60] = T.CRATES;

        tiles[H - 11][35] = T.BARREL; tiles[H - 11][37] = T.BARREL;
        tiles[H - 11][42] = T.BARREL; tiles[H - 11][44] = T.BARREL;

        tiles[3][39] = T.DIRT; tiles[3][40] = T.DIRT;
        tiles[2][39] = T.MOUNTAIN_BASE; tiles[2][40] = T.MOUNTAIN_BASE;

        tiles[H - 7][39] = T.PORTAL; tiles[H - 7][40] = T.PORTAL;

        tiles[12][39] = T.SIGN; tiles[12][40] = T.SIGN;
        tiles[H - 9][30] = T.SIGN; tiles[H - 9][50] = T.SIGN;

        const collision = makeCollision(tiles, W, H);

        const npcs = [
            {
                x: 39, y: 27, name: 'Factory Foreman',
                spriteType: 'npc', color: '#886644', facing: 'down', stationary: true, spriteId: 0,
                dialogue: ["Welcome to The Iron Basin!", "This is the heart of industrial progress.", "Every factory here teaches you about operations, supply chains, and production.", "Speak with the specialists to learn!"],
                action: 'operations', route: '/scenarios/Operations'
            },
            {
                x: 16, y: 11, name: 'Steel Mill Supervisor',
                spriteType: 'npc', color: '#cc6633', facing: 'up', spriteId: 1,
                dialogue: ["The steel mill runs day and night.", "Managing production schedules is critical.", "One bottleneck can halt the entire operation!"],
                action: 'operations', route: '/scenarios/Operations'
            },
            {
                x: 33, y: 11, name: 'Chief Engineer',
                spriteType: 'npc', color: '#3366aa', facing: 'up', spriteId: 2,
                dialogue: ["Engineering is the backbone of industry.", "I can teach you about process optimization.", "Efficiency separates the profitable from the bankrupt."],
                action: 'strategy', route: '/scenarios/Strategy'
            },
            {
                x: 49, y: 11, name: 'Power Plant Manager',
                spriteType: 'npc', color: '#aa4444', facing: 'up', spriteId: 3,
                dialogue: ["Steam power drives our factories!", "Energy management is a crucial business skill.", "Too much waste means lost profits."],
                action: 'operations', route: '/scenarios/Operations'
            },
            {
                x: 65, y: 11, name: 'Mining Foreman',
                spriteType: 'npc', color: '#665544', facing: 'up', spriteId: 4,
                dialogue: ["The mines supply our raw materials.", "Resource extraction requires careful planning.", "Safety and efficiency must go hand in hand."],
                action: 'operations', route: '/scenarios/Operations'
            },
            {
                x: 12, y: 27, name: 'Accountant',
                spriteType: 'npc', color: '#334455', facing: 'right', spriteId: 5,
                dialogue: ["Every penny counts in this business!", "I track all the factory finances.", "Profit margins, cost analysis, capital allocation...", "Let me show you the books."],
                action: 'finance', route: '/scenarios/Finance'
            },
            {
                x: 68, y: 27, name: 'Logistics Manager',
                spriteType: 'npc', color: '#558844', facing: 'left', spriteId: 6,
                dialogue: ["Moving goods from factory to market...", "That's what logistics is all about.", "Rail, ship, or cart - each has its trade-offs."],
                action: 'operations', route: '/scenarios/Operations'
            },
            {
                x: 23, y: 37, name: 'Inventor',
                spriteType: 'npc', color: '#997733', facing: 'down', spriteId: 7,
                dialogue: ["I've been working on a new steam engine design!", "Innovation drives industry forward.", "Would you like to learn about product development?"],
                action: 'strategy', route: '/scenarios/Strategy'
            },
            {
                x: 50, y: 37, name: 'Union Representative',
                spriteType: 'npc', color: '#884444', facing: 'down', spriteId: 8,
                dialogue: ["Workers' rights matter!", "Managing your workforce fairly leads to better outcomes.", "Happy workers are productive workers."],
                action: 'hr', route: '/scenarios/Human Resources'
            },
            {
                x: 39, y: 53, name: 'Railroad Engineer',
                spriteType: 'npc', color: '#445566', facing: 'up', spriteId: 9,
                dialogue: ["The railroad connects all our operations.", "Scheduling trains is like managing any supply chain.", "Timing and coordination are everything!"],
                action: 'operations', route: '/scenarios/Operations'
            },
            {
                x: 25, y: H - 10, name: 'Dock Master',
                spriteType: 'npc', color: '#446688', facing: 'up', stationary: true, spriteId: 10,
                dialogue: ["Ships come and go with raw materials and finished goods.", "International trade is the lifeblood of industry.", "Let me teach you about import/export management."],
                action: 'marketing', route: '/scenarios/Marketing'
            },
            {
                x: 55, y: H - 10, name: 'Shipping Clerk',
                spriteType: 'npc', color: '#668844', facing: 'up', stationary: true, spriteId: 11,
                dialogue: ["Tracking shipments, managing inventory...", "The paperwork never ends!", "But good record-keeping prevents costly mistakes."],
                action: 'finance', route: '/scenarios/Finance'
            },
            {
                x: 38, y: 15, name: 'Safety Inspector',
                spriteType: 'npc', color: '#cc8833', facing: 'down', spriteId: 12,
                dialogue: ["Safety regulations protect workers AND your bottom line.", "An accident shuts down production for days.", "Investing in safety pays for itself."],
                action: 'legal', route: '/scenarios/Legal'
            },
            {
                x: 15, y: 37, name: 'Blacksmith',
                spriteType: 'npc', color: '#554433', facing: 'right', spriteId: 13,
                dialogue: ["I forge the tools that keep the factories running.", "Quality equipment means quality output.", "Let me show you my finest work."],
                action: 'shop', route: '/inventory'
            },
            {
                x: 65, y: 37, name: 'Merchant',
                spriteType: 'npc', color: '#887744', facing: 'left', spriteId: 14,
                dialogue: ["I trade goods between The Iron Basin and other regions.", "Buy low, sell high - the oldest rule in business!", "Check my wares, you might find something useful."],
                action: 'shop', route: '/inventory'
            },
            {
                x: 39, y: 38, name: 'Bank Manager',
                spriteType: 'npc', color: '#223344', facing: 'down', stationary: true, spriteId: 15,
                dialogue: ["The Industrial Bank finances the growth of this basin.", "Loans, investments, interest rates...", "Understanding capital is essential for any tycoon.", "Come discuss your financial strategy."],
                action: 'finance', route: '/scenarios/Finance'
            }
        ];

        return {
            name: 'The Iron Basin',
            width: W, height: H,
            tiles, collision,
            spawnX: 39, spawnY: 25,
            npcs,
            transitions: [
                { x: 39, y: 3, target: 'hub', spawnX: 39, spawnY: 62 },
                { x: 40, y: 3, target: 'hub', spawnX: 40, spawnY: 62 },
                { x: 39, y: H - 7, target: 'hub', spawnX: 39, spawnY: 5 },
                { x: 40, y: H - 7, target: 'hub', spawnX: 40, spawnY: 5 }
            ],
            interactables: [
                { x: 39, y: 12, name: 'Factory Notice', dialogue: ["THE IRON BASIN - Industrial District", "Master the art of manufacturing and trade.", "Visit each factory to learn different business skills!"] },
                { x: 40, y: 12, name: 'Production Board', dialogue: ["Daily Production Targets", "Steel Mill: 500 tons", "Textile Factory: 2000 yards", "Assembly Plant: 150 units"] },
                { x: 30, y: H - 9, name: 'Shipping Schedule', dialogue: ["HARBOR SHIPPING SCHEDULE", "Morning: Raw materials arrive from overseas.", "Afternoon: Finished goods depart.", "Evening: Maintenance and inventory."] },
                { x: 50, y: H - 9, name: 'Trade Manifest', dialogue: ["TRADE MANIFEST", "Exports: Steel, Textiles, Machinery", "Imports: Coal, Lumber, Cotton", "Balance: Favorable this quarter."] }
            ]
        };
    }

    function getMap(name) {
        switch(name) {
            case 'hub': return createHubTown();
            case 'market_district': return createMarketDistrict();
            case 'iron_basin': return createIronBasin();
            default: return createHubTown();
        }
    }

    return { getMap, T };
})();
