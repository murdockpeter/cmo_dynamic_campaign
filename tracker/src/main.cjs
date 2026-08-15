'use strict';

const { app, BrowserWindow, ipcMain, safeStorage } = require('electron');
const fs = require('node:fs');
const fsp = require('node:fs/promises');
const http = require('node:http');
const path = require('node:path');
const { loadSituation } = require('./situation.cjs');

const APP_HOST = '127.0.0.1';
const APP_PORT = 43127;
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
  if (!encrypted) return '';
  try { return safeStorage.decryptString(Buffer.from(encrypted, 'base64')); } catch { return ''; }
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
}

ipcMain.handle('situation:load', () => loadSituation(PROJECT_ROOT));
ipcMain.handle('maps-key:get', getMapsKey);
ipcMain.handle('maps-key:set', (_event, key) => setMapsKey(key));

app.whenReady().then(async () => { await startServer(); watchData(); await createWindow(); });
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
app.on('before-quit', () => localServer?.close());
