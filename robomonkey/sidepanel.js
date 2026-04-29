// sidepanel.js - Main UI logic for RoboMonkey

// =================== STATE ===================
let scripts = [];
let versions = {};
let chatHistory = [];
let settings = {
  apiKey: '',
  selectedModel: 'openai/gpt-4o-mini',
  temperature: 0.7,
  systemPrompt: 'You are an expert userscript developer for Tampermonkey/Greasemonkey. Generate working JavaScript code with proper metadata block (// ==UserScript== with @name, @match, @grant). Use GM_* APIs when needed. Return only the script inside a code block.',
  theme: 'dark'
};
let isGenerating = false;

// =================== INIT ===================
document.addEventListener('DOMContentLoaded', async () => {
  await loadData();
  setupNavigation();
  setupChat();
  setupTemperature();
  renderScripts();
  updateStatusIndicator();
  checkApiConnection();
});

async function loadData() {
  const data = await chrome.storage.local.get(['scripts', 'versions', 'chatHistory', 'settings']);
  scripts = data.scripts || [];
  versions = data.versions || {};
  chatHistory = data.chatHistory || [];
  if (data.settings) settings = { ...settings, ...data.settings };
  
  // Restore UI state
  document.getElementById('apiKey').value = settings.apiKey || '';
  document.getElementById('modelSelect').value = settings.selectedModel;
  document.getElementById('systemPrompt').value = settings.systemPrompt;
  document.getElementById('temperature').value = Math.round(settings.temperature * 10);
  document.getElementById('tempValue').textContent = settings.temperature;
  
  // Restore chat
  const chatContainer = document.getElementById('chatMessages');
  chatContainer.innerHTML = '';
  if (chatHistory.length === 0) {
    chatContainer.innerHTML = `
      <div class="msg assistant">
        <strong>RoboMonkey AI</strong><br>
        Describe what userscript you want. For example: <em>"Hide ads on YouTube"</em> or <em>"Add a dark mode button to Reddit"</em>.
      </div>`;
  } else {
    chatHistory.forEach(msg => appendMessage(msg.role, msg.content, false));
  }
}

async function saveData() {
  await chrome.storage.local.set({ scripts, versions, chatHistory, settings });
  // Notify background to reload scripts
  chrome.runtime.sendMessage({ type: 'SAVE_SCRIPTS', scripts });
}

// =================== NAVIGATION ===================
function setupNavigation() {
  document.querySelectorAll('.nav button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(`screen-${btn.dataset.screen}`).classList.add('active');
    });
  });
}

// =================== STATUS ===================
function updateStatusIndicator() {
  const el = document.getElementById('statusIndicator');
  if (!settings.apiKey) {
    el.textContent = '● No API Key';
    el.className = 'status error';
    return;
  }
  el.textContent = '● Ready';
  el.className = 'status connected';
}

async function checkApiConnection() {
  if (!settings.apiKey) return;
  try {
    const res = await chrome.runtime.sendMessage({
      type: 'FETCH_MODELS',
      apiKey: settings.apiKey
    });
    if (res.error) throw new Error(res.error);
    updateStatusIndicator();
  } catch (e) {
    const el = document.getElementById('statusIndicator');
    el.textContent = '● API Error';
    el.className = 'status error';
  }
}

// =================== CHAT ===================
function setupChat() {
  const input = document.getElementById('chatInput');
  const btn = document.getElementById('sendBtn');
  
  btn.addEventListener('click', () => sendMessage());
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
}

async function sendMessage() {
  if (isGenerating) return;
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;
  
  if (!settings.apiKey) {
    alert('Please set your OpenRouter API Key in Settings first.');
    switchScreen('settings');
    return;
  }
  
  input.value = '';
  appendMessage('user', text);
  chatHistory.push({ role: 'user', content: text });
  
  isGenerating = true;
  document.getElementById('typingIndicator').style.display = 'block';
  document.getElementById('sendBtn').disabled = true;
  
  const messages = [
    { role: 'system', content: settings.systemPrompt },
    ...chatHistory.slice(-20)
  ];
  
  try {
    const res = await chrome.runtime.sendMessage({
      type: 'FETCH_OPENROUTER',
      apiKey: settings.apiKey,
      payload: {
        model: settings.selectedModel,
        messages,
        temperature: settings.temperature,
        max_tokens: 4000
      }
    });
    
    if (res.error) throw new Error(res.error);
    
    const content = res.choices?.[0]?.message?.content || 'No response';
    chatHistory.push({ role: 'assistant', content });
    appendMessage('assistant', content, true);
    await saveData();
  } catch (e) {
    appendMessage('assistant', `**Error:** ${e.message}`);
  } finally {
    isGenerating = false;
    document.getElementById('typingIndicator').style.display = 'none';
    document.getElementById('sendBtn').disabled = false;
  }
}

function appendMessage(role, content, parseCode = false) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  
  if (parseCode && content.includes('```')) {
    // Parse markdown code blocks
    let html = '';
    const parts = content.split(/```(\w+)?\n/);
    let inCode = false;
    let lang = '';
    
    parts.forEach((part, i) => {
      if (i % 2 === 0) {
        // Text part
        html += escapeHtml(part).replace(/\n/g, '<br>')
          .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.+?)\*/g, '<em>$1</em>');
      } else {
        // Code language
        lang = part || 'javascript';
      }
      if (i % 2 === 1 && parts[i+1]) {
        // Code content (next part)
        const code = parts[i+1];
        const extractedScript = extractScriptFromCode(code);
        html += `<div class="code-block"><span class="lang-label">${lang}</span>${escapeHtml(code)}</div>`;
        if (extractedScript) {
          html += `<div class="actions">
            <button class="btn-sm btn-primary" onclick='installGeneratedScript(${JSON.stringify(extractedScript).replace(/'/g, "&#39;")})'>📥 Install Script</button>
            <button class="btn-sm btn-secondary" onclick="copyToClipboard(${JSON.stringify(code).replace(/'/g, "&#39;")})">📋 Copy</button>
          </div>`;
        }
        // Skip the code content part since we just processed it
        parts[i+1] = '';
      }
    });
    
    div.innerHTML = html;
  } else {
    div.innerHTML = escapeHtml(content).replace(/\n/g, '<br>');
  }
  
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function extractScriptFromCode(code) {
  // Extract metadata and code
  const nameMatch = code.match(/@name\s+(.+)/);
  const matchMatch = code.match(/@match\s+(.+)/);
  const grantMatch = code.match(/@grant\s+(.+)/);
  
  const name = nameMatch ? nameMatch[1].trim() : 'AI Generated Script';
  const matches = matchMatch ? [matchMatch[1].trim()] : ['*://*/*'];
  const grants = grantMatch ? [grantMatch[1].trim()] : ['none'];
  
  return {
    name,
    description: 'Generated by RoboMonkey AI',
    code,
    matches,
    grants
  };
}

function installGeneratedScript(scriptData) {
  const script = {
    id: generateId(),
    name: scriptData.name,
    description: scriptData.description,
    code: scriptData.code,
    matches: scriptData.matches,
    grants: scriptData.grants,
    enabled: true,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    source: 'ai'
  };
  
  scripts.push(script);
  versions[script.id] = [{ version: 1, code: script.code, createdAt: Date.now(), comment: 'Initial AI generation' }];
  saveData();
  renderScripts();
  switchScreen('scripts');
  
  // Show toast
  showToast('Script installed! Check "My Scripts" tab.');
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => showToast('Copied to clipboard'));
}

// =================== SCRIPTS MANAGER ===================
function renderScripts() {
  const container = document.getElementById('scriptsList');
  const filter = document.getElementById('scriptFilter')?.value.toLowerCase() || '';
  const filtered = scripts.filter(s => 
    s.name.toLowerCase().includes(filter) || 
    s.description?.toLowerCase().includes(filter) ||
    s.matches.some(m => m.toLowerCase().includes(filter))
  );
  
  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="icon">📜</div>
        <div>No scripts yet.</div>
        <div style="font-size:12px;margin-top:8px;">Generate one in the Chat tab or create manually.</div>
      </div>`;
    return;
  }
  
  container.innerHTML = filtered.map(script => `
    <div class="script-card">
      <div class="title">
        <div class="toggle-switch ${script.enabled ? 'on' : ''}" onclick="toggleScript('${script.id}')"></div>
        ${escapeHtml(script.name)}
      </div>
      <div class="meta">
        ${script.matches.map(m => `<span class="match-tag">${escapeHtml(m)}</span>`).join('')}
        <span style="margin-left:8px;color:#555;">v${versions[script.id]?.length || 1} • ${new Date(script.updatedAt).toLocaleDateString()}</span>
      </div>
      <div style="font-size:12px;color:#777;margin-bottom:6px;">${escapeHtml(script.description || '')}</div>
      <div class="actions">
        <button class="btn-sm btn-secondary" onclick="editScript('${script.id}')">✏️ Edit</button>
        <button class="btn-sm btn-secondary" onclick="showVersions('${script.id}')">📝 Versions (${versions[script.id]?.length || 1})</button>
        <button class="btn-sm btn-secondary" onclick="exportScript('${script.id}')">📤 Export</button>
        <button class="btn-sm btn-secondary" onclick="deleteScript('${script.id}')" style="color:#f87171;">🗑️ Delete</button>
      </div>
    </div>
  `).join('');
}

function toggleScript(id) {
  const script = scripts.find(s => s.id === id);
  if (!script) return;
  script.enabled = !script.enabled;
  script.updatedAt = Date.now();
  saveData();
  renderScripts();
}

function createNewScript() {
  const template = `// ==UserScript==
// @name         New Script
// @match        *://*/*
// @grant        none
// @version      1.0
// @description  
// ==/UserScript==

(function() {
  'use strict';
  // Your code here
  console.log('Hello from RoboMonkey!');
})();`;

  const script = {
    id: generateId(),
    name: 'New Script',
    description: 'Manually created',
    code: template,
    matches: ['*://*/*'],
    grants: ['none'],
    enabled: false,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    source: 'manual'
  };
  
  scripts.push(script);
  versions[script.id] = [{ version: 1, code: template, createdAt: Date.now(), comment: 'Created manually' }];
  saveData();
  openEditor(script.id);
}

function editScript(id) {
  openEditor(id);
}

function openEditor(scriptId) {
  const url = chrome.runtime.getURL(`editor.html?id=${scriptId}`);
  window.open(url, '_blank');
}

function showVersions(id) {
  const script = scripts.find(s => s.id === id);
  const vers = versions[id] || [];
  if (!vers.length) return;
  
  let html = `<div style="background:#16161e;border:1px solid #2a2a35;border-radius:10px;padding:14px;">
    <h3 style="margin-bottom:12px;color:#ff6b35;">Versions: ${escapeHtml(script.name)}</h3>`;
  
  html += vers.slice().reverse().map((v, idx) => `
    <div style="padding:10px;border-bottom:1px solid #2a2a35;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong>Version ${v.version}</strong>
        <span style="font-size:11px;color:#555;">${new Date(v.createdAt).toLocaleString()}</span>
      </div>
      <div style="font-size:11px;color:#666;margin:4px 0;">${escapeHtml(v.comment || '')}</div>
      ${idx !== 0 ? `<button class="btn-sm btn-primary" onclick="restoreVersion('${id}', ${v.version})">↩️ Restore</button>` : '<span style="font-size:11px;color:#4ade80;">✓ Current</span>'}
    </div>
  `).join('');
  
  html += '</div>';
  
  // Show in a modal-like overlay
  const overlay = document.createElement('div');
  overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);z-index:9999;overflow:auto;padding:20px;';
  overlay.innerHTML = html + '<button class="btn-full" style="margin-top:12px;" onclick="this.parentElement.remove()">Close</button>';
  document.body.appendChild(overlay);
}

function restoreVersion(scriptId, versionNum) {
  const vers = versions[scriptId];
  const v = vers?.find(x => x.version === versionNum);
  if (!v) return;
  
  const script = scripts.find(s => s.id === scriptId);
  if (!script) return;
  
  script.code = v.code;
  script.updatedAt = Date.now();
  
  // Save as new version
  const newVersion = {
    version: vers.length + 1,
    code: v.code,
    createdAt: Date.now(),
    comment: `Restored from version ${versionNum}`
  };
  vers.push(newVersion);
  
  // Trim to 20 versions
  if (vers.length > 20) vers.shift();
  
  saveData();
  showToast(`Restored version ${versionNum}`);
  renderScripts();
}

function exportScript(id) {
  const script = scripts.find(s => s.id === id);
  if (!script) return;
  const blob = new Blob([script.code], { type: 'application/javascript' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${script.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.user.js`;
  a.click();
  URL.revokeObjectURL(url);
}

function deleteScript(id) {
  if (!confirm('Delete this script? This cannot be undone.')) return;
  scripts = scripts.filter(s => s.id !== id);
  delete versions[id];
  saveData();
  renderScripts();
}

function importScript() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.js,.user.js';
  input.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const text = await file.text();
    const meta = parseUserScriptMeta(text);
    
    const script = {
      id: generateId(),
      name: meta.name || file.name.replace('.user.js', ''),
      description: meta.description || 'Imported script',
      code: text,
      matches: meta.matches || ['*://*/*'],
      grants: meta.grants || ['none'],
      enabled: false,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      source: 'import'
    };
    
    scripts.push(script);
    versions[script.id] = [{ version: 1, code: text, createdAt: Date.now(), comment: 'Imported from file' }];
    saveData();
    renderScripts();
    showToast('Script imported');
  };
  input.click();
}

// =================== GREASYFORK ===================
async function searchGreasyFork() {
  const query = document.getElementById('gfSearch').value.trim();
  if (!query) return;
  
  const container = document.getElementById('gfResults');
  container.innerHTML = '<div class="empty-state">Searching...</div>';
  
  try {
    // GreasyFork search page scraping
    const url = `https://greasyfork.org/en/scripts?q=${encodeURIComponent(query)}`;
    const res = await chrome.runtime.sendMessage({ type: 'FETCH_GREASYFORK', url });
    if (res.error) throw new Error(res.error);
    
    // Parse HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(res, 'text/html');
    const items = doc.querySelectorAll('.script-list-item');
    
    if (items.length === 0) {
      container.innerHTML = '<div class="empty-state">No results found</div>';
      return;
    }
    
    container.innerHTML = Array.from(items).slice(0, 10).map(item => {
      const link = item.querySelector('a');
      const title = link?.textContent || 'Unknown';
      const href = link?.href || '';
      const desc = item.querySelector('.script-description')?.textContent || '';
      const author = item.querySelector('.script-author')?.textContent || '';
      const scriptId = href.match(/scripts\/(\d+)/)?.[1];
      
      return `
        <div class="script-card">
          <div class="title">${escapeHtml(title)}</div>
          <div class="meta">${escapeHtml(author)}</div>
          <div style="font-size:12px;color:#777;margin-bottom:8px;">${escapeHtml(desc)}</div>
          <button class="btn-sm btn-primary" onclick="importFromGreasyFork('${scriptId}')">📥 Import</button>
        </div>
      `;
    }).join('');
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Error: ${escapeHtml(e.message)}</div>`;
  }
}

async function importFromGreasyFork(scriptId) {
  if (!scriptId) return;
  const url = `https://greasyfork.org/scripts/${scriptId}.user.js`;
  
  try {
    const res = await chrome.runtime.sendMessage({ type: 'FETCH_GREASYFORK', url });
    if (res.error) throw new Error(res.error);
    
    const meta = parseUserScriptMeta(res);
    const script = {
      id: generateId(),
      name: meta.name || `GreasyFork #${scriptId}`,
      description: meta.description || 'From GreasyFork',
      code: res,
      matches: meta.matches || ['*://*/*'],
      grants: meta.grants || ['none'],
      enabled: false,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      source: 'greasyfork'
    };
    
    scripts.push(script);
    versions[script.id] = [{ version: 1, code: res, createdAt: Date.now(), comment: `Imported from GreasyFork #${scriptId}` }];
    saveData();
    renderScripts();
    showToast('GreasyFork script imported');
  } catch (e) {
    alert('Import failed: ' + e.message);
  }
}

// =================== SETTINGS ===================
function setupTemperature() {
  const slider = document.getElementById('temperature');
  const display = document.getElementById('tempValue');
  slider.addEventListener('input', () => {
    const val = slider.value / 10;
    display.textContent = val.toFixed(1);
  });
}

function saveSettings() {
  settings.apiKey = document.getElementById('apiKey').value.trim();
  settings.selectedModel = document.getElementById('modelSelect').value;
  settings.systemPrompt = document.getElementById('systemPrompt').value;
  settings.temperature = parseFloat(document.getElementById('tempValue').textContent);
  saveData();
  updateStatusIndicator();
  checkApiConnection();
  showToast('Settings saved');
}

async function loadModels() {
  if (!settings.apiKey) {
    alert('Enter API Key first');
    return;
  }
  
  const select = document.getElementById('modelSelect');
  const freeOnly = document.getElementById('freeOnly').checked;
  select.innerHTML = '<option>Loading...</option>';
  
  try {
    const res = await chrome.runtime.sendMessage({
      type: 'FETCH_MODELS',
      apiKey: settings.apiKey
    });
    if (res.error) throw new Error(res.error);
    
    const models = res.data || [];
    const filtered = freeOnly 
      ? models.filter(m => m.pricing?.prompt === 0 && m.pricing?.completion === 0)
      : models;
    
    select.innerHTML = filtered.map(m => {
      const price = m.pricing?.prompt > 0 || m.pricing?.completion > 0
        ? `$${m.pricing.prompt}/$${m.pricing.completion}`
        : 'FREE';
      return `<option value="${m.id}">${m.id} (${m.context_length || '?'} ctx) [${price}]</option>`;
    }).join('');
    
    showToast(`Loaded ${filtered.length} models`);
  } catch (e) {
    select.innerHTML = '<option>Error loading models</option>';
    alert('Failed: ' + e.message);
  }
}

// =================== UTILITIES ===================
function generateId() {
  return 'rm_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 7);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function parseUserScriptMeta(code) {
  const meta = {};
  const blockMatch = code.match(/==UserScript==([\s\S]*?)==\/UserScript==/);
  if (!blockMatch) return meta;
  
  const block = blockMatch[1];
  const single = ['name', 'description', 'version', 'author', 'grant', 'match', 'include', 'exclude'];
  
  single.forEach(key => {
    const regex = new RegExp(`//@${key}\\s+(.+)`, 'g');
    const matches = [];
    let m;
    while ((m = regex.exec(block)) !== null) matches.push(m[1].trim());
    if (matches.length === 1) meta[key] = matches[0];
    else if (matches.length > 1) meta[key + 's'] = matches;
  });
  
  return {
    name: meta.name,
    description: meta.description,
    version: meta.version,
    matches: meta.matches || (meta.match ? [meta.match] : null),
    grants: meta.grants || (meta.grant ? [meta.grant] : null)
  };
}

function switchScreen(name) {
  document.querySelectorAll('.nav button').forEach(b => {
    b.classList.toggle('active', b.dataset.screen === name);
  });
  document.querySelectorAll('.screen').forEach(s => {
    s.classList.toggle('active', s.id === `screen-${name}`);
  });
}

function showToast(msg) {
  const toast = document.createElement('div');
  toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#ff6b35;color:#fff;padding:10px 20px;border-radius:8px;font-size:13px;z-index:9999;animation:fadein 0.3s;';
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2500);
}
