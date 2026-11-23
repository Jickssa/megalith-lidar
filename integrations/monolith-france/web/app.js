(() => {
'use strict';
const CFG='/assets/web/france/config/france-config.json', SRC='/assets/web/france/config/data-sources.json';
const STORE='monolith.france.observations.v1', GEO='https://data.geopf.fr/geocodage/search';
const OVERPASS=['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter'];
const $=id=>document.getElementById(id), S={map:null,cfg:null,base:{},over:{},markers:null,results:[],observations:[],pending:null,busy:false};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function toast(s){const e=$('toast');e.textContent=s;e.classList.add('show');clearTimeout(toast.t);toast.t=setTimeout(()=>e.classList.remove('show'),3200)}
async function getJson(url,opts={},timeout=18000){const c=new AbortController(),t=setTimeout(()=>c.abort(),timeout);try{const r=await fetch(url,{...opts,signal:c.signal,cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);return await r.json()}finally{clearTimeout(t)}}
const tile=layer=>'https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER='+encodeURIComponent(layer)+'&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}';
function initMap(){if(!window.L)throw Error('Leaflet absent');const d=S.cfg.defaultMap;S.map=L.map('map',{center:d.center,zoom:d.zoom,minZoom:d.minZoom,maxZoom:d.maxZoom,preferCanvas:true});S.base.ign=L.tileLayer(tile('GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2'),{attribution:'© IGN — Géoplateforme'});S.base.osm=L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors'});S.base.ign.addTo(S.map);
S.over.mnt=L.tileLayer(tile('IGNF_LIDAR-HD_MNT_ELEVATION.ELEVATIONGRIDCOVERAGE.SHADOW'),{opacity:.82,attribution:'© IGN — LiDAR HD'});S.over.mns=L.tileLayer(tile('IGNF_LIDAR-HD_MNS_ELEVATION.ELEVATIONGRIDCOVERAGE.SHADOW'),{opacity:.8,attribution:'© IGN — LiDAR HD'});S.over.mnh=L.tileLayer(tile('IGNF_LIDAR-HD_MNH_ELEVATION.ELEVATIONGRIDCOVERAGE.SHADOW'),{opacity:.8,attribution:'© IGN — LiDAR HD'});S.markers=L.featureGroup().addTo(S.map);S.map.on('mousemove',e=>$('cursorCoordinates').textContent=e.latlng.lat.toFixed(5)+', '+e.latlng.lng.toFixed(5));S.map.on('click',e=>S.pending=e.latlng);$('mapStatus').textContent='Plan IGN prêt — France métropolitaine'}
function item(f,source){const p=f.properties||f,t=f.tags||{},g=f.geometry||{};let lat=f.lat??f.center?.lat??g.coordinates?.[1],lon=f.lon??f.center?.lon??g.coordinates?.[0];lat=Number(lat);lon=Number(lon);if(!Number.isFinite(lat)||!Number.isFinite(lon)||Math.abs(lat)>90||Math.abs(lon)>180)return null;return {title:p.label||p.name||p.nom||t.name||t['name:fr']||p.toponym||'Site sans nom',kind:p.category||p.type||t.historic||t.megalith_type||'Site documenté',source,lat,lon}}
function showResults(a,source){S.results=a.filter(Boolean);S.markers.clearLayers();$('resultsList').innerHTML='';$('resultCount').textContent=S.results.length;$('resultSource').textContent=source;if(!S.results.length){$('resultsList').textContent='Aucun résultat renvoyé. Cela ne permet pas de conclure à une absence archéologique.';return}S.results.forEach((x,i)=>{const m=L.circleMarker([x.lat,x.lon],{radius:7,color:'#d5aa70',fillColor:'#d5aa70',fillOpacity:.9}).addTo(S.markers).bindPopup('<b>'+esc(x.title)+'</b><br>'+esc(x.kind)+'<br>'+esc(x.source));const d=document.createElement('article');d.className='result';d.innerHTML='<b>'+esc(x.title)+'</b><small>'+esc(x.kind)+' · '+esc(x.source)+'</small><small>'+x.lat.toFixed(5)+', '+x.lon.toFixed(5)+'</small><button type="button">Centrer</button>';d.querySelector('button').addEventListener('click',()=>{S.map.setView([x.lat,x.lon],15);m.openPopup()});$('resultsList').appendChild(d)})}
async function searchIgn(q){throw Error('Recherche du sous-type POI « mégalithe » non activée : le schéma de découverte et le paramètre de catégorie IGN ne sont pas encore validés. Utilise « Lieu / adresse » ou « Sites archéologiques OSM » comme sources de repérage distinctes.');}
async function searchPlace(q){const u=new URL(GEO);u.searchParams.set('q',q);u.searchParams.set('limit','30');const r=await getJson(u);return (r.features||r.results||[]).map(f=>item(f,'IGN / Géoplateforme'))}
async function searchOsm(){if(S.map.getZoom()<8)throw Error('Zoome davantage avant la recherche OSM.');const b=S.map.getBounds(),bb=[b.getSouth(),b.getWest(),b.getNorth(),b.getEast()].join(',');const q='[out:json][timeout:25];(node[historic~"^(archaeological_site|megalith|tumulus)$"]('+bb+');way[historic~"^(archaeological_site|megalith|tumulus)$"]('+bb+');relation[historic~"^(archaeological_site|megalith|tumulus)$"]('+bb+');node[site_type~"^(megalith|dolmen|menhir)$"]('+bb+');way[site_type~"^(megalith|dolmen|menhir)$"]('+bb+'););out center tags;';let last;for(const ep of OVERPASS){try{const r=await getJson(ep,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},body:'data='+encodeURIComponent(q)},30000);return (r.elements||[]).map(f=>item(f,'OpenStreetMap'))}catch(e){last=e}}throw last||Error('Overpass indisponible')}
async function search(){if(S.busy)return;const mode=$('searchMode').value,q=$('searchInput').value.trim();if(!['place','osm'].includes(mode)){toast('Mode de recherche non disponible.');return}if(mode!=='osm'&&!q){toast('Saisis un terme de recherche.');return}S.busy=true;$('searchButton').disabled=true;$('searchButton').textContent='Recherche…';try{const a=mode==='place'?await searchPlace(q):await searchOsm();showResults(a,mode==='place'?'IGN — géocodage':'OSM — emprise courante');$('mapStatus').textContent=a.length+' résultat(s)'}catch(e){showResults([],'Service distant indisponible');toast('Recherche impossible : '+e.message);$('mapStatus').textContent='Erreur de service'}finally{S.busy=false;$('searchButton').disabled=false;$('searchButton').textContent='Rechercher'}}
function getStorageLimits(config=S.cfg){
 const storage=config?.storage||{},limit=(key,fallback)=>Number.isSafeInteger(storage[key])&&storage[key]>0?storage[key]:fallback;
 return {maxImportBytes:limit('maxImportBytes',20*1024*1024),maxFeatures:limit('maxFeatures',5000)};
}
function isValidObservationFeature(feature){
 const geometry=feature?.geometry,coords=geometry?.coordinates,properties=feature?.properties;
 return feature?.type==='Feature'&&geometry?.type==='Point'&&Array.isArray(coords)&&coords.length>=2&&Number.isFinite(coords[0])&&Number.isFinite(coords[1])&&coords[0]>=-180&&coords[0]<=180&&coords[1]>=-90&&coords[1]<=90&&(properties===null||(typeof properties==='object'&&!Array.isArray(properties)));
}
function parseObservationImport(collection,fileSize,existingCount,limits){
 if(!Number.isFinite(fileSize)||fileSize<0||fileSize>limits.maxImportBytes)throw Error('Fichier trop volumineux (limite '+Math.round(limits.maxImportBytes/1024/1024)+' Mio).');
 if(collection?.type!=='FeatureCollection'||!Array.isArray(collection.features))throw Error('GeoJSON FeatureCollection attendu.');
 if(collection.features.length>limits.maxFeatures)throw Error('Le fichier dépasse '+limits.maxFeatures+' entités.');
 const valid=collection.features.filter(isValidObservationFeature),remaining=Math.max(0,limits.maxFeatures-existingCount);
 return {features:valid.slice(0,remaining),invalid:collection.features.length-valid.length,skipped:Math.max(0,valid.length-remaining)};
}
function persistObs(next){
 const max=getStorageLimits().maxFeatures;
 if(next.length>max){toast('Limite atteinte : '+max+' observations locales maximum.');return false}
 try{localStorage.setItem(STORE,JSON.stringify(next));S.observations=next;renderObs();return true}
 catch(e){toast('Écriture locale impossible : espace de stockage insuffisant ou indisponible.');return false}
}
function loadObs(){
 try{const stored=JSON.parse(localStorage.getItem(STORE)||'[]'),max=getStorageLimits().maxFeatures;S.observations=Array.isArray(stored)?stored.filter(isValidObservationFeature).slice(0,max):[]}
 catch{S.observations=[]}
 renderObs()
}
function renderObs(){
 $('observationCount').textContent=S.observations.length;$('observationList').innerHTML='';
 S.observations.forEach((f,i)=>{const p=f.properties||{},c=f.geometry.coordinates,d=document.createElement('div');d.className='obs';d.innerHTML='<b>'+esc(p.title||'Observation sans titre')+'</b><small>'+esc(p.type||'indéterminé')+' · '+Number(c[1]).toFixed(5)+', '+Number(c[0]).toFixed(5)+'</small><button type="button">Supprimer</button>';d.querySelector('button').addEventListener('click',()=>persistObs(S.observations.filter((_,j)=>j!==i)));$('observationList').appendChild(d)})
}
function addObs(){
 if(S.observations.length>=getStorageLimits().maxFeatures){toast('Limite atteinte : '+getStorageLimits().maxFeatures+' observations locales maximum.');return}
 const p=S.pending||S.map.getCenter();$('observationCoordinates').textContent=p.lat.toFixed(6)+', '+p.lng.toFixed(6);$('observationDialog').showModal()
}
function saveObs(){
 if(S.observations.length>=getStorageLimits().maxFeatures){toast('Limite atteinte : '+getStorageLimits().maxFeatures+' observations locales maximum.');return}
 const p=S.pending||S.map.getCenter(),title=$('observationTitle').value.trim();
 if(!title)return;
 const feature={type:'Feature',geometry:{type:'Point',coordinates:[p.lng,p.lat]},properties:{title,type:$('observationType').value,notes:$('observationNotes').value,createdAt:new Date().toISOString(),source:'observation-personnelle'}};
 if(!isValidObservationFeature(feature)){toast('Coordonnées du relevé invalides.');return}
 if(!persistObs([...S.observations,feature]))return;
 $('observationDialog').close();$('observationForm').reset();toast('Relevé enregistré sur cet appareil.')
}
function download(name,mime,data){if(window.MegalithAndroid?.saveOrShareFile){window.MegalithAndroid.saveOrShareFile(name,mime,data);return}const u=URL.createObjectURL(new Blob([data],{type:mime})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1200)}
function exportObs(){download('monolith-france-observations.geojson','application/geo+json',JSON.stringify({type:'FeatureCollection',features:S.observations},null,2))}
async function importObs(f){
 if(!f)return;
 try{
  const limits=getStorageLimits();
  if(f.size>limits.maxImportBytes)throw Error('Fichier trop volumineux (limite '+Math.round(limits.maxImportBytes/1024/1024)+' Mio).');
  const collection=JSON.parse(await f.text()),result=parseObservationImport(collection,f.size,S.observations.length,limits);
  if(!result.features.length){toast('Aucun nouveau point valide importable. '+result.invalid+' entité(s) invalide(s), '+result.skipped+' refusée(s) par la limite cumulée.');return}
  if(!persistObs([...S.observations,...result.features]))return;
  toast(result.features.length+' relevé(s) importé(s) ; '+result.invalid+' invalide(s), '+result.skipped+' hors limite ignoré(s).')
 }catch(e){toast('Import refusé : '+e.message)}
 finally{$('importGeoJson').value=''}
}
function events(){$('searchButton').addEventListener('click',search);$('searchInput').addEventListener('keydown',e=>{if(e.key==='Enter')search()});$('basemapSelect').addEventListener('change',e=>{Object.values(S.base).forEach(l=>S.map.removeLayer(l));S.base[e.target.value].addTo(S.map)});[['layerMnt','mnt'],['layerMns','mns'],['layerMnh','mnh']].forEach(([id,k])=>$(id).addEventListener('change',e=>e.target.checked?S.over[k].addTo(S.map):S.map.removeLayer(S.over[k])));$('locateButton').addEventListener('click',()=>{if(!navigator.geolocation)return toast('Géolocalisation indisponible');navigator.geolocation.getCurrentPosition(p=>S.map.setView([p.coords.latitude,p.coords.longitude],15),e=>toast('Position indisponible : '+e.message),{timeout:10000})});$('addObservation').addEventListener('click',addObs);$('exportObservations').addEventListener('click',exportObs);$('importGeoJson').addEventListener('change',e=>importObs(e.target.files?.[0]));$('cancelDialog').addEventListener('click',()=>$('observationDialog').close());$('observationForm').addEventListener('submit',e=>{e.preventDefault();saveObs()})}
async function init(){try{S.cfg=await getJson(CFG);await getJson(SRC);initMap();events();loadObs();$('mapStatus').textContent='Module prêt — requêtes à la demande'}catch(e){$('mapStatus').textContent='Initialisation impossible : '+e.message;toast('Erreur au démarrage du module France.')}}
if(typeof module!=='undefined'&&module.exports)module.exports={getStorageLimits,isValidObservationFeature,parseObservationImport};
if(typeof document!=='undefined')document.addEventListener('DOMContentLoaded',init);
})();