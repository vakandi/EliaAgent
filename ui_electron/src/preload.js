const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('jarvis', {
  onConfig:      (cb) => ipcRenderer.on('config-updated', (_e, data) => cb(data)),
  onMessage:     (cb) => ipcRenderer.on('ntfy-message',   (_e, data) => cb(data)),
  onAgentStatus:     (cb) => ipcRenderer.on('agent-status',     (_e, data) => cb(data)),
  onRecordingStarted: (cb) => ipcRenderer.on('recording-started', (_e) => cb && cb()),
  onRecordingStopped: (cb) => ipcRenderer.on('recording-stopped', (_e) => cb && cb()),
  onStatusLiveToggle: (cb) => ipcRenderer.on('status-live-toggle', (_e, enabled) => cb(enabled)),
  onVoiceTriggerToggle: (cb) => ipcRenderer.on('voice-trigger-toggle', (_e, enabled) => cb(enabled)),
  onOpencodeContext: (cb) => ipcRenderer.on('opencode-context', (_e, data) => cb(data)),
  getConfig:       ()   => ipcRenderer.send('get-config'),
  hideWindow:      ()   => ipcRenderer.send('hide-window'),
  quitApp:         ()   => ipcRenderer.send('quit-app'),
  executeCommand:  ()   => ipcRenderer.send('execute-elia-command'),
  executeMiniCommand: () => ipcRenderer.send('execute-mini-orb'),
  stopRecording:   ()   => ipcRenderer.send('stop-recording'),
  setIgnoreMouseEvents: (ignore, options) => ipcRenderer.send('set-ignore-mouse-events', ignore, options),
  saveModelForCron: (model) => ipcRenderer.send('save-model-for-cron', model),
});

contextBridge.exposeInMainWorld('electronAPI', {
  send: (channel, data) => ipcRenderer.send(channel, data),
  on: (channel, callback) => {
    ipcRenderer.on(channel, (_event, ...args) => callback(...args));
  },
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel),
});

contextBridge.exposeInMainWorld('popupAPI', {
  runMorning: () => ipcRenderer.send('run-morning-routine'),
  runCron: () => ipcRenderer.send('run-cron-manual'),
  close: () => ipcRenderer.send('close-popup'),
  openUrl: (url) => ipcRenderer.send('open-url', url),
  openLogsTerminal: () => ipcRenderer.send('open-logs-terminal'),
});
