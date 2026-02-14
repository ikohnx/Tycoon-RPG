const RPGMaps = (function() {

    const T = {
        EMPTY: 0, GRASS: 1, PATH: 2, WATER: 3,
        WALL: 4, WALL_TOP: 5, ROOF: 6, DOOR: 7,
        WINDOW: 8, TREE: 9, FLOWERS: 10, WOOD_FLOOR: 11,
        SIGN: 12, SAND: 13, STONE_FLOOR: 14, HEDGE: 15,
        CHEST: 16, PORTAL: 17, FOUNTAIN: 18, LAMP: 19,
        STALL: 20, BENCH: 21, WELL: 22, CRATES: 23,
        FIREPLACE: 24, BOOKSHELF: 25,
        CLIFF: 26, CLIFF_TOP: 27, WATERFALL: 28, ROCK: 29
    };

    function createHubTown() {
        const W = 40;
        const H = 36;

        const tiles = [];
        for (let r = 0; r < H; r++) {
            tiles[r] = [];
            for (let c = 0; c < W; c++) tiles[r][c] = T.GRASS;
        }

        for (let c = 0; c < W; c++) { tiles[0][c] = T.TREE; tiles[1][c] = T.TREE; tiles[H-1][c] = T.TREE; tiles[H-2][c] = T.TREE; }
        for (let r = 0; r < H; r++) { tiles[r][0] = T.TREE; tiles[r][1] = T.TREE; tiles[r][W-1] = T.TREE; tiles[r][W-2] = T.TREE; }

        for (let r = 2; r < H - 2; r++) {
            for (let c = 18; c <= 21; c++) tiles[r][c] = T.PATH;
        }
        for (let c = 2; c < W - 2; c++) {
            for (let r = 16; r <= 19; r++) tiles[r][c] = T.PATH;
        }

        for (let r = 8; r <= 12; r++) { tiles[r][7] = T.PATH; tiles[r][8] = T.PATH; }
        for (let r = 8; r <= 12; r++) { tiles[r][31] = T.PATH; tiles[r][32] = T.PATH; }
        for (let r = 22; r <= 26; r++) { tiles[r][7] = T.PATH; tiles[r][8] = T.PATH; }
        for (let r = 22; r <= 26; r++) { tiles[r][31] = T.PATH; tiles[r][32] = T.PATH; }
        for (let c = 7; c <= 18; c++) { tiles[10][c] = T.PATH; tiles[11][c] = T.PATH; }
        for (let c = 21; c <= 32; c++) { tiles[10][c] = T.PATH; tiles[11][c] = T.PATH; }
        for (let c = 7; c <= 18; c++) { tiles[24][c] = T.PATH; tiles[25][c] = T.PATH; }
        for (let c = 21; c <= 32; c++) { tiles[24][c] = T.PATH; tiles[25][c] = T.PATH; }

        for (let r = 14; r <= 21; r++) {
            for (let c = 16; c <= 23; c++) tiles[r][c] = T.STONE_FLOOR;
        }

        tiles[17][19] = T.FOUNTAIN;
        tiles[17][20] = T.FOUNTAIN;
        tiles[18][19] = T.FOUNTAIN;
        tiles[18][20] = T.FOUNTAIN;

        tiles[14][18] = T.LAMP; tiles[14][21] = T.LAMP;
        tiles[21][18] = T.LAMP; tiles[21][21] = T.LAMP;

        tiles[15][16] = T.FLOWERS; tiles[15][23] = T.FLOWERS;
        tiles[20][16] = T.FLOWERS; tiles[20][23] = T.FLOWERS;
        tiles[14][16] = T.BENCH; tiles[14][23] = T.BENCH;
        tiles[21][16] = T.BENCH; tiles[21][23] = T.BENCH;

        function placeBuilding(sr, sc, w, h, hasTwoWindows) {
            for (let c = sc; c < sc + w; c++) {
                tiles[sr][c] = T.ROOF;
                tiles[sr + 1][c] = T.ROOF;
            }
            for (let r = sr + 2; r < sr + h; r++) {
                for (let c = sc; c < sc + w; c++) tiles[r][c] = T.WALL;
            }
            const dc = sc + Math.floor(w / 2);
            tiles[sr + h - 1][dc] = T.DOOR;
            if (w >= 5) {
                tiles[sr + 2][sc + 1] = T.WINDOW;
                tiles[sr + 2][sc + w - 2] = T.WINDOW;
            }
            if (hasTwoWindows && w >= 7) {
                tiles[sr + 3][sc + 1] = T.WINDOW;
                tiles[sr + 3][sc + w - 2] = T.WINDOW;
            }
        }

        placeBuilding(4, 4, 6, 5);
        tiles[3][5] = T.SIGN; tiles[3][8] = T.SIGN;
        tiles[9][5] = T.CRATES; tiles[9][9] = T.CRATES;

        placeBuilding(4, 12, 5, 5);
        tiles[3][13] = T.FLOWERS; tiles[3][15] = T.FLOWERS;

        placeBuilding(4, 24, 5, 5);
        tiles[3][25] = T.FLOWERS; tiles[3][27] = T.FLOWERS;

        placeBuilding(4, 31, 6, 5, true);
        tiles[3][32] = T.SIGN; tiles[3][35] = T.SIGN;
        tiles[9][32] = T.CRATES; tiles[9][36] = T.CRATES;

        placeBuilding(22, 4, 6, 5);
        tiles[27][5] = T.CRATES; tiles[27][9] = T.CRATES;

        placeBuilding(22, 12, 5, 5);

        placeBuilding(22, 24, 5, 5);

        placeBuilding(22, 31, 6, 5);
        tiles[27][32] = T.CRATES;

        for (let c = 16; c <= 23; c++) {
            tiles[4][c] = T.WALL_TOP;
            tiles[5][c] = T.WALL;
            tiles[6][c] = T.WALL;
        }
        tiles[6][19] = T.DOOR; tiles[6][20] = T.DOOR;
        tiles[5][17] = T.WINDOW; tiles[5][22] = T.WINDOW;
        tiles[3][17] = T.SIGN; tiles[3][22] = T.SIGN;

        tiles[10][5] = T.LAMP; tiles[10][9] = T.LAMP;
        tiles[10][30] = T.LAMP; tiles[10][34] = T.LAMP;
        tiles[24][5] = T.LAMP; tiles[24][9] = T.LAMP;
        tiles[24][30] = T.LAMP; tiles[24][34] = T.LAMP;

        tiles[16][6] = T.STALL; tiles[16][8] = T.STALL;
        tiles[16][31] = T.STALL; tiles[16][33] = T.STALL;
        tiles[19][6] = T.STALL; tiles[19][8] = T.STALL;
        tiles[19][31] = T.STALL; tiles[19][33] = T.STALL;

        tiles[28][12] = T.WELL;
        tiles[28][27] = T.WELL;

        for (let c = 10; c <= 12; c++) { tiles[30][c] = T.WATER; tiles[31][c] = T.WATER; tiles[32][c] = T.WATER; }
        for (let c = 27; c <= 29; c++) { tiles[30][c] = T.WATER; tiles[31][c] = T.WATER; tiles[32][c] = T.WATER; }

        tiles[29][10] = T.CLIFF_TOP; tiles[29][11] = T.CLIFF_TOP; tiles[29][12] = T.CLIFF_TOP;
        tiles[29][27] = T.CLIFF_TOP; tiles[29][28] = T.CLIFF_TOP; tiles[29][29] = T.CLIFF_TOP;
        tiles[33][10] = T.ROCK; tiles[33][12] = T.ROCK;
        tiles[33][27] = T.ROCK; tiles[33][29] = T.ROCK;
        tiles[32][9] = T.CLIFF; tiles[32][13] = T.CLIFF;
        tiles[32][26] = T.CLIFF; tiles[32][30] = T.CLIFF;

        tiles[30][14] = T.FLOWERS; tiles[30][15] = T.FLOWERS;
        tiles[31][14] = T.FLOWERS; tiles[31][15] = T.FLOWERS;
        tiles[30][24] = T.FLOWERS; tiles[30][25] = T.FLOWERS;
        tiles[31][24] = T.FLOWERS; tiles[31][25] = T.FLOWERS;

        tiles[12][14] = T.FLOWERS; tiles[12][15] = T.FLOWERS;
        tiles[12][24] = T.FLOWERS; tiles[12][25] = T.FLOWERS;
        tiles[13][14] = T.HEDGE; tiles[13][15] = T.HEDGE;
        tiles[13][24] = T.HEDGE; tiles[13][25] = T.HEDGE;

        for (let r = 3; r <= 5; r++) { tiles[r][3] = T.TREE; tiles[r][10] = T.TREE; tiles[r][23] = T.TREE; tiles[r][30] = T.TREE; tiles[r][37] = T.TREE; }

        tiles[H-2][19] = T.PORTAL; tiles[H-2][20] = T.PORTAL;
        tiles[H-1][19] = T.PORTAL; tiles[H-1][20] = T.PORTAL;

        tiles[0][19] = T.GRASS; tiles[0][20] = T.GRASS;
        tiles[1][19] = T.GRASS; tiles[1][20] = T.GRASS;

        const collision = [];
        for (let r = 0; r < H; r++) {
            collision[r] = [];
            for (let c = 0; c < W; c++) {
                const t = tiles[r][c];
                collision[r][c] = [T.TREE, T.WALL, T.WALL_TOP, T.ROOF, T.WINDOW, T.WATER, T.HEDGE, T.CHEST, T.SIGN, T.FOUNTAIN, T.STALL, T.WELL, T.LAMP, T.BENCH, T.CRATES, T.FIREPLACE, T.BOOKSHELF, T.CLIFF, T.CLIFF_TOP, T.WATERFALL, T.ROCK].includes(t) ? 1 : 0;
            }
        }

        const npcs = [
            {
                x: 7, y: 9, name: 'Marketing Maven',
                spriteType: 'npc', color: '#cc4488', facing: 'down',
                dialogue: ["Welcome to the Marketing Guild!", "I specialize in branding, campaigns, and customer acquisition.", "Let me show you how to boost your company's reach."],
                action: 'marketing', route: '/scenarios/Marketing'
            },
            {
                x: 14, y: 9, name: 'Finance Director',
                spriteType: 'npc', color: '#44aa44', facing: 'down',
                dialogue: ["The Treasury is just behind me.", "Budgets, investments, financial forecasting... I manage it all.", "Let's make sure your books are balanced!"],
                action: 'finance', route: '/scenarios/Finance'
            },
            {
                x: 19, y: 8, name: 'Town Elder',
                spriteType: 'npc', color: '#8866aa', facing: 'down', stationary: true,
                dialogue: ["Welcome to Business Town, young entrepreneur!", "Each building here represents a different business discipline.", "Speak with the guild masters to learn and grow your empire.", "Use the arrow keys to move and press Enter or Space to talk."],
                action: 'tutorial', route: '/tutorial'
            },
            {
                x: 26, y: 9, name: 'Operations Chief',
                spriteType: 'npc', color: '#dd8833', facing: 'down',
                dialogue: ["I oversee the operations and logistics.", "Supply chains, inventory, scheduling...", "Come learn how to streamline your business!"],
                action: 'operations', route: '/scenarios/Operations'
            },
            {
                x: 33, y: 9, name: 'HR Manager',
                spriteType: 'npc', color: '#33aadd', facing: 'down',
                dialogue: ["People are any company's greatest asset!", "Hiring, training, team dynamics...", "Let me teach you to build an amazing team."],
                action: 'hr', route: '/scenarios/Human Resources'
            },
            {
                x: 7, y: 25, name: 'Legal Counsel',
                spriteType: 'npc', color: '#aa6633', facing: 'up',
                dialogue: ["Contracts, compliance, intellectual property...", "The law can be complex, but I'll guide you.", "Protect your business from legal pitfalls!"],
                action: 'legal', route: '/scenarios/Legal'
            },
            {
                x: 14, y: 25, name: 'Strategy Advisor',
                spriteType: 'npc', color: '#8844cc', facing: 'up',
                dialogue: ["Strategy is the art of seeing the big picture.", "Market analysis, competitive positioning, long-term planning...", "Let me sharpen your strategic thinking!"],
                action: 'strategy', route: '/scenarios/Strategy'
            },
            {
                x: 26, y: 25, name: 'Merchant',
                spriteType: 'npc', color: '#ccaa33', facing: 'up',
                dialogue: ["Looking to buy or sell? You've come to the right place!", "I have equipment, items, and special offers!", "Step into my shop to browse the inventory."],
                action: 'shop', route: '/inventory'
            },
            {
                x: 33, y: 25, name: 'Guild Master',
                spriteType: 'npc', color: '#cc3355', facing: 'up',
                dialogue: ["The Business Guild offers challenges and competitions.", "Prove your skills against other entrepreneurs!", "Are you ready for the next challenge?"],
                action: 'guild', route: '/dashboard'
            },
            {
                x: 19, y: 15, name: 'Mayor',
                spriteType: 'npc', color: '#dddd44', facing: 'down', stationary: true,
                dialogue: ["I am the Mayor of Business Town.", "This plaza is the heart of our community.", "All paths lead here. Visit the guilds to learn!", "Your progress is tracked in the Command Center."],
                action: 'hub', route: '/hub'
            },
            {
                x: 7, y: 17, name: 'Wandering Trader',
                spriteType: 'npc', color: '#55bb88', facing: 'right',
                dialogue: ["I travel between worlds collecting rare goods.", "Sometimes the market stalls have special deals!", "Check back often for new stock."]
            },
            {
                x: 33, y: 17, name: 'Courier',
                spriteType: 'npc', color: '#bb5555', facing: 'left',
                dialogue: ["I deliver messages and daily missions.", "Check your mission board regularly!", "There are always new opportunities."]
            }
        ];

        return {
            name: 'Business Town',
            width: W, height: H,
            tiles, collision,
            spawnX: 19, spawnY: 12,
            npcs,
            transitions: [
                { x: 19, y: 0, target: 'world_map' },
                { x: 20, y: 0, target: 'world_map' },
                { x: 19, y: H - 1, target: 'market_district', spawnX: 15, spawnY: 2 },
                { x: 20, y: H - 1, target: 'market_district', spawnX: 16, spawnY: 2 }
            ],
            interactables: [
                { x: 17, y: 3, name: 'Town Notice', dialogue: ["Business Town Notice Board", "Visit each guild master to learn business skills.", "Complete challenges to earn gold and reputation!"] },
                { x: 22, y: 3, name: 'Town Crest', dialogue: ["The crest of Business Town.", "Founded by entrepreneurs, for entrepreneurs."] }
            ]
        };
    }

    function createMarketDistrict() {
        const W = 30;
        const H = 24;
        const tiles = [];
        for (let r = 0; r < H; r++) {
            tiles[r] = [];
            for (let c = 0; c < W; c++) tiles[r][c] = T.GRASS;
        }

        for (let c = 0; c < W; c++) { tiles[0][c] = T.TREE; tiles[H-1][c] = T.TREE; }
        for (let r = 0; r < H; r++) { tiles[r][0] = T.TREE; tiles[r][W-1] = T.TREE; }

        for (let r = 1; r < H - 1; r++) { tiles[r][14] = T.PATH; tiles[r][15] = T.PATH; }
        for (let c = 1; c < W - 1; c++) { tiles[11][c] = T.PATH; tiles[12][c] = T.PATH; }

        tiles[0][14] = T.GRASS; tiles[0][15] = T.GRASS;
        tiles[1][14] = T.PATH; tiles[1][15] = T.PATH;

        for (let r = 4; r <= 9; r++) {
            for (let c = 3; c <= 8; c++) tiles[r][c] = T.STONE_FLOOR;
        }
        for (let r = 4; r <= 9; r++) {
            for (let c = 21; c <= 26; c++) tiles[r][c] = T.STONE_FLOOR;
        }
        for (let r = 14; r <= 19; r++) {
            for (let c = 3; c <= 8; c++) tiles[r][c] = T.STONE_FLOOR;
        }
        for (let r = 14; r <= 19; r++) {
            for (let c = 21; c <= 26; c++) tiles[r][c] = T.STONE_FLOOR;
        }

        tiles[5][4] = T.STALL; tiles[5][6] = T.STALL;
        tiles[7][4] = T.STALL; tiles[7][6] = T.STALL;
        tiles[5][22] = T.STALL; tiles[5][24] = T.STALL;
        tiles[7][22] = T.STALL; tiles[7][24] = T.STALL;
        tiles[15][4] = T.STALL; tiles[15][6] = T.STALL;
        tiles[17][4] = T.STALL; tiles[17][6] = T.STALL;
        tiles[15][22] = T.STALL; tiles[15][24] = T.STALL;
        tiles[17][22] = T.STALL; tiles[17][24] = T.STALL;

        tiles[6][5] = T.LAMP; tiles[6][25] = T.LAMP;
        tiles[16][5] = T.LAMP; tiles[16][25] = T.LAMP;

        tiles[8][3] = T.CRATES; tiles[8][8] = T.CRATES;
        tiles[18][3] = T.CRATES; tiles[18][8] = T.CRATES;
        tiles[8][21] = T.CRATES; tiles[8][26] = T.CRATES;
        tiles[18][21] = T.CRATES; tiles[18][26] = T.CRATES;

        tiles[3][10] = T.FLOWERS; tiles[3][11] = T.FLOWERS;
        tiles[3][18] = T.FLOWERS; tiles[3][19] = T.FLOWERS;
        tiles[20][10] = T.FLOWERS; tiles[20][11] = T.FLOWERS;
        tiles[20][18] = T.FLOWERS; tiles[20][19] = T.FLOWERS;

        const collision = [];
        for (let r = 0; r < H; r++) {
            collision[r] = [];
            for (let c = 0; c < W; c++) {
                const t = tiles[r][c];
                collision[r][c] = [T.TREE, T.WALL, T.WALL_TOP, T.ROOF, T.WINDOW, T.WATER, T.HEDGE, T.STALL, T.LAMP, T.BENCH, T.SIGN, T.FOUNTAIN, T.WELL, T.CHEST, T.CRATES, T.FIREPLACE, T.BOOKSHELF].includes(t) ? 1 : 0;
            }
        }

        return {
            name: 'Market District',
            width: W, height: H,
            tiles, collision,
            spawnX: 15, spawnY: 2,
            npcs: [
                { x: 5, y: 6, name: 'Item Merchant', spriteType: 'npc', color: '#ddaa33', facing: 'down', stationary: true,
                  dialogue: ["Welcome to my stall!", "I sell potions, scrolls, and more.", "Browse my wares!"], action: 'shop', route: '/inventory' },
                { x: 23, y: 6, name: 'Equipment Smith', spriteType: 'npc', color: '#887766', facing: 'down', stationary: true,
                  dialogue: ["Need better gear?", "I forge the finest business tools!", "Let me show you my crafts."], action: 'equipment', route: '/inventory' },
                { x: 5, y: 16, name: 'Fortune Teller', spriteType: 'npc', color: '#9933cc', facing: 'down', stationary: true,
                  dialogue: ["The stars foretell great success...", "But only if you make the right decisions!", "Shall I read your business fortune?"] },
                { x: 23, y: 16, name: 'Recruiter', spriteType: 'npc', color: '#3388aa', facing: 'down', stationary: true,
                  dialogue: ["Looking to expand your team?", "I can help you find the best talent!", "Visit the HR Guild for more."], action: 'hr', route: '/scenarios/Human Resources' }
            ],
            transitions: [
                { x: 14, y: 0, target: 'hub', spawnX: 19, spawnY: 33 },
                { x: 15, y: 0, target: 'hub', spawnX: 20, spawnY: 33 }
            ]
        };
    }

    function getMap(name) {
        switch(name) {
            case 'hub': return createHubTown();
            case 'market_district': return createMarketDistrict();
            default: return createHubTown();
        }
    }

    return { getMap, T };
})();
