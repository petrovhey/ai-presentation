# RoboMonkey — AI Userscript Builder & Manager

Chrome Extension (Manifest V3) для создания, редактирования и управления userscripts (Tampermonkey/Greasemonkey) с помощью AI через OpenRouter API.

## Возможности

- 🤖 **AI Chat** — опиши задачу текстом, AI сгенерирует рабочий userscript
- 📜 **Менеджер скриптов** — вкл/выкл, редактирование, удаление, экспорт .user.js
- 📝 **Версионирование** — каждое сохранение = новая версия, можно откатиться
- 🌐 **GreasyFork** — поиск и импорт скриптов прямо из расширения
- ⚙️ **OpenRouter** — выбор любой модели, включая бесплатные
- ✏️ **Редактор кода** — с нумерацией строк, форматированием, метаданными
- 🐵 **Инжекция** — автоматическая вставка скриптов на страницы по @match

## Установка

1. Скачай архив и распакуй в папку
2. Открой Chrome → `chrome://extensions/`
3. Включи **Developer mode** (верхний правый угол)
4. Нажми **Load unpacked** → выбери папку `robomonkey`
5. Готово! Нажми на иконку 🐵 в тулбаре

## Первая настройка

1. Открой Side Panel (кникни иконку → "Open Dashboard")
2. Перейди во вкладку **Settings**
3. Вставь **OpenRouter API Key** (получить: https://openrouter.ai/keys)
4. Выбери модель (или нажми "Load All Models" для загрузки списка)
5. Сохрани

## Использование

### Создать скрипт через AI
1. Вкладка **Chat** → опиши что нужно («Скрыть рекламу на YouTube»)
2. AI ответит с кодом → нажми **Install Script**
3. Скрипт появится во вкладке **My Scripts**

### Редактировать скрипт
1. Найди скрипт в списке → нажми **Edit**
2. Откроется редактор с кодом и метаданными
3. Меняй код, @match, @grant
4. **Save** или **Save as Version**

### Версии
- Каждое сохранение через "Save as Version" создаёт новую версию
- В списке скриптов нажми **Versions** → выбери старую → **Restore**

### GreasyFork
- Вкладка **GreasyFork** → поиск по названию
- Найди скрипт → **Import**
- Скрипт добавится в твою библиотеку (по умолчанию выключен)

## Технологии

- Manifest V3
- Chrome Storage API
- OpenRouter API (совместим с OpenAI, Anthropic, Google и др.)
- Emulation GM_* API (GM_setValue, GM_getValue, GM_addStyle, GM_xmlhttpRequest)

## Файлы

| Файл | Назначение |
|------|------------|
| `manifest.json` | Конфигурация расширения |
| `background.js` | Service Worker — инжекция скриптов, прокси API |
| `sidepanel.html/js` | Основной UI (чат, менеджер, настройки) |
| `popup.html/js` | Мини-дашборд по иконке |
| `editor.html/js` | Полноэкранный редактор |
| `icons/` | Иконки расширения |

## Ограничения MVP

- Редактор — textarea с базовой подсветкой (не Monaco/CodeMirror)
- GreasyFork — HTML-парсинг (не официальный API)
- GM_* — базовая эмуляция через localStorage/fetch
- Нет Telegram-бота (только email-уведомления через Chrome)

## Лицензия

MIT — делай что хочешь, это твой проект.
