# AI Monkey v4 — Исправлено CSP + match pattern

AI Userscript Builder & Manager для Chrome (Manifest V3). Как Tampermonkey, но с ИИ внутри.

## Как это работает

1. Заходишь на любую страницу (например, Wildberries)
2. Открываешь AI Monkey Dashboard (клик на 🐵 в тулбаре)
3. Пишешь в чате что хочешь: "Добавь кнопку темной темы"
4. AI генерирует скрипт **конкретно для этого сайта** (URL передаётся автоматически)
5. Скрипт **сразу активируется** на текущей вкладке
6. В чате только: "✅ Готово! Обнови страницу"
7. **F5** — скрипт работает

## ⚠️ Важно: Разрешение пользовательских скриптов

После установки расширения:
1. Открой `chrome://extensions/`
2. Найди **AI Monkey**
3. Включи переключатель **"Разрешить пользовательские скрипты"**
4. Без этого скрипты не будут инжектироваться

## Установка

1. Распакуй папку `v3`
2. Chrome → `chrome://extensions/` → включи **Developer mode**
3. **Load unpacked** → выбери папку `v3`
4. Найди AI Monkey в списке → включи **"Разрешить пользовательские скрипты"**
5. Кликни на иконку 🐵 → откроется **Sidepanel Dashboard**
6. **⚙️ Settings** → введи OpenRouter API Key → Save
7. Выбери модель или введи свою → Test → Save

## Создание скрипта

1. Зайди на сайт (wildberries.ru)
2. Открой Dashboard → вкладка **🤖 Chat**
3. Нажми **🛠️ Create New Script** или пиши в чат
4. Опиши что хочешь
5. AI создаёт → **сразу активирует** → "✅ Готово"
6. **F5** — работает

## Что пофикшено (все баги Саши)

| # | Баг | Причина | Фикс |
|---|-----|---------|------|
| **1** | Скрипт создаётся, но ничего не появляется | `wrapUserScript()` возвращал `undefined` | `buildScriptString()` — возвращает JS-строку |
| **2** | Ошибка `Sync failed` | `chrome.userScripts` API отсутствует в стабильном Chrome | **Dual mode**: fallback на `chrome.scripting.executeScript` |
| **3** | "Новый скрипт" меняет предыдущий | Inline `onclick` блокируется CSP Chrome | `data-action` + event delegation |
| **4** | Чат не обновляется при смене сайта | `chatHistory` общий для всех сайтов | **Chat keyed by domain** — каждый сайт свой чат |
| **5** | Кнопки в скриптах не работают | CSP Chrome Extension блокирует inline `onclick` | Все inline onclick убраны |
| **6** | Load all models не работал | Inline `onclick="loadModels()"` | `data-action="loadModels"` |
| **7** | Скрипт не инжектируется на WB | `new Function(code)` блокируется CSP страницы | Код вставляется **напрямую**, без eval/new Function |
| **8** | `@match` с пробелом ломается | AI генерировал `@match https://site/ *` | **Sanitize**: пробелы удаляются автоматически + промпт исправлен |

### Как проверить что работает

1. **Открой консоль сервис-воркера**: `chrome://extensions/` → AI Monkey → **service worker** → Inspect → Console
2. Создай скрипт → смотри логи:
   - `[AI Monkey] INJECT_NOW request:` — запрос на инъекцию
   - `[AI Monkey] INJECT_NOW success:` — инъекция успешна
   - `[AI Monkey] Injected via script tag` — fallback сработал
   - `[AI Monkey] Script tag injection failed` — CSP блокирует даже script tag
3. **Если `userScripts` API работает** — скрипты регистрируются без eval, всё должно работать
4. **Если toggle выключен** — fallback `executeScript` использует `<script>` тег, но может быть заблокирован CSP WB

## Технология

- **Primary:** `chrome.userScripts` API (Manifest V3) — официальный API Chrome для userscripts
- **Fallback:** `chrome.scripting.executeScript` с `world: 'MAIN'` — работает на любом Chrome
- **Инъекция:** Код вставляется напрямую как текст, без `new Function` или `eval` — обходит CSP
- **Кнопки:** Event delegation через `data-action` — обходит CSP restrictions
- **Чат:** Привязан к домену (hostname), не общий

## Структура

```
v3/
├── manifest.json       ← Manifest V3 + userScripts permission
├── background.js       ← Dual mode: userScripts API + scripting fallback, CSP-safe injection
├── sidepanel.html/js   ← Event delegation, URL-keyed chat, match sanitize
├── popup.html/js       ← Мини-дашборд
├── editor.html/js      ← Редактор с event delegation
├── icons/
└── README.md
```

## Требования

- Chrome 120+ (Manifest V3)
- OpenRouter API Key

## Не забудь

- После загрузки новой версии: **Remove** старую → **Load unpacked** снова
- Chrome кеширует старый service worker, только Remove помогает
- Включи **"Разрешить пользовательские скрипты"** в настройках расширения
- Если скрипт не появляется — открой консоль service worker и смотри логи
