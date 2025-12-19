const CACHE_NAME = 'biztycoon-v1';
const STATIC_CACHE = 'biztycoon-static-v1';
const DYNAMIC_CACHE = 'biztycoon-dynamic-v1';

const STATIC_ASSETS = [
  '/',
  '/static/manifest.json',
  '/static/images/game_title_backdrop.png',
  '/static/images/business_tycoon_character_avatar.png',
  '/static/images/business_tycoon_hero_portrait.png',
  '/static/images/gold_coin_resource_icon.png',
  '/static/images/reputation_star_icon.png',
  '/static/images/modern_office_hub_background.png',
  '/static/images/fantasy_tavern_hub_background.png',
  '/static/images/industrial_factory_hub_background.png',
  '/static/images/sci-fi_starship_hub_background.png',
  '/static/images/marketing_manager_portrait.png',
  '/static/images/finance_director_portrait.png',
  '/static/images/hr_manager_portrait.png',
  '/static/images/operations_chief_portrait.png',
  '/static/images/legal_counsel_portrait.png',
  '/static/images/strategy_advisor_portrait.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css',
  'https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Staatliches&family=Press+Start+2P&display=swap'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('Caching static assets');
        return cache.addAll(STATIC_ASSETS.filter(url => url.startsWith('/')));
      })
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== STATIC_CACHE && key !== DYNAMIC_CACHE)
          .map(key => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  if (request.method !== 'GET') {
    return;
  }
  
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(cacheFirst(request));
  } else if (url.origin === location.origin) {
    event.respondWith(networkFirst(request));
  }
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }
  
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    return new Response('Offline', { status: 503 });
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }
    
    if (request.headers.get('Accept').includes('text/html')) {
      return new Response(`
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Offline - Business Tycoon RPG</title>
          <style>
            body {
              font-family: 'Segoe UI', sans-serif;
              background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
              color: #ffd700;
              min-height: 100vh;
              display: flex;
              align-items: center;
              justify-content: center;
              margin: 0;
              text-align: center;
            }
            .offline-container {
              padding: 2rem;
            }
            h1 { font-size: 2rem; margin-bottom: 1rem; }
            p { color: #e8e8e8; margin-bottom: 1.5rem; }
            button {
              background: linear-gradient(135deg, #ffd700, #b8860b);
              border: none;
              padding: 12px 24px;
              color: #1a1a2e;
              font-weight: bold;
              border-radius: 8px;
              cursor: pointer;
            }
          </style>
        </head>
        <body>
          <div class="offline-container">
            <h1>You're Offline</h1>
            <p>Business Tycoon RPG needs an internet connection to sync your progress.</p>
            <button onclick="location.reload()">Try Again</button>
          </div>
        </body>
        </html>
      `, {
        status: 503,
        headers: { 'Content-Type': 'text/html' }
      });
    }
    
    return new Response('Offline', { status: 503 });
  }
}

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
