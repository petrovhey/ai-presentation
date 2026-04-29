// popup.js - Mini dashboard for current tab
let currentTabUrl = '';

document.addEventListener('DOMContentLoaded', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  currentTabUrl = tab?.url || '';
  
  await loadActiveScripts();
  checkApiStatus();
  
  document.getElementById('openSidepanel').addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'OPEN_SIDEPANEL' });
    window.close();
  });
  
  document.getElementById('quickChat').addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'OPEN_SIDEPANEL' });
    window.close();
  });
});

async function loadActiveScripts() {
  const container = document.getElementById('activeScripts');
  const data = await chrome.storage.local.get(['scripts']);
  const scripts = data.scripts || [];
  
  const active = scripts.filter(s => {
    if (!s.enabled) return false;
    return s.matches.some(m => matchPattern(currentTabUrl, m));
  });
  
  if (active.length === 0) {
    container.innerHTML = '<div class="empty">No scripts active on this page</div>';
    return;
  }
  
  container.innerHTML = active.map(s => `
    <div class="script-row">
      <div class="name" title="${s.name}">${s.name}</div>
      <div class="toggle ${s.enabled ? 'on' : ''}" data-id="${s.id}"></div>
    </div>
  `).join('');
  
  container.querySelectorAll('.toggle').forEach(t => {
    t.addEventListener('click', async () => {
      const id = t.dataset.id;
      const data = await chrome.storage.local.get(['scripts']);
      const scripts = data.scripts || [];
      const s = scripts.find(x => x.id === id);
      if (s) {
        s.enabled = !s.enabled;
        s.updatedAt = Date.now();
        await chrome.storage.local.set({ scripts });
        chrome.runtime.sendMessage({ type: 'SAVE_SCRIPTS', scripts });
        t.classList.toggle('on');
      }
    });
  });
}

async function checkApiStatus() {
  const data = await chrome.storage.local.get(['settings']);
  const settings = data.settings || {};
  const status = document.getElementById('status');
  
  if (!settings.apiKey) {
    status.textContent = '● No Key';
    status.className = 'status bad';
    return;
  }
  
  status.textContent = '● Ready';
  status.className = 'status ok';
}

function matchPattern(url, pattern) {
  try {
    const pParts = pattern.split('/');
    const schemePat = pParts[0];
    const hostPat = pParts[2];
    const pathPat = pParts.slice(3).join('/');
    const u = new URL(url);
    if (schemePat !== '*') {
      const schemes = schemePat.split('|');
      if (!schemes.includes(u.protocol.slice(0, -1))) return false;
    }
    if (hostPat !== '*') {
      const hostRe = '^' + hostPat
        .replace(/\*\./g, '([^/.]+\\.)*')
        .replace(/\.\*/g, '(\\.[^/]+)*')
        .replace(/\*/g, '[^/.]*') + '$';
      if (!new RegExp(hostRe).test(u.hostname)) return false;
    }
    const pathRe = '^' + pathPat
      .replace(/\*\*/g, '<<<DOUBLE>>>')
      .replace(/\*/g, '[^/]*')
      .replace(/<<<DOUBLE>>>/g, '.*') + '$';
    return new RegExp(pathRe).test(u.pathname);
  } catch (e) {
    return false;
  }
}