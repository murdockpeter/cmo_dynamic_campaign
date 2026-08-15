'use strict';

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('campaignTracker', {
  loadSituation: () => ipcRenderer.invoke('situation:load'),
  getMapsKey: () => ipcRenderer.invoke('maps-key:get'),
  setMapsKey: (key) => ipcRenderer.invoke('maps-key:set', key),
  onSituationChanged: (callback) => {
    const listener = () => callback();
    ipcRenderer.on('situation:changed', listener);
    return () => ipcRenderer.removeListener('situation:changed', listener);
  },
});
