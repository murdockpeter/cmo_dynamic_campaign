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
  'TG B-1 George Washington CSG': [15.0, 125.1],
  'TG B-2 Philippine West Sea SAG': [10.8, 117.8],
  'TG B-3 America ARG': [10.2, 121.1],
  'TG R-1 Shandong CSG': [16.3, 114.5],
  'TG R-2 Southern Theater SAG': [12.5, 113.8],
  'TG R-3 Hainan Amphibious Group': [17.8, 111.8],
};

const ROUTES = [
  ['BLUE', 'TG B-1 George Washington CSG', [[15,125.1],[14.5,124.9],[13.8,124.5]]],
  ['BLUE', 'TG B-2 Philippine West Sea SAG', [[10.8,117.8],[11.4,117.3],[12,116.9]]],
  ['BLUE', 'TG B-3 America ARG', [[10.2,121.1],[10.6,120.3],[11.2,119.7]]],
  ['RED', 'TG R-1 Shandong CSG', [[16.3,114.5],[15.5,114.2],[14.7,114]]],
  ['RED', 'TG R-2 Southern Theater SAG', [[12.5,113.8],[11.8,114],[10.8,114.5]]],
  ['RED', 'TG R-3 Hainan Amphibious Group', [[17.8,111.8],[17,112.3],[16,112.9]]],
];

const MISSIONS = [
  ['BLUE','AAW','West Luzon CAP',[[14,117.5],[18,117.5],[18,120],[14,120]]],
  ['BLUE','AAW','Palawan CAP',[[8,116.8],[12.5,116.8],[12.5,119.3],[8,119.3]]],
  ['BLUE','ASW','Palawan ASW',[[8,115],[12.5,115],[12.5,117.5],[8,117.5]]],
  ['BLUE','AEW','AEW Central',[[12.3,122],[14,122]]],
  ['BLUE','TANKER','Tanker Central',[[11.5,122.5],[14.5,122.5]]],
  ['RED','AAW','Hainan CAP',[[16.5,109.5],[22,109.5],[22,114],[16.5,114]]],
  ['RED','AAW','Spratly CAP',[[8,111],[12,111],[12,115],[8,115]]],
  ['RED','ASW','Central Basin ASW',[[11,114],[17,114],[17,118],[11,118]]],
  ['RED','AEW','AEW Hainan',[[17,112],[19,112]]],
  ['RED','TANKER','Tanker Hainan',[[18,113],[20,113]]],
];

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
    submarines, routes: ROUTES.map(([side,name,points]) => ({ side,name,points })),
    missions: MISSIONS.map(([side,type,name,points]) => ({ side,type,name,points })),
    boundaries: [
      { name: 'Mainland strike restriction', note: 'Attacks require an explicit escalation event.', points: [[18.0,108.2],[23.0,108.2],[23.0,117.5],[18.0,117.5]] },
    ],
  };
}

module.exports = { loadSituation };
