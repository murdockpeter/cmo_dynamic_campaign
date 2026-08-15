'use strict';

const { spawn } = require('node:child_process');
const path = require('node:path');
const electronPath = require('electron');

const environment = { ...process.env };
delete environment.ELECTRON_RUN_AS_NODE;

const child = spawn(electronPath, ['.'], {
  cwd: path.resolve(__dirname, '..'), env: environment, stdio: 'inherit', windowsHide: false,
});
child.on('error', (error) => { console.error(`Unable to start Electron: ${error.message}`); process.exitCode = 1; });
child.on('exit', (code) => { process.exitCode = code ?? 0; });
