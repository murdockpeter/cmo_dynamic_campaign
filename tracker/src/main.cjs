'use strict';

const { app, BrowserWindow, ipcMain, safeStorage } = require('electron');
const fs = require('node:fs');
const fsp = require('node:fs/promises');
const http = require('node:http');
const path = require('node:path');
const { loadSituation } = require('./situation.cjs');

const APP_HOST = '127.0.0.1';
const APP_PORT = 43117;
const PROJECT_ROOT = path.resolve(__dirname, '..', '..');
const RENDERER_ROOT = path.resolve(__dirname, '..', 'renderer');
const MANIFEST_PATH = path.join(PROJECT_ROOT, 'days', 'day-001', 'manifest.json');
const INPUT_PATH = path.join(PROJECT_ROOT, 'days', 'day-001', 'input.json');
let mainWindow;
let localServer;
let reloadTimer;

if (!app.requestSingleInstanceLock()) app.quit();

function settingsPath() {
  return path.join(app.getPath('userData'), 'settings.json');
}

async function readSettings() {
  try { return JSON.parse(await fsp.readFile(settingsPath(), 'utf8')); } catch { return {}; }
}

async function writeSettings(settings) {
  await fsp.mkdir(path.dirname(settingsPath()), { recursive: true });
  await fsp.writeFile(settingsPath(), `${JSON.stringify(settings, null, 2)}\n`, 'utf8');
}

async function getMapsKey() {
  const settings = await readSettings();
  if (!safeStorage.isEncryptionAvailable()) return '';
  let encrypted = settings.mapsKey;
  if (!encrypted) {
    try {
      const legacyPath = path.join(app.getPath('appData'), 'gcbh-mission-map', 'settings.json');
      encrypted = JSON.parse(await fsp.readFile(legacyPath, 'utf8')).mapsKey;
    } catch { encrypted = ''; }
  }
  if (encrypted) {
    try { return safeStorage.decryptString(Buffer.from(encrypted, 'base64')); } catch { /* app-bound ciphertext; try local reports */ }
  }
  const reportRoot = path.resolve(PROJECT_ROOT, '..', 'il2korea_dynamic_campaign', 'reports');
  for (const filename of ['campaign-tracker.html', 'current-situation.html', 'historical-frontline.html']) {
    try {
      const html = await fsp.readFile(path.join(reportRoot, filename), 'utf8');
      const match = html.match(/const GOOGLE_MAPS_API_KEY="([A-Za-z0-9_-]+)";/);
      if (match) return match[1];
    } catch { /* local fallback is optional */ }
  }
  return '';
}

async function setMapsKey(key) {
  const value = String(key || '').trim();
  const settings = await readSettings();
  if (!value) {
    settings.mapsKey = '';
    await writeSettings(settings);
    return { saved: true, encrypted: false };
  }
  if (!/^[A-Za-z0-9_-]+$/.test(value)) return { saved: false, error: 'The key contains unexpected characters.' };
  if (!safeStorage.isEncryptionAvailable()) return { saved: false, error: 'OS-backed encryption is unavailable.' };
  settings.mapsKey = safeStorage.encryptString(value).toString('base64');
  await writeSettings(settings);
  return { saved: true, encrypted: true };
}

function contentType(filePath) {
  return ({ '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8' })[path.extname(filePath)] || 'application/octet-stream';
}

function startServer() {
  return new Promise((resolve, reject) => {
    localServer = http.createServer(async (request, response) => {
      try {
        const requestPath = new URL(request.url, `http://${APP_HOST}`).pathname;
        const relative = requestPath === '/' ? 'index.html' : decodeURIComponent(requestPath.slice(1));
        const filePath = path.resolve(RENDERER_ROOT, relative);
        if (!filePath.startsWith(`${RENDERER_ROOT}${path.sep}`) && filePath !== path.join(RENDERER_ROOT, 'index.html')) {
          response.writeHead(403).end('Forbidden'); return;
        }
        const body = await fsp.readFile(filePath);
        response.writeHead(200, {
          'Content-Type': contentType(filePath),
          'Cache-Control': 'no-store',
          'Content-Security-Policy': [
            "default-src 'self'", "script-src 'self' https://maps.googleapis.com https://maps.gstatic.com",
            "style-src 'self' 'unsafe-inline'", "img-src 'self' data: https://*.googleapis.com https://*.gstatic.com https://*.google.com https://*.ggpht.com",
            "connect-src 'self' https://maps.googleapis.com https://maps.gstatic.com https://*.googleapis.com", "worker-src 'self' blob:"
          ].join('; '),
        });
        response.end(body);
      } catch { response.writeHead(404).end('Not found'); }
    });
    localServer.once('error', reject);
    localServer.listen(APP_PORT, APP_HOST, resolve);
  });
}

function watchData() {
  for (const filePath of [MANIFEST_PATH, INPUT_PATH]) {
    fs.watch(filePath, () => {
      clearTimeout(reloadTimer);
      reloadTimer = setTimeout(() => mainWindow?.webContents.send('situation:changed'), 250);
    });
  }
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1580, height: 960, minWidth: 1100, minHeight: 720, backgroundColor: '#061018',
    title: 'SCS-2026 Common Operational Picture',
    webPreferences: { preload: path.join(__dirname, 'preload.cjs'), nodeIntegration: false, contextIsolation: true, sandbox: true },
  });
  mainWindow.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (!url.startsWith(`http://${APP_HOST}:${APP_PORT}/`)) event.preventDefault();
  });
  await mainWindow.loadURL(`http://${APP_HOST}:${APP_PORT}/`);
  if (process.env.CMO_TRACKER_SMOKE_TEST === '1') {
    setTimeout(async () => {
      const result = await mainWindow.webContents.executeJavaScript(`(() => { const snapshot = (side) => { document.querySelector('[data-side="' + side + '"]').click(); return { nodes: document.querySelectorAll('.node-card').length, missions: document.querySelectorAll('.mission').length, missionBadge: document.querySelector('#mission-count').textContent, blueSummary: !document.querySelector('#blue-balance').hidden, redSummary: !document.querySelector('#red-balance').hidden }; }; const blueView = snapshot('BLUE'); const redView = snapshot('RED'); const allView = snapshot('all'); document.querySelector('#search').value = 'SSN'; document.querySelector('#search').dispatchEvent(new Event('input')); document.querySelector('#toggle-missions').click(); document.querySelector('#toggle-satellite').click(); document.querySelector('.node-card')?.click(); document.querySelector('#reset-view-button').click(); const reset = { nodes: document.querySelectorAll('.node-card').length, missions: document.querySelectorAll('.mission').length, missionBadge: document.querySelector('#mission-count').textContent, selectedSide: document.querySelector('.side-segment.active').dataset.side, blueSummary: !document.querySelector('#blue-balance').hidden, redSummary: !document.querySelector('#red-balance').hidden, search: document.querySelector('#search').value, layersOn: [...document.querySelectorAll('.map-tools input')].filter((input) => input.id !== 'toggle-satellite').every((input) => input.checked), satellite: document.querySelector('#toggle-satellite').checked, detailsCleared: !document.querySelector('#detail-empty').hidden }; return { title: document.title, blueView, redView, allView, reset, blue: document.querySelector('#blue-total').textContent, red: document.querySelector('#red-total').textContent, mapOnline: document.querySelector('#map-placeholder').hidden, mapMessage: document.querySelector('#settings-message').textContent }; })()`);
      console.log(`TRACKER_SMOKE|${JSON.stringify(result)}`);
      app.quit();
    }, 8000);
  }
}

ipcMain.handle('situation:load', () => loadSituation(PROJECT_ROOT));
ipcMain.handle('maps-key:get', getMapsKey);
ipcMain.handle('maps-key:set', (_event, key) => setMapsKey(key));

app.whenReady().then(async () => { await startServer(); watchData(); await createWindow(); });
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
app.on('before-quit', () => localServer?.close());
