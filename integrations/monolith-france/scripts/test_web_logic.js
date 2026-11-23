'use strict';
const assert=require('node:assert/strict');
const {getStorageLimits,isValidObservationFeature,parseObservationImport}=require('../web/app.js');
const point=(lon,lat,properties={title:'test'})=>({type:'Feature',geometry:{type:'Point',coordinates:[lon,lat]},properties});

assert.equal(isValidObservationFeature(point(2.35,48.86)),true,'coordonnées WGS84 valides');
assert.equal(isValidObservationFeature(point(181,48.86)),false,'longitude hors plage');
assert.equal(isValidObservationFeature(point(2.35,91)),false,'latitude hors plage');
assert.equal(isValidObservationFeature(point('2.35',48.86)),false,'coordonnée chaîne refusée');
assert.equal(isValidObservationFeature({...point(2.35,48.86),geometry:{type:'LineString',coordinates:[[2,48],[3,49]]}}),false,'géométrie non ponctuelle refusée');
assert.equal(isValidObservationFeature(point(2.35,48.86,[])),false,'propriétés tableau refusées');
assert.equal(isValidObservationFeature(point(2.35,48.86,null)),true,'properties:null autorisé');

const limits={maxImportBytes:1024,maxFeatures:3};
const batch={type:'FeatureCollection',features:[point(2.35,48.86),point(3.1,49.2),point(181,48)]};
const parsed=parseObservationImport(batch,512,2,limits);
assert.equal(parsed.features.length,1,'respecte le plafond cumulé');
assert.equal(parsed.invalid,1,'compte les entités invalides');
assert.equal(parsed.skipped,1,'compte les entités au-delà du plafond');
assert.throws(()=>parseObservationImport(batch,2048,0,limits),/trop volumineux/);
assert.throws(()=>parseObservationImport({type:'Feature',geometry:{}},10,0,limits),/FeatureCollection/);
assert.throws(()=>parseObservationImport({type:'FeatureCollection',features:[1,2,3,4]},10,0,limits),/dépasse/);
assert.deepEqual(getStorageLimits({storage:{maxImportBytes:1234,maxFeatures:42}}),{maxImportBytes:1234,maxFeatures:42});
assert.deepEqual(getStorageLimits({storage:{maxImportBytes:-1,maxFeatures:'40'}}),{maxImportBytes:20*1024*1024,maxFeatures:5000});
console.log('PASS — GeoJSON validation, WGS84 ranges, per-file/cumulative limits and configuration fallbacks.');
