// AIShield Service Worker
// PWA 离线缓存 — 网络优先策略（Network First）

const CACHE_NAME = 'aishield-v1';
const CACHE_URLS = [
  '/',
  '/agent.html',
  '/banned-words',
  '/report',
  '/tool/profile',
  '/.well-known/agent-card.json',
  '/sitemap.xml',
];

// Install: 预缓存关键资源
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(CACHE_URLS);
    }).then(function() {
      return self.skipWaiting();
    })
  );
});

// Activate: 清理旧缓存
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(key) {
          return key !== CACHE_NAME;
        }).map(function(key) {
          return caches.delete(key);
        })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// Fetch: 网络优先策略（离线时回退缓存）
self.addEventListener('fetch', function(event) {
  // 只处理 GET 请求
  if (event.request.method !== 'GET') {
    return;
  }

  // 跳过 API 调用和非同源请求
  var url = new URL(event.request.url);
  if (url.pathname.startsWith('/api/') && !url.pathname.startsWith('/api/v1/health')) {
    return;
  }

  event.respondWith(
    fetch(event.request).then(function(response) {
      // 网络请求成功，更新缓存
      if (response.ok) {
        var responseClone = response.clone();
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(event.request, responseClone);
        });
      }
      return response;
    }).catch(function() {
      // 网络失败，回退缓存
      return caches.match(event.request).then(function(cachedResponse) {
        if (cachedResponse) {
          return cachedResponse;
        }
        // 如果缓存也没有，返回离线提示页（仅对 HTML 请求）
        if (event.request.headers.get('accept') &&
            event.request.headers.get('accept').indexOf('text/html') !== -1) {
          return caches.match('/');
        }
        return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
      });
    })
  );
});
