(() => {
'use strict';
const CFG='/assets/web/france/config/france-config.json', SRC='/assets/web/france/config/data-sources.json';
const STORE='monolith.france.observations.v1', GEO='https://data.geopf.fr/geocodage/search';
const OVERPASS=['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter'];
const $=id=>document.getElementById(id), S={map:null,cfg:null,taxonomy:null,base:{},over:{},markers:null,results:[],observations:[],pending:null,busy:false,searchId:0,searchController:null};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function toast(s){const e=$('toast');e.textContent=s;e.classList.add('show');clearTimeout(toast.t);toast.t=setTimeout(()=>e.classList.remove('show'),3200)}
async function getJson(url,opts={},timeout=18000){const c=new AbortController(),t=setTimeout(()=>c.abort(),timeout);try{const r=await fetch(url,{...opts,signal:c.signal,cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);return await r.json()}finally{clearTimeout(t)}}
const tile=layer=>'https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER='+encodeURIComponent(layer)+'&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}';
function initMap(){if(!window.L)throw Error('Leaflet absent');const d=S.cfg.defaultMap;S.map=L.map('map',{center:d.center,zoom:d.zoom,minZoom:d.minZoom,maxZoom:d.maxZoom,preferCanvas:true});S.base.ign=L.tileLayer(tile('GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2'),{attribution:'© IGN — Géoplateforme'});S.base.osm=L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors'});S.base.ign.addTo(S.map);
S.over.mnt=L.tileLayer(tile('IGNF_LIDAR-HD_MNT_ELEVATION.ELEVATIONGRIDCOVERAGE.SHADOW'),{opacity:.82,attribution:'© IGN — LiDAR HD'});S.over.mns=L.tileLayer(tile('IGNF_LIDAR-HD_MNS_ELEVATION.ELEVATIONGRIDCOVERAGE.SHADOW'),{opacity:.8,attribution:'© IGN — LiDAR HD'});S.over.mnh=L.tileLayer(tile('IGNF_LIDAR-HD_MNH_ELEVATION.ELEVATIONGRIDCOVERAGE.SHADOW'),{opacity:.8,attribution:'© IGN — LiDAR HD'});S.markers=L.featureGroup().addTo(S.map);S.map.on('mousemove',e=>$('cursorCoordinates').textContent=e.latlng.lat.toFixed(5)+', '+e.latlng.lng.toFixed(5));S.map.on('click',e=>S.pending=e.latlng);$('mapStatus').textContent='Plan IGN prêt — France métropolitaine'}
function item(f,source){const p=f.properties||f,t=f.tags||{},g=f.geometry||{};let lat=f.lat??f.center?.lat??g.coordinates?.[1],lon=f.lon??f.center?.lon??g.coordinates?.[0];lat=Number(lat);lon=Number(lon);if(!Number.isFinite(lat)||!Number.isFinite(lon)||Math.abs(lat)>90||Math.abs(lon)>180)return null;return {title:p.label||p.name||p.nom||t.name||t['name:fr']||p.toponym||'Site sans nom',kind:p.category||p.type||t.historic||t.megalith_type||'Site documenté',source,lat,lon}}
function showResults(a,source){S.results=a.filter(Boolean);S.markers.clearLayers();$('resultsList').innerHTML='';$('resultCount').textContent=S.results.length;$('resultSource').textContent=source;if(!S.results.length){$('resultsList').textContent='Aucun résultat renvoyé. Cela ne permet pas de conclure à une absence archéologique.';return}S.results.forEach((x,i)=>{const m=L.circleMarker([x.lat,x.lon],{radius:7,color:'#d5aa70',fillColor:'#d5aa70',fillOpacity:.9}).addTo(S.markers).bindPopup('<b>'+esc(x.title)+'</b><br>'+esc(x.kind)+'<br>'+esc(x.source));const d=document.createElement('article');d.className='result';d.innerHTML='<b>'+esc(x.title)+'</b><small>'+esc(x.kind)+' · '+esc(x.source)+'</small><small>'+x.lat.toFixed(5)+', '+x.lon.toFixed(5)+'</small><button type="button">Centrer</button>';d.querySelector('button').addEventListener('click',()=>{S.map.setView([x.lat,x.lon],15);m.openPopup()});$('resultsList').appendChild(d)})}
function normalizeTaxonomy(taxonomy){
 const categories=Array.isArray(taxonomy?.categories)?taxonomy.categories:[];
 const seen=new Set();
 return categories.filter(category=>{
  if(!category||typeof category.id!=='string'||!category.id.trim()||seen.has(category.id))return false;
  seen.add(category.id);
  return Array.isArray(category.osm)&&(category.osm.length>0);
 }).map(category=>({
  id:category.id,
  label:String(category.label||category.id),
  terms:Array.isArray(category.terms)?category.terms.map(String):[],
  osm:category.osm.filter(rule=>rule&&typeof rule.key==='string'&&typeof rule.value==='string')
 }));
}
function escapeOverpassValue(value){
 return String(value).replace(/\\/g,'\\\\').replace(/"/g,'\\"');
}
function getSearchSettings(config=S.cfg){
 const search=config?.search||{};
 const maxResults=Number.isSafeInteger(search.maxResults)&&search.maxResults>0?Math.min(search.maxResults,30):30;
 const osmMinimumZoom=Number.isSafeInteger(search.osmMinimumZoom)&&search.osmMinimumZoom>=0?Math.min(search.osmMinimumZoom,19):8;
 const territory=['METROPOLE','DOMTOM'].includes(search.territory)?search.territory:'METROPOLE';
 const maxSearchAreaKm2=Number.isFinite(search.maxSearchAreaKm2)&&search.maxSearchAreaKm2>0?Math.min(search.maxSearchAreaKm2,2500):2500;
 return {maxResults,osmMinimumZoom,territory,maxSearchAreaKm2};
}
function buildPlaceSearchUrl(query,config=S.cfg){
 const settings=getSearchSettings(config),url=new URL(GEO);
 url.searchParams.set('q',String(query||'').trim());
 url.searchParams.set('limit',String(settings.maxResults));
 url.searchParams.set('terr',settings.territory);
 return url;
}
function buildPoiAutocompleteUrl(text,poiType,config=S.cfg){
 if(!String(text||'').trim())throw Error('Saisis un terme de recherche.');
 if(!String(poiType||'').trim())throw Error('Le type POI IGN doit provenir de GetCapabilities.');
 const settings=getSearchSettings(config);
 const url=new URL('https://data.geopf.fr/geocodage/completion/');
 url.searchParams.set('text',String(text).trim());
 url.searchParams.set('terr',settings.territory);
 url.searchParams.set('poiType',String(poiType).trim());
 url.searchParams.set('maximumResponses',String(settings.maxResults));
 return url;
}
function queryBoxFromBounds(bounds){
 const south=Number(bounds?.getSouth?.()),west=Number(bounds?.getWest?.()),north=Number(bounds?.getNorth?.()),east=Number(bounds?.getEast?.());
 if(![south,west,north,east].every(Number.isFinite)||south>=north||west>=east||south< -90||north>90||west< -180||east>180)throw Error('Emprise cartographique invalide.');
 const midLat=(south+north)/2;
 const widthKm=(east-west)*111.32*Math.max(.01,Math.cos(midLat*Math.PI/180));
 const heightKm=(north-south)*111.32;
 return {south,west,north,east,areaKm2:Math.abs(widthKm*heightKm)};
}
function buildOverpassQuery({bounds,category,taxonomy,query,limit=1200}){
 const box=queryBoxFromBounds(bounds);
 if(box.areaKm2>getSearchSettings().maxSearchAreaKm2)throw Error('Emprise trop vaste ('+Math.round(box.areaKm2)+' km²). Zoome davantage pour limiter la requête.');
 const categories=normalizeTaxonomy(taxonomy);
 const selected=categories.find(item=>item.id===category);
 if(!selected)throw Error('Catégorie archéologique inconnue : '+category);
 const bbox=[box.south,box.west,box.north,box.east].join(',');
 const clauses=selected.osm.map(rule=>{
  const key=escapeOverpassValue(rule.key),value=escapeOverpassValue(rule.value);
  return ['node','way','relation'].map(type=>type+'["'+key+'"="'+value+'"]('+bbox+');').join('');
 }).join('');
 const text=String(query||'').trim();
 const nameFilter=text?'[name~"'+escapeOverpassValue(text)+'",i]':'';
 const queryClauses=clauses.replaceAll('('+bbox+');',''+nameFilter+'('+bbox+');');
 const safeLimit=Math.max(1,Math.min(Number.isSafeInteger(limit)?limit:1200,2000));
 return '[out:json][timeout:25];('+queryClauses+');out center tags '+safeLimit+';';
}
function osmElementToItem(feature,source='OpenStreetMap'){
 const tags=feature?.tags||{};
 let lat=feature?.lat??feature?.center?.lat??feature?.geometry?.coordinates?.[1];
 let lon=feature?.lon??feature?.center?.lon??feature?.geometry?.coordinates?.[0];
 if((!Number.isFinite(Number(lat))||!Number.isFinite(Number(lon)))&&Array.isArray(feature?.nodesGeometry)&&feature.nodesGeometry.length){
  const valid=feature.nodesGeometry.filter(p=>Number.isFinite(Number(p.lat))&&Number.isFinite(Number(p.lon)));
  if(valid.length){lat=valid.reduce((sum,p)=>sum+Number(p.lat),0)/valid.length;lon=valid.reduce((sum,p)=>sum+Number(p.lon),0)/valid.length}
 }
 lat=Number(lat);lon=Number(lon);
 if(!Number.isFinite(lat)||!Number.isFinite(lon)||Math.abs(lat)>90||Math.abs(lon)>180)return null;
 const type=tags.megalith_type||tags.archaeological_site||tags.historic||tags.heritage||tags.man_made||'Site documenté';
 const title=tags.name||tags['name:fr']||tags.ref||type;
 return {id:feature.id!=null?'osm:'+feature.type+':'+feature.id:undefined,title,kind:type,source,lat,lon,tags,osmType:feature.type,osmId:feature.id,url:feature.id?'https://www.openstreetmap.org/'+feature.type+'/'+feature.id:undefined};
}
async function searchPlace(q){const u=buildPlaceSearchUrl(q);const r=await getJson(u);return (r.features||r.results||[]).map(f=>item(f,'IGN / Géoplateforme'))}
async function searchOsm(category,query,signal){
 if(!S.map)throw Error('Carte non initialisée.');
 const settings=getSearchSettings();
 if(S.map.getZoom()<settings.osmMinimumZoom)throw Error('Zoome davantage avant la recherche OSM (niveau '+settings.osmMinimumZoom+' minimum).');
 const taxonomy=S.taxonomy||await getJson('/assets/web/france/config/archaeology-taxonomy.fr.json');
 const overpass=buildOverpassQuery({bounds:S.map.getBounds(),category,taxonomy,query,limit:1200});
 let last;
 for(const endpoint of OVERPASS){
  try{
   const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},body:'data='+encodeURIComponent(overpass),signal,cache:'no-store'});
   if(!response.ok)throw Error('Overpass HTTP '+response.status);
   const payload=await response.json();
   if(!Array.isArray(payload.elements))throw Error('Réponse Overpass invalide : tableau elements absent.');
   return payload.elements.map(feature=>osmElementToItem(feature)).filter(Boolean);
  }catch(error){if(signal?.aborted)throw error;last=error}
 }
 throw last||Error('Overpass indisponible.');
}
async function search(){
 if(S.busy)return;
 const mode=$('searchMode').value,query=$('searchInput').value.trim(),category=$('archaeologyCategory')?.value||'megaliths';
 if(!['place','osm'].includes(mode)){toast('Mode de recherche non disponible.');return}
 if(mode==='place'&&!query){toast('Saisis une adresse ou un lieu.');return}
 if(mode==='osm'&&!S.taxonomy?.categories?.some(c=>c.id===category)){toast('Taxonomie archéologique indisponible.');return}
 if(S.searchController)S.searchController.abort();
 const controller=new AbortController(),searchId=(S.searchId||0)+1;
 S.searchId=searchId;S.searchController=controller;S.busy=true;
 $('searchButton').disabled=true;$('searchButton').textContent='Recherche…';
 $('mapStatus').textContent=mode==='osm'?'Interrogation OpenStreetMap…':'Interrogation IGN…';
 try{
  const results=mode==='place'?await searchPlace(query):await searchOsm(category,query,controller.signal);
  if(controller.signal.aborted||searchId!==S.searchId)return;
  showResults(results,mode==='place'?'IGN — géocodage des lieux':'OSM — '+(S.taxonomy.categories.find(c=>c.id===category)?.label||category));
  $('mapStatus').textContent=results.length+' résultat(s)';
  if($('osmStatus'))$('osmStatus').textContent='Réponse reçue';
 }catch(error){
  if(controller.signal.aborted||searchId!==S.searchId)return;
  showResults([],'Échec du service de recherche');
  toast('Recherche impossible : '+error.message);
  $('mapStatus').textContent='Échec de la recherche — carte conservée';
  if($('osmStatus'))$('osmStatus').textContent=error.message;
 }finally{
  if(searchId===S.searchId){S.busy=false;$('searchButton').disabled=false;$('searchButton').textContent='Rechercher';}
 }
}
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
function isGeoJsonFile(f){
 const name=String(f?.name||'').toLowerCase(),type=String(f?.type||'').toLowerCase();
 return /\.(json|geojson)$/.test(name)||['application/json','application/geo+json','text/json'].includes(type);
}
async function importObs(f){
 if(!f)return;
 try{
  if(!isGeoJsonFile(f))throw Error('Sélectionne un fichier .json ou .geojson.');
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
async function init(){try{[S.cfg,S.taxonomy]=await Promise.all([getJson(CFG),getJson('/assets/web/france/config/archaeology-taxonomy.fr.json')]);S.sources=await getJson(SRC);initMap();events();loadObs();$('mapStatus').textContent='Module prêt — requêtes à la demande'}catch(e){$('mapStatus').textContent='Initialisation impossible : '+e.message;toast('Erreur au démarrage du module France.')}}
if(typeof module!=='undefined'&&module.exports)module.exports={getStorageLimits,isValidObservationFeature,parseObservationImport,isGeoJsonFile,getSearchSettings,buildPlaceSearchUrl,normalizeTaxonomy,escapeOverpassValue,queryBoxFromBounds,buildOverpassQuery,osmElementToItem,buildPoiAutocompleteUrl};
if(typeof document!=='undefined')document.addEventListener('DOMContentLoaded',init);
})();