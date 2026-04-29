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

  document.getElementById('codeEditor').value = scriptData.code;
  document.getElementById('editName').value = scriptData.name;
  document.getElementById('editDesc').value = scriptData.description || '';
  document.getElementById('editGrant').value = (scriptData.grants || ['none'])[0];
  document.getElementById('scriptMeta').textContent = `${scriptData.name} | v${versions[scriptId]?.length || 1}`;

  renderMatches();
  updateLineNumbers();

  const editor = document.getElementById('codeEditor');
  const lines = document.getElementById('lineNumbers');
  editor.addEventListener('scroll', () => { lines.scrollTop = editor.scrollTop; });
  editor.addEventListener('input', updateLineNumbers);
  editor.addEventListener('keydown', handleTab);

  setupEditorEvents();
});

function setupEditorEvents() {
  document.body.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;

    const action = btn.dataset.action;
    switch (action) {
      case 'formatCode': formatCode(); break;
      case 'saveScript': saveScript(); break;
      case 'saveNewVersion': saveNewVersion(); break;
      case 'testScript': testScript(); break;
      case 'addMatch': addMatch(); break;
      case 'removeMatch': {
        const idx = parseInt(btn.dataset.index);
        if (!isNaN(idx)) removeMatch(idx);
        break;
      }
    }
  });
}

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
    <span class="match-tag">${escapeHtml(m)} <span class="del" data-action="removeMatch" data-index="${i}">×</span></span>
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

  const name = document.getElementById('editName').value || scriptData.name;
  const desc = document.getElementById('editDesc').value || '';
  const grant = document.getElementById('editGrant').value || 'none';
  const matches = scriptData.matches || ['*://*/*'];

  // Update metadata block
  code = code.replace(/\/\/\s*==UserScript==[\s\S]*?\/\/\s*==\/UserScript==/, () => {
    return `// ==UserScript==\n` +
      `// @name         ${name}\n` +
      `// @match        ${matches[0]}\n` +
      (matches.length > 1 ? matches.slice(1).map(m => `// @match        ${m}`).join('\n') + '\n' : '') +
      `// @grant        ${grant}\n` +
      (desc ? `// @description  ${desc}\n` : '') +
      `// @version      ${(versions[scriptId]?.length || 1) + 1}\n` +
      `// ==/UserScript==`;
  });

  return code;
}

function saveScript() {
  const code = getUpdatedCode();
  scriptData.code = code;
  scriptData.name = document.getElementById('editName').value || scriptData.name;
  scriptData.description = document.getElementById('editDesc').value || '';
  scriptData.grants = [document.getElementById('editGrant').value || 'none'];
  scriptData.updatedAt = Date.now();

  chrome.storage.local.set({ scripts, versions }).then(() => {
    chrome.runtime.sendMessage({ type: 'SAVE_SCRIPTS', scripts });
    showToast('Saved!');
  });
}

function saveNewVersion() {
  const code = getUpdatedCode();
  scriptData.code = code;
  scriptData.updatedAt = Date.now();

  const vers = versions[scriptId] || [];
  const newVersion = {
    version: vers.length + 1,
    code,
    createdAt: Date.now(),
    comment: `Manual edit v${vers.length + 1}`
  };
  vers.push(newVersion);
  if (vers.length > 20) vers.shift();
  versions[scriptId] = vers;

  chrome.storage.local.set({ scripts, versions }).then(() => {
    chrome.runtime.sendMessage({ type: 'SAVE_SCRIPTS', scripts });
    showToast(`Saved as version ${newVersion.version}`);
    document.getElementById('scriptMeta').textContent =
      `${scriptData.name} | v${vers.length}`;
  });
}

function testScript() {
  const code = document.getElementById('codeEditor').value;
  const tabUrl = scriptData.matches[0] || '*://*/*';

  chrome.tabs.query({ active: true, currentWindow: true }).then(tabs => {
    const tab = tabs[0];
    if (!tab) return;
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (testCode) => {
        try {
          new Function(testCode)();
          return 'Test executed successfully';
        } catch (e) {
          return 'Error: ' + e.message;
        }
      },
      args: [code],
      world: 'MAIN'
    }).then(results => {
      const msg = results[0]?.result || 'No result';
      showToast('Test: ' + msg);
    }).catch(e => {
      showToast('Test failed: ' + e.message);
    });
  });
}

function formatCode() {
  const editor = document.getElementById('codeEditor');
  let code = editor.value;
  // Very basic formatting
  code = code.replace(/;\s*\n/g, ';\n').replace(/\{\s*\n/g, '{\n').replace(/\n\s*\}/g, '\n}');
  editor.value = code;
  updateLineNumbers();
  showToast('Formatted (basic)');
}

function showToast(msg) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2500);
}
