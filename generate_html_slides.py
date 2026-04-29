#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генерация 25 HTML-слайдов для рендеринга в PNG через headless Chrome.
Каждый слайд — отдельная HTML-страница 1920x1080.
"""
import os

os.makedirs("slides_html", exist_ok=True)

CSS = """

* { margin: 0; padding: 0; box-sizing: border-box; }
body { width: 1920px; height: 1080px; overflow: hidden; font-family: 'DejaVu Sans', 'Arial', 'Liberation Sans', sans-serif; background: #FAFBFD; color: #0F172A; -webkit-font-smoothing: antialiased; }
.slide { width: 1920px; height: 1080px; position: relative; padding: 0; overflow: hidden; }
.header-bar { position: absolute; top: 0; left: 0; right: 0; height: 100px; padding: 24px 70px; display: flex; align-items: center; justify-content: space-between; z-index: 10; }
.header-bar .title { font-family: 'DejaVu Sans', 'Arial Black', 'Liberation Sans', sans-serif; font-size: 38px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em; }
.header-bar .subtitle { font-size: 16px; color: rgba(255,255,255,0.85); margin-top: 2px; }
.header-bar .slide-num { font-size: 15px; font-weight: 600; color: rgba(255,255,255,0.7); }
.content { margin-top: 100px; padding: 30px 70px 40px; height: calc(1080px - 100px); overflow: hidden; }
.no-header .content { margin-top: 0; padding-top: 60px; }
h1 { font-family: 'DejaVu Sans', 'Arial Black', 'Liberation Sans', sans-serif; font-size: 56px; font-weight: 800; letter-spacing: -0.03em; line-height: 1.1; color: #0F172A; }
h2 { font-family: 'DejaVu Sans', 'Arial Black', 'Liberation Sans', sans-serif; font-size: 40px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.2; color: #0F172A; }
h3 { font-size: 22px; font-weight: 700; color: #0F172A; line-height: 1.3; }
.lead { font-size: 20px; color: #334155; line-height: 1.5; margin-top: 14px; }
.text { font-size: 17px; color: #334155; line-height: 1.6; }
.text-sm { font-size: 15px; color: #64748B; line-height: 1.5; }
.card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 22px 26px; box-shadow: 0 4px 20px rgba(15,23,42,0.05), 0 1px 3px rgba(15,23,42,0.03); position: relative; overflow: hidden; }
.card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--accent, #2563EB); }
.card-title { font-size: 18px; font-weight: 700; color: var(--accent, #2563EB); margin-bottom: 8px; }
.card-body { font-size: 15px; color: #334155; line-height: 1.55; }
.badge { display: inline-flex; align-items: center; gap: 8px; padding: 8px 18px; border-radius: 100px; font-size: 14px; font-weight: 600; color: #FFFFFF; background: var(--badge-bg, #22C55E); }
table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 14px; }
th { background: #0F172A; color: #FFFFFF; padding: 12px 14px; text-align: left; font-weight: 600; }
td { padding: 10px 14px; border-bottom: 1px solid #E2E8F0; color: #334155; }
tr:nth-child(even) td { background: #F1F5F9; }
.num-circle { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 800; color: #FFFFFF; background: var(--accent, #2563EB); flex-shrink: 0; }
.deco-circle { position: absolute; border-radius: 50%; filter: blur(70px); opacity: 0.12; pointer-events: none; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
.grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 16px; }
.grid-7 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.flex { display: flex; }
.flex-col { display: flex; flex-direction: column; }
.gap-12 { gap: 12px; }
.gap-16 { gap: 16px; }
.gap-20 { gap: 20px; }
.gap-24 { gap: 24px; }
.mt-8 { margin-top: 8px; }
.mt-12 { margin-top: 12px; }
.mt-16 { margin-top: 16px; }
.mt-20 { margin-top: 20px; }
.mt-24 { margin-top: 24px; }
.mt-32 { margin-top: 32px; }
.hero-title { font-family: 'DejaVu Sans', 'Arial Black', 'Liberation Sans', sans-serif; font-size: 80px; font-weight: 900; letter-spacing: -0.04em; line-height: 1.05; color: #0F172A; }
.hero-subtitle { font-size: 28px; color: #334155; margin-top: 16px; font-weight: 400; }
.hero-accent { width: 100px; height: 6px; border-radius: 3px; background: #2563EB; margin-top: 24px; }
.hero-meta { font-size: 16px; color: #64748B; margin-top: 20px; }
.dept-col { display: flex; flex-direction: column; gap: 10px; }
.dept-col-title { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent, #2563EB); margin-bottom: 2px; }
.dept-item { display: flex; gap: 8px; align-items: flex-start; }
.dept-bar { width: 4px; min-height: 20px; border-radius: 2px; background: var(--accent, #2563EB); flex-shrink: 0; margin-top: 3px; }
.dept-text { font-size: 14px; color: #0F172A; line-height: 1.45; }
.prompt-box { background: #F1F5F9; border-radius: 10px; padding: 12px 16px; font-size: 13px; color: #334155; line-height: 1.45; border-left: 3px solid var(--accent, #2563EB); }
.prompt-num { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; color: #FFFFFF; background: var(--accent, #2563EB); flex-shrink: 0; }
.icon-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--dot-color, #22C55E); flex-shrink: 0; margin-top: 6px; }
.rec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
.rec-item { display: flex; gap: 14px; }
.rec-num { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; color: #FFFFFF; background: var(--accent, #2563EB); flex-shrink: 0; }
.rec-title { font-size: 16px; font-weight: 700; color: #0F172A; line-height: 1.3; }
.rec-body { font-size: 14px; color: #64748B; line-height: 1.5; margin-top: 4px; }
"""

ACCENTS = {
    'blue': '#2563EB', 'violet': '#7C3AED', 'pink': '#EC4899',
    'green': '#22C55E', 'orange': '#F59E0B', 'red': '#EF4444',
    'cyan': '#06B6D4', 'amber': '#FBBF24', 'dark': '#0F172A',
}

def wrap(content, title="", subtitle="", color="", num="", has_header=True):
    header = f'<div class="header-bar" style="background:{color};"><div><div class="title">{title}</div>{f"<div class=\'subtitle\'>{subtitle}</div>" if subtitle else ""}</div>{f"<div class=\'slide-num\'>{num}</div>" if num else ""}</div></div>' if has_header else ""
    cls = "slide" + (" no-header" if not has_header else "")
    return f'<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{CSS}</style></head><body><div class="{cls}">{header}<div class="content">{content}</div></div></body></html>'

def write(n, html):
    with open(f"slides_html/slide_{n:02d}.html", "w", encoding="utf-8") as f:
        f.write(html)

# ═══════════════════════════════════════════════════════════════
# 1 — Титул
# ═══════════════════════════════════════════════════════════════
write(1, wrap("""
<div style="display:flex;flex-direction:column;justify-content:center;height:100%;padding-left:30px;">
    <div class="hero-title">Нейросети и ИИ</div>
    <div class="hero-subtitle">как использовать в работе</div>
    <div class="hero-accent"></div>
    <div class="hero-meta">Доклад для сотрудников компании • 2026</div>
</div>
<div class="deco-circle" style="width:500px;height:500px;background:#2563EB;top:-120px;right:-80px;"></div>
<div class="deco-circle" style="width:400px;height:400px;background:#7C3AED;bottom:-80px;left:-80px;"></div>
<div class="deco-circle" style="width:300px;height:300px;background:#EC4899;bottom:80px;right:180px;"></div>
""", has_header=False))

# ═══════════════════════════════════════════════════════════════
# 2 — Что такое ИИ
# ═══════════════════════════════════════════════════════════════
write(2, wrap("""
<div style="margin-top:-10px;"><h2>Что такое ИИ</h2>
<div class="lead">Программа, которая учится на данных и делает выводы, которые раньше требовали человека</div></div>
<div class="grid-3 mt-32" style="gap:28px;">
    <div>
        <div class="num-circle" style="background:#2563EB;">01</div>
        <h3 style="margin-top:16px;">Обучение</h3>
        <div class="text mt-12">Модель «читает» огромные массивы текста, кода, изображений — и запоминает закономерности. Это как если бы человек прочитал миллионы книг за одну ночь.</div>
    </div>
    <div>
        <div class="num-circle" style="background:#7C3AED;">02</div>
        <h3 style="margin-top:16px;">Инференс</h3>
        <div class="text mt-12">При получении запроса модель предсказывает наиболее вероятный ответ, основываясь на том, что выучила. Не думает — считает вероятности.</div>
    </div>
    <div>
        <div class="num-circle" style="background:#EC4899;">03</div>
        <h3 style="margin-top:16px;">Токены</h3>
        <div class="text mt-12">Текст разбивается на маленькие кусочки. 1 токен ≈ 0.75 слова. Контекстное окно = сколько токенов модель помнит одновременно.</div>
    </div>
</div>
""", title="Что такое ИИ", color=ACCENTS['blue'], num="02/25"))

# ═══════════════════════════════════════════════════════════════
# 3 — Модальности
# ═══════════════════════════════════════════════════════════════
mods = [
    ("Текст", "Письма, документы, анализ, ответы", 'blue'),
    ("Код", "Скрипты, баги, ревью, объяснение", 'violet'),
    ("Изображение", "Скриншот → цифры. Фото → аналоги. Скан → текст", 'pink'),
    ("Аудио", "Записи совещаний → расшифровка. Голосовые → текст", 'green'),
    ("Видео", "Ролики → summary, ключевые моменты", 'orange'),
    ("Документы", "Договоры → риски. Отчёты → тренды. Таблицы → ошибки", 'blue'),
    ("Многомодальность", "Скрин + вопрос = анализ. Всё вместе", 'violet'),
]
cards = ""
for title, body, c in mods:
    cards += f'<div class="card" style="--accent:{ACCENTS[c]};"><div class="card-title">{title}</div><div class="card-body">{body}</div></div>'
write(3, wrap(f"""
<div style="margin-top:-10px;"><h2>Модальности</h2>
<div class="lead">Что модель может воспринимать на вход — для рабочих задач</div></div>
<div class="grid-7 mt-24">{cards}</div>
""", title="Модальности", color=ACCENTS['violet'], num="03/25"))

# ═══════════════════════════════════════════════════════════════
# 4 — Сравнительная таблица
# ═══════════════════════════════════════════════════════════════
table_data = [
    ["Модель", "Разраб.", "VPN", "Текст", "Код", "Карт.", "Ауд.", "Вид.", "Док.", "Беспл. лимит", "Платный"],
    ["Claude 4.7", "Anthropic", "Да", "•", "•", "•", "—", "—", "•", "~45к/3ч", "$18–30"],
    ["GPT-5.4", "OpenAI", "Да", "•", "•", "•", "•", "•", "•", "~40–80/3ч", "$20"],
    ["Gemini 3.1", "Google", "Да", "•", "•", "•", "•", "•", "•", "~60/мин", "$20"],
    ["Perplexity", "Perplexity", "Да", "•", "•", "—", "—", "—", "•", "~20/ч", "$20"],
    ["Grok 4", "xAI", "Да", "•", "•", "•", "•", "•", "•", "~25/2ч", "$30"],
    ["Kimi 2.6", "Moonshot", "Нет", "•", "•", "•", "—", "—", "•", "~100/мин", "API"],
    ["DeepSeek V4", "DeepSeek", "Нет", "•", "•", "•", "—", "—", "•", "∞", "API $0.25"],
    ["Qwen 3.6", "Alibaba", "Нет", "•", "•", "•", "•", "•", "•", "~120/мин", "API"],
]
tbl = ""
for i, row in enumerate(table_data):
    tag = "th" if i == 0 else "td"
    style = ' style="font-weight:700;color:' + (['#2563EB','#7C3AED','#EC4899','#22C55E','#F59E0B','#06B6D4','#FBBF24','#EF4444'][i-1] if i > 0 else '#FFFFFF') + '"' if i > 0 and tag == "td" else ''
    tbl += "<tr>" + "".join([f"<{tag}{style if j==0 and i>0 else ''}>{cell}</{tag}>" for j, cell in enumerate(row)]) + "</tr>"
write(4, wrap(f"""
<div style="margin-top:-10px;"><h2>Сравнительная таблица моделей</h2></div>
<div class="mt-16"><table><tbody>{tbl}</tbody></table></div>
""", title="Сравнение моделей", color=ACCENTS['dark'], num="04/25"))

# ═══════════════════════════════════════════════════════════════
# 5–12 — Модели
# ═══════════════════════════════════════════════════════════════
models = [
    ("Claude 4.7", "Anthropic", "Лидер Arena #1", 'blue',
     ["Минимум галлюцинаций — скажет «не уверен»", "Контекст до 4M токенов (целая книга за раз)", "Отлично понимает инструкции. Самый «человечный» стиль"],
     ["Нет видео и аудио. Дорогой API. Нужен VPN", "Бесплатно — 45к токенов каждые 3 часа"],
     "Анализ длинных документов и договоров. Написание сложных текстов. Разработка.", "$18–30/мес — больше лимитов, ранний доступ"),
    ("GPT-5.4", "OpenAI", "Самая известная модель", 'violet',
     ["Всё-в-одном: текст, код, картинки, видео, голос", "Экосистема: плагины, GPTs, интеграции везде", "Голосовой режим. Canvas — совместное редактирование"],
     ["Галлюцинирует чаще, чем Claude. Нужен VPN", "Бесплатно 40–80 сообщений/3ч. Дорогой API"],
     "Универсальные задачи. Генерация изображений. Голосовые диалоги.", "$20/мес — GPT-5.4 без лимитов, Canvas"),
    ("Gemini 3.1", "Google", "Google-экосистема", 'pink',
     ["Многомодальность: текст + картинки + видео + аудио", "2M контекст — 1500 страниц. Notebook LM", "Интеграция с Docs, Sheets, Drive, Gmail"],
     ["Нужен VPN. Иногда «врёт» увереннее других"],
     "Работа с Google-экосистемой. Анализ видео. Notebook LM.", "$20/мес — Gemini 3.1 Pro"),
    ("Perplexity", "Perplexity", "Поисковик с ИИ", 'green',
     ["Ищет в интернете в реальном времени. Ответы со ссылками", "Минимум галлюцинаций (опирается на факты)", "Pro Search по документам. Pro API — 3000/сутки"],
     ["Не умеет картинки/видео/аудио. Меньше контекста. VPN", "Бесплатно ~20 запросов/час"],
     "Поиск актуальной информации. Фактчекинг. Исследования.", "$20/мес — Pro Search, API"),
    ("Grok 4", "xAI", "Доступ к X/Twitter", 'orange',
     ["DeepSearch — поиск + X/Twitter в реальном времени", "Agentic Tasks — модель сама выполняет задачи", "Voice Mode. SuperGrok — ранний доступ"],
     ["Нужен VPN. Бесплатно мало токенов (25/2ч)", "Менее надёжен для серьёзных задач"],
     "Мониторинг трендов в X/Twitter. Быстрые задачи с агентами.", "$30/мес — больше токенов, ранний доступ"),
    ("Kimi 2.6", "Moonshot AI", "Без VPN", 'cyan',
     ["Не нужен VPN — работает из России", "2M контекст. Agent Swarm — параллельные агенты", "Long-Context Inferencing. ~100 запросов/мин"],
     ["Нет видео и аудио. Интерфейс китайский/английский"],
     "Длинные документы. Сложные параллельные задачи. Программирование.", "Нет фиксированного — API по расходу"),
    ("DeepSeek V4", "DeepSeek", "Цена/качество #1", 'amber',
     ["Не нужен VPN. API в 20–50 раз дешевле западных", "#2 в Arena. MoE: 1.2T параметров, активны 32B", "Неограниченный бесплатный чат. DeepThink"],
     ["Нет видео и аудио. Спартанский интерфейс. Цензура"],
     "Разработка и API-интеграции. Сложные расчёты (DeepThink).", "API ~$0.25–0.50 за 1M токенов"),
    ("Qwen 3.6", "Alibaba", "Универсальная (без VPN)", 'red',
     ["Не нужен VPN. Мультимодальность: всё-в-одном", "Agentic Mode + Swarm Mode. QwQ-vision", "2.56M контекст. ~120 запросов/мин"],
     ["Интерфейс китайский/английский. Видео/аудио уступает"],
     "Универсальные задачи без VPN. Изображения/видео. Агенты.", "Нет фиксированного — API по расходу"),
]

for idx, (name, company, tagline, color_key, pluses, minuses, purpose, price) in enumerate(models):
    n = 5 + idx
    color = ACCENTS[color_key]
    pl = ""
    for p in pluses:
        pl += f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;"><div class="icon-dot" style="--dot-color:#22C55E;"></div><div class="text">{p}</div></div>'
    mi = ""
    for m in minuses:
        mi += f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;"><div class="icon-dot" style="--dot-color:#EF4444;"></div><div class="text" style="color:#64748B;">{m}</div></div>'
    write(n, wrap(f"""
<div style="display:flex;gap:40px;">
    <div style="flex:1;">
        <div style="font-size:15px;color:{color};font-weight:700;margin-bottom:6px;">{company}  •  {tagline}</div>
        <div class="mt-12" style="font-size:13px;font-weight:700;color:#22C55E;text-transform:uppercase;letter-spacing:0.06em;">ПЛЮСЫ</div>
        <div class="mt-8">{pl}</div>
        <div class="mt-16" style="font-size:13px;font-weight:700;color:#EF4444;text-transform:uppercase;letter-spacing:0.06em;">МИНУСЫ</div>
        <div class="mt-8">{mi}</div>
    </div>
    <div style="flex:1;display:flex;flex-direction:column;gap:16px;">
        <div class="card" style="--accent:{color};"><div class="card-title">Для чего использовать</div><div class="card-body">{purpose}</div></div>
        <div class="card" style="--accent:#22C55E;"><div class="card-title">Платный тариф</div><div class="card-body">{price}</div></div>
    </div>
</div>
""", title=name, color=color, num=f"{n:02d}/25"))

# ═══════════════════════════════════════════════════════════════
# 13 — Фишки моделей
# ═══════════════════════════════════════════════════════════════
features = [
    ("Claude", "4M контекст + минимум галлюцинаций", "Когда нужна точность на длинных документах", 'blue'),
    ("GPT-5.4", "Голос + Canvas + всё-в-одном", "Когда нужен универсальный помощник", 'violet'),
    ("Gemini", "Notebook LM + 2M контекст + Google", "Когда работаешь в Google-экосистеме", 'pink'),
    ("Perplexity", "Поиск с источниками в реальном времени", "Когда нужны факты, а не домыслы", 'green'),
    ("Grok", "DeepSearch + Agentic Tasks + доступ к X", "Когда нужны тренды и агенты", 'orange'),
    ("Kimi", "Agent Swarm + 2M контекст без VPN", "Когда нет VPN и нужны сложные задачи", 'cyan'),
    ("DeepSeek", "MoE + дёшевый API + DeepThink", "Когда важна экономия и сложные расчёты", 'amber'),
    ("Qwen", "Swarm Mode + Agentic + QwQ-vision", "Когда нужен «всё-в-одном» без VPN", 'red'),
]
feat_rows = ""
for i in range(0, len(features), 2):
    row = "<div style=\"display:flex;gap:30px;\">"
    for j in range(2):
        if i+j < len(features):
            name, feat, reason, c = features[i+j]
            row += f'<div style="flex:1;display:flex;gap:12px;"><div class="icon-dot" style="--dot-color:{ACCENTS[c]};margin-top:7px;"></div><div><div style="font-size:17px;font-weight:700;color:#0F172A;">{name}</div><div class="text-sm mt-4">{feat} <span style="color:{ACCENTS[c]};">→</span> {reason}</div></div></div>'
    row += "</div>"
    feat_rows += row + '<div style="margin-top:16px;"></div>'
write(13, wrap(f"""
<div style="margin-top:-10px;"><h2>Зачем именно эта модель?</h2></div>
<div class="mt-20">{feat_rows}</div>
""", title="Зачем эта модель?", color=ACCENTS['blue'], num="13/25"))

# ═══════════════════════════════════════════════════════════════
# 14 — LM Arena
# ═══════════════════════════════════════════════════════════════
write(14, wrap("""
<div style="display:flex;gap:28px;height:100%;">
    <div class="card" style="flex:1;--accent:#2563EB;">
        <div class="card-title">Как работает</div>
        <div class="card-body">Вводите вопрос → получаете два ответа от анонимных моделей → голосуете за лучший → узнаёте, кто победил.<br><br>Рейтинг Elo — объективная таблица лидеров.</div>
    </div>
    <div class="card" style="flex:1;--accent:#7C3AED;">
        <div class="card-title">Что есть в 2026</div>
        <div class="card-body">Text Arena — текстовые модели.<br>Video Arena — генерация видео.<br>Image Arena — картинки.<br>Мультимодальные сравнения.</div>
    </div>
</div>
<div class="mt-24">
    <div class="badge" style="--badge-bg:#22C55E;">Регистрация бесплатная. Карта не нужна.</div>
    <div class="text-sm mt-8">lmarena.ai</div>
</div>
""", title="LM Arena", subtitle="Бесплатный способ попробовать любую модель", color=ACCENTS['blue'], num="14/25"))

# ═══════════════════════════════════════════════════════════════
# 15 — Robomonkey
# ═══════════════════════════════════════════════════════════════
write(15, wrap("""
<div style="display:flex;gap:28px;height:100%;">
    <div class="card" style="flex:1;--accent:#7C3AED;">
        <div class="card-title">Как работает</div>
        <div class="card-body">Описываете задачу текстом → Robomonkey генерирует Chrome-расширение → устанавливаете в браузер → работает само.<br><br>Сбор данных, парсинг, автозаполнение форм, мониторинг цен.</div>
    </div>
    <div class="card" style="flex:1;--accent:#EC4899;">
        <div class="card-title">Альтернативы 2026</div>
        <div class="card-body">Stagehand — для разработчиков (open-source).<br>Gumloop — no-code для бизнеса.<br>Browser Use — Python для кодеров.<br>Make.com / n8n — связка сервисов.</div>
    </div>
</div>
<div class="mt-24"><div class="badge" style="--badge-bg:#22C55E;">Экономия 90–95% стоимости виртуального ассистента</div></div>
""", title="Robomonkey", subtitle="Автоматизация процессов без программирования", color=ACCENTS['violet'], num="15/25"))

# ═══════════════════════════════════════════════════════════════
# 16 — AI-разработка
# ═══════════════════════════════════════════════════════════════
devs = [
    ("Lovable", "Генерация веб-приложений и сайтов из текста", "MVP, лендинг, внутренний инструмент", 'blue'),
    ("Blink.new", "Создание сайтов с AI-дизайном", "Красивый сайт за минуты", 'violet'),
    ("Bolt.new", "AI-разработка на Next.js / React", "Настоящий код под капотом", 'green'),
    ("Hercules.app", "Внутренние бизнес-приложения", "CRM, дашборды, формы без IT", 'orange'),
]
dev_cards = ""
for name, what, why, c in devs:
    dev_cards += f'<div class="card" style="--accent:{ACCENTS[c]};"><div class="card-title">{name}</div><div class="card-body">{what}<br><br><span style="color:{ACCENTS[c]};font-weight:600;">→</span> {why}</div></div>'
write(16, wrap(f"""
<div style="margin-top:-10px;"><h2>AI-разработка без программиста</h2></div>
<div class="grid-4 mt-20">{dev_cards}</div>
<div class="text mt-20">Принцип: «Сделай сайт для приёма заявок с полями имя, телефон, выбор услуги и отправкой в Telegram» — платформа генерирует работающий сайт. Не нужно уметь кодить.</div>
<div class="badge mt-12" style="--badge-bg:#2563EB;">Для бизнеса: прототипы за часы, внутренние инструменты без IT</div>
""", title="AI-разработка", color=ACCENTS['green'], num="16/25"))

# ═══════════════════════════════════════════════════════════════
# 17–24 — Отделы
# ═══════════════════════════════════════════════════════════════
departments = [
    {
        "name": "БУХГАЛТЕРИЯ",
        "subtitle": "Распознавание, сверка, проверка",
        "color": 'green',
        "tasks": [
            "Распознавание первичных документов (счета, акты, накладные) → структурированные данные",
            "Сверка банковской выписки с 1С и выявление расхождений",
            "Проверка правильности проводок и соответствия учетной политике",
            "Подготовка форм налоговых деклараций по шаблонам",
            "Анализ дебиторской / кредиторской задолженности"
        ],
        "paid": "Claude — лучший для структурирования длинных документов. GPT-4 — универсальный (Canvas для таблиц).",
        "free": "DeepSeek — неограниченно, без VPN, отлично справляется с таблицами. Qwen — 120 запросов/мин.",
        "prompts": [
            "Я загрузил скан 50 счетов поставщиков. Извлеки из каждого: ИНН, КПП, сумму, дату, номер счета. Сформируй таблицу.",
            "Сверь эту банковскую выписку с данными из 1С. Найди расхождения по суммам и датам. Выдели строки без соответствия.",
            "Проверь правильность проводки: Дебет 62 Кредит 90 на сумму 150 000 руб. Это реализация услуг. Соответствует ли учетной политике?"
        ]
    },
    {
        "name": "ФИНАНСЫ",
        "subtitle": "Прогнозирование, бюджеты, сценарии",
        "color": 'blue',
        "tasks": [
            "Прогнозирование cash flow на основе исторических данных",
            "Сценарное моделирование (оптимистичный, реалистичный, пессимистичный)",
            "Подготовка отчетности для совета директоров / инвесторов",
            "Анализ инвестиционных проектов (NPV, IRR, срок окупаемости)",
            "Выявление аномалий в финансовых данных"
        ],
        "paid": "Claude — точность и структура для сложных расчетов. GPT-4 — Canvas для совместной работы с Excel.",
        "free": "DeepSeek — DeepThink для сложных расчетов, без VPN. Kimi — 2M контекст для больших таблиц.",
        "prompts": [
            "На основе данных о выручке за 24 месяца построй прогноз cash flow на следующие 6 месяцев. Учти сезонность.",
            "Построй 3 сценария при росте выручки: +10%, +20%, +30%. Для каждого посчитай EBITDA и точку безубыточности.",
            "Проанализируй этот Excel-файл с P&L. Найди 3 главных отклонения от бюджета и объясни причины. Дай рекомендации."
        ]
    },
    {
        "name": "ЮРИСТЫ",
        "subtitle": "Анализ договоров, риски, претензии",
        "color": 'violet',
        "tasks": [
            "Анализ договоров на предмет рисковых пунктов",
            "Сравнение двух редакций одного документа",
            "Подготовка претензий, исковых заявлений по шаблонам",
            "Проверка compliance с законодательством",
            "Поиск судебной практики по аналогичным делам"
        ],
        "paid": "Claude 4 — минимум галлюцинаций, 4M контекст для длинных договоров. GPT-4 — для генерации документов.",
        "free": "DeepSeek — без VPN, неограниченно. Perplexity — поиск судебной практики с источниками.",
        "prompts": [
            "Проанализируй этот договор поставки. Найди: неблагоприятные условия оплаты, отсутствие штрафных санкций, рисковые пункты о возврате. Дай рекомендации по доработке.",
            "Сравни две редакции NDA. Выдели все изменения, которые увеличивают риски для нашей компании. Оформи таблицу: пункт, было, стало, риск.",
            "Подготовь претензию поставщику о нарушении сроков поставки по договору №123 от 01.03.2026. Требование: неустойка 0.1% за каждый день просрочки."
        ]
    },
    {
        "name": "ПРОДАКТЫ",
        "subtitle": "Отзывы, ТЗ, конкуренты, приоритизация",
        "color": 'orange',
        "tasks": [
            "Анализ пользовательских отзывов и выявление болей",
            "Написание user stories и acceptance criteria",
            "Исследование конкурентов (фичи, цены, positioning)",
            "Приоритизация бэклога (RICE, MoSCoW)",
            "Подготовка ТЗ для разработчиков"
        ],
        "paid": "GPT-4 — Canvas для документов. Claude — структурирование сложных ТЗ.",
        "free": "Kimi — Agent Swarm для параллельных задач (конкуренты + отзывы одновременно). Qwen — Swarm Mode.",
        "prompts": [
            "Вот 500 отзывов наших клиентов с Wildberries. Выдели топ-10 проблем и сгруппируй по категориям. Для каждой предложи решение.",
            "Напиши user story для функции: клиент хочет отслеживать доставку в личном кабинете. Acceptance criteria, критерии готовности, оценка сложности.",
            "Проанализируй 3 конкурента в нише БАДов. Сравни: цены, состав, упаковку, каналы продаж. Сформируй SWOT-анализ."
        ]
    },
    {
        "name": "КОММЕРЧЕСКИЙ",
        "subtitle": "Скрипты, КП, воронка, реактивация",
        "color": 'pink',
        "tasks": [
            "Написание скриптов продаж и возражений",
            "Подготовка коммерческих предложений (КП)",
            "Анализ воронки продаж и выявление узких мест",
            "Реактивация «спящих» клиентов",
            "Сегментация клиентской базы"
        ],
        "paid": "GPT-4 — генерация текстов и скриптов. Claude — анализ данных воронки.",
        "free": "Grok — доступ к трендам в X/Twitter для мониторинга. DeepSeek — для аналитики.",
        "prompts": [
            "Напиши 5 вариантов письма для реактивации клиентов, которые не купили 90 дней. Тон: дружелюбный, без давления. Добавь 3 варианта темы письма.",
            "Проанализируй воронку: 1000 лидов → 300 встреч → 80 КП → 20 сделок. Найди узкие места. Дай 3 рекомендации по улучшению конверсии на каждом этапе.",
            "Составь коммерческое предложение для B2B-клиента на поставку БАДов оптом. Условия: от 100 шт — скидка 20%, от 500 шт — скидка 30%. Добавь кейсы."
        ]
    },
    {
        "name": "ТОП-МЕНЕДЖМЕНТ",
        "subtitle": "Стратегия, due diligence, выходы на рынки",
        "color": 'amber',
        "tasks": [
            "Стратегический анализ и сценарное планирование",
            "Due diligence при acquisitions / партнерствах",
            "Структурирование сложных решений",
            "Подготовка к совещаниям и публичным выступлениям",
            "Анализ новых рынков и точек входа"
        ],
        "paid": "Claude — точность, структура, минимум галлюцинаций для важных решений. GPT-4 — всё-в-одном.",
        "free": "DeepSeek — DeepThink для сложных рассуждений. Perplexity — исследования рынков с источниками.",
        "prompts": [
            "Проанализируй 3 варианта выхода нашего бренда БАДов на рынок Казахстана. Для каждого: бюджет, сроки, риски, конкуренты, regulatory requirements. Рекомендуй лучший.",
            "Мы рассматриваем покупку компании-производителя БАДов. Проведи due diligence: какие риски, что проверять, какие документы запросить. Оформи чек-лист.",
            "Подготовь структуру 15-минутного выступления на конференции о внедрении ИИ в компанию. Аудитория: 200 CEO среднего бизнеса. Добавь 1 слайд = 1 тезис."
        ]
    },
    {
        "name": "АНАЛИТИКИ",
        "subtitle": "Данные, SQL, визуализация, прогнозирование",
        "color": 'cyan',
        "tasks": [
            "Обработка и очистка больших данных",
            "Написание SQL-запросов для сложных отчетов",
            "Визуализация данных (Python, Excel, BI)",
            "Прогнозирование (временные ряды, регрессия)",
            "A/B тестирование и статистическая значимость"
        ],
        "paid": "Claude — кодинг, объяснение сложных запросов. GPT-4 — Canvas для совместной работы.",
        "free": "DeepSeek — лучший для кода, без VPN. Kimi — 2M контекст для больших датасетов. Gemini — интеграция с Google Sheets.",
        "prompts": [
            "Напиши SQL-запрос для отчета: выручка по регионам за последний квартал с динамикой к предыдущему. Добавь ранжирование регионов по росту.",
            "Загрузи этот CSV (10 000 строк). Найди аномалии: выбросы, пропуски, дубликаты. Построй гистограмму распределения по категориям. Выдай summary.",
            "У нас данные о 2 вариантах лендинга (A и B). 1000 показов каждому, конверсия A = 3.2%, B = 4.1%. Рассчитай статистическую значимость (p-value). Достоверна ли разница?"
        ]
    },
    {
        "name": "HR И ПОДБОР",
        "subtitle": "Вакансии, скрининг, адаптация, обратная связь",
        "color": 'green',
        "tasks": [
            "Составление привлекательных вакансий",
            "Скрининг резюме и ранжирование кандидатов",
            "Составление планов адаптации",
            "Описание компетенций и KPI",
            "Подготовка обратной связи (review, 1-on-1)"
        ],
        "paid": "Claude — структурирование, анализ резюме. GPT-4 — генерация текстов, Canvas для документов.",
        "free": "Kimi — обработка больших массивов резюме (2M контекст). Qwen — Swarm Mode для параллельных задач.",
        "prompts": [
            "Вот 50 резюме на позицию Product Manager. Проанализируй каждое по критериям: опыт в e-commerce, знание Agile, аналитические навыки. Выдели топ-10 кандидатов с обоснованием.",
            "Напиши план адаптации нового менеджера по продажам на первые 30 дней. День 1–7: знакомство. День 8–14: продукт. День 15–21: процессы. День 22–30: самостоятельность. Добавь чек-листы.",
            "Составь вакансию на позицию SMM-менеджера для бренда БАДов. Тон: молодежный, энергичный. Обязанности: TikTok, Instagram, UGC. Добавь 3 необычных требования, которые отсеют неподходящих."
        ]
    },
]

for idx, dept in enumerate(departments):
    n = 17 + idx
    color = ACCENTS[dept["color"]]
    tasks_html = ""
    for t in dept["tasks"]:
        tasks_html += f'<div class="dept-item"><div class="dept-bar" style="background:{color};"></div><div class="dept-text">{t}</div></div>'
    prompts_html = ""
    for i, p in enumerate(dept["prompts"]):
        prompts_html += f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;"><div class="prompt-num" style="background:{color};">{i+1}</div><div class="prompt-box" style="--accent:{color};">{p}</div></div>'
    write(n, wrap(f"""
<div style="display:flex;gap:24px;height:100%;">
    <div style="flex:1.1;" class="dept-col">
        <div class="dept-col-title" style="color:{color};">ЗАДАЧИ</div>
        {tasks_html}
    </div>
    <div style="flex:1;" class="dept-col">
        <div class="dept-col-title" style="color:{color};">КАКУЮ ИИ ИСПОЛЬЗОВАТЬ</div>
        <div class="card" style="--accent:#22C55E;"><div class="card-title" style="color:#22C55E;">Платные</div><div class="card-body">{dept["paid"]}</div></div>
        <div class="card" style="--accent:#2563EB;"><div class="card-title" style="color:#2563EB;">Бесплатные</div><div class="card-body">{dept["free"]}</div></div>
    </div>
    <div style="flex:1.1;" class="dept-col">
        <div class="dept-col-title" style="color:{color};">ПРИМЕРЫ ПРОМПТОВ</div>
        {prompts_html}
    </div>
</div>
""", title=dept["name"], subtitle=dept["subtitle"], color=color, num=f"{n:02d}/25"))

# ═══════════════════════════════════════════════════════════════
# 25 — Рекомендации
# ═══════════════════════════════════════════════════════════════
recs = [
    ("01", "Если не уверены — обсудите с другой моделью", "Задайте тот же вопрос Claude, GPT и DeepSeek. Если все три говорят одно — можно доверять.", 'blue'),
    ("02", "Формулируйте результат, не задачу", "Плохо: «Вот отчёт, сделай что-нибудь». Хорошо: «Выдели 3 тренда и предложи 2 действия».", 'violet'),
    ("03", "Вначале план, потом реализация", "Сначала составьте план и согласуйте его. Только потом выполняйте.", 'green'),
    ("04", "Заставьте ИИ задать вопросы", "«Есть вопросы? Всё ли понятно?» — лучшие результаты даёт диалог, не монолог.", 'orange'),
    ("05", "Разбивайте сложное на шаги", "Не «напиши бизнес-план». Разбейте: структура → рынок → экономика → риски.", 'pink'),
    ("06", "Давайте контекст", "«Ты финдиректор, готовишь презентацию для совета директоров» — результат в разы точнее.", 'blue'),
    ("07", "Проверяйте факты", "ИИ уверенно выдумывает даты и ссылки. Всегда перепроверяйте.", 'red'),
    ("08", "Системные промпты для рутины", "«Ты аналитик. Каждый CSV → аномалии, топ-3 тренда, рекомендации» — экономит время.", 'violet'),
    ("09", "Конфиденциальность", "Для чувствительных данных — локальные модели (DeepSeek, Qwen) или корпоративные тарифы.", 'green'),
]
recs_html = ""
for i, (num, title, body, c) in enumerate(recs):
    col = i % 3
    row = i // 3
    if col == 0:
        recs_html += '<div style="display:flex;gap:24px;margin-bottom:24px;">'
    recs_html += f'''
    <div style="flex:1;display:flex;gap:14px;">
        <div class="rec-num" style="background:{ACCENTS[c]};">{num}</div>
        <div>
            <div class="rec-title">{title}</div>
            <div class="rec-body">{body}</div>
        </div>
    </div>'''
    if col == 2 or i == len(recs)-1:
        recs_html += '</div>'

write(25, wrap(f"""
<div style="margin-top:-10px;"><h2>Рекомендации по работе с ИИ</h2></div>
<div class="mt-16">{recs_html}</div>
<div class="text" style="margin-top:28px;font-weight:600;color:#0F172A;">
    Главное: ИИ — инструмент. Результат зависит от того, насколько точно вы формулируете задачу.
</div>
""", title="Рекомендации", color=ACCENTS['dark'], num="25/25"))

print(f"✅ Генерация завершена. Слайдов: 25")
print(f"   Папка: slides_html/")
