const { app, BrowserWindow, ipcMain, screen, Tray, Menu, nativeImage, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');
const https = require('https');
const { execSync, spawn } = require('child_process');

const envPath = path.join(__dirname, '..', '..', '.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  envContent.split('\n').forEach(line => {
    const match = line.match(/^([^#=]+)=(.*)$/);
    if (match) process.env[match[1].trim()] = match[2].trim();
  });
}

let mainWindow = null;
let setPositionOverlay = null;
let agentStatusInterval = null;
let tray = null;
let telegramBotProcess = null;
let discordBotProcess = null;
let configPath = path.join(__dirname, '..', 'config.json');
let config = {};
let ntfyStream = null;
let isProcessingCron = false;
let isProcessingMorning = false;
let morningPopup = null;
let cronPopup = null;
let welcomePopup = null;
let proxyPopup = null;
let welcomeShown = false;

const EliaAIRoot = path.join(__dirname, '..', '..');
const contextPath = path.join(EliaAIRoot, 'context');

function loadContextFiles() {
  const context = { memory: '', tools: '', business: '' };
  try {
    context.memory = fs.readFileSync(path.join(contextPath, 'MEMORY.md'), 'utf8').substring(0, 500);
  } catch (e) {}
  try {
    context.tools = fs.readFileSync(path.join(contextPath, 'TOOLS.md'), 'utf8').substring(0, 500);
  } catch (e) {}
  try {
    context.business = fs.readFileSync(path.join(contextPath, 'business.md'), 'utf8').substring(0, 500);
  } catch (e) {}
  return context;
}

function getOpencodeStatus() {
  try {
    const pgrepOut = execSync('pgrep -f "oh-my-opencode" 2>/dev/null || pgrep -f "start_agents\\.sh" 2>/dev/null || pgrep -f "trigger_opencode" 2>/dev/null || true', { encoding: 'utf8' }).trim();
    const pids = pgrepOut ? pgrepOut.split(/\s+/).filter(Boolean) : [];
    return pids.length > 0;
  } catch (e) {
    return false;
  }
}

function loadConfig() {
  try {
    config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    trayMenuState.statusLive = config.display?.statusLive ?? false;
    trayMenuState.voiceTrigger = config.display?.voiceTrigger ?? false;
  } catch (e) {
    console.error('Config load error:', e);
    config = { ntfy: { server: 'https://ntfy.sh', topic: 'test', token: '' }, display: {} };
  }
}

const WIN_W = 350;
const WIN_H = 250;
const positionPath = path.join(__dirname, '..', '.jarvis-position.json');
const SET_POSITION_FLAG = process.argv.includes('--set-position');

function getSavedPosition() {
  try {
    const data = JSON.parse(fs.readFileSync(positionPath, 'utf8'));
    if (typeof data.x === 'number' && typeof data.y === 'number') return { x: data.x, y: data.y };
  } catch (e) {}
  return null;
}

function savePosition(x, y) {
  try {
    fs.writeFileSync(positionPath, JSON.stringify({ x, y }) + '\n', 'utf8');
  } catch (e) {
    console.error('Save position:', e.message);
  }
}

function getDefaultBounds() {
  const saved = getSavedPosition();
  if (saved) return { x: saved.x, y: saved.y, width: WIN_W, height: WIN_H };
  const display = screen.getPrimaryDisplay();
  const { x: dx, y: dy, width: dw, height: dh } = display.bounds;
  return {
    x: dx + dw - WIN_W,
    y: dy + dh - WIN_H,
    width: WIN_W,
    height: WIN_H
  };
}

function createWindow() {
  loadConfig();
  const bounds = getDefaultBounds();

  mainWindow = new BrowserWindow({
    width: bounds.width,
    height: bounds.height,
    x: bounds.x,
    y: bounds.y,
    show: false,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    hasShadow: false,
    resizable: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  mainWindow.once('ready-to-show', () => {
    const b = getDefaultBounds();
    mainWindow.setBounds(b);
    mainWindow.show();
    setTimeout(() => mainWindow.setBounds(getDefaultBounds()), 50);
  });

  // Fix: Restore position when macOS menu bar or external forces move the window
  let _isRestoringPosition = false;
  mainWindow.on('moved', () => {
    if (_isRestoringPosition) return;
    _isRestoringPosition = true;
    // Restore saved position immediately (macOS menu bar can nudge the window)
    const saved = getSavedPosition();
    if (saved) {
      mainWindow.setPosition(saved.x, saved.y);
    }
    _isRestoringPosition = false;
  });

  mainWindow.loadFile(path.join(__dirname, 'index.html'));
  mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: false });

  // Watch config changes
  fs.watch(configPath, () => {
    loadConfig();
    mainWindow?.webContents.send('config-updated', config);
    restartNtfyStream();
  });

  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.webContents.send('config-updated', config);
    startNtfyStream();
    startAgentStatusPolling();
    setTimeout(() => mainWindow?.setBounds(getDefaultBounds()), 150);
    mainWindow.setIgnoreMouseEvents(false, { forward: true });
  });
}

// ── Agent status (start_agents.sh / opencode) ─────────────────────────────
function getAgentStatus() {
  try {
    // Get the opencode serve PID (daemon) to exclude it
    const servePid = execSync('pgrep -f "opencode serve$" 2>/dev/null || echo ""', { encoding: 'utf8' }).trim().split(/\s+/)[0];
    
    // Match EliaAI-specific agent processes first (most specific)
    let pgrepOut = execSync(
      'pgrep -f "oh-my-opencode" 2>/dev/null || pgrep -f "start_agents\\.sh" 2>/dev/null || pgrep -f "trigger_opencode" 2>/dev/null || true',
      { encoding: 'utf8' }
    ).trim();
    
    const pids = pgrepOut ? pgrepOut.split(/\s+/).filter(Boolean) : [];
    
    // Filter out serve PID from the results
    const allPids = pids.filter(pid => pid !== servePid);
    
    // If no specific agent after filtering, get first opencode that's NOT the serve daemon
    if (allPids.length === 0) {
      pgrepOut = execSync(
        `pgrep -x opencode 2>/dev/null | grep -v "${servePid}" | head -1 || true`,
        { encoding: 'utf8' }
      ).trim();
      const fallbackPids = pgrepOut ? pgrepOut.split(/\s+/).filter(Boolean) : [];
      const pid = fallbackPids[0];
      if (!pid) return { running: false };
      if (servePid && pid === servePid) return { running: false };
      const etimeOut = execSync(`ps -o etime= -p ${pid} 2>/dev/null || true`, { encoding: 'utf8' }).trim();
      if (!etimeOut) return { running: false };
      const trimmed = etimeOut.trim();
      const dashParts = trimmed.split('-');
      let timePart = trimmed;
      let days = 0;
      if (dashParts.length > 1) {
        days = parseInt(dashParts[0], 10) || 0;
        timePart = dashParts[1];
      }
      const parts = timePart.split(':').map(s => parseInt(s, 10) || 0);
      let totalSec = days * 86400;
      if (parts.length === 1) totalSec += parts[0];
      else if (parts.length === 2) totalSec += parts[0] * 60 + parts[1];
      else if (parts.length >= 3) totalSec += parts[0] * 3600 + parts[1] * 60 + parts[2];
      if (totalSec < 3) return { running: false };
      let formatted = totalSec < 120 ? `${totalSec}s` : `${Math.floor(totalSec / 60)}m ${totalSec % 60}s`;
      if (totalSec >= 3600) formatted = `${Math.floor(totalSec / 3600)}h ${Math.floor((totalSec % 3600) / 60)}m`;
      return { running: true, pid, elapsedSeconds: totalSec, formatted };
    }
    
    const pid = allPids[0];
    if (!pid) return { running: false };

    const etimeOut = execSync(`ps -o etime= -p ${pid} 2>/dev/null || true`, { encoding: 'utf8' }).trim();
    if (!etimeOut) return { running: false };

    // etime format: [[dd-]hh:]mm:ss
    const trimmed = etimeOut.trim();
    const dashParts = trimmed.split('-');
    let timePart = trimmed;
    let days = 0;
    if (dashParts.length > 1) {
      days = parseInt(dashParts[0], 10) || 0;
      timePart = dashParts[1];
    }
    const parts = timePart.split(':').map(s => parseInt(s, 10) || 0);
    let totalSec = days * 86400;
    if (parts.length === 1) totalSec += parts[0];
    else if (parts.length === 2) totalSec += parts[0] * 60 + parts[1];
    else if (parts.length >= 3) totalSec += parts[0] * 3600 + parts[1] * 60 + parts[2];

    // Require at least 3 seconds elapsed - ignore processes that just started
    if (totalSec < 3) return { running: false };

    let formatted = totalSec < 120 ? `${totalSec}s` : `${Math.floor(totalSec / 60)}m ${totalSec % 60}s`;
    if (totalSec >= 3600) formatted = `${Math.floor(totalSec / 3600)}h ${Math.floor((totalSec % 3600) / 60)}m`;

    return { running: true, pid, elapsedSeconds: totalSec, formatted };
  } catch (e) {
    return { running: false };
  }
}

function startAgentStatusPolling() {
  if (agentStatusInterval) clearInterval(agentStatusInterval);
  function send() {
    if (mainWindow && !mainWindow.isDestroyed()) mainWindow.webContents.send('agent-status', getAgentStatus());
  }
  send();
  agentStatusInterval = setInterval(send, 2000);
}

// ── ntfy SSE Stream ──────────────────────────────────────────
function startNtfyStream() {
  if (!config.ntfy?.topic) return;
  restartNtfyStream();
}

function restartNtfyStream() {
  if (ntfyStream) {
    try { ntfyStream.destroy(); } catch (e) {}
    ntfyStream = null;
  }
  const { server, topic, token } = config.ntfy || {};
  if (!server || !topic) return;

  const url = `${server}/${topic}/json`;
  const parsed = new URL(url);
  const lib = parsed.protocol === 'https:' ? https : http;

  const headers = { 'Accept': 'application/x-ndjson' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const req = lib.get(url, { headers }, (res) => {
    ntfyStream = res;
    let buf = '';
    res.on('data', chunk => {
      buf += chunk.toString();
      const lines = buf.split('\n');
      buf = lines.pop();
      lines.forEach(line => {
        line = line.trim();
        if (!line) return;
        try {
          const msg = JSON.parse(line);
          if (msg.event === 'message') {
            mainWindow?.webContents.send('ntfy-message', {
              id: msg.id,
              time: msg.time,
              title: msg.title || topic,
              message: msg.message || '',
              priority: msg.priority || 3,
              tags: msg.tags || []
            });
          }
        } catch (e) {}
      });
    });
    res.on('error', () => scheduleReconnect());
    res.on('close', () => scheduleReconnect());
  });

  req.on('error', () => scheduleReconnect());
}

let reconnectTimer = null;
function scheduleReconnect() {
  if (reconnectTimer) return;
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    restartNtfyStream();
  }, 5000);
}

// ── IPC ───────────────────────────────────────────────────────
ipcMain.on('hide-window', () => mainWindow?.hide());
ipcMain.on('show-window', () => mainWindow?.show());
ipcMain.on('get-selected-model', (event) => {
  // This will be handled by the renderer process
  // We need to get the selected model from the renderer
  mainWindow?.webContents.executeJavaScript(`
    localStorage.getItem('selectedModel') || 'minimax'
  `).then(model => {
    event.reply('selected-model', model);
  });
});

ipcMain.on('set-selected-model', (event, model) => {
  mainWindow?.webContents.executeJavaScript(`
    localStorage.setItem('selectedModel', '${model}');
    selectModel('${model}');
  `);
  writeModelForCron(model);
});

// Persist selected model for cron/trigger_opencode.sh (JARVIS choice = cron job model)
const opencodeModelPath = path.join(EliaAIRoot, '.opencode_model');
function writeModelForCron(model) {
  if (!model || typeof model !== 'string') return;
  const safe = ['big-pickle', 'nvidia', 'minimax'].includes(model) ? model : 'minimax';
  try {
    fs.writeFileSync(opencodeModelPath, safe + '\n', 'utf8');
  } catch (e) {
    console.error('writeModelForCron:', e.message);
  }
}
ipcMain.on('save-model-for-cron', (_event, model) => {
  writeModelForCron(model);
});

// OMO & RALPH/ULW Toggle IPC Handlers
// ULW is now the DEFAULT mode. Ralph mode uses .ralph_mode file.
const opencodeOmoPath = path.join(EliaAIRoot, '.omo_disabled');
const opencodeRalphPath = path.join(EliaAIRoot, '.ralph_mode');

function writeOmoState(enabled) {
  try {
    if (enabled) {
      if (fs.existsSync(opencodeOmoPath)) fs.unlinkSync(opencodeOmoPath);
    } else {
      fs.writeFileSync(opencodeOmoPath, 'disabled\n', 'utf8');
    }
    console.log('OMO state:', enabled ? 'enabled' : 'disabled');
  } catch (e) {
    console.error('writeOmoState:', e.message);
  }
}

function writeRalphMode(enabled) {
  // When Ralph is enabled, create .ralph_mode file
  // When ULW (default), delete .ralph_mode file
  try {
    if (enabled) {
      fs.writeFileSync(opencodeRalphPath, 'enabled\n', 'utf8');
    } else {
      if (fs.existsSync(opencodeRalphPath)) fs.unlinkSync(opencodeRalphPath);
    }
    console.log('Ralph mode:', enabled ? 'enabled (ULW disabled)' : 'disabled (ULW default)');
  } catch (e) {
    console.error('writeRalphMode:', e.message);
  }
}

ipcMain.on('omo-toggle', (_event, enabled) => {
  writeOmoState(enabled);
});

ipcMain.on('ulw-toggle', (_event, enabled) => {
  // enabled=true means ULW is ON (Ralph OFF), enabled=false means Ralph ON (ULW OFF)
  // We store Ralph state (inverse of ULW)
  writeRalphMode(!enabled);
});

const manageCronScript = path.join(EliaAIRoot, 'scripts/manage_cron.sh');

ipcMain.on('cron-toggle', (_event, { action, interval }) => {
  const { exec } = require('child_process');
  let cmd;
  if (action === 'uninstall') {
    cmd = `/bin/zsh "${manageCronScript}" uninstall`;
    console.log('Uninstalling cronjob...');
  } else if (action === 'install') {
    cmd = `/bin/zsh "${manageCronScript}" install --interval ${interval} --start 9 --end 23`;
    console.log('Installing cronjob with interval:', interval);
  }
  exec(cmd, (error, stdout, stderr) => {
    if (error) {
      console.error('Cron toggle error:', error.message);
    } else {
      try {
        console.log('Cron toggle result:', stdout || 'Done');
      } catch (e) {
        console.log('Cron toggle completed');
      }
    }
  });
});

ipcMain.on('show-cron-popup', () => {
  showCronConfirmation();
});

// Run Morning Routine
ipcMain.on('run-morning-routine', () => {
  const { exec } = require('child_process');
  const morningScript = path.join(EliaAIRoot, 'scripts/trigger_morning.sh');
  if (fs.existsSync(morningScript)) {
    exec(`/bin/zsh "${morningScript}"`, (error, stdout, stderr) => {
      if (error) {
        console.error('Morning routine error:', error.message);
      } else {
        console.log('Morning routine started:', stdout);
      }
    });
  } else {
    console.error('Morning routine script not found:', morningScript);
  }
});

// Run Morning Speak (vocal briefing)
ipcMain.on('run-morning-speak', () => {
  runMorningSpeak();
});

// Close Morning Popup
ipcMain.on('close-popup', () => {
  if (morningPopup && !morningPopup.isDestroyed()) {
    morningPopup.close();
  }
  if (cronPopup && !cronPopup.isDestroyed()) {
    cronPopup.close();
  }
  if (welcomePopup && !welcomePopup.isDestroyed()) {
    welcomePopup.close();
  }
});

// Run Manual Cron (from cron popup)
ipcMain.on('run-cron-manual', () => {
  const { exec } = require('child_process');
  const startAgentsScript = path.join(EliaAIRoot, 'scripts/start_agents.sh');
  if (fs.existsSync(startAgentsScript)) {
    exec(`/bin/zsh "${startAgentsScript}"`, (error, stdout, stderr) => {
      if (error) {
        console.error('Manual cron error:', error.message);
      } else {
        console.log('Manual cron started:', stdout);
      }
    });
  } else {
    console.error('start_agents.sh not found:', startAgentsScript);
  }
});

// Open URL in browser
ipcMain.on('open-url', (_event, url) => {
  shell.openExternal(url);
});

// Open logs terminal
ipcMain.on('open-logs-terminal', () => {
  const { exec } = require('child_process');
  const fs = require('fs');
  const path = require('path');
  
  // Find latest opencode_interactive log file
  const logsDir = '/Users/vakandi/EliaAI/logs';
  let latestLog = null;
  let latestTime = 0;
  
  try {
    const files = fs.readdirSync(logsDir);
    for (const file of files) {
      if (file.startsWith('opencode_interactive_') && file.endsWith('.log')) {
        const filePath = path.join(logsDir, file);
        const stats = fs.statSync(filePath);
        if (stats.mtimeMs > latestTime) {
          latestTime = stats.mtimeMs;
          latestLog = filePath;
        }
      }
    }
  } catch (e) {}
  
  // Fallback to cron.log if no opencode log found
  const logFile = latestLog || '/Users/vakandi/EliaAI/logs/cron.log';
  // Show whole file + follow in realtime
  const cmd = 'tail -n 5000 -f ' + logFile;
  
  const script = [
    'tell application "Terminal" to activate',
    'tell application "Terminal" to do script ' + JSON.stringify(cmd),
    'delay 0.3',
    'tell application "Terminal" to set bounds of front window to {20, 50, 900, 900}'
  ].map(s => '-e ' + JSON.stringify(s)).join(' ');
  exec('osascript ' + script, (error) => {
    if (error) console.error('Logs terminal error:', error.message);
  });
});

ipcMain.on('get-toggle-states', (event) => {
  const omoEnabled = !fs.existsSync(opencodeOmoPath);
  // ULW is default (enabled when .ralph_mode does NOT exist)
  const ulwEnabled = !fs.existsSync(opencodeRalphPath);
  
  // Get actual scheduler state from launchd
  const cronSettings = getCurrentCronSettings();
  
  event.reply('toggle-states', { 
    omoEnabled, 
    ulwEnabled,
    cronEnabled: cronSettings.standardEnabled,
    cronInterval: cronSettings.interval,
    cronStartHour: cronSettings.startHour,
    cronEndHour: cronSettings.endHour
  });
});

ipcMain.on('get-config', (evt) => evt.reply('config-updated', config));
ipcMain.on('quit-app', () => app.quit());
ipcMain.on('set-ignore-mouse-events', (event, ignore, options) => {
  mainWindow?.setIgnoreMouseEvents(ignore, options);
});
ipcMain.on('execute-elia-command', () => {
  const { exec } = require('child_process');
  mainWindow?.webContents.send('recording-started');

  mainWindow.webContents.executeJavaScript('localStorage.getItem("selectedModel") || "minimax"')
    .then(model => {
      const modelMap = {
        'big-pickle': 'big-pickle',
        'nvidia': 'nvidia',
        'minimax': 'minimax'
      };
      const modelValue = modelMap[model] || 'minimax';
      // Run dictate.command in Terminal with JARVIS_MODEL set so it can pass model to start_agents.sh.
      // Also check proxy state and pass USE_PROXY if enabled.
      const proxyEnabled = fs.existsSync(proxyStatePath);
      const proxyExport = proxyEnabled ? 'export USE_PROXY=1 && ' : '';
      const cmd = `cd /Users/vakandi/EliaAI && ${proxyExport}export JARVIS_MODEL=${modelValue} && /Users/vakandi/Documents/dictate.command`;
      const script = [
        'tell application "Terminal" to activate',
        'tell application "Terminal" to do script ' + JSON.stringify(cmd),
        'delay 0.3',
        'tell application "Terminal" to set bounds of front window to {100, 50, 500, 900}'
      ].map(s => `-e ${JSON.stringify(s)}`).join(' ');
      exec(`osascript ${script}`, (error, stdout, stderr) => {
        if (error) console.error('Execution error:', error.message);
      });
    })
    .catch(err => {
      console.error('get selectedModel:', err);
      mainWindow?.webContents.send('recording-stopped');
    });
});

ipcMain.on('execute-mini-orb', () => {
  const { exec } = require('child_process');
  const proxyEnabled = fs.existsSync(proxyStatePath);
  const proxyExport = proxyEnabled ? 'export USE_PROXY=1 && ' : '';
  
  const cmd = `${proxyExport}/Users/vakandi/EliaAI/scripts/voice-command-only.sh`;
  const script = [
    'tell application "Terminal" to activate',
    'delay 0.5',
    'tell application "Terminal" to do script ' + JSON.stringify(cmd),
    'delay 0.5',
    'tell application "Terminal" to set bounds of front window to {100, 50, 500, 900}'
  ].map(s => `-e ${JSON.stringify(s)}`).join(' ');
  exec(`osascript ${script}`, (error, stdout, stderr) => {
    if (error) console.error('Mini orb execution error:', error.message);
  });
});

ipcMain.on('stop-recording', () => {
  const { exec } = require('child_process');
  exec('osascript -e \'tell application "System Events" to keystroke "c" using command down\'', (error) => {
    if (error) console.error('Stop recording:', error.message);
  });
  mainWindow?.webContents.send('recording-stopped');
});

ipcMain.on('set-position-click', (_event, screenX, screenY) => {
  const x = Math.round(screenX - WIN_W / 2);
  const y = Math.round(screenY - WIN_H / 2);
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.setBounds({ x, y, width: WIN_W, height: WIN_H });
    mainWindow.show();
  }
  savePosition(x, y);
  if (setPositionOverlay && !setPositionOverlay.isDestroyed()) {
    setPositionOverlay.close();
    setPositionOverlay = null;
  }
});

// ── Tray ──────────────────────────────────────────────────────
let trayMenuState = {
  statusLive: false,
  voiceTrigger: false,
  selectedModel: 'minimax',
  proxyEnabled: false
};

// Proxy state file
const proxyStatePath = path.join(EliaAIRoot, '.proxy_enabled');

// Load proxy state from file
function loadProxyState() {
  try {
    trayMenuState.proxyEnabled = fs.existsSync(proxyStatePath);
  } catch (e) {
    trayMenuState.proxyEnabled = false;
  }
  return trayMenuState.proxyEnabled;
}

// Toggle proxy state
function toggleProxy(enabled) {
  try {
    if (enabled) {
      fs.writeFileSync(proxyStatePath, 'enabled\n', 'utf8');
    } else {
      if (fs.existsSync(proxyStatePath)) fs.unlinkSync(proxyStatePath);
    }
    trayMenuState.proxyEnabled = enabled;
    console.log('Proxy:', enabled ? 'ENABLED' : 'DISABLED');
  } catch (e) {
    console.error('toggleProxy:', e.message);
  }
}

// Load current model from file or default
function loadCurrentModel() {
  try {
    const modelPath = path.join(EliaAIRoot, '.opencode_model');
    if (fs.existsSync(modelPath)) {
      const model = fs.readFileSync(modelPath, 'utf8').trim();
      if (['big-pickle', 'nvidia', 'minimax'].includes(model)) {
        trayMenuState.selectedModel = model;
        return model;
      }
    }
  } catch (e) {
    console.error('Load current model:', e.message);
  }
  return 'minimax';
}

// Get current scheduler settings from launchd state file
function getCurrentCronSettings() {
  const stateFile = path.join(EliaAIRoot, '.scheduler_state');
  const launchdPlist = path.join(process.env.HOME || '/Users/vakandi', 'Library/LaunchAgents/com.elia.elia-agent.plist');
  const morningPlist = path.join(process.env.HOME || '/Users/vakandi', 'library/LaunchAgents/com.elia.elia-agent-morning.plist');
  
  try {
    // First try to read state file
    if (fs.existsSync(stateFile)) {
      const state = fs.readFileSync(stateFile, 'utf8');
      const lines = state.trim().split('\n');
      const settings = {};
      lines.forEach(line => {
        const [key, value] = line.split('=');
        if (key && value !== undefined) {
          settings[key] = value;
        }
      });
      
      return {
        morningEnabled: settings.morningEnabled === 'true',
        morningHour: parseInt(settings.morningHour) || 10,
        standardEnabled: settings.enabled === 'true',
        interval: settings.interval || '1h',
        startHour: parseInt(settings.startHour) || 11,
        endHour: parseInt(settings.endHour) || 21
      };
    }
    
    // Fallback: check if launchd plist exists (check both StartInterval and StartCalendarInterval)
    if (fs.existsSync(launchdPlist)) {
      const content = fs.readFileSync(launchdPlist, 'utf8');
      const intervalMatch = content.match(/<key>StartInterval<\/key>\s*<integer>(\d+)<\/integer>/);
      const calendarMatch = content.match(/<key>StartCalendarInterval<\/key>/);
      const minuteMatches = content.match(/<key>Minute<\/key><integer>(\d+)<\/integer>/g);
      
      let detectedInterval = '1h';
      if (intervalMatch) {
        detectedInterval = parseInt(intervalMatch[1]) === 1800 ? '30min' : 
                          parseInt(intervalMatch[1]) === 1200 ? '20min' :
                          parseInt(intervalMatch[1]) === 7200 ? '2h' :
                          parseInt(intervalMatch[1]) === 10800 ? '3h' :
                          parseInt(intervalMatch[1]) === 14400 ? '4h' : '1h';
      } else if (calendarMatch && minuteMatches) {
        const minutes = minuteMatches.map(m => parseInt(m.match(/\d+/)[0]));
        if (minutes.includes(0) && minutes.includes(30)) detectedInterval = '30min';
        else if (minutes.includes(0) && minutes.includes(20) && minutes.includes(40)) detectedInterval = '20min';
        else if (minutes.length === 1 && minutes[0] === 0) detectedInterval = '1h';
      }
      
      return {
        morningEnabled: fs.existsSync(morningPlist),
        morningHour: 10,
        standardEnabled: true,
        interval: detectedInterval,
        startHour: 9,
        endHour: 23
      };
    }
  } catch (e) {
    console.error('Error reading scheduler state:', e.message);
  }
  
  // Default values if nothing found
  return {
    morningEnabled: false,
    morningHour: 10,
    standardEnabled: false,
    interval: '1h',
    startHour: 11,
    endHour: 21
  };
}


function updateTrayMenu() {
  // Load current model
  const currentModel = loadCurrentModel();
  trayMenuState.selectedModel = currentModel;
  
  // Load proxy state
  loadProxyState();
  
  // Get current cron settings
  const cronSettings = getCurrentCronSettings();
  
  const models = [
    { id: 'minimax', label: 'MiniMax 2.5' },
    { id: 'big-pickle', label: 'Big Pickle' },
    { id: 'nvidia', label: 'Kimi 2.5' }
  ];

  const modelSubmenu = models.map(m => ({
    label: m.label,
    type: 'checkbox',
    checked: trayMenuState.selectedModel === m.id,
    click: () => {
      trayMenuState.selectedModel = m.id;
      writeModelForCron(m.id);
      mainWindow?.webContents.executeJavaScript(`
        localStorage.setItem('selectedModel', '${m.id}');
        if (typeof selectModel === 'function') selectModel('${m.id}');
      `);
      updateTrayMenu();
    }
  }));
  
  // Morning cron submenu
  const morningHours = [];
  for (let h = 6; h <= 12; h++) {
    morningHours.push({
      label: `${h}:00`,
      type: 'radio',
      checked: cronSettings.morningHour === h,
      click: () => {
        try {
          execSync(`/bin/zsh ${EliaAIRoot}/scripts/manage_cron.sh install-morning --morning-hour ${h} >/dev/null 2>&1`, { encoding: 'utf8' });
        } catch (e) {}
        updateTrayMenu();
      }
    });
  }
  
  const morningSubmenu = [
    {
      label: isProcessingMorning ? '⏳ Morning Cron (Processing...)' : 'Morning Cron',
      type: 'checkbox',
      checked: cronSettings.morningEnabled,
      click: () => {
        if (isProcessingMorning) return;
        isProcessingMorning = true;
        updateTrayMenu();
        setTimeout(() => {
          try {
            if (cronSettings.morningEnabled) {
              execSync(`/bin/zsh ${EliaAIRoot}/scripts/manage_cron.sh uninstall-morning >/dev/null 2>&1`, { encoding: 'utf8' });
            } else {
              execSync(`/bin/zsh ${EliaAIRoot}/scripts/manage_cron.sh install-morning --morning-hour ${cronSettings.morningHour} >/dev/null 2>&1`, { encoding: 'utf8' });
            }
          } catch (e) {}
          isProcessingMorning = false;
          updateTrayMenu();
        }, 100);
      }
    },
    { type: 'separator' },
    { label: 'Hour:', enabled: false },
    ...morningHours
  ];
  
  // Standard cron submenu - intervals
  const intervals = ['20min', '30min', '1h', '2h', '3h', '4h'];
  const intervalSubmenu = intervals.map(i => ({
    label: i,
    type: 'radio',
    checked: cronSettings.interval === i,
    click: () => {
      try {
        execSync(`/bin/zsh ${EliaAIRoot}/scripts/manage_cron.sh install --interval ${i} --start ${cronSettings.startHour} --end ${cronSettings.endHour} >/dev/null 2>&1`, { encoding: 'utf8' });
      } catch (e) {}
      updateTrayMenu();
    }
  }));
  
  // Standard cron submenu - hours
  const hoursSubmenu = [];
  for (let start = 8; start <= 18; start++) {
    for (let end = start + 2; end <= 22; end += 2) {
      hoursSubmenu.push({
        label: `${start}:00 - ${end}:00`,
        type: 'radio',
        checked: cronSettings.startHour === start && cronSettings.endHour === end,
        click: () => {
          try {
            execSync(`/bin/zsh ${EliaAIRoot}/scripts/manage_cron.sh install --interval ${cronSettings.interval} --start ${start} --end ${end} >/dev/null 2>&1`, { encoding: 'utf8' });
          } catch (e) {}
          updateTrayMenu();
        }
      });
    }
  }
  
  const cronSubmenu = [
    {
      label: 'Cron Job',
      type: 'checkbox',
      checked: cronSettings.standardEnabled,
      click: () => {
        isProcessingCron = true;
        updateTrayMenu();
        setTimeout(() => {
          try {
            if (cronSettings.standardEnabled) {
              execSync(`/bin/zsh ${EliaAIRoot}/scripts/manage_cron.sh uninstall >/dev/null 2>&1`, { encoding: 'utf8' });
            } else {
              execSync(`/bin/zsh ${EliaAIRoot}/scripts/manage_cron.sh install --interval ${cronSettings.interval} --start ${cronSettings.startHour} --end ${cronSettings.endHour} >/dev/null 2>&1`, { encoding: 'utf8' });
            }
          } catch (e) {}
          isProcessingCron = false;
          updateTrayMenu();
        }, 100);
      }
    },
    { type: 'separator' },
    { label: 'Interval:', enabled: false },
    ...intervalSubmenu,
    { type: 'separator' },
    { label: 'Hours:', enabled: false },
    ...hoursSubmenu
  ];
  
  const menu = Menu.buildFromTemplate([
    { label: 'Afficher', click: () => mainWindow?.show() },
    { label: 'Masquer', click: () => mainWindow?.hide() },
    { type: 'separator' },
    {
      label: 'Morning Routine',
      submenu: [
        {
          label: 'Run Morning Routine',
          click: () => showMorningRoutineConfirmation()
        },
        { type: 'separator' },
        {
          label: 'Morning Speak',
          click: () => runMorningSpeak()
        },
        { type: 'separator' },
        ...morningSubmenu
      ]
    },
    {
      label: isProcessingCron ? '⏳ Cron Job (Processing...)' : 'Cron Job',
      submenu: cronSubmenu
    },
    { type: 'separator' },
    {
      label: 'Modèle',
      submenu: modelSubmenu
    },
    { type: 'separator' },
    {
      label: 'Proxy',
      submenu: [
        {
          label: 'Enable Proxy',
          type: 'checkbox',
          checked: trayMenuState.proxyEnabled,
          click: () => {
            const newState = !trayMenuState.proxyEnabled;
            if (newState && !isProxychainsInstalled()) {
              showProxyErrorPopup();
              return;
            }
            toggleProxy(newState);
            updateTrayMenu();
          }
        },
        {
          label: trayMenuState.proxyEnabled ? 'Status: ENABLED' : 'Status: DISABLED',
          enabled: false
        }
      ]
    },
    { type: 'separator' },
    { label: 'Quitter', click: () => app.quit() }
  ]);
  tray.setContextMenu(menu);
}

function saveTraySettings() {
  try {
    const currentConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    currentConfig.display = currentConfig.display || {};
    currentConfig.display.statusLive = trayMenuState.statusLive;
    currentConfig.display.voiceTrigger = trayMenuState.voiceTrigger;
    fs.writeFileSync(configPath, JSON.stringify(currentConfig, null, 2) + '\n', 'utf8');
  } catch (e) {
    console.error('Save tray settings:', e.message);
  }
}

function createTray() {
  const iconPath = '/Users/vakandi/EliaAI/ui_electron/imgs/electronui.png';
  let trayIcon = nativeImage.createFromPath(iconPath);
  if (trayIcon.isEmpty()) {
    trayIcon = nativeImage.createEmpty();
  }
  tray = new Tray(trayIcon, 'EliaUI-Tray');
  tray.setToolTip('EliaUI');
  console.log('Tray created with title:', tray.getTitle ? tray.getTitle() : 'N/A');
  tray.setToolTip('EliaUI');
  tray.setTitle('Elia');
  console.log('Tray title set to: Elia');
  updateTrayMenu();
  tray.on('click', () => {
    mainWindow?.isVisible() ? mainWindow.hide() : mainWindow?.show();
  });
}

// Morning Routine Confirmation Popup
function showMorningRoutineConfirmation() {
  if (morningPopup && !morningPopup.isDestroyed()) {
    morningPopup.focus();
    return;
  }
  
  const display = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = display.workAreaSize;
  
  const popupW = 750;
  const popupH = 525;
  const x = Math.round((screenWidth - popupW) / 2);
  const y = Math.round((screenHeight - popupH) / 2);
  
  morningPopup = new BrowserWindow({
    width: popupW,
    height: popupH,
    x,
    y,
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    backgroundColor: '#00000000',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });
  
  morningPopup.loadFile(path.join(__dirname, '..', 'morning-popup.html'));
  
  morningPopup.on('closed', () => {
    morningPopup = null;
  });
}

// Morning Speak - trigger cron job with morning briefing prompt
function runMorningSpeak() {
  const { exec } = require('child_process');
  const fs = require('fs');
  const path = require('path');
  
  const eliaAI = '/Users/vakandi/EliaAI';
  const promptFile = path.join(eliaAI, '.morning_briefing_prompt.txt');
  
  const morningPrompt = `MORNING BRIEFING - COMPREHENSIVE DAILY UPDATE:

You are Elia's morning briefing assistant. Your task is to gather ALL relevant information and provide a complete spoken briefing to Wael.

CRITICAL: You must SPEAK to Wael during the ENTIRE process, not just at the end. Use elia-voxtral-speak throughout.

SPEAK AT THESE MOMENTS:
1. AT THE START: "Salut Wael, je démarre le briefing matinal. Je check tout ça."
2. AFTER EACH CHECK: "Je finishes de checker [Google Calendar / WhatsApp / Telegram / Jira], je te donne le point."
3. BEFORE SENDING TASKS: "Je t'ajoute [X] tâches sur ton téléphone."
4. AT THE END: "C'est bon Wael, voici le résumé complet de la matinée."

MUST DO:
1. CHECK GOOGLE CALENDAR: Use gws-workspace list-events to get today's meetings and events
2. CHECK TELEGRAM: Read recent messages from Watson IA group (chat ID: -5148361692)
3. CHECK WHATSAPP: Read B2LUXE BUSINESS (120363408208578679@g.us) and COBOU PowerRangers (120363420711538035@g.us)
4. CHECK JIRA: Get pending tickets for BEN, COBOUAGENC, ZOVAPANEL, TIKYT
5. CHECK MEMORY FILES: Read /Users/vakandi/EliaAI/memory/*.md for important context
6. GATHER BUSINESS UPDATES: Status of all 8 businesses
7. IDENTIFY ACTION ITEMS: What needs Wael's attention today?
8. IDENTIFY WAITING ON: What are team members waiting for?

AFTER GATHERING ALL INFO:
- Use gws-workspace create-task to add any important tasks to Wael's phone
- Use gws-workspace create-event to add any meetings to calendar if missing

IMPORTANT: Speak at EACH step using elia-voxtral-speak (fast, French) → fallback: elia-speak`;
  
  fs.writeFileSync(promptFile, morningPrompt, 'utf8');
  
  const cmd = `cd ${eliaAI} && EXTRA_PROMPT_FILE=${promptFile} /bin/zsh ${eliaAI}/scripts/start_agents.sh`;
  const script = [
    'tell application "Terminal" to activate',
    'tell application "Terminal" to do script ' + JSON.stringify(cmd),
    'delay 0.3',
    'tell application "Terminal" to set bounds of front window to {100, 50, 600, 900}'
  ].map(s => `-e ${JSON.stringify(s)}`).join(' ');
  
  require('child_process').exec(`osascript ${script}`, (error, stdout, stderr) => {
    if (error) {
      console.error('Morning Speak error:', error.message);
      try { fs.unlinkSync(promptFile); } catch(e) {}
    }
  });
}

// Manual Cron Confirmation Popup
function showCronConfirmation() {
  if (cronPopup && !cronPopup.isDestroyed()) {
    cronPopup.focus();
    return;
  }
  
  const display = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = display.workAreaSize;
  
  const popupW = 750;
  const popupH = 525;
  const x = Math.round((screenWidth - popupW) / 2);
  const y = Math.round((screenHeight - popupH) / 2);
  
  cronPopup = new BrowserWindow({
    width: popupW,
    height: popupH,
    x,
    y,
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    backgroundColor: '#00000000',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });
  
  cronPopup.loadFile(path.join(__dirname, '..', 'cron-popup.html'));
  
  cronPopup.on('closed', () => {
    cronPopup = null;
  });
}

function showWelcomePopup() {
  if (welcomeShown) return;
  welcomeShown = true;
  
  const display = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = display.workAreaSize;
  
  const popupW = 750;
  const popupH = 525;
  const x = Math.round((screenWidth - popupW) / 2);
  const y = Math.round((screenHeight - popupH) / 2);
  
  welcomePopup = new BrowserWindow({
    width: popupW,
    height: popupH,
    x,
    y,
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    backgroundColor: '#00000000',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });
  
  welcomePopup.loadFile(path.join(__dirname, '..', 'welcome-popup.html'));
  
  setTimeout(() => {
    if (welcomePopup && !welcomePopup.isDestroyed()) {
      welcomePopup.close();
    }
  }, 10000);
  
  welcomePopup.on('closed', () => {
    welcomePopup = null;
  });
}

// Proxy Error Popup
function showProxyErrorPopup() {
  if (proxyPopup && !proxyPopup.isDestroyed()) {
    proxyPopup.focus();
    return;
  }
  
  const display = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = display.workAreaSize;
  
  const popupW = 600;
  const popupH = 300;
  const x = Math.round((screenWidth - popupW) / 2);
  const y = Math.round((screenHeight - popupH) / 2);
  
  proxyPopup = new BrowserWindow({
    width: popupW,
    height: popupH,
    x,
    y,
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    backgroundColor: '#00000000',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });
  
  proxyPopup.loadFile(path.join(__dirname, '..', 'proxy-error-popup.html'));
  
  proxyPopup.on('closed', () => {
    proxyPopup = null;
  });
}

// Check if proxychains4 is installed
function isProxychainsInstalled() {
  try {
    execSync('which proxychains4 2>/dev/null', { encoding: 'utf8' });
    return true;
  } catch (e) {
    return false;
  }
}

function startTelegramBot() {
  const botDir = path.join(EliaAIRoot, 'integrations', 'telegram-opencode-bot');
  const botScript = path.join(botDir, 'dist', 'cli.js');
  if (!fs.existsSync(botScript)) {
    console.log('Telegram bot: dist missing, run build in integrations/telegram-opencode-bot');
    return;
  }
  const envPath = path.join(botDir, '.env');
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf8');
    if (!/TELEGRAM_BOT_TOKENS\s*=\s*.+/.test(envContent)) {
      return;
    }
  } else {
    return;
  }
  try {
    telegramBotProcess = spawn('node', [botScript], {
      cwd: botDir,
      env: { ...process.env, ELIA_HELPER_DIR: EliaAIRoot },
      stdio: ['ignore', 'pipe', 'pipe']
    });
    telegramBotProcess.on('error', (err) => {
      console.error('Telegram bot error:', err.message);
      telegramBotProcess = null;
    });
    telegramBotProcess.on('exit', (code, signal) => {
      telegramBotProcess = null;
    });
  } catch (e) {
    console.error('Telegram bot spawn failed:', e.message);
  }
}

function startDiscordBot() {
  const botDir = path.join(EliaAIRoot, 'integrations', 'elia-discord-bot');
  const botScript = path.join(botDir, 'bot.py');
  if (!fs.existsSync(botScript)) {
    console.log('Discord bot: bot.py not found');
    return;
  }
  const envPath = path.join(botDir, '.env');
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf8');
    if (!/DISCORD_BOT_TOKEN\s*=\s*.+/.test(envContent)) {
      console.log('Discord bot: DISCORD_BOT_TOKEN not set in .env');
      return;
    }
  } else {
    console.log('Discord bot: .env not found');
    return;
  }
  try {
    const venvPython = path.join(botDir, 'venv', 'bin', 'python3');
    const pythonBin = fs.existsSync(venvPython) ? venvPython : 'python3';
    discordBotProcess = spawn(pythonBin, [botScript], {
      cwd: botDir,
      env: { ...process.env },
      stdio: ['ignore', 'pipe', 'pipe']
    });
    discordBotProcess.stdout.on('data', (data) => {
      console.log('[Discord]', data.toString().trim());
    });
    discordBotProcess.stderr.on('data', (data) => {
      console.error('[Discord Error]', data.toString().trim());
    });
    discordBotProcess.on('error', (err) => {
      console.error('Discord bot error:', err.message);
      discordBotProcess = null;
    });
    discordBotProcess.on('exit', (code, signal) => {
      discordBotProcess = null;
    });
  } catch (e) {
    console.error('Discord bot spawn failed:', e.message);
  }
}

app.whenReady().then(() => {
  console.log('EliaUI starting...');
  app.setName('EliaUI');
  
  const template = [
    {
      label: 'EliaUI',
      submenu: [
        { label: 'About EliaUI', role: 'about' },
        { type: 'separator' },
        { label: 'Services', role: 'services' },
        { type: 'separator' },
        { label: 'Hide EliaUI', role: 'hide' },
        { label: 'Hide Others', role: 'hideOthers' },
        { label: 'Show All', role: 'unhide' },
        { type: 'separator' },
        { label: 'Quit EliaUI', role: 'quit' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { label: 'Undo', role: 'undo' },
        { label: 'Redo', role: 'redo' },
        { type: 'separator' },
        { label: 'Cut', role: 'cut' },
        { label: 'Copy', role: 'copy' },
        { label: 'Paste', role: 'paste' },
        { label: 'Select All', role: 'selectAll' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { label: 'Reload', role: 'reload' },
        { label: 'Force Reload', role: 'forceReload' },
        { label: 'Toggle DevTools', role: 'toggleDevTools' },
        { type: 'separator' },
        { label: 'Actual Size', role: 'resetZoom' },
        { label: 'Zoom In', role: 'zoomIn' },
        { label: 'Zoom Out', role: 'zoomOut' },
        { type: 'separator' },
        { label: 'Toggle Fullscreen', role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { label: 'Minimize', role: 'minimize' },
        { label: 'Zoom', role: 'zoom' },
        { type: 'separator' },
        { label: 'Bring All to Front', role: 'front' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        { label: 'EliaUI Help', role: 'help' }
      ]
    }
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
  console.log('Application menu set');
  
  const dockIconPath = path.join(__dirname, '..', 'imgs', 'dock_icon.png');
  if (fs.existsSync(dockIconPath)) {
    app.dock?.setIcon(dockIconPath);
  }
  
  createTray();
  createWindow();
  showWelcomePopup();
  startTelegramBot();
  if (SET_POSITION_FLAG) {
    const display = screen.getPrimaryDisplay();
    const { x: ox, y: oy, width: dw, height: dh } = display.bounds;
    setPositionOverlay = new BrowserWindow({
      x: ox,
      y: oy,
      width: dw,
      height: dh,
      frame: false,
      transparent: true,
      alwaysOnTop: true,
      skipTaskbar: true,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'set-position-preload.js')
      }
    });
    setPositionOverlay.setIgnoreMouseEvents(false);
    setPositionOverlay.loadFile(path.join(__dirname, 'set-position-overlay.html'));
    setPositionOverlay.on('closed', () => { setPositionOverlay = null; });
  }
});

app.on('window-all-closed', (e) => e.preventDefault());
app.on('before-quit', () => {
  if (ntfyStream) try { ntfyStream.destroy(); } catch (e) {}
  if (agentStatusInterval) clearInterval(agentStatusInterval);
  if (telegramBotProcess) {
    telegramBotProcess.kill('SIGTERM');
    telegramBotProcess = null;
  }
  if (discordBotProcess) {
    discordBotProcess.kill('SIGTERM');
    discordBotProcess = null;
  }
});
