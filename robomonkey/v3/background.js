// Background Service Worker — userscript injection with dual mode:
// Primary: chrome.userScripts API (if available, creates toggle in Chrome settings)
// Fallback: chrome.scripting.executeScript (works everywhere)

const SCRIPT_CACHE = new Map();
let userScriptsAvailable = false;

// ===== INIT =====
chrome.runtime.onInstalled.addListener(() => {
  console.log('[AI Monkey] Extension installed');
  checkUserScriptsApi();
  loadAllScripts();
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
});

chrome.runtime.onStartup.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
});

function checkUserScriptsApi() {
  try {
    if (chrome.userScripts && chrome.userScripts.register) {
      userScriptsAvailable = true;
      console.log('[AI Monkey] chrome.userScripts API available');
    }
  } catch (e) {
    console.log('[AI Monkey] chrome.userScripts API not available, using fallback');
    userScriptsAvailable = false;
  }
}

chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'local' && changes.scripts) {
    loadAllScripts();
    if (userScriptsAvailable) syncUserScripts();
  }
});

// ===== SCRIPT CACHE (for fallback mode) =====
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
  console.log('[AI Monkey] Loaded', scripts.length, 'scripts into cache');
}

// ===== FALLBACK: Inject via chrome.scripting on page load =====
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'complete' || !tab?.url || tab.url.startsWith('chrome://')) return;
  if (userScriptsAvailable) {
    console.log('[AI Monkey] userScripts API active, skipping scripting fallback for', tab.url);
    return;
  }
  console.log('[AI Monkey] Tab loaded, checking scripts for', tab.url);
  await injectViaScripting(tabId, tab.url);
});

async function injectViaScripting(tabId, url) {
  // Guard
  if (!chrome.scripting || !chrome.scripting.executeScript) {
    console.error('[AI Monkey] chrome.scripting API not available. Remove and reload extension.');
    return;
  }

  const scriptsToInject = [];
  for (const [pattern, scripts] of SCRIPT_CACHE) {
    if (matchPattern(url, pattern)) scriptsToInject.push(...scripts);
  }
  if (scriptsToInject.length === 0) {
    console.log('[AI Monkey] No scripts match', url);
    return;
  }

  const unique = [...new Map(scriptsToInject.map(s => [s.id, s])).values()];
  console.log('[AI Monkey] Injecting', unique.length, 'scripts via scripting.executeScript for', url);

  for (const script of unique) {
    try {
      await chrome.scripting.executeScript({
        target: { tabId },
        func: runUserScriptInMainWorld,
        args: [script.id, script.code, script.grants || ['none']],
        world: 'MAIN'
      });
      console.log('[AI Monkey] Injected via scripting', script.name, 'on', url);
    } catch (e) {
      console.error('[AI Monkey] Scripting injection failed for', script.name, ':', e.message);
    }
  }
}

// ===== PRIMARY: chrome.userScripts API =====
async function syncUserScripts() {
  if (!userScriptsAvailable) {
    console.log('[AI Monkey] syncUserScripts: API not available');
    return;
  }
  try {
    const data = await chrome.storage.local.get(['scripts']);
    const scripts = data.scripts || [];
    const enabled = scripts.filter(s => s.enabled);
    console.log('[AI Monkey] Syncing', enabled.length, 'scripts via userScripts API');

    let existing = [];
    try {
      existing = await chrome.userScripts.getScripts();
      console.log('[AI Monkey] Existing userScripts:', existing.length);
    } catch (e) {
      console.log('[AI Monkey] getScripts failed (maybe empty):', e.message);
    }

    if (existing && existing.length > 0) {
      await chrome.userScripts.unregister({ ids: existing.map(s => s.id) });
      console.log('[AI Monkey] Unregistered', existing.length, 'existing scripts');
    }

    for (const script of enabled) {
      const wrappedCode = buildScriptString(script.id, script.code, script.grants || ['none']);
      const userScript = {
        id: script.id,
        matches: script.matches && script.matches.length > 0 ? script.matches : ['*://*/*'],
        js: [{ code: wrappedCode }],
        runAt: 'document_idle',
        world: 'MAIN'
      };
      console.log('[AI Monkey] Registering script:', script.name, 'matches:', userScript.matches);
      try {
        await chrome.userScripts.register([userScript]);
        console.log('[AI Monkey] Registered successfully:', script.name);
      } catch (regErr) {
        console.error('[AI Monkey] Register failed for', script.name, ':', regErr.message);
        // Try with generic match if specific match failed
        if (userScript.matches[0] !== '*://*/*') {
          console.log('[AI Monkey] Retrying with generic match for', script.name);
          userScript.matches = ['*://*/*'];
          try {
            await chrome.userScripts.register([userScript]);
            console.log('[AI Monkey] Registered with generic match');
          } catch (e2) {
            console.error('[AI Monkey] Generic match also failed:', e2.message);
          }
        }
      }
    }
    console.log('[AI Monkey] Synced', enabled.length, 'userScripts');
  } catch (e) {
    console.error('[AI Monkey] userScripts sync failed:', e);
    userScriptsAvailable = false;
  }
}

// ===== BUILD SCRIPT STRING (returns actual JS string) =====
// Code is inserted DIRECTLY — no new Function, no eval. CSP-safe for userScripts API.
function buildScriptString(scriptId, code, grants) {
  var gmSetup =
    "  const storageKey = 'gm_" + scriptId + "_';\n" +
    "  const GM_setValue = function(key, value) { localStorage.setItem(storageKey + key, JSON.stringify(value)); };\n" +
    "  const GM_getValue = function(key, defaultValue) { var v = localStorage.getItem(storageKey + key); return v ? JSON.parse(v) : defaultValue; };\n" +
    "  const GM_deleteValue = function(key) { localStorage.removeItem(storageKey + key); };\n" +
    "  const GM_listValues = function() { var keys = []; for (var i = 0; i < localStorage.length; i++) { var k = localStorage.key(i); if (k && k.startsWith(storageKey)) keys.push(k.slice(storageKey.length)); } return keys; };\n" +
    "  const GM_addStyle = function(css) { var style = document.createElement('style'); style.textContent = css; (document.head || document.documentElement).appendChild(style); };\n" +
    "  const GM_xmlHttpRequest = function(details) { return fetch(details.url, { method: details.method || 'GET', headers: details.headers || {}, body: details.data || undefined, credentials: details.withCredentials ? 'include' : 'same-origin' }).then(function(r) { return r.text().then(function(text) { return { responseText: text, status: r.status, statusText: r.statusText, finalUrl: r.url, responseHeaders: Array.from(r.headers.entries()).map(function(e) { return e[0] + ': ' + e[1]; }).join('\\n') }; }); }); };\n" +
    "  const GM_log = function() { var args = Array.prototype.slice.call(arguments); args.unshift('[AM:" + scriptId + "]'); console.log.apply(console, args); };\n" +
    "  const GM_info = { script: { name: '" + scriptId + "', version: '1.0' }, scriptMetaStr: '', version: '1.0', scriptWillUpdate: false };\n";

  return "(function() {\n" +
    "  'use strict';\n" +
    gmSetup +
    "  try {\n" +
    code.split('\n').map(function(l) { return '    ' + l; }).join('\n') + "\n" +
    "  } catch (err) {\n" +
    "    console.error('[AI Monkey:" + scriptId + "]', err);\n" +
    "  }\n" +
    "})();";
}

// ===== INJECTED FUNCTION (fallback mode, runs in page context) =====
// Uses <script> tag injection instead of new Function to bypass CSP eval restrictions.
function runUserScriptInMainWorld(scriptId, code, grants) {
  // Setup GM_* API in window scope so user code can access them
  window.GM_setValue = function(key, value) {
    localStorage.setItem('gm_' + scriptId + '_' + key, JSON.stringify(value));
  };
  window.GM_getValue = function(key, defaultValue) {
    var v = localStorage.getItem('gm_' + scriptId + '_' + key);
    return v ? JSON.parse(v) : defaultValue;
  };
  window.GM_deleteValue = function(key) {
    localStorage.removeItem('gm_' + scriptId + '_' + key);
  };
  window.GM_listValues = function() {
    var keys = [];
    for (var i = 0; i < localStorage.length; i++) {
      var k = localStorage.key(i);
      if (k && k.startsWith('gm_' + scriptId + '_')) keys.push(k.slice(('gm_' + scriptId + '_').length));
    }
    return keys;
  };
  window.GM_addStyle = function(css) {
    var style = document.createElement('style');
    style.textContent = css;
    (document.head || document.documentElement).appendChild(style);
  };
  window.GM_xmlHttpRequest = function(details) {
    return fetch(details.url, {
      method: details.method || 'GET',
      headers: details.headers || {},
      body: details.data || undefined,
      credentials: details.withCredentials ? 'include' : 'same-origin'
    }).then(function(r) {
      return r.text().then(function(text) {
        return {
          responseText: text,
          status: r.status,
          statusText: r.statusText,
          finalUrl: r.url,
          responseHeaders: Array.from(r.headers.entries()).map(function(e) { return e[0] + ': ' + e[1]; }).join('\n')
        };
      });
    });
  };
  window.GM_log = function() {
    var args = Array.prototype.slice.call(arguments);
    args.unshift('[AM:' + scriptId + ']');
    console.log.apply(console, args);
  };
  window.GM_info = {
    script: { name: scriptId, version: '1.0' },
    scriptMetaStr: '',
    version: '1.0',
    scriptWillUpdate: false
  };

  // Inject user code via <script> tag — bypasses eval CSP
  try {
    var script = document.createElement('script');
    script.setAttribute('data-ai-monkey', scriptId);
    script.textContent =
      "(function() {\n" +
      "  'use strict';\n" +
      "  try {\n" +
      code.split('\n').map(function(l) { return '    ' + l; }).join('\n') + "\n" +
      "  } catch (err) {\n" +
      "    console.error('[AI Monkey:" + scriptId + "]', err);\n" +
      "  }\n" +
      "})();";
    (document.body || document.documentElement).appendChild(script);
    script.remove();
    console.log('[AI Monkey] Injected via script tag', scriptId);
  } catch (err) {
    console.error('[AI Monkey] Script tag injection failed:', err);
    // Last resort: try new Function
    try {
      var fn = new Function(code);
      fn();
    } catch (e2) {
      console.error('[AI Monkey] new Function also failed:', e2);
    }
  }
}

// ===== PATTERN MATCHING =====
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
    if (!new RegExp(pathRe).test(u.pathname)) return false;

    return true;
  } catch (e) {
    return false;
  }
}

// ===== MESSAGE HANDLER =====
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  const { type } = request;

  if (type === 'GET_SCRIPTS') {
    chrome.storage.local.get(['scripts']).then(d => sendResponse(d.scripts || []));
    return true;
  }

  if (type === 'SAVE_SCRIPTS') {
    (async () => {
      await chrome.storage.local.set({ scripts: request.scripts });
      loadAllScripts();
      if (userScriptsAvailable) {
        try {
          await syncUserScripts();
          console.log('[AI Monkey] syncUserScripts completed after SAVE');
        } catch (e) {
          console.error('[AI Monkey] syncUserScripts failed:', e);
        }
      }
      sendResponse({ ok: true });
    })();
    return true;
  }

  if (type === 'INJECT_NOW') {
    console.log('[AI Monkey] INJECT_NOW request:', request.script?.id, 'tab:', request.tabId);

    // Guard: scripting API must be available
    if (!chrome.scripting || !chrome.scripting.executeScript) {
      console.error('[AI Monkey] chrome.scripting API not available. Remove extension and reload unpacked to refresh permissions.');
      sendResponse({ error: 'chrome.scripting API not available. Remove extension and reload unpacked.' });
      return true;
    }

    if (!request.script || !request.tabId) {
      console.error('[AI Monkey] INJECT_NOW: missing script or tabId');
      sendResponse({ error: 'No script or tabId' });
      return true;
    }

    // Guard: verify tab URL before injecting
    (async () => {
      try {
        const tab = await chrome.tabs.get(request.tabId);
        if (!tab || !tab.url || tab.url.startsWith('about:') || tab.url.startsWith('chrome://') || tab.url.startsWith('edge://') || tab.url.startsWith('devtools://')) {
          console.error('[AI Monkey] Cannot inject into', tab?.url);
          sendResponse({ error: 'Cannot inject into ' + (tab?.url || 'unknown tab') });
          return;
        }

        await chrome.scripting.executeScript({
          target: { tabId: request.tabId },
          func: runUserScriptInMainWorld,
          args: [request.script.id, request.script.code, request.script.grants || ['none']],
          world: 'MAIN'
        });
        console.log('[AI Monkey] INJECT_NOW success:', request.script.id, 'on', tab.url);
        sendResponse({ ok: true });
      } catch (e) {
        console.error('[AI Monkey] INJECT_NOW failed:', e.message);
        sendResponse({ error: e.message });
      }
    })();
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
      'HTTP-Referer': 'https://ai-monkey.local',
      'X-Title': 'AI Monkey'
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
      'HTTP-Referer': 'https://ai-monkey.local',
      'X-Title': 'AI Monkey'
    }
  });
  if (!res.ok) throw new Error('Failed to fetch models');
  return await res.json();
}
