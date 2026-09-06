const CACHE_NAME = 'openrights-v28';
const ASSETS = ['./','./index.html','./styles.css?v=21','./app.js?v=41','./data/index.js?v=6','./manifest.webmanifest'];
self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE_NAME).then(cache=>cache.addAll(ASSETS.map(url=>new Request(url,{cache:'reload'})))).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('openrights-') && key!==CACHE_NAME).map(key=>caches.delete(key)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',event=>{
  const request=event.request, url=new URL(request.url);
  if(request.method!=='GET' || url.origin!==self.location.origin || url.pathname.startsWith('/api/')) return;
  if(request.mode==='navigate') {
    event.respondWith(fetch(request).catch(async()=> (await caches.open(CACHE_NAME)).match('./index.html')).then(response=>response || new Response('Offline archive unavailable. Reconnect and reload.',{status:503})));
    return;
  }
  event.respondWith((async()=>{
    const cache=await caches.open(CACHE_NAME), cached=await cache.match(request);
    return cached || fetch(request);
  })());
});
