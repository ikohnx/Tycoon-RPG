const RPGMaps = (function() {

    const T = {
        EMPTY: 0, GRASS: 1, PATH: 2, WATER: 3,
        WALL: 4, WALL_TOP: 5, ROOF: 6, DOOR: 7,
        WINDOW: 8, TREE: 9, FLOWERS: 10, WOOD_FLOOR: 11,
        SIGN: 12, SAND: 13, STONE_FLOOR: 14, HEDGE: 15,
        CHEST: 16, PORTAL: 17, FOUNTAIN: 18, LAMP: 19,
        STALL: 20, BENCH: 21, WELL: 22
    };

    function createHubTown() {
        const W = 34;
        const H = 30;

        const tiles = [];
        for (let r = 0; r < H; r++) {
            tiles[r] = [];
            for (let c = 0; c < W; c++) {
                tiles[r][c] = T.GRASS;
            }
        }

        for (let c = 0; c < W; c++) { tiles[0][c] = T.TREE; tiles[1][c] = T.TREE; tiles[H-1][c] = T.TREE; tiles[H-2][c] = T.TREE; }
        for (let r = 0; r < H; r++) { tiles[r][0] = T.TREE; tiles[r][1] = T.TREE; tiles[r][W-1] = T.TREE; tiles[r][W-2] = T.TREE; }

        tiles[0][16] = T.GRASS; tiles[0][17] = T.GRASS;
        tiles[1][16] = T.GRASS; tiles[1][17] = T.GRASS;

        for (let r = 3; r <= H - 4; r++) {
            for (let c = 14; c <= 19; c++) tiles[r][c] = T.PATH;
        }
        for (let c = 3; c <= W - 4; c++) {
            for (let r = 13; r <= 16; r++) tiles[r][c] = T.PATH;
        }

        for (let c = 5; c <= 8; c++) {
            for (let r = 8; r <= 10; r++) tiles[r][c] = T.PATH;
        }
        for (let c = 25; c <= 28; c++) {
            for (let r = 8; r <= 10; r++) tiles[r][c] = T.PATH;
        }
        for (let c = 5; c <= 8; c++) {
            for (let r = 19; r <= 21; r++) tiles[r][c] = T.PATH;
        }
        for (let c = 25; c <= 28; c++) {
            for (let r = 19; r <= 21; r++) tiles[r][c] = T.PATH;
        }

        for (let c = 14; c <= 19; c++) {
            for (let r = 10; r <= 13; r++) tiles[r][c] = T.STONE_FLOOR;
        }
        for (let c = 13; c <= 20; c++) {
            for (let r = 11; r <= 12; r++) tiles[r][c] = T.STONE_FLOOR;
        }

        tiles[11][16] = T.FOUNTAIN;
        tiles[11][17] = T.FOUNTAIN;
        tiles[12][16] = T.FOUNTAIN;
        tiles[12][17] = T.FOUNTAIN;

        function placeBuilding(startR, startC, w, h) {
            for (let c = startC; c < startC + w; c++) {
                tiles[startR][c] = T.ROOF;
                tiles[startR + 1][c] = T.ROOF;
            }
            for (let r = startR + 2; r < startR + h; r++) {
                for (let c = startC; c < startC + w; c++) {
                    tiles[r][c] = T.WALL;
                }
            }
            if (w >= 5) {
                tiles[startR + 2][startC + 1] = T.WINDOW;
                tiles[startR + 2][startC + w - 2] = T.WINDOW;
            }
            const doorC = startC + Math.floor(w / 2);
            tiles[startR + h - 1][doorC] = T.DOOR;
        }

        placeBuilding(3, 3, 6, 5);
        placeBuilding(3, 10, 5, 5);

        placeBuilding(3, 22, 5, 5);
        placeBuilding(3, 28, 5, 5);

        placeBuilding(18, 3, 6, 5);
        placeBuilding(18, 10, 5, 5);

        placeBuilding(18, 22, 5, 5);
        placeBuilding(18, 28, 5, 5);

        for (let c = 13; c <= 20; c++) {
            tiles[3][c] = T.WALL_TOP;
            tiles[4][c] = T.WALL;
            tiles[5][c] = T.WALL;
        }
        tiles[5][16] = T.DOOR; tiles[5][17] = T.DOOR;
        tiles[4][14] = T.WINDOW; tiles[4][19] = T.WINDOW;

        tiles[9][5] = T.LAMP;
        tiles[9][8] = T.LAMP;
        tiles[9][25] = T.LAMP;
        tiles[9][28] = T.LAMP;
        tiles[20][5] = T.LAMP;
        tiles[20][8] = T.LAMP;
        tiles[20][25] = T.LAMP;
        tiles[20][28] = T.LAMP;

        tiles[13][5] = T.STALL;
        tiles[13][7] = T.STALL;
        tiles[13][26] = T.STALL;
        tiles[13][28] = T.STALL;

        tiles[15][5] = T.BENCH;
        tiles[15][28] = T.BENCH;

        tiles[9][16] = T.SIGN;
        tiles[9][17] = T.SIGN;

        tiles[15][11] = T.FLOWERS;
        tiles[15][12] = T.FLOWERS;
        tiles[15][21] = T.FLOWERS;
        tiles[15][22] = T.FLOWERS;
        tiles[10][11] = T.FLOWERS;
        tiles[10][12] = T.FLOWERS;
        tiles[10][21] = T.FLOWERS;
        tiles[10][22] = T.FLOWERS;

        tiles[8][3] = T.FLOWERS;
        tiles[8][8] = T.FLOWERS;
        tiles[8][25] = T.FLOWERS;
        tiles[8][30] = T.FLOWERS;
        tiles[22][3] = T.FLOWERS;
        tiles[22][8] = T.FLOWERS;
        tiles[22][25] = T.FLOWERS;
        tiles[22][30] = T.FLOWERS;

        tiles[24][10] = T.WELL;
        tiles[24][23] = T.WELL;

        for (let c = 7; c <= 9; c++) {
            tiles[25][c] = T.WATER;
            tiles[26][c] = T.WATER;
        }
        for (let c = 24; c <= 26; c++) {
            tiles[25][c] = T.WATER;
            tiles[26][c] = T.WATER;
        }

        tiles[H-2][16] = T.PORTAL;
        tiles[H-2][17] = T.PORTAL;
        tiles[H-1][16] = T.PORTAL;
        tiles[H-1][17] = T.PORTAL;

        const collision = [];
        for (let r = 0; r < H; r++) {
            collision[r] = [];
            for (let c = 0; c < W; c++) {
                const t = tiles[r][c];
                collision[r][c] = [T.TREE, T.WALL, T.WALL_TOP, T.ROOF, T.WINDOW, T.WATER, T.HEDGE, T.CHEST, T.SIGN, T.FOUNTAIN, T.STALL, T.WELL, T.LAMP, T.BENCH].includes(t) ? 1 : 0;
            }
        }

        const npcs = [
            {
                x: 6, y: 9, name: 'Marketing Maven',
                spriteType: 'npc', color: '#cc4488',
                facing: 'down',
                dialogue: [
                    "Welcome to the Marketing Guild!",
                    "I specialize in branding, campaigns, and customer acquisition.",
                    "Let me show you how to boost your company's reach."
                ],
                action: 'marketing', route: '/scenarios/Marketing'
            },
            {
                x: 12, y: 9, name: 'Finance Director',
                spriteType: 'npc', color: '#44aa44',
                facing: 'down',
                dialogue: [
                    "The Treasury is just behind me.",
                    "Budgets, investments, financial forecasting... I manage it all.",
                    "Let's make sure your books are balanced!"
                ],
                action: 'finance', route: '/scenarios/Finance'
            },
            {
                x: 16, y: 7, name: 'Town Elder',
                spriteType: 'npc', color: '#8866aa',
                facing: 'down', stationary: true,
                dialogue: [
                    "Welcome to Business Town, young entrepreneur!",
                    "Each building here represents a different business discipline.",
                    "Speak with the guild masters to learn and grow your empire.",
                    "Use the arrow keys to move, and press Enter to interact."
                ],
                action: 'tutorial', route: '/tutorial'
            },
            {
                x: 24, y: 9, name: 'Operations Chief',
                spriteType: 'npc', color: '#dd8833',
                facing: 'down',
                dialogue: [
                    "The Operations Center stands behind me.",
                    "Supply chains, logistics, scheduling... I keep it all running.",
                    "Ready to optimize your business processes?"
                ],
                action: 'operations', route: '/scenarios/Operations'
            },
            {
                x: 30, y: 9, name: 'Legal Counsel',
                spriteType: 'npc', color: '#5577bb',
                facing: 'down',
                dialogue: [
                    "Greetings. The Law Office is right here.",
                    "Contracts, regulations, compliance... all essential foundations.",
                    "Shall we review your legal standing?"
                ],
                action: 'legal', route: '/scenarios/Legal'
            },
            {
                x: 6, y: 23, name: 'HR Manager',
                spriteType: 'npc', color: '#ee6655',
                facing: 'up',
                dialogue: [
                    "Welcome to the HR Department!",
                    "Building a great team is the key to any successful venture.",
                    "Let me teach you about hiring, management, and team dynamics."
                ],
                action: 'hr', route: '/scenarios/Human Resources'
            },
            {
                x: 12, y: 23, name: 'Strategy Advisor',
                spriteType: 'npc', color: '#aaaa33',
                facing: 'up',
                dialogue: [
                    "Strategy is everything in business!",
                    "Competition analysis, market positioning, long-term planning...",
                    "Ready to think like a CEO?"
                ],
                action: 'strategy', route: '/scenarios/Strategy'
            },
            {
                x: 24, y: 23, name: 'Shop Keeper',
                spriteType: 'npc', color: '#bb8844',
                facing: 'up',
                dialogue: [
                    "Welcome to my shop, traveler!",
                    "I sell equipment and supplies to help on your journey.",
                    "Care to browse my finest wares?"
                ],
                action: 'shop', route: '/shop'
            },
            {
                x: 30, y: 23, name: 'Arena Champion',
                spriteType: 'npc', color: '#cc2222',
                facing: 'up',
                dialogue: [
                    "The Battle Arena awaits, challenger!",
                    "Only the sharpest business minds survive here.",
                    "Do you have what it takes to compete?"
                ],
                action: 'battle', route: '/battle_arena'
            },
            {
                x: 14, y: 14, name: 'Command Officer',
                spriteType: 'npc', color: '#4488cc',
                facing: 'right', stationary: true,
                dialogue: [
                    "This is the Command Center.",
                    "Monitor your company's resources, view reports, and plan strategy.",
                    "Your dashboard has the latest intel."
                ],
                action: 'command_center', route: '/dashboard'
            },
            {
                x: 19, y: 14, name: 'Quest Master',
                spriteType: 'npc', color: '#996633',
                facing: 'left', stationary: true,
                dialogue: [
                    "The Quest Board has daily missions and challenges!",
                    "Complete them for bonus rewards and experience.",
                    "New assignments arrive every day. Check back often!"
                ],
                action: 'quests', route: '/daily_missions'
            }
        ];

        const interactables = [
            {
                x: 16, y: 9, name: 'Town Notice Board',
                dialogue: [
                    "== BUSINESS TOWN NOTICE BOARD ==",
                    "Explore the town and speak with the guild masters.",
                    "Each building houses a different discipline.",
                    "Visit the plaza fountain for a moment of peace."
                ],
            },
            {
                x: 17, y: 9, name: 'Town Notice Board',
                dialogue: [
                    "== COMING SOON ==",
                    "New trade routes opening to the Industrial District!",
                    "Arena tournament season begins next quarter."
                ],
            }
        ];

        return {
            name: 'Business Town',
            width: W, height: H,
            tiles, collision, npcs, interactables,
            spawnX: 16, spawnY: 14,
            transitions: [
                { x: 16, y: 29, target: 'world_map', spawnX: 5, spawnY: 5 },
                { x: 17, y: 29, target: 'world_map', spawnX: 5, spawnY: 5 }
            ],
            playerSprite: 'hero'
        };
    }

    function createMarketDistrict() {
        const W = 24;
        const H = 18;

        const tiles = [];
        for (let r = 0; r < H; r++) {
            tiles[r] = [];
            for (let c = 0; c < W; c++) {
                tiles[r][c] = T.STONE_FLOOR;
            }
        }

        for (let c = 0; c < W; c++) { tiles[0][c] = T.WALL; tiles[H-1][c] = T.WALL; }
        for (let r = 0; r < H; r++) { tiles[r][0] = T.WALL; tiles[r][W-1] = T.WALL; }

        for (let r = 6; r <= 11; r++) for (let c = 4; c <= W - 5; c++) tiles[r][c] = T.PATH;

        for (let c = 3; c <= 8; c++) { tiles[2][c] = T.ROOF; tiles[3][c] = T.WALL; tiles[4][c] = T.WALL; }
        tiles[3][4] = T.WINDOW; tiles[3][7] = T.WINDOW;
        tiles[4][5] = T.DOOR;

        for (let c = 15; c <= 20; c++) { tiles[2][c] = T.ROOF; tiles[3][c] = T.WALL; tiles[4][c] = T.WALL; }
        tiles[3][16] = T.WINDOW; tiles[3][19] = T.WINDOW;
        tiles[4][17] = T.DOOR;

        tiles[8][6] = T.STALL;
        tiles[8][8] = T.STALL;
        tiles[8][15] = T.STALL;
        tiles[8][17] = T.STALL;

        tiles[10][10] = T.LAMP;
        tiles[10][13] = T.LAMP;

        tiles[H-1][12] = T.DOOR;

        const collision = [];
        for (let r = 0; r < H; r++) {
            collision[r] = [];
            for (let c = 0; c < W; c++) {
                const t = tiles[r][c];
                collision[r][c] = [T.TREE, T.WALL, T.WALL_TOP, T.ROOF, T.WINDOW, T.WATER, T.HEDGE, T.STALL, T.LAMP, T.BENCH, T.SIGN, T.FOUNTAIN, T.WELL, T.CHEST].includes(t) ? 1 : 0;
            }
        }

        return {
            name: 'Market District',
            width: W, height: H,
            tiles, collision,
            npcs: [
                {
                    x: 7, y: 7, name: 'Merchant',
                    spriteType: 'npc', color: '#ddaa33',
                    facing: 'down',
                    dialogue: ["Looking to buy or sell?", "I have the finest wares in all the land!"],
                    action: 'market', route: '/market'
                },
                {
                    x: 16, y: 7, name: 'Investor',
                    spriteType: 'npc', color: '#33aa77',
                    facing: 'down',
                    dialogue: ["I seek promising ventures to fund.", "Have you prepared your pitch?"],
                    action: 'pitch', route: '/pitch'
                }
            ],
            interactables: [],
            spawnX: 12, spawnY: 15,
            transitions: [
                { x: 12, y: 17, target: 'hub', spawnX: 16, spawnY: 12 }
            ],
            playerSprite: 'hero'
        };
    }

    function getMap(mapId) {
        switch(mapId) {
            case 'hub': return createHubTown();
            case 'market_district': return createMarketDistrict();
            default: return createHubTown();
        }
    }

    return { getMap };
})();
