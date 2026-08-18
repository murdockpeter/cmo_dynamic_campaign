'use strict';

const fs = require('node:fs');
const path = require('node:path');

const LOCATIONS = {
  'Basa Air Base': [14.986, 120.493],
  'Puerto Princesa International Airport/Antonio Bautista AB': [9.742, 118.759],
  'Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport': [10.307, 123.979],
  'Lingshui AB (PLAN)': [18.505, 110.039],
  'Suixi AB  (PLAAF)': [21.214, 110.358],
  'Woody Island': [16.833, 112.333],
  'Fiery Cross Reef': [9.550, 112.883],
};

function nodeName(unit) { return unit.base || unit.group || unit.campaign_id; }
function packageName(id) { return id.replace(/-\d{2,4}$/, ''); }

function loadSituation(root) {
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'days/day-001/manifest.json'), 'utf8'));
  const input = JSON.parse(fs.readFileSync(path.join(root, 'days/day-001/input.json'), 'utf8'));
  const nodes = new Map();
  for (const unit of manifest.units) {
    const name = nodeName(unit);
    const position = unit.start || LOCATIONS[name];
    if (!position) continue;
    if (!nodes.has(name)) nodes.set(name, { name, side: unit.side, position, units: [], packages: {}, kinds: {} });
    const node = nodes.get(name);
    node.units.push(unit);
    node.kinds[unit.kind] = (node.kinds[unit.kind] || 0) + 1;
    const packageId = packageName(unit.campaign_id);
    if (!node.packages[packageId]) node.packages[packageId] = { id: packageId, kind: unit.kind, count: 0, ready: 0, dbids: [] };
    const pkg = node.packages[packageId];
    pkg.count += 1;
    if (unit.kind !== 'aircraft' || unit.loadout_id !== 4) pkg.ready += 1;
    if (!pkg.dbids.includes(unit.dbid)) pkg.dbids.push(unit.dbid);
  }
  const submarines = manifest.units.filter((unit) => unit.kind === 'submarine').map((unit) => ({
    name: unit.campaign_id, side: unit.side, position: unit.start, course: unit.course, kind: 'submarine', dbid: unit.dbid,
  }));
  const totals = manifest.units.reduce((out, unit) => {
    out[unit.side] = (out[unit.side] || 0) + 1;
    out[unit.kind] = (out[unit.kind] || 0) + 1;
    return out;
  }, {});
  return {
    meta: { ...input, updated: new Date().toISOString(), source: 'Day 1 planning baseline' }, totals,
    nodes: [...nodes.values()].filter((node) => !node.name.includes('SSN-') && !node.name.includes('SSK-') && !node.name.includes('SSBN-')),
    submarines,
    routes: (input.navigation?.routes || []).filter((route) => route.domain === 'surface'),
    missions: (input.missions || []).map((mission) => ({ side:mission.side,type:mission.type,name:mission.display_name || mission.name,points:mission.points })),
    boundaries: input.boundaries || [],
  };
}

module.exports = { loadSituation };
