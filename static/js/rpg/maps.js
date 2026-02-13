const RPGMaps = (function() {

    function createHubTown() {
        const W = 30;
        const H = 25;

        const T = {
            EMPTY: 0, GRASS: 1, PATH: 2, WATER: 3,
            WALL: 4, WALL_TOP: 5, ROOF: 6, DOOR: 7,
            WINDOW: 8, TREE: 9, FLOWERS: 10, WOOD_FLOOR: 11,
            SIGN: 12, SAND: 13, STONE_FLOOR: 14, HEDGE: 15,
            CHEST: 16, PORTAL: 17
        };

        const tiles = [];
        for (let r = 0; r < H; r++) {
            tiles[r] = [];
            for (let c = 0; c < W; c++) {
                tiles[r][c] = T.GRASS;
            }
        }

        for (let c = 0; c < W; c++) { tiles[0][c] = T.TREE; tiles[H-1][c] = T.TREE; }
        for (let r = 0; r < H; r++) { tiles[r][0] = T.TREE; tiles[r][W-1] = T.TREE; }

        for (let r = 10; r <= 14; r++) {
            for (let c = 2; c < W - 2; c++) tiles[r][c] = T.PATH;
        }
        for (let r = 2; r < H - 2; r++) {
            for (let c = 13; c <= 16; c++) tiles[r][c] = T.PATH;
        }

        function placeBuilding(startR, startC, w, h, hasDoor) {
            for (let c = startC; c < startC + w; c++) tiles[startR][c] = T.ROOF;
            for (let c = startC; c < startC + w; c++) tiles[startR + 1][c] = T.ROOF;
            for (let r = startR + 2; r < startR + h; r++) {
                for (let c = startC; c < startC + w; c++) {
                    tiles[r][c] = T.WALL;
                }
            }
            if (w >= 4) {
                tiles[startR + 2][startC + 1] = T.WINDOW;
                tiles[startR + 2][startC + w - 2] = T.WINDOW;
            }
            if (hasDoor) {
                const doorC = startC + Math.floor(w / 2);
                tiles[startR + h - 1][doorC] = T.DOOR;
            }
        }

        placeBuilding(2, 2, 5, 5, true);
        placeBuilding(2, 8, 4, 5, true);
        placeBuilding(2, 18, 5, 5, true);
        placeBuilding(2, 24, 5, 5, true);

        placeBuilding(16, 2, 5, 5, true);
        placeBuilding(16, 8, 4, 5, true);
        placeBuilding(16, 18, 5, 5, true);
        placeBuilding(16, 24, 5, 5, true);

        for (let c = 12; c <= 17; c++) {
            tiles[3][c] = T.STONE_FLOOR;
            tiles[4][c] = T.STONE_FLOOR;
            tiles[5][c] = T.STONE_FLOOR;
        }
        tiles[2][13] = T.WALL_TOP; tiles[2][14] = T.WALL_TOP; tiles[2][15] = T.WALL_TOP; tiles[2][16] = T.WALL_TOP;

        tiles[8][5] = T.FLOWERS;
        tiles[8][7] = T.FLOWERS;
        tiles[8][22] = T.FLOWERS;
        tiles[8][24] = T.FLOWERS;

        tiles[12][6] = T.SIGN;
        tiles[12][23] = T.SIGN;

        tiles[22][14] = T.PORTAL;
        tiles[22][15] = T.PORTAL;

        for (let c = 3; c < 8; c++) tiles[15][c] = T.FLOWERS;
        for (let c = 22; c < 27; c++) tiles[15][c] = T.FLOWERS;

        const collision = [];
        for (let r = 0; r < H; r++) {
            collision[r] = [];
            for (let c = 0; c < W; c++) {
                const t = tiles[r][c];
                collision[r][c] = [T.TREE, T.WALL, T.WALL_TOP, T.ROOF, T.WINDOW, T.WATER, T.HEDGE, T.CHEST, T.SIGN].includes(t) ? 1 : 0;
            }
        }

        const npcs = [
            {
                x: 4, y: 8, name: 'Marketing Maven',
                spriteType: 'npc', color: '#cc4488',
                facing: 'down',
                dialogue: [
                    "Welcome to the Marketing District!",
                    "I can teach you about branding, campaigns, and customer acquisition.",
                    "Ready to boost your company's visibility?"
                ],
                action: 'marketing',
                route: '/scenarios/Marketing'
            },
            {
                x: 10, y: 8, name: 'Finance Director',
                spriteType: 'npc', color: '#44aa44',
                facing: 'down',
                dialogue: [
                    "Ah, the Finance Office is right here.",
                    "I handle budgets, investments, and financial forecasting.",
                    "Let's make sure your books are in order!"
                ],
                action: 'finance',
                route: '/scenarios/Finance'
            },
            {
                x: 14, y: 5, name: 'Town Elder',
                spriteType: 'npc', color: '#8866aa',
                facing: 'down',
                dialogue: [
                    "Welcome to Business Town, young entrepreneur!",
                    "Each building in this town represents a different business discipline.",
                    "Talk to the specialists to learn and grow your empire!",
                    "Use arrow keys to move and Enter to interact."
                ],
                action: 'tutorial',
                route: '/tutorial'
            },
            {
                x: 20, y: 8, name: 'Operations Chief',
                spriteType: 'npc', color: '#dd8833',
                facing: 'down',
                dialogue: [
                    "The Operations Center is behind me.",
                    "Supply chains, logistics, scheduling... I handle it all!",
                    "Want to optimize your business processes?"
                ],
                action: 'operations',
                route: '/scenarios/Operations'
            },
            {
                x: 26, y: 8, name: 'Legal Counsel',
                spriteType: 'npc', color: '#5577bb',
                facing: 'down',
                dialogue: [
                    "The Law Office. Contracts, regulations, compliance.",
                    "Every successful business needs solid legal foundations.",
                    "Shall we review your legal standing?"
                ],
                action: 'legal',
                route: '/scenarios/Legal'
            },
            {
                x: 4, y: 22, name: 'HR Manager',
                spriteType: 'npc', color: '#ee6655',
                facing: 'up',
                dialogue: [
                    "Welcome to Human Resources!",
                    "Building a great team is the key to any successful business.",
                    "Let me teach you about hiring, management, and team dynamics."
                ],
                action: 'hr',
                route: '/scenarios/Human Resources'
            },
            {
                x: 10, y: 22, name: 'Strategy Advisor',
                spriteType: 'npc', color: '#aaaa33',
                facing: 'up',
                dialogue: [
                    "Strategy is everything in business!",
                    "Competition analysis, market positioning, long-term planning...",
                    "Ready to think like a CEO?"
                ],
                action: 'strategy',
                route: '/scenarios/Strategy'
            },
            {
                x: 20, y: 22, name: 'Shop Keeper',
                spriteType: 'npc', color: '#bb8844',
                facing: 'up',
                dialogue: [
                    "Welcome to the Item Shop!",
                    "I sell equipment and supplies to help on your journey.",
                    "Browse my wares?"
                ],
                action: 'shop',
                route: '/shop'
            },
            {
                x: 26, y: 22, name: 'Arena Champion',
                spriteType: 'npc', color: '#cc2222',
                facing: 'up',
                dialogue: [
                    "The Battle Arena awaits, challenger!",
                    "Test your business knowledge against rivals!",
                    "Are you brave enough to enter?"
                ],
                action: 'battle',
                route: '/battle_arena'
            },
            {
                x: 14, y: 12, name: 'Command Officer',
                spriteType: 'npc', color: '#4488cc',
                facing: 'right',
                dialogue: [
                    "This is the Command Center.",
                    "Monitor your company's resources, view reports, and plan strategy.",
                    "Check your dashboard for the latest updates."
                ],
                action: 'command_center',
                route: '/dashboard'
            },
            {
                x: 16, y: 12, name: 'Quest Board',
                spriteType: 'npc', color: '#996633',
                facing: 'left',
                dialogue: [
                    "The Quest Board has daily missions and challenges!",
                    "Complete them for bonus rewards.",
                    "Check back every day for new tasks."
                ],
                action: 'quests',
                route: '/daily_missions'
            }
        ];

        const interactables = [
            {
                x: 12, y: 6, name: 'Notice Board',
                dialogue: ["== BUSINESS TOWN NOTICE BOARD ==", "Explore the town and talk to NPCs to access different game features!", "Each specialist can teach you a different business discipline."],
            },
            {
                x: 23, y: 12, name: 'Signpost',
                dialogue: ["East: Legal Office & Arena", "West: Marketing & Finance"],
            },
            {
                x: 6, y: 12, name: 'Signpost',
                dialogue: ["North: Marketing & Finance", "South: HR & Strategy"],
            }
        ];

        return {
            name: 'Business Town',
            width: W,
            height: H,
            tiles: tiles,
            collision: collision,
            npcs: npcs,
            interactables: interactables,
            spawnX: 14,
            spawnY: 12,
            transitions: [
                { x: 14, y: 24, target: 'world_map', spawnX: 5, spawnY: 5 },
                { x: 15, y: 24, target: 'world_map', spawnX: 5, spawnY: 5 }
            ],
            playerSprite: 'hero'
        };
    }

    function createMarketDistrict() {
        const W = 20;
        const H = 15;
        const T = {
            EMPTY: 0, GRASS: 1, PATH: 2, WATER: 3,
            WALL: 4, WALL_TOP: 5, ROOF: 6, DOOR: 7,
            WINDOW: 8, TREE: 9, FLOWERS: 10, WOOD_FLOOR: 11,
            SIGN: 12, SAND: 13, STONE_FLOOR: 14, HEDGE: 15,
            CHEST: 16, PORTAL: 17
        };

        const tiles = [];
        for (let r = 0; r < H; r++) {
            tiles[r] = [];
            for (let c = 0; c < W; c++) {
                tiles[r][c] = T.STONE_FLOOR;
            }
        }

        for (let c = 0; c < W; c++) { tiles[0][c] = T.WALL; tiles[H-1][c] = T.WALL; }
        for (let r = 0; r < H; r++) { tiles[r][0] = T.WALL; tiles[r][W-1] = T.WALL; }

        for (let r = 5; r <= 9; r++) for (let c = 3; c <= W - 4; c++) tiles[r][c] = T.PATH;

        for (let c = 3; c <= 7; c++) { tiles[2][c] = T.ROOF; tiles[3][c] = T.WALL; tiles[4][c] = T.WALL; }
        tiles[4][5] = T.DOOR;

        for (let c = 12; c <= 16; c++) { tiles[2][c] = T.ROOF; tiles[3][c] = T.WALL; tiles[4][c] = T.WALL; }
        tiles[4][14] = T.DOOR;

        tiles[H-1][W/2] = T.DOOR;

        const collision = [];
        for (let r = 0; r < H; r++) {
            collision[r] = [];
            for (let c = 0; c < W; c++) {
                const t = tiles[r][c];
                collision[r][c] = [T.TREE, T.WALL, T.WALL_TOP, T.ROOF, T.WINDOW, T.WATER, T.HEDGE].includes(t) ? 1 : 0;
            }
        }

        return {
            name: 'Market District',
            width: W,
            height: H,
            tiles: tiles,
            collision: collision,
            npcs: [
                {
                    x: 5, y: 6, name: 'Merchant',
                    spriteType: 'npc', color: '#ddaa33',
                    facing: 'down',
                    dialogue: ["Looking to buy or sell?", "Check out our finest wares!"],
                    action: 'market',
                    route: '/market'
                },
                {
                    x: 14, y: 6, name: 'Investor',
                    spriteType: 'npc', color: '#33aa77',
                    facing: 'down',
                    dialogue: ["I'm looking for promising ventures to invest in.", "Got a pitch for me?"],
                    action: 'pitch',
                    route: '/pitch'
                }
            ],
            interactables: [],
            spawnX: 10,
            spawnY: 12,
            transitions: [
                { x: 10, y: 14, target: 'hub', spawnX: 14, spawnY: 10 }
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
