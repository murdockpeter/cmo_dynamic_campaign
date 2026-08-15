const $ = (id) => document.getElementById(id);
const elements = Object.fromEntries([
  'game-day','start-time','pause-time','live-status','reload-button','settings-button','scenario-title','campaign-meta',
  'blue-total','red-total','blue-breakdown','red-breakdown','node-count','search','side-filter','node-list','map','map-placeholder',
  'placeholder-key-button','toggle-forces','toggle-routes','toggle-missions','toggle-restrictions','toggle-satellite','detail-empty',
  'detail','detail-side','detail-kind','detail-name','detail-position','detail-stats','package-list','element-count','element-list',
  'mission-list','settings-dialog','settings-form','api-key','settings-message','save-key-button'
].map((id) => [id.replaceAll('-', '_'), $(id)]));

const COLORS = { BLUE: '#3ba8ff', RED: '#f0525a' };
const state = { data: null, map: null, mapsReady: false, markers: [], routes: [], missions: [], restrictions: [], selected: null, info: null };

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({ '&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;' })[char]);
}

function formatTime(value) {
  return new Intl.DateTimeFormat('en-US', { month:'short', day:'2-digit', hour:'2-digit', minute:'2-digit', timeZone:'UTC', hour12:false }).format(new Date(value)).toUpperCase() + 'Z';
}

function locationText(position) {
  if (!position) return 'POSITION UNAVAILABLE';
  return `${Math.abs(position[0]).toFixed(3)}°${position[0] >= 0 ? 'N' : 'S'} / ${Math.abs(position[1]).toFixed(3)}°${position[1] >= 0 ? 'E' : 'W'}`;
}

function allNodes() {
  const subs = state.data.submarines.map((sub) => ({
    ...sub, units: [{ campaign_id: sub.name, side: sub.side, kind:'submarine', dbid:sub.dbid }],
    packages: { [sub.name]: { id:sub.name, kind:'submarine', count:1, ready:1, dbids:[sub.dbid] } }, kinds:{ submarine:1 }
  }));
  return [...state.data.nodes, ...subs];
}

function matchesFilter(node) {
  if (elements.side_filter.value !== 'all' && node.side !== elements.side_filter.value) return false;
  const query = elements.search.value.trim().toLowerCase();
  if (!query) return true;
  return [node.name, ...node.units.flatMap((unit) => [unit.campaign_id, unit.dbid])].some((value) => String(value).toLowerCase().includes(query));
}

function kindSummary(node) {
  return Object.entries(node.kinds).map(([kind,count]) => `${count} ${kind}`).join(' • ');
}

function renderOverview() {
  const { meta, totals } = state.data;
  elements.game_day.textContent = `DAY ${String(meta.day).padStart(3,'0')}`;
  elements.start_time.textContent = formatTime(meta.start);
  elements.pause_time.textContent = formatTime(meta.operational_pause);
  elements.scenario_title.textContent = meta.title;
  elements.campaign_meta.textContent = `${meta.campaign} • ${meta.database} • ${meta.source}`;
  elements.blue_total.textContent = totals.BLUE;
  elements.red_total.textContent = totals.RED;
  elements.blue_breakdown.textContent = '150 AIR • 11 SURFACE • 4 SUB';
  elements.red_breakdown.textContent = '149 AIR • 16 SURFACE • 6 SUB';
  renderNodeList(); renderMissionList();
}

function renderNodeList() {
  const nodes = allNodes().filter(matchesFilter);
  elements.node_count.textContent = nodes.length;
  elements.node_list.innerHTML = nodes.map((node) => `
    <article class="node-card ${state.selected?.name === node.name ? 'selected' : ''}" data-node="${escapeHtml(node.name)}" style="--side-color:${COLORS[node.side]}">
      <strong>${escapeHtml(node.name)}</strong><b>${node.units.length}</b><span>${escapeHtml(kindSummary(node))}</span>
    </article>`).join('') || '<div class="empty-detail">No matching elements</div>';
  elements.node_list.querySelectorAll('[data-node]').forEach((card) => card.addEventListener('click', () => selectNode(card.dataset.node, true)));
  applyVisibility();
}

function renderMissionList() {
  elements.mission_list.innerHTML = state.data.missions.map((mission, index) => `
    <article class="mission" data-mission="${index}" style="--side-color:${COLORS[mission.side]}"><strong>${mission.side} / ${escapeHtml(mission.type)}</strong><span>${escapeHtml(mission.name)}</span></article>`).join('');
  elements.mission_list.querySelectorAll('[data-mission]').forEach((card) => card.addEventListener('click', () => focusMission(Number(card.dataset.mission))));
}

function selectNode(name, pan = false) {
  const node = allNodes().find((item) => item.name === name);
  if (!node) return;
  state.selected = node;
  elements.detail_empty.hidden = true; elements.detail.hidden = false;
  elements.detail_side.textContent = node.side; elements.detail_side.style.setProperty('--side-color', COLORS[node.side]);
  elements.detail_kind.textContent = Object.keys(node.kinds).join(' / ');
  elements.detail_name.textContent = node.name; elements.detail_position.textContent = locationText(node.position);
  const ready = Object.values(node.packages).reduce((sum,pkg) => sum + pkg.ready, 0);
  const dbids = new Set(node.units.map((unit) => unit.dbid)).size;
  elements.detail_stats.innerHTML = [['TRACKED',node.units.length],['READY / ARMED',ready],['PLATFORM DBIDS',dbids]].map(([label,value]) => `<div class="detail-stat"><strong>${value}</strong><span>${label}</span></div>`).join('');
  elements.package_list.innerHTML = Object.values(node.packages).map((pkg) => `<div class="package" style="--side-color:${COLORS[node.side]}"><strong>${escapeHtml(pkg.id)}</strong><b>${pkg.ready}/${pkg.count}</b><span>${escapeHtml(pkg.kind.toUpperCase())} • DBID ${pkg.dbids.join(', ')}</span></div>`).join('');
  elements.element_count.textContent = node.units.length;
  elements.element_list.innerHTML = node.units.map((unit) => `<div class="element"><span>${escapeHtml(unit.campaign_id)}</span><b>DBID ${unit.dbid}${unit.loadout_id ? ` / LOAD ${unit.loadout_id}` : ''}</b></div>`).join('');
  renderNodeList();
  if (pan && state.map) { state.map.panTo({ lat:node.position[0], lng:node.position[1] }); state.map.setZoom(Math.max(state.map.getZoom(), 7)); }
}

function markerIcon(node) {
  const isSub = node.kinds.submarine;
  const isAirbase = node.kinds.aircraft && !node.kinds.ship;
  return {
    path: isSub ? 'M -8 2 L -3 -3 L 4 -3 L 8 2 L 4 4 L -4 4 Z' : isAirbase ? 'M 0 -9 L 9 0 L 0 9 L -9 0 Z' : 'M -10 -5 L 7 -5 L 11 0 L 7 5 L -10 5 Z',
    fillColor: COLORS[node.side], fillOpacity:.84, strokeColor:'#071018', strokeWeight:1.6, scale:1,
    anchor: new google.maps.Point(0,0), labelOrigin:new google.maps.Point(0, isAirbase ? 17 : 14),
  };
}

function drawMap() {
  [...state.markers,...state.routes,...state.missions,...state.restrictions].forEach((overlay) => overlay.setMap(null));
  state.markers=[];state.routes=[];state.missions=[];state.restrictions=[];
  const bounds = new google.maps.LatLngBounds();
  for (const node of allNodes()) {
    const marker = new google.maps.Marker({
      position:{lat:node.position[0],lng:node.position[1]}, map:state.map, title:node.name, icon:markerIcon(node),
      label:{ text:String(node.units.length), color:'#eaf7fa', fontSize:'9px', fontWeight:'800' }, zIndex:node.kinds.submarine ? 5 : 10,
    });
    marker.__node=node; marker.addListener('click', () => {
      selectNode(node.name);
      state.info.setContent(`<div style="color:#10222d;font:12px system-ui;min-width:190px"><b>${escapeHtml(node.name)}</b><br>${node.side} • ${node.units.length} tracked<br><small>${locationText(node.position)}</small></div>`);
      state.info.open({ map:state.map, anchor:marker });
    });
    state.markers.push(marker); bounds.extend(marker.getPosition());
    if (node.course?.length) {
      const line = new google.maps.Polyline({ path:[node.position,...node.course].map(([lat,lng]) => ({lat,lng})), strokeColor:COLORS[node.side], strokeOpacity:.72, strokeWeight:1.5, icons:[{icon:{path:google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale:2},offset:'100%'}], map:state.map });
      line.__side=node.side; state.routes.push(line);
    }
  }
  for (const route of state.data.routes) {
    const line = new google.maps.Polyline({ path:route.points.map(([lat,lng]) => ({lat,lng})), strokeColor:COLORS[route.side], strokeOpacity:.74, strokeWeight:2, icons:[{icon:{path:google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale:2.5},offset:'100%'}], map:state.map });
    line.__side=route.side; state.routes.push(line);
  }
  for (const mission of state.data.missions) {
    const options = { strokeColor:COLORS[mission.side],strokeOpacity:.65,strokeWeight:1.3,fillColor:COLORS[mission.side],fillOpacity:.09,map:state.map };
    const overlay = mission.points.length > 2
      ? new google.maps.Polygon({ ...options, paths:mission.points.map(([lat,lng])=>({lat,lng})) })
      : new google.maps.Polyline({ ...options, path:mission.points.map(([lat,lng])=>({lat,lng})),strokeWeight:4,strokeOpacity:.32 });
    overlay.__side=mission.side; overlay.__mission=mission; overlay.addListener('click', () => showMissionInfo(overlay, mission)); state.missions.push(overlay);
  }
  for (const area of state.data.boundaries) {
    const overlay = new google.maps.Polygon({ paths:area.points.map(([lat,lng])=>({lat,lng})),strokeColor:'#ef9d45',strokeOpacity:.7,strokeWeight:1,fillColor:'#ef9d45',fillOpacity:.055,map:state.map });
    overlay.addListener('click', (event) => { state.info.setPosition(event.latLng);state.info.setContent(`<div style="color:#10222d;font:12px system-ui"><b>${area.name}</b><br>${area.note}</div>`);state.info.open({map:state.map}); });state.restrictions.push(overlay);
  }
  state.map.fitBounds(bounds, 42); applyVisibility();
}

function showMissionInfo(overlay, mission) {
  const bounds = new google.maps.LatLngBounds(); mission.points.forEach(([lat,lng])=>bounds.extend({lat,lng}));
  state.info.setPosition(bounds.getCenter());state.info.setContent(`<div style="color:#10222d;font:12px system-ui"><b>${mission.side} ${mission.name}</b><br>${mission.type} mission layer</div>`);state.info.open({map:state.map});
}

function focusMission(index) {
  if (!state.map) return; const mission=state.data.missions[index];const bounds=new google.maps.LatLngBounds();mission.points.forEach(([lat,lng])=>bounds.extend({lat,lng}));state.map.fitBounds(bounds,80);showMissionInfo(state.missions[index],mission);
}

function applyVisibility() {
  if (!state.mapsReady) return;
  const side=elements.side_filter.value;
  state.markers.forEach((marker)=>marker.setMap(elements.toggle_forces.checked && matchesFilter(marker.__node) ? state.map:null));
  state.routes.forEach((route)=>route.setMap(elements.toggle_routes.checked && (side==='all'||route.__side===side) ? state.map:null));
  state.missions.forEach((mission)=>mission.setMap(elements.toggle_missions.checked && (side==='all'||mission.__side===side) ? state.map:null));
  state.restrictions.forEach((area)=>area.setMap(elements.toggle_restrictions.checked ? state.map:null));
}

async function loadGoogleMaps(key) {
  if (!key || state.mapsReady) return;
  await new Promise((resolve,reject) => {
    let settled=false;const finish=(fn,value)=>{if(settled)return;settled=true;clearTimeout(timeout);fn(value);};
    globalThis.__cmoTrackerGoogleReady=()=>finish(resolve);
    globalThis.gm_authFailure=()=>finish(reject,new Error('Google rejected the API key. Check API enablement and localhost restrictions.'));
    const script=document.createElement('script');script.src=`https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(key)}&loading=async&v=weekly&callback=__cmoTrackerGoogleReady`;script.async=true;script.onerror=()=>finish(reject,new Error('Google Maps could not be downloaded.'));document.head.append(script);
    const timeout=setTimeout(()=>finish(reject,new Error('Google Maps did not initialize within 15 seconds.')),15000);
  });
  state.map=new google.maps.Map(elements.map,{center:{lat:14.5,lng:117},zoom:5,mapTypeId:'terrain',mapTypeControl:false,streetViewControl:false,fullscreenControl:true,gestureHandling:'greedy',styles:[{featureType:'poi',stylers:[{visibility:'off'}]},{featureType:'transit',stylers:[{visibility:'off'}]}]});
  state.info=new google.maps.InfoWindow();state.mapsReady=true;elements.map_placeholder.hidden=true;drawMap();
}

async function loadData() {
  state.data=await window.campaignTracker.loadSituation();renderOverview();if(state.mapsReady)drawMap();elements.live_status.textContent='LIVE DATA';
}

function showSettings() { elements.settings_message.textContent='';elements.api_key.value='';elements.settings_dialog.showModal(); }
elements.settings_button.addEventListener('click',showSettings);elements.placeholder_key_button.addEventListener('click',showSettings);
elements.settings_form.addEventListener('submit',async(event)=>{if(event.submitter!==elements.save_key_button)return;event.preventDefault();const result=await window.campaignTracker.setMapsKey(elements.api_key.value);if(!result.saved){elements.settings_message.textContent=result.error;return;}elements.settings_message.textContent='Saved with OS-backed encryption. Loading map…';try{await loadGoogleMaps(elements.api_key.value);elements.settings_dialog.close();}catch(error){elements.settings_message.textContent=error.message;}});
elements.reload_button.addEventListener('click',loadData);elements.search.addEventListener('input',renderNodeList);elements.side_filter.addEventListener('change',()=>{renderNodeList();applyVisibility();});
for(const key of ['toggle_forces','toggle_routes','toggle_missions','toggle_restrictions'])elements[key].addEventListener('change',applyVisibility);
elements.toggle_satellite.addEventListener('change',()=>state.map?.setMapTypeId(elements.toggle_satellite.checked?'hybrid':'terrain'));
window.campaignTracker.onSituationChanged(()=>{elements.live_status.textContent='SOURCE CHANGED';loadData();});

await loadData();
const key=await window.campaignTracker.getMapsKey();
if(key){try{await loadGoogleMaps(key);}catch(error){elements.settings_message.textContent=error.message;showSettings();}}
