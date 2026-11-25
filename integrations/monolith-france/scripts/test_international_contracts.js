'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { spawnSync } = require('node:child_process');

const root = process.cwd();
const ukHtml = fs.readFileSync(root + '/index.html', 'utf8');
const gbProfile = JSON.parse(fs.readFileSync(root + '/integrations/monolith-france/config/countries/profiles/GB.json', 'utf8'));
const frApp = fs.readFileSync(root + '/integrations/monolith-france/web/app.js', 'utf8');
const frHtml = fs.readFileSync(root + '/integrations/monolith-france/web/index.html', 'utf8');

const inlineScripts = [...ukHtml.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.ok(inlineScripts.length >= 1, 'UK inline application script exists');
const syntax = spawnSync('node', ['--check'], { input: inlineScripts[inlineScripts.length - 1][1], encoding: 'utf8' });
assert.equal(syntax.status, 0, 'UK inline application JavaScript syntax: ' + syntax.stderr);

const helperMatch = ukHtml.match(/function groupCandidateFeaturesByScreenCell\(features, projectPoint, cellSize, selectedKey, keyForFeature, isKnownFn\) \{[\s\S]*?\n    \}/);
assert.ok(helperMatch, 'pure screen-cell grouping helper is present');
const groupFeatures = vm.runInNewContext('(' + helperMatch[0] + ')');
const makeFeature = (id, x, y, domain, known = false) => ({
  properties: {
    id,
    lat: 50 + y / 1000,
    lon: -2 + x / 1000,
    target_domain: domain,
    context_category: known ? 'rediscovered_nhle_scheduled' : 'unidentified_candidate'
  },
  screen: { x, y }
});
const fixtures = [
  makeFeature('a', 10, 10, 'prehistoric'),
  makeFeature('b', 18, 14, 'roman'),
  makeFeature('c', 90, 14, 'enclosure'),
  makeFeature('d', 12, 11, 'prehistoric', true)
];
const groups = groupFeatures(
  fixtures,
  ([lat, lon]) => {
    const f = fixtures.find(item => item.properties.lat === lat && item.properties.lon === lon);
    return f.screen;
  },
  48,
  'd',
  p => p.id,
  p => p.context_category === 'rediscovered_nhle_scheduled'
);
assert.equal(groups.length, 2, 'features in nearby cells are grouped; separate cells remain separate');
const first = groups.find(group => group.features.some(feature => feature.properties.id === 'a'));
assert.equal(first.count, 3, 'all source features retained in the group');
assert.equal(first.domains.roman, 1, 'Roman count remains separate');
assert.equal(first.knownCount, 1, 'known-site count remains explicit');
assert.equal(first.selected, true, 'selected record state remains discoverable in aggregate');

assert.ok(ukHtml.includes('markerZoom<11'), 'aggregate markers are used below detail zoom');
assert.ok(ukHtml.includes('Math.min(11,markerZoom+2)'), 'cluster click zooms into the grouped area');
assert.ok(ukHtml.includes('new ShapeMarker'), 'historical individual marker rendering remains available');
assert.ok(!ukHtml.includes('130279.0'), 'hard-coded national percentage denominator has been removed');
assert.ok(ukHtml.includes('England campaign'), 'campaign extent is stated explicitly');
assert.equal(gbProfile.capabilities.activeSurveyExtent, 'England', 'GB profile distinguishes actual campaign extent');
assert.ok(gbProfile.capabilities.activeSurveyExtentNote.includes('United Kingdom'), 'profile documents the territory/survey distinction');

assert.ok(frApp.includes("layer.on('tileerror'"), 'France tile errors are monitored');
assert.ok(frApp.includes('function buildTileHealthSummary'), 'France tile status summary is available');
assert.ok(frHtml.includes('id="tileHealthNote"'), 'France map shows tile status to users');
console.log('PASS — international contracts: UK aggregation, campaign scope, syntax, France tile diagnostics.');
