// sidepanel.js — RoboMonkey v3: AI Chat → Auto-install flow

// Default system prompt (used for migrations)
const DEFAULT_SYSTEM_PROMPT = `You are RoboMonkey AI — an expert Chrome Extension and Userscript developer embedded inside a browser extension. You help users build, edit, and deploy scripts through natural conversation — no coding experience required.

## 🌐 LANGUAGE RULE (CRITICAL)
Detect the user's language from their message. If they write in Russian, you MUST respond in Russian. If in English, respond in English. Match the user's language exactly — never switch languages mid-conversation.

## Core Capabilities
- Userscripts (Tampermonkey/Greasemonkey compatible) with proper ==UserScript== header
- Chrome Extensions (Manifest V3) — content scripts, popups, background workers
- Data extraction & scraping tools (CSV, JSON, TXT output)
- UI modifications — buttons, panels, overlays on any website
- Form autofill & automation tools
- Workflow automations triggered by user actions or page events

## How You Work
1. For clear requests — generate code immediately. No unnecessary questions.
2. For ambiguous requests, make a reasonable assumption, state it briefly, and build — don't ask multiple clarifying questions.
3. Ask clarifying questions ONLY if truly necessary (target site is unclear, behavior is undefined, the request is too vague to build anything).
4. You have access to the current page's URL and DOM context. Use this to write accurate selectors.

## Output Format
- Userscript: single .js file with ==UserScript== header including @name, @match, @grant, @run-at
- Extension: clearly label each file (manifest.json, content.js, background.js, popup.html)
- The code is extracted AUTOMATICALLY and the user does NOT see it in the chat. Therefore:
  - Put the complete code inside a markdown code block ('''javascript ... ''')
  - After the code block, give a 2-3 sentence plain-language summary of what was built and how to test it
  - End with: "✅ Готово! Обнови страницу чтобы проверить." (if Russian) or "✅ Ready! Refresh the page to test it." (if English)

## Code Standards
- Use vanilla JavaScript unless a library is clearly needed
- Query selectors must be robust — prefer data-* attributes and semantic roles over fragile class names
- Always wrap logic in try/catch with console error logging
- For userscripts, use @run-at document-idle to ensure DOM is ready
- For data extraction, default output format is CSV unless user specifies otherwise
- Never request more permissions than necessary

## Tone
Friendly, fast, and capable. Like a senior developer sitting next to the user. Use simple language; avoid developer jargon unless the user uses it first. Celebrate small wins. Never make the user feel dumb for not knowing how to code.`;

// =================== STATE ===================
let scripts = [];
let versions = {};
let chatHistory = [];
let settings = {
  apiKey: '',
  selectedModel: 'openai/gpt-4o-mini',
  customModel: '',
  temperature: 0.7,
  autoInstall: true,
  settingsVersion: 2,
  systemPrompt: DEFAULT_SYSTEM_PROMPT,
  theme: 'dark'
};
let modelsList = [];
let isGenerating = false;
// =================== INIT ===================
document.addEventListener('DOMContentLoaded', async () => {
  await loadData();
  setupNavigation();
  setupChat();
  setupTemperature();
  setupAutosave();
  setupCustomModel();
  renderScripts();
  updateStatusIndicator();
  checkApiConnection();
  handleQuickAsk();
});

// =================== DATA ===================
async function loadData() {
  const data = await chrome.storage.local.get(['scripts', 'versions', 'chatHistory', 'settings', 'modelsList']);
  scripts = data.scripts || [];
  versions = data.versions || {};
  chatHistory = data.chatHistory || [];
  modelsList = data.modelsList || [];
  if (data.settings) {
    settings = { ...settings, ...data.settings };
    // Migrate system prompt on version bump
    if (!settings.settingsVersion || settings.settingsVersion < 2) {
      settings.systemPrompt = DEFAULT_SYSTEM_PROMPT;
      settings.settingsVersion = 2;
    }
  }

  // Restore UI
  document.getElementById('apiKey').value = settings.apiKey || '';
  document.getElementById('customModel').value = settings.customModel || '';
  document.getElementById('systemPrompt').value = settings.systemPrompt;
  document.getElementById('temperature').value = Math.round(settings.temperature * 10);
  document.getElementById('tempValue').textContent = settings.temperature;
  document.getElementById('autoInstall').checked = settings.autoInstall !== false;

  // Restore model list
  const select = document.getElementById('modelSelect');
  if (modelsList.length > 0) {
    const freeOnly = document.getElementById('freeOnly')?.checked;
    const filtered = freeOnly
      ? modelsList.filter(m => m.pricing?.prompt === 0 && m.pricing?.completion === 0)
      : modelsList;
    select.innerHTML = filtered.map(m => {
      const price = (m.pricing?.prompt > 0 || m.pricing?.completion > 0)
        ? `$${m.pricing.prompt}/$${m.pricing.completion}`
        : 'FREE';
      return `<option value="${m.id}">${m.id} (${m.context_length || '?'} ctx) [${price}]</option>`;
    }).join('') || '<option>Error loading models</option>';
  }
  select.value = settings.selectedModel;

  // Restore chat
  const container = document.getElementById('chatMessages');
  container.innerHTML = '';
  if (chatHistory.length === 0) {
    container.innerHTML = `
      <div class="msg assistant">
        <strong>🐵 RoboMonkey AI</strong><br><br>
        Tell me what userscript you want. I'll ask questions if needed, then create it automatically.<br><br>
        <em>Example: "Hide all ads on YouTube and make the dark theme permanent"</em>
      </div>`;
  } else {
    chatHistory.forEach(msg => appendMessage(msg.role, msg.content, false));
  }
}

async function saveData() {
  await chrome.storage.local.set({ scripts, versions, chatHistory, settings, modelsList });
  chrome.runtime.sendMessage({ type: 'SAVE_SCRIPTS', scripts });
}

function setupAutosave() {
  const fields = ['apiKey', 'modelSelect', 'customModel', 'systemPrompt', 'autoInstall'];
  fields.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const handler = () => {
      settings.apiKey = document.getElementById('apiKey').value.trim();
      settings.selectedModel = document.getElementById('modelSelect').value;
      settings.customModel = document.getElementById('customModel').value.trim();
      settings.systemPrompt = document.getElementById('systemPrompt').value;
      settings.temperature = parseFloat(document.getElementById('tempValue').textContent);
      settings.autoInstall = document.getElementById('autoInstall').checked;
      saveData();
      updateStatusIndicator();
    };
    if (el.type === 'checkbox') el.addEventListener('change', handler);
    else el.addEventListener('change', handler);
  });
}

async function handleQuickAsk() {
  try {
    const data = await chrome.storage.session.get(['quickAsk']);
    if (data.quickAsk) {
      document.getElementById('chatInput').value = data.quickAsk;
      await chrome.storage.session.remove(['quickAsk']);
      sendMessage();
    }
  } catch (e) {
    console.error('[RoboMonkey] QuickAsk error:', e);
  }
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

function switchScreen(name) {
  document.querySelectorAll('.nav button').forEach(b => {
    b.classList.toggle('active', b.dataset.screen === name);
  });
  document.querySelectorAll('.screen').forEach(s => {
    s.classList.toggle('active', s.id === `screen-${name}`);
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
  const createBtn = document.getElementById('createScriptBtn');

  btn.addEventListener('click', () => sendMessage());
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  createBtn.addEventListener('click', () => {
    input.focus();
    showToast('Describe what you want in the chat below 👇');
  });
}

async function sendMessage() {
  if (isGenerating) return;
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;

  const apiKey = document.getElementById('apiKey').value.trim() || settings.apiKey;
  const model = getModel();

  if (!apiKey) {
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
    ...chatHistory.slice(-30)
  ];

  try {
    const res = await chrome.runtime.sendMessage({
      type: 'FETCH_OPENROUTER',
      apiKey,
      payload: {
        model,
        messages,
        temperature: settings.temperature,
        max_tokens: 4000
      }
    });

    if (res.error) throw new Error(res.error);

    const fullContent = res.choices?.[0]?.message?.content || 'No response';

    // === AUTO-INSTALL LOGIC ===
    const autoInstall = document.getElementById('autoInstall').checked;
    let cleanContent = fullContent;
    let installed = false;

    if (autoInstall) {
      // Extract ALL code blocks
      const codeBlocks = [];
      cleanContent = fullContent.replace(/```(?:\w+)?\n([\s\S]*?)```/g, (match, code) => {
        codeBlocks.push(code);
        return '';
      }).trim();

      if (codeBlocks.length > 0) {
        const firstCode = codeBlocks[0];
        const scriptData = extractScriptFromCode(firstCode);
        if (scriptData && scriptData.code) {
          installGeneratedScript(scriptData, false); // silent
          installed = true;
          // If no remaining text, add success message
          if (!cleanContent) {
            cleanContent = `✅ Готово! Скрипт «${scriptData.name}» создан и активирован. Обнови страницу — он уже работает.`;
          }
        }
      }
    }

    // Fallback: if nothing left to show
    if (!cleanContent) {
      cleanContent = installed
        ? '✅ Скрипт создан и активирован. Обнови страницу чтобы проверить.'
        : fullContent;
    }

    chatHistory.push({ role: 'assistant', content: cleanContent });
    appendMessage('assistant', cleanContent);
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
  div.innerHTML = escapeHtml(content).replace(/\n/g, '<br>');
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

// =================== SCRIPT MANAGEMENT ===================
function extractScriptFromCode(code) {
  const nameMatch = code.match(/@name\s+(.+)/);
  const matchMatch = code.match(/@match\s+(.+)/);
  const grantMatch = code.match(/@grant\s+(.+)/);

  const name = nameMatch ? nameMatch[1].trim() : 'AI Generated Script';
  const matches = matchMatch ? [matchMatch[1].trim()] : ['*://*/*'];
  const grants = grantMatch ? [grantMatch[1].trim()] : ['none'];

  return { name, description: 'Generated by RoboMonkey AI', code, matches, grants };
}

function installGeneratedScript(scriptData, showNotification = true) {
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
  versions[script.id] = [{ version: 1, code: script.code, createdAt: Date.now(), comment: 'AI generated' }];
  saveData();
  renderScripts();

  if (showNotification) showToast('Script installed! Check "My Scripts" tab.');
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => showToast('Copied to clipboard'));
}

// =================== SCRIPTS LIST ===================
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
        <div style="font-size:12px;margin-top:8px;">Go to Chat and describe what you want — I'll create it automatically.</div>
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

  const newVersion = {
    version: vers.length + 1,
    code: v.code,
    createdAt: Date.now(),
    comment: `Restored from version ${versionNum}`
  };
  vers.push(newVersion);
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
    const url = `https://greasyfork.org/en/scripts?q=${encodeURIComponent(query)}`;
    const res = await chrome.runtime.sendMessage({ type: 'FETCH_GREASYFORK', url });
    if (res.error) throw new Error(res.error);

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

function setupCustomModel() {
  const custom = document.getElementById('customModel');
  const select = document.getElementById('modelSelect');
  // If custom model is entered, it takes priority
  custom.addEventListener('input', () => {
    if (custom.value.trim()) {
      // visual cue: dim the select
      select.style.opacity = '0.5';
    } else {
      select.style.opacity = '1';
    }
  });
}

function getModel() {
  const custom = document.getElementById('customModel')?.value.trim();
  if (custom) return custom;
  return document.getElementById('modelSelect')?.value || settings.selectedModel;
}

async function saveSettings() {
  settings.apiKey = document.getElementById('apiKey').value.trim();
  settings.selectedModel = document.getElementById('modelSelect').value;
  settings.customModel = document.getElementById('customModel').value.trim();
  settings.systemPrompt = document.getElementById('systemPrompt').value;
  settings.temperature = parseFloat(document.getElementById('tempValue').textContent);
  settings.autoInstall = document.getElementById('autoInstall').checked;
  await saveData();
  updateStatusIndicator();
  checkApiConnection();
  showToast('Settings saved');
}

async function loadModels() {
  const apiKey = document.getElementById('apiKey').value.trim() || settings.apiKey;
  if (!apiKey) {
    alert('Enter API Key first');
    return;
  }

  const select = document.getElementById('modelSelect');
  const freeOnly = document.getElementById('freeOnly').checked;
  select.innerHTML = '<option>Loading...</option>';

  try {
    const res = await chrome.runtime.sendMessage({
      type: 'FETCH_MODELS',
      apiKey
    });
    if (res.error) throw new Error(res.error);

    const models = res.data || [];
    modelsList = models;
    const filtered = freeOnly
      ? models.filter(m => m.pricing?.prompt === 0 && m.pricing?.completion === 0)
      : models;

    select.innerHTML = filtered.map(m => {
      const price = (m.pricing?.prompt > 0 || m.pricing?.completion > 0)
        ? `$${m.pricing.prompt}/$${m.pricing.completion}`
        : 'FREE';
      return `<option value="${m.id}">${m.id} (${m.context_length || '?'} ctx) [${price}]</option>`;
    }).join('');

    await saveData();
    showToast(`Loaded ${filtered.length} models`);
  } catch (e) {
    select.innerHTML = '<option>Error loading models</option>';
    alert('Failed: ' + e.message);
  }
}

async function testModel() {
  const apiKey = document.getElementById('apiKey').value.trim() || settings.apiKey;
  const model = getModel();

  if (!apiKey) {
    alert('Enter API Key first');
    return;
  }
  if (!model) {
    alert('Select or enter a model first');
    return;
  }

  const btn = event.target;
  const originalText = btn.textContent;
  btn.textContent = 'Testing...';
  btn.disabled = true;

  try {
    const res = await chrome.runtime.sendMessage({
      type: 'FETCH_OPENROUTER',
      apiKey,
      payload: {
        model,
        messages: [{ role: 'user', content: 'Say exactly "Model works" and nothing else.' }],
        temperature: 0.1,
        max_tokens: 20
      }
    });

    if (res.error) throw new Error(res.error);
    const reply = res.choices?.[0]?.message?.content?.trim() || 'No response';

    if (reply.toLowerCase().includes('works') || reply.toLowerCase().includes('model')) {
      alert(`✅ Model "${model}" works!\n\nResponse: "${reply}"`);
    } else {
      alert(`⚠️ Model responded but not as expected:\n"${reply}"`);
    }
  } catch (e) {
    alert(`❌ Model "${model}" failed:\n${e.message}`);
  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
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
  const keys = ['name', 'description', 'version', 'author', 'grant', 'match', 'include', 'exclude'];

  keys.forEach(key => {
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

function showToast(msg) {
  const toast = document.createElement('div');
  toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#ff6b35;color:#fff;padding:10px 20px;border-radius:8px;font-size:13px;z-index:9999;animation:fadein 0.3s;';
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2500);
}
