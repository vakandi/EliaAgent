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
let subworkerPopup = null;
let welcomePopup = null;
let proxyPopup = null;
let welcomeShown = false;

const EliaAIRoot = path.join(__dirname, '..', '..');
const contextPath = path.join(EliaAIRoot, 'context');
const subworkersRoot = path.join(EliaAIRoot, 'subworkers');

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
const positionPath = path.join(__dirname, '..', '.elia-position.json');
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

// ── Subworker status ─────────────────────────────────────────
function parsePlistSchedule(plistPath) {
  try {
    if (!fs.existsSync(plistPath)) return null;
    const { execSync } = require('child_process');
    const json = execSync(`plutil -convert json -o - "${plistPath}" 2>/dev/null`, { encoding: 'utf8', timeout: 5000 }).trim();
    const plist = JSON.parse(json);

    // StartInterval (seconds-based, e.g. 1800 = every 30 min)
    if (plist.StartInterval) {
      const secs = plist.StartInterval;
      let label;
      if (secs >= 3600 && secs % 3600 === 0) label = `every ${secs / 3600}h`;
      else if (secs >= 60 && secs % 60 === 0) label = `every ${secs / 60}min`;
      else label = `every ${secs}s`;
      return {
        type: 'interval',
        description: label,
        intervalSeconds: secs,
        intervals: null,
        startHour: null,
        endHour: null,
        minutePattern: null
      };
    }

    // StartCalendarInterval (list of Hour+Minute dicts)
    const entries = plist.StartCalendarInterval;
    if (!entries || !Array.isArray(entries) || entries.length === 0) return null;

    const intervals = entries.map(e => ({ hour: e.Hour, minute: e.Minute }));
    intervals.sort((a, b) => a.hour - b.hour || a.minute - b.minute);

    const hours = [...new Set(intervals.map(i => i.hour))].sort((a, b) => a - b);
    const minutes = [...new Set(intervals.map(i => i.minute))].sort((a, b) => a - b);

    // Detect pattern
    let description;
    if (intervals.length === 1) {
      const e = intervals[0];
      description = `${String(e.hour).padStart(2, '0')}:${String(e.minute).padStart(2, '0')} daily`;
    } else if (minutes.length === 1 && hours.length > 1) {
      // Same minute every hour: hourly pattern
      const minStr = String(minutes[0]).padStart(2, '0');
      description = `${String(hours[0]).padStart(2, '0')}h→${String(hours[hours.length - 1]).padStart(2, '0')}h hourly at :${minStr}`;
    } else if (minutes.length === 2 && minutes[0] === 0 && minutes[1] === 30 && hours.length > 1) {
      // :00 and :30 → every 30 min
      description = `${String(hours[0]).padStart(2, '0')}h→${String(hours[hours.length - 1]).padStart(2, '0')}h every 30min`;
    } else {
      // Generic list
      description = intervals.map(e => `${String(e.hour).padStart(2, '0')}:${String(e.minute).padStart(2, '0')}`).join(', ');
    }

    return {
      type: 'calendar',
      description,
      intervalSeconds: null,
      intervals,
      startHour: hours[0],
      endHour: hours[hours.length - 1],
      minutePattern: minutes
    };
  } catch (e) {
    console.error('parsePlistSchedule error:', e.message);
    return null;
  }
}

function getSubworkerStatus() {
  const results = [];
  try {
    const items = fs.readdirSync(subworkersRoot, { withFileTypes: true });
    const skipDirs = new Set(['logs', 'plists', 'scripts']);
    for (const item of items) {
      if (!item.isDirectory()) continue;
      if (skipDirs.has(item.name)) continue;

      const dirPath = path.join(subworkersRoot, item.name);
      const promptPath = path.join(dirPath, 'PROMPT.md');
      const enabledPath = path.join(dirPath, '.enabled');
      const plistName = `com.elia.${item.name}`;
      const plistPath = path.join(subworkersRoot, 'plists', `${plistName}.plist`);

      // Read description from PROMPT.md first line
      let description = '';
      try {
        const firstLine = fs.readFileSync(promptPath, 'utf8').split('\n')[0] || '';
        description = firstLine.replace(/^#\s*/, '').trim();
      } catch (e) {
        description = '';
      }

      // Check .enabled flag
      const enabled = fs.existsSync(enabledPath);

      // Check launchd status
      let running = false;
      try {
        const out = require('child_process').execSync(
          `launchctl list ${plistName} 2>/dev/null || true`,
          { encoding: 'utf8' }
        ).trim();
        if (out && !out.includes('Could not find')) {
          const lastField = out.split('\t').pop() || '';
          running = lastField !== ''; // non-empty = process is running
        }
      } catch (e) {}

      // Parse schedule from plist
      const schedule = parsePlistSchedule(plistPath);

      results.push({
        name: item.name,
        label: item.name.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
        description,
        path: dirPath,
        enabled,
        running,
        plistExists: fs.existsSync(plistPath),
        schedule
      });
    }
    results.sort((a, b) => a.name.localeCompare(b.name));
  } catch (e) {
    console.error('getSubworkerStatus error:', e.message);
  }
  return results;
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

// Persist selected model for cron/trigger_opencode.sh (Elia choice = cron job model)
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
  const { execSync } = require('child_process');
  let cmd;
  if (action === 'uninstall') {
    cmd = `/bin/zsh "${manageCronScript}" uninstall`;
    console.log('Uninstalling launchd scheduler (cron-toggle)...');
  } else if (action === 'install') {
    cmd = `/bin/zsh "${manageCronScript}" install --interval ${interval} --start 9 --end 23`;
    console.log('Installing launchd scheduler with interval:', interval);
  } else {
    console.error('cron-toggle: unknown action', action);
    return;
  }
  try {
    execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
    console.log('cron-toggle: OK');
  } catch (error) {
    console.error('Cron toggle error:', error.message);
  }
});

ipcMain.on('show-cron-popup', () => {
  showCronConfirmation();
});

// Subworker popup
ipcMain.on('show-subworker-popup', () => {
  showSubworkerPopupWindow();
});

// Get subworker list
ipcMain.on('get-subworkers', (event) => {
  const workers = getSubworkerStatus();
  event.reply('subworkers-list', workers);
});

// Toggle subworker enabled state
ipcMain.on('toggle-subworker', (event, name) => {
  if (!name) return;
  const subworkerDir = path.join(subworkersRoot, name);
  const plistName = `com.elia.${name}`;
  const plistPath = path.join(subworkersRoot, 'plists', `${plistName}.plist`);
  const enabledPath = path.join(subworkerDir, '.enabled');

  let enabled = false;
  try {
    if (fs.existsSync(enabledPath)) {
      fs.unlinkSync(enabledPath);
      enabled = false;
      // Unload from launchd if plist exists
      if (fs.existsSync(plistPath)) {
        require('child_process').execSync(`launchctl bootout gui/$(id -u) ${plistPath} 2>/dev/null || true`);
      }
    } else {
      fs.writeFileSync(enabledPath, 'enabled\n', 'utf8');
      enabled = true;
      // Load into launchd if plist exists
      if (fs.existsSync(plistPath)) {
        require('child_process').execSync(`launchctl bootstrap gui/$(id -u) ${plistPath} 2>/dev/null || true`);
      }
    }
  } catch (e) {
    console.error(`toggle-subworker ${name}:`, e.message);
  }

  // Check running state after toggle
  let running = false;
  try {
    const out = require('child_process').execSync(
      `launchctl list ${plistName} 2>/dev/null || true`,
      { encoding: 'utf8' }
    ).trim();
    if (out && !out.includes('Could not find')) {
      const lastField = out.split('\t').pop() || '';
      running = lastField !== '';
    }
  } catch (e) {}

  event.reply('subworker-toggled', { name, enabled, running });
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

// Close all popups
ipcMain.on('close-popup', () => {
  if (morningPopup && !morningPopup.isDestroyed()) {
    morningPopup.close();
  }
  if (cronPopup && !cronPopup.isDestroyed()) {
    cronPopup.close();
  }
  if (subworkerPopup && !subworkerPopup.isDestroyed()) {
    subworkerPopup.close();
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

ipcMain.on('open-subworker-logs', (_event, name) => {
  if (!name) return;
  const { exec } = require('child_process');
  // Try to open the LATEST per-run log file first, fallback to aggregate
  const runsDir = path.join(subworkersRoot, 'logs', 'runs', name.replace(/-/g, '_'));
  let logFile = path.join(subworkersRoot, 'logs', name.replace(/-/g, '_') + '.log');
  try {
    if (fs.existsSync(runsDir)) {
      const files = fs.readdirSync(runsDir)
        .filter(f => f.endsWith('.log'))
        .sort()
        .reverse();
      if (files.length > 0) {
        logFile = path.join(runsDir, files[0]);
      }
    }
  } catch (_) {}
  if (!fs.existsSync(logFile)) {
    const { dialog } = require('electron');
    dialog.showMessageBox({
      type: 'info',
      title: 'No logs',
      message: `No run logs yet for ${name}.`,
      detail: 'Run the trigger script once to generate the first log file.'
    });
    return;
  }
  const cmd = 'tail -n 5000 -f ' + logFile;
  const script = [
    'tell application "Terminal" to activate',
    'tell application "Terminal" to do script ' + JSON.stringify(cmd),
    'delay 0.3',
    'tell application "Terminal" to set bounds of front window to {20, 50, 900, 500}'
  ].map(s => '-e ' + JSON.stringify(s)).join(' ');
  exec('osascript ' + script, (error) => {
    if (error) console.error('open-subworker-logs error:', error.message);
  });
});

// List per-run log files for a subworker (last 100, sorted newest first)
ipcMain.on('get-subworker-runs', (event, name) => {
  if (!name) return;
  const runsDir = path.join(subworkersRoot, 'logs', 'runs', name.replace(/-/g, '_'));
  const runs = [];
  try {
    if (fs.existsSync(runsDir)) {
      const files = fs.readdirSync(runsDir)
        .filter(f => f.endsWith('.log'))
        .sort()
        .reverse()
        .slice(0, 100);
      for (const file of files) {
        const filePath = path.join(runsDir, file);
        try {
          const stats = fs.statSync(filePath);
          runs.push({ filename: file, path: filePath, mtime: stats.mtimeMs, size: stats.size });
        } catch (_) {}
      }
    }
  } catch (_) {}
  event.reply('subworker-runs', { name, runs });
});

// Open a specific log file in Terminal
ipcMain.on('open-subworker-log-file', (_event, logFilePath) => {
  if (!logFilePath) return;
  const { exec } = require('child_process');
  const cmd = 'tail -n 5000 -f ' + logFilePath;
  const script = [
    'tell application "Terminal" to activate',
    'tell application "Terminal" to do script ' + JSON.stringify(cmd),
    'delay 0.3',
    'tell application "Terminal" to set bounds of front window to {20, 50, 900, 500}'
  ].map(s => '-e ' + JSON.stringify(s)).join(' ');
  exec('osascript ' + script, (error) => {
    if (error) console.error('open-subworker-log-file error:', error.message);
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

      const proxyEnabled = fs.existsSync(proxyStatePath);

      let cmd;
      if (proxyEnabled) {
        const proxyConf = require('path').join(require('os').homedir(), '.proxychains.conf');
        try {
          const proxyContent = fs.readFileSync(proxyConf, 'utf8');
          const proxyLine = proxyContent.split('\n').find(l => l.trim() && !l.trim().startsWith('#') && l.includes('http '));
          if (proxyLine) {
            const parts = proxyLine.trim().split(/\s+/);
            if (parts.length >= 5) {
              const ip = parts[1];
              const port = parts[2];
              const user = parts[3];
              const pass = parts[4];
              const proxyUrl = `http://${user}:${pass}@${ip}:${port}`;
              cmd = `cd /Users/vakandi/EliaAI && env HTTP_PROXY="${proxyUrl}" HTTPS_PROXY="${proxyUrl}" http_proxy="${proxyUrl}" https_proxy="${proxyUrl}" ELIA_MODEL=${modelValue} /Users/vakandi/Documents/dictate.command`;
            }
          }
        } catch (e) {
          console.error('Proxy config read error:', e.message);
        }
      }

      if (!cmd) {
        cmd = `cd /Users/vakandi/EliaAI && ELIA_MODEL=${modelValue} /Users/vakandi/Documents/dictate.command`;
      }

      const script = [
        'tell application "Terminal" to activate',
        'tell application "Terminal" to do script ' + JSON.stringify(cmd),
        'delay 0.3',
        'tell application "Terminal" to set bounds of front window to {100, 50, 500, 900}'
      ].map(s => '-e ' + JSON.stringify(s)).join(' ');
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
  
  let cmd;
  if (proxyEnabled) {
    const proxyConf = require('path').join(require('os').homedir(), '.proxychains.conf');
    try {
      const proxyContent = fs.readFileSync(proxyConf, 'utf8');
      const proxyLine = proxyContent.split('\n').find(l => l.trim() && !l.trim().startsWith('#') && l.includes('http '));
      if (proxyLine) {
        const parts = proxyLine.trim().split(/\s+/);
        if (parts.length >= 5) {
          const ip = parts[1];
          const port = parts[2];
          const user = parts[3];
          const pass = parts[4];
          const proxyUrl = `http://${user}:${pass}@${ip}:${port}`;
          cmd = `env HTTP_PROXY="${proxyUrl}" HTTPS_PROXY="${proxyUrl}" http_proxy="${proxyUrl}" https_proxy="${proxyUrl}" /Users/vakandi/EliaAI/scripts/voice-command-only.sh`;
        }
      }
    } catch (e) {
      console.error('Proxy config read error:', e.message);
    }
  }
  
  if (!cmd) {
    cmd = '/Users/vakandi/EliaAI/scripts/voice-command-only.sh';
  }
  
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

// Get current scheduler settings — standardEnabled follows the real LaunchAgent plist (not stale .scheduler_state).
function getCurrentCronSettings() {
  const stateFile = path.join(EliaAIRoot, '.scheduler_state');
  const home = process.env.HOME || '/Users/vakandi';
  const launchdPlist = path.join(home, 'Library/LaunchAgents/com.elia.elia-agent.plist');
  const morningPlist = path.join(home, 'Library/LaunchAgents/com.elia.elia-agent-morning.plist');
  const plistInstalled = fs.existsSync(launchdPlist);

  const parseIntervalFromPlist = (content) => {
    const intervalMatch = content.match(/<key>StartInterval<\/key>\s*<integer>(\d+)<\/integer>/);
    const calendarMatch = content.match(/<key>StartCalendarInterval<\/key>/);
    const minuteMatches = content.match(/<key>Minute<\/key><integer>(\d+)<\/integer>/g);
    let detectedInterval = '1h';
    if (intervalMatch) {
      const sec = parseInt(intervalMatch[1], 10);
      detectedInterval =
        sec === 1800 ? '30min' :
        sec === 1200 ? '20min' :
        sec === 7200 ? '2h' :
        sec === 10800 ? '3h' :
        sec === 14400 ? '4h' : '1h';
    } else if (calendarMatch && minuteMatches) {
      const minutes = minuteMatches.map((m) => parseInt(m.match(/\d+/)[0], 10));
      if (minutes.includes(0) && minutes.includes(30)) detectedInterval = '30min';
      else if (minutes.includes(0) && minutes.includes(20) && minutes.includes(40)) detectedInterval = '20min';
      else if (minutes.length === 1 && minutes[0] === 0) detectedInterval = '1h';
    }
    return detectedInterval;
  };

  try {
    let fromFile = null;
    if (fs.existsSync(stateFile)) {
      const state = fs.readFileSync(stateFile, 'utf8');
      const lines = state.trim().split('\n');
      const settings = {};
      lines.forEach((line) => {
        const [key, value] = line.split('=');
        if (key && value !== undefined) {
          settings[key] = value;
        }
      });
      fromFile = {
        morningEnabled: settings.morningEnabled === 'true',
        morningHour: parseInt(settings.morningHour, 10) || 10,
        interval: settings.interval || '1h',
        startHour: parseInt(settings.startHour, 10) || 11,
        endHour: parseInt(settings.endHour, 10) || 21,
      };
    }

    if (plistInstalled) {
      const content = fs.readFileSync(launchdPlist, 'utf8');
      const detectedInterval = parseIntervalFromPlist(content);
      return {
        morningEnabled: fs.existsSync(morningPlist),
        morningHour: fromFile?.morningHour ?? 10,
        standardEnabled: true,
        interval: fromFile?.interval || detectedInterval,
        startHour: fromFile?.startHour ?? 9,
        endHour: fromFile?.endHour ?? 23,
      };
    }

    if (fromFile) {
      return {
        morningEnabled: fs.existsSync(morningPlist),
        morningHour: fromFile.morningHour,
        standardEnabled: false,
        interval: fromFile.interval,
        startHour: fromFile.startHour,
        endHour: fromFile.endHour,
      };
    }
  } catch (e) {
    console.error('Error reading scheduler state:', e.message);
  }

  return {
    morningEnabled: fs.existsSync(morningPlist),
    morningHour: 10,
    standardEnabled: false,
    interval: '1h',
    startHour: 11,
    endHour: 21,
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

// Subworker Manager Popup
function showSubworkerPopupWindow() {
  if (subworkerPopup && !subworkerPopup.isDestroyed()) {
    subworkerPopup.focus();
    return;
  }

  const display = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = display.workAreaSize;

  const popupW = 950;
  const popupH = 680;
  const x = Math.round((screenWidth - popupW) / 2);
  const y = Math.round((screenHeight - popupH) / 2);

  subworkerPopup = new BrowserWindow({
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

  subworkerPopup.loadFile(path.join(__dirname, '..', 'subworker-popup.html'));

  subworkerPopup.on('closed', () => {
    subworkerPopup = null;
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
