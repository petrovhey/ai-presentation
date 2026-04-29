// Background Service Worker — script injection, API proxy, GM_* emulation
const SCRIPT_CACHE = new Map();

// ===== INIT =====
chrome.runtime.onInstalled.addListener(() => {
  console.log('[RoboMonkey] Extension installed');
  loadAllScripts();
});

chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'local' && changes.scripts) loadAllScripts();
});

// ===== SCRIPT CACHE =====
async function loadAllScripts() {
  const data = await chrome.storage.local.get(['scripts']);
  const scripts = data.scripts || [];
  SCRIPT_CACHE.clear();
  scripts.filter(s => s.enabled).forEach(script => {
    (script.matches || []).forEach(pattern => {
      if (!SCRIPT_CACHE.has(pattern)) SCRIPT_CACHE.set(pattern, []);
      SCRIPT_CACHE.get(pattern).push(script);
    });
  });
  console.log('[RoboMonkey] Loaded', scripts.length, 'scripts');
}

// ===== INJECTION =====
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'complete' || !tab?.url || tab.url.startsWith('chrome://')) return;
  
  const scriptsToInject = [];
  for (const [pattern, scripts] of SCRIPT_CACHE) {
    if (matchPattern(tab.url, pattern)) scriptsToInject.push(...scripts);
  }
  if (scriptsToInject.length === 0) return;
  
  const unique = [...new Map(scriptsToInject.map(s => [s.id, s])).values()];
  
  for (const script of unique) {
    try {
      await chrome.scripting.executeScript({
        target: { tabId },
        func: injectUserScript,
        args: [script.id, script.code, script.grants || ['none']],
        world: 'MAIN'
      });
      console.log('[RoboMonkey] Injected', script.name, 'into', tab.url);
    } catch (e) {
      console.error('[RoboMonkey] Injection failed:', e);
    }
  }
});

// ===== INJECTED FUNCTION (runs in page context) =====
function injectUserScript(scriptId, code, grants) {
  const storageKey = `gm_${scriptId}_`;

  function GM_setValue(key, value) {
    return Promise.resolve().then(() => {
      localStorage.setItem(storageKey + key, JSON.stringify(value));
    });
  }

  function GM_getValue(key, defaultValue) {
    return Promise.resolve().then(() => {
      const v = localStorage.getItem(storageKey + key);
      return v ? JSON.parse(v) : defaultValue;
    });
  }

  function GM_deleteValue(key) {
    return Promise.resolve().then(() => {
      localStorage.removeItem(storageKey + key);
    });
  }

  function GM_listValues() {
    return Promise.resolve().then(() => {
      const keys = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.startsWith(storageKey)) keys.push(k.slice(storageKey.length));
      }
      return keys;
    });
  }

  function GM_addStyle(css) {
    const style = document.createElement('style');
    style.textContent = css;
    style.setAttribute('data-robo', scriptId);
    (document.head || document.documentElement).appendChild(style);
  }

  function GM_xmlHttpRequest(details) {
    return fetch(details.url, {
      method: details.method || 'GET',
      headers: details.headers || {},
      body: details.data || undefined,
      credentials: details.withCredentials ? 'include' : 'same-origin'
    })
    .then(r => r.text().then(text => ({
      responseText: text,
      status: r.status,
      statusText: r.statusText,
      finalUrl: r.url,
      responseHeaders: [...r.headers.entries()].map(([k, v]) => `${k}: ${v}`).join('\n')
    })));
  }

  function GM_log(...args) { console.log(`[GM:${scriptId}]`, ...args); }

  const GM_info = {
    script: { name: scriptId, version: '1.0' },
    scriptMetaStr: '',
    version: '1.0',
    scriptWillUpdate: false
  };

  // Build wrapper — functions must be in scope for eval/code to access them
  const wrapper = `
    (function() {
      'use strict';
      const GM_setValue = ${GM_setValue.toString()};
      const GM_getValue = ${GM_getValue.toString()};
      const GM_deleteValue = ${GM_deleteValue.toString()};
      const GM_listValues = ${GM_listValues.toString()};
      const GM_addStyle = ${GM_addStyle.toString()};
      const GM_xmlHttpRequest = ${GM_xmlHttpRequest.toString()};
      const GM_log = ${GM_log.toString()};
      const GM_info = ${JSON.stringify(GM_info)};
      ${code}
    })();
  `;

  const el = document.createElement('script');
  el.textContent = wrapper;
  el.setAttribute('data-robo-monkey', scriptId);
  (document.body || document.documentElement).appendChild(el);
  // Remove after execution to keep DOM clean
  setTimeout(() => el.remove(), 0);
}

// ===== PATTERN MATCHING (Tampermonkey-style @match) =====
function matchPattern(url, pattern) {
  // @match format: scheme://host/path
  // * = any characters in this segment (not crossing / for host)
  // For MVP: convert pattern to regex
  try {
    // Parse pattern parts
    const pParts = pattern.split('/');
    const schemePat = pParts[0];
    const hostPat = pParts[2];
    const pathPat = pParts.slice(3).join('/');
    
    // Parse URL
    const u = new URL(url);
    
    // Check scheme
    if (schemePat !== '*') {
      const schemes = schemePat.split('|');
      if (!schemes.includes(u.protocol.slice(0, -1))) return false;
    }
    
    // Check host
    if (hostPat !== '*') {
      const hostRe = '^' + hostPat
        .replace(/\*\./g, '([^/.]+\\.)*')    // *.example.com
        .replace(/\.\*/g, '(\\.[^/]+)*')     // example.*
        .replace(/\*/g, '[^/.]*') + '$';     // * in middle
      if (!new RegExp(hostRe).test(u.hostname)) return false;
    }
    
    // Check path
    const pathRe = '^' + pathPat
      .replace(/\*\*/g, '<<<DOUBLE>>>')       // ** = anything
      .replace(/\*/g, '[^/]*')                // * = any path segment chars
      .replace(/<<<DOUBLE>>>/g, '.*') + '$'; // restore **
    if (!new RegExp(pathRe).test(u.pathname)) return false;
    
    return true;
  } catch (e) {
    // Fallback for invalid URLs or patterns
    const regex = pattern
      .replace(/\*\*/g, '<<<DS>>>')
      .replace(/[.+^${}()|[\]\\]/g, '\\$&')
      .replace(/<<<DS>>>/g, '.*')
      .replace(/\\\*/g, '[^/]*');
    return new RegExp('^' + regex + '$').test(url);
  }
}

// ===== MESSAGE HANDLER (single listener) =====
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  const { type } = request;
  
  if (type === 'OPEN_SIDEPANEL') {
    chrome.sidePanel.open({ windowId: sender.tab?.windowId });
    return false;
  }
  
  if (type === 'GET_SCRIPTS') {
    chrome.storage.local.get(['scripts']).then(d => sendResponse(d.scripts || []));
    return true;
  }
  
  if (type === 'SAVE_SCRIPTS') {
    chrome.storage.local.set({ scripts: request.scripts }).then(() => {
      loadAllScripts();
      sendResponse({ ok: true });
    });
    return true;
  }
  
  if (type === 'GET_VERSIONS') {
    chrome.storage.local.get(['versions']).then(d => sendResponse(d.versions || {}));
    return true;
  }
  
  if (type === 'SAVE_VERSIONS') {
    chrome.storage.local.set({ versions: request.versions }).then(() => sendResponse({ ok: true }));
    return true;
  }
  
  if (type === 'FETCH_OPENROUTER') {
    fetchOpenRouter(request.payload, request.apiKey)
      .then(sendResponse)
      .catch(e => sendResponse({ error: e.message }));
    return true;
  }
  
  if (type === 'FETCH_GREASYFORK') {
    fetch(request.url).then(r => r.text()).then(sendResponse)
      .catch(e => sendResponse({ error: e.message }));
    return true;
  }
  
  if (type === 'FETCH_MODELS') {
    fetchModels(request.apiKey)
      .then(sendResponse)
      .catch(e => sendResponse({ error: e.message }));
    return true;
  }
  
  return false;
});

// ===== API HELPERS =====
async function fetchOpenRouter(payload, apiKey) {
  const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
      'HTTP-Referer': 'https://robomonkey.local',
      'X-Title': 'RoboMonkey'
    },
    body: JSON.stringify(payload)
  });
  
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: { message: res.statusText } }));
    throw new Error(err.error?.message || `HTTP ${res.status}`);
  }
  return await res.json();
}

async function fetchModels(apiKey) {
  const res = await fetch('https://openrouter.ai/api/v1/models', {
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'HTTP-Referer': 'https://robomonkey.local',
      'X-Title': 'RoboMonkey'
    }
  });
  if (!res.ok) throw new Error('Failed to fetch models');
  return await res.json();
}
