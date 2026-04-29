// editor.js - Full-page code editor for userscripts

let scriptId = null;
let originalCode = '';
let scriptData = null;
let scripts = [];
let versions = {};

const params = new URLSearchParams(window.location.search);
scriptId = params.get('id');

document.addEventListener('DOMContentLoaded', async () => {
  const data = await chrome.storage.local.get(['scripts', 'versions']);
  scripts = data.scripts || [];
  versions = data.versions || {};
  
  scriptData = scripts.find(s => s.id === scriptId);
  if (!scriptData) {
    document.body.innerHTML = '<div style="padding:40px;color:#f87171;">Script not found</div>';
    return;
  }
  
  originalCode = scriptData.code;
  
  // Fill fields
  document.getElementById('codeEditor').value = scriptData.code;
  document.getElementById('editName').value = scriptData.name;
  document.getElementById('editDesc').value = scriptData.description || '';
  document.getElementById('editGrant').value = (scriptData.grants || ['none'])[0];
  document.getElementById('scriptMeta').textContent = `${scriptData.name} | v${versions[scriptId]?.length || 1}`;
  
  renderMatches();
  updateLineNumbers();
  
  // Sync scroll
  const editor = document.getElementById('codeEditor');
  const lines = document.getElementById('lineNumbers');
  editor.addEventListener('scroll', () => {
    lines.scrollTop = editor.scrollTop;
  });
  editor.addEventListener('input', () => {
    updateLineNumbers();
  });
  editor.addEventListener('keydown', handleTab);
});

function updateLineNumbers() {
  const editor = document.getElementById('codeEditor');
  const lines = document.getElementById('lineNumbers');
  const count = editor.value.split('\n').length;
  lines.innerHTML = Array.from({ length: count }, (_, i) => i + 1).join('\n');
}

function handleTab(e) {
  if (e.key === 'Tab') {
    e.preventDefault();
    const editor = document.getElementById('codeEditor');
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    editor.value = editor.value.substring(0, start) + '  ' + editor.value.substring(end);
    editor.selectionStart = editor.selectionEnd = start + 2;
  }
}

function renderMatches() {
  const container = document.getElementById('editMatches');
  const matches = scriptData.matches || ['*://*/*'];
  container.innerHTML = matches.map((m, i) => `
    <span class="match-tag">${escapeHtml(m)} <span class="del" onclick="removeMatch(${i})">×</span></span>
  `).join('');
}

function addMatch() {
  const input = document.getElementById('newMatch');
  const val = input.value.trim();
  if (!val) return;
  if (!scriptData.matches) scriptData.matches = [];
  scriptData.matches.push(val);
  input.value = '';
  renderMatches();
}

function removeMatch(index) {
  scriptData.matches.splice(index, 1);
  renderMatches();
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function getUpdatedCode() {
  const editor = document.getElementById('codeEditor');
  let code = editor.value;
  
  // Update metadata in code from form fields
  const name = document.getElementById('editName').value || scriptData.name;
  const desc = document.getElementById('editDesc').value || '';
  const matches = scriptData.matches || ['*://*/*'];
  const grant = document.getElementById('editGrant').value || 'none';
  
  // Replace or add metadata block
  const metaBlock = `// ==UserScript==
// @name         ${name}
// @match        ${matches.join('\n// @match        ')}
// @grant        ${grant}
// @version      ${(versions[scriptId]?.length || 1) + 1}.0
// @description  ${desc}
// ==/UserScript==`;
  
  if (code.includes('==UserScript==')) {
    code = code.replace(/==UserScript==[\s\S]*?==\/UserScript==/, metaBlock);
  } else {
    code = metaBlock + '\n\n' + code;
  }
  
  return code;
}

async function saveScript() {
  const code = getUpdatedCode();
  scriptData.code = code;
  scriptData.name = document.getElementById('editName').value || scriptData.name;
  scriptData.description = document.getElementById('editDesc').value;
  scriptData.grants = [document.getElementById('editGrant').value || 'none'];
  scriptData.updatedAt = Date.now();
  
  await chrome.storage.local.set({ scripts, versions });
  chrome.runtime.sendMessage({ type: 'SAVE_SCRIPTS', scripts });
  
  showToast('Saved');
  originalCode = code;
}

async function saveNewVersion() {
  const code = getUpdatedCode();
  scriptData.code = code;
  scriptData.updatedAt = Date.now();
  
  if (!versions[scriptId]) versions[scriptId] = [];
  const verNum = versions[scriptId].length + 1;
  versions[scriptId].push({
    version: verNum,
    code: code,
    createdAt: Date.now(),
    comment: `Edited in editor (v${verNum})`
  });
  
  if (versions[scriptId].length > 20) versions[scriptId].shift();
  
  await chrome.storage.local.set({ scripts, versions });
  chrome.runtime.sendMessage({ type: 'SAVE_VERSIONS', versions });
  chrome.runtime.sendMessage({ type: 'SAVE_SCRIPTS', scripts });
  
  document.getElementById('scriptMeta').textContent = `${scriptData.name} | v${verNum}`;
  showToast(`Saved as version ${verNum}`);
  originalCode = code;
}

function formatCode() {
  // Simple formatter: fix indentation
  const editor = document.getElementById('codeEditor');
  let code = editor.value;
  // Basic cleanup
  code = code.replace(/\t/g, '  ');
  editor.value = code;
  updateLineNumbers();
  showToast('Formatted (basic)');
}

async function testScript() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) {
    showToast('No active tab');
    return;
  }
  
  try {
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (code) => {
        try {
          eval(code);
          return { ok: true };
        } catch (e) {
          return { ok: false, error: e.message };
        }
      },
      args: [document.getElementById('codeEditor').value]
    });
    showToast('Script executed on tab');
  } catch (e) {
    showToast('Error: ' + e.message);
  }
}

function showToast(msg) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2500);
}
