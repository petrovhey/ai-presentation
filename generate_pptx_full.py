#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Современная презентация в PowerPoint — 25 слайдов
Темный фон, яркие акценты, минимализм
Версия с детальными слайдами по отделам
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ─── ЦВЕТА ─────────────────────────────────────────────────────
BG = RGBColor(15, 23, 42)
CARD = RGBColor(30, 41, 59)
BLUE = RGBColor(59, 130, 246)
VIOLET = RGBColor(139, 92, 246)
PINK = RGBColor(236, 72, 153)
GREEN = RGBColor(16, 185, 129)
ORANGE = RGBColor(245, 158, 11)
RED = RGBColor(239, 68, 68)
WHITE = RGBColor(248, 250, 252)
GRAY = RGBColor(148, 163, 184)
DARK_GRAY = RGBColor(71, 85, 105)
CYAN = RGBColor(6, 182, 212)
AMBER = RGBColor(251, 191, 36)

# ─── РАЗМЕРЫ ─────────────────────────────────────────────────
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MARGIN = Inches(0.6)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
blank_layout = prs.slide_layouts[6]

def add_bg(slide, color=BG):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    spTree = slide.shapes._spTree
    sp = shape._element
    spTree.remove(sp)
    spTree.insert(2, sp)

def add_textbox(slide, left, top, width, height, text, font_size=14,
                bold=False, color=WHITE, align=PP_ALIGN.LEFT, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = align
    return txBox

def add_card(slide, left, top, width, height, title, body,
             title_color=BLUE, border_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD
    shape.line.color.rgb = border_color or RGBColor(51, 65, 85)
    shape.line.width = Pt(1)
    add_textbox(slide, left + Inches(0.15), top + Inches(0.1),
                width - Inches(0.3), Inches(0.4),
                title, font_size=13, bold=True, color=title_color)
    add_textbox(slide, left + Inches(0.15), top + Inches(0.45),
                width - Inches(0.3), height - Inches(0.55),
                body, font_size=10.5, color=GRAY)

def add_bullet_list(slide, left, top, width, items, color=WHITE, font_size=11):
    y = top
    for item in items:
        add_textbox(slide, left + Inches(0.15), y, width - Inches(0.3), Inches(0.4),
                    f"•  {item}", font_size=font_size, color=color)
        y += Inches(0.38)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 1 — Титульный
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
c1 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9), Inches(-2), Inches(6), Inches(6))
c1.fill.solid(); c1.fill.fore_color.rgb = BLUE; c1.line.fill.background()
c2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-2), Inches(4), Inches(5), Inches(5))
c2.fill.solid(); c2.fill.fore_color.rgb = VIOLET; c2.line.fill.background()
bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(2.8), Inches(3), Inches(0.15))
bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()
add_textbox(slide, Inches(0.6), Inches(2.5), Inches(10), Inches(1.2), "Нейросети и ИИ", font_size=54, bold=True, color=WHITE)
add_textbox(slide, Inches(0.6), Inches(3.5), Inches(10), Inches(0.6), "как использовать в работе", font_size=28, color=GRAY)
add_textbox(slide, Inches(0.6), Inches(4.3), Inches(8), Inches(0.4), "Доклад для сотрудников компании  •  2026", font_size=14, color=DARK_GRAY)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 2 — Что такое ИИ
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.5), Inches(12), Inches(0.7), "Что такое ИИ", font_size=36, bold=True, color=WHITE)
add_textbox(slide, MARGIN, Inches(1.1), Inches(12), Inches(0.4), "Программа, которая учится на данных и делает выводы, которые раньше требовали человека", font_size=14, color=GRAY)
cols = [
    ("01", "Обучение", "Модель «читает» огромные массивы текста, кода, изображений — и запоминает закономерности. Это как если бы человек прочитал миллионы книг за одну ночь.", BLUE),
    ("02", "Инференс", "При получении запроса модель предсказывает наиболее вероятный ответ, основываясь на том, что выучила. Не думает — считает вероятности.", VIOLET),
    ("03", "Токены", "Текст разбивается на маленькие кусочки. 1 токен ≈ 0.75 слова. Контекстное окно = сколько токенов модель помнит «в голове» одновременно.", PINK),
]
for i, (num, title, body, color) in enumerate(cols):
    x = MARGIN + i * Inches(4.2)
    add_textbox(slide, x, Inches(2), Inches(1), Inches(0.6), num, font_size=48, bold=True, color=color)
    add_textbox(slide, x, Inches(2.7), Inches(3.8), Inches(0.4), title, font_size=18, bold=True, color=WHITE)
    add_textbox(slide, x, Inches(3.2), Inches(3.6), Inches(2.5), body, font_size=12, color=GRAY)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 3 — Модальности
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.5), Inches(12), Inches(0.7), "Модальности", font_size=36, bold=True, color=WHITE)
add_textbox(slide, MARGIN, Inches(1.1), Inches(12), Inches(0.4), "Что модель может воспринимать на вход — для рабочих задач", font_size=14, color=GRAY)
mods = [
    ("Текст", "Письма, документы, анализ, ответы на вопросы", BLUE),
    ("Код", "Скрипты, баги, ревью, объяснение чужого кода", VIOLET),
    ("Изображение", "Скриншоты → цифры. Фото → аналоги. Сканы → текст", PINK),
    ("Аудио", "Записи совещаний → расшифровка. Голосовые → текст", GREEN),
    ("Видео", "Ролики → summary, ключевые моменты, расшифровка", ORANGE),
    ("Документы", "Договоры → риски. Отчёты → тренды. Таблицы → ошибки", BLUE),
    ("Многомодальность", "Скрин + вопрос = анализ. Всё вместе", VIOLET),
]
for i, (title, body, color) in enumerate(mods):
    col = i % 4
    row = i // 4
    x = MARGIN + col * Inches(3.1)
    y = Inches(1.8) + row * Inches(2.5)
    add_card(slide, x, y, Inches(2.9), Inches(2.2), title, body, title_color=color)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 4 — Сравнительная таблица
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.4), Inches(12), Inches(0.6), "Сравнительная таблица моделей", font_size=32, bold=True, color=WHITE)
rows, cols = 9, 11
table = slide.shapes.add_table(rows, cols, MARGIN, Inches(1.1), Inches(12), Inches(5.8)).table
table_data = [
    ["Модель", "Разраб.", "VPN", "Текст", "Код", "Картинки", "Аудио", "Видео", "Док-ты", "Беспл. лимит", "Платный тариф"],
    ["Claude 4.7", "Anthropic", "Да", "•", "•", "•", "—", "—", "•", "~45к/3ч", "$18–30"],
    ["GPT-5.4", "OpenAI", "Да", "•", "•", "•", "•", "•", "•", "~40–80/3ч", "$20"],
    ["Gemini 3.1", "Google", "Да", "•", "•", "•", "•", "•", "•", "~60/мин", "$20"],
    ["Perplexity", "Perplexity", "Да", "•", "•", "—", "—", "—", "•", "~20/ч", "$20"],
    ["Grok 4", "xAI", "Да", "•", "•", "•", "•", "•", "•", "~25/2ч", "$30"],
    ["Kimi 2.6", "Moonshot", "Нет", "•", "•", "•", "—", "—", "•", "~100/мин", "API"],
    ["DeepSeek V4", "DeepSeek", "Нет", "•", "•", "•", "—", "—", "•", "∞", "API $0.25"],
    ["Qwen 3.6", "Alibaba", "Нет", "•", "•", "•", "•", "•", "•", "~120/мин", "API"],
]
for i, row_data in enumerate(table_data):
    for j, cell_text in enumerate(row_data):
        cell = table.cell(i, j)
        cell.text = cell_text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(9.5 if i == 0 else 9)
            paragraph.font.bold = (i == 0)
            paragraph.font.color.rgb = WHITE if i == 0 else GRAY
            paragraph.alignment = PP_ALIGN.CENTER if j > 1 else PP_ALIGN.LEFT
        if i == 0:
            cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor(51, 65, 85)
        else:
            cell.fill.solid(); cell.fill.fore_color.rgb = CARD if i % 2 == 1 else BG
col_widths = [Inches(1.3), Inches(1.2), Inches(0.7), Inches(0.6), Inches(0.6), Inches(0.9), Inches(0.6), Inches(0.6), Inches(0.7), Inches(1.1), Inches(1.0)]
for i, w in enumerate(col_widths):
    table.columns[i].width = w

# ═══════════════════════════════════════════════════════════════
# СЛАЙДЫ 5–12 — Модели (по 1 слайду на модель)
# ═══════════════════════════════════════════════════════════════
models = [
    ("Claude 4.7", "Anthropic", "Лидер Arena #1 по тексту", BLUE,
     ["Минимум галлюцинаций — если не знает, скажет «не уверен»",
      "Огромный контекст — до 4M токенов (целая книга за раз)",
      "Отлично понимает инструкции и форматы. Самый «человечный» стиль"],
     ["Нет видео и аудио на входе. Дорогой API. Нужен VPN",
      "Бесплатно — 45к токенов каждые 3 часа"],
     "Анализ длинных документов и договоров. Написание сложных текстов. Разработка.",
     "$18–30/мес — больше лимитов, ранний доступ"),
    ("GPT-5.4", "OpenAI", "Самая известная модель в мире", VIOLET,
     ["Универсальность: текст, код, картинки, видео, голос — всё в одном",
      "Огромная экосистема: плагины, GPTs, интеграции везде",
      "Голосовой режим. Canvas — совместное редактирование документов"],
     ["Галлюцинирует чаще, чем Claude. Нужен VPN",
      "Бесплатно ограниченно (40–80 сообщений/3ч). Дорогой API"],
     "Универсальные задачи. Генерация изображений. Голосовые диалоги. Canvas.",
     "$20/мес — GPT-5.4 без лимитов, Canvas, приоритет"),
    ("Gemini 3.1", "Google", "Тесная интеграция с Google", GREEN,
     ["Многомодальность: текст + картинки + видео + аудио",
      "2M контекст — 1500 страниц. Notebook LM — аудио-обзоры из документов",
      "Интеграция с Docs, Sheets, Drive, Gmail. Дешевле Claude/OpenAI"],
     ["Нужен VPN. Иногда «врёт» увереннее других"],
     "Работа с Google-экосистемой. Анализ видео. Notebook LM.",
     "$20/мес — Gemini 3.1 Pro, больше запросов"),
    ("Perplexity", "Perplexity", "Поисковик с ИИ — не чатбот", ORANGE,
     ["Ищет в интернете в реальном времени. Каждый ответ — со ссылками",
      "Минимум галлюцинаций (опирается на факты)",
      "Pro Search по документам. Pro API — 3000 запросов/сутки"],
     ["Не умеет картинки/видео/аудио. Контекст меньше. Нужен VPN",
      "Бесплатно ~20 запросов/час"],
     "Поиск актуальной информации. Фактчекинг. Исследования.",
     "$20/мес — Pro Search, API, больше запросов"),
    ("Grok 4", "xAI / Илон Маск", "Доступ к X/Twitter в реальном времени", PINK,
     ["DeepSearch — поиск по интернету + X/Twitter",
      "Agentic Tasks — модель сама выполняет задачи",
      "Voice Mode. SuperGrok — ранний доступ к экспериментальным фичам"],
     ["Нужен VPN. Бесплатно мало токенов (25/2ч)",
      "Менее надёжен для серьёзных задач"],
     "Мониторинг трендов в X/Twitter. Быстрые задачи с агентами.",
     "$30/мес — больше токенов, ранний доступ"),
    ("Kimi 2.6", "Moonshot AI", "Лучший выбор без VPN", BLUE,
     ["Не нужен VPN — работает из России напрямую",
      "Огромный контекст — 2M токенов. Agent Swarm — параллельные агенты",
      "Long-Context Inferencing. Бесплатно щедро (~100/мин)"],
     ["Нет видео и аудио. Интерфейс на китайском/английском"],
     "Длинные документы. Сложные параллельные задачи. Программирование.",
     "Нет фиксированного — API по использованию"),
    ("DeepSeek V4", "DeepSeek", "Лидер по цена/качество", VIOLET,
     ["Не нужен VPN. API в 20–50 раз дешевле Claude/OpenAI",
      "#2 в Arena по тексту. MoE: 1.2T параметров, активны 32B",
      "Неограниченный бесплатный чат. DeepThink — глубокое рассуждение"],
     ["Нет видео и аудио. Спартанский интерфейс. Цензура"],
     "Разработка и API-интеграции (дешево!). Сложные расчёты (DeepThink).",
     "API дёшево: ~$0.25–0.50 за 1M токенов"),
    ("Qwen 3.6", "Alibaba", "Самая универсальная китайская модель", GREEN,
     ["Не нужен VPN. Мультимодальность: всё-в-одном",
      "Agentic Mode — сама выполняет задачи. Swarm Mode — параллельные агенты",
      "QwQ-vision — мультимодальное рассуждение. 2.56M контекст. ~120/мин"],
     ["Интерфейс на китайском/английском. Видео/аудио уступает западным"],
     "Универсальные задачи без VPN. Изображения/видео. Агенты.",
     "Нет фиксированного — API по использованию"),
]

for name, company, tagline, color, pluses, minuses, purpose, price in models:
    slide = prs.slides.add_slide(blank_layout)
    add_bg(slide)
    add_textbox(slide, MARGIN, Inches(0.4), Inches(8), Inches(0.7), name, font_size=40, bold=True, color=WHITE)
    add_textbox(slide, MARGIN, Inches(1.1), Inches(8), Inches(0.35), f"{company}  •  {tagline}", font_size=13, color=color)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, MARGIN, Inches(1.45), Inches(2), Inches(0.06))
    bar.fill.solid(); bar.fill.fore_color.rgb = color; bar.line.fill.background()
    add_textbox(slide, MARGIN, Inches(1.7), Inches(2), Inches(0.3), "ПЛЮСЫ", font_size=10, bold=True, color=GREEN)
    y = Inches(2.0)
    for p in pluses:
        add_textbox(slide, MARGIN + Inches(0.2), y, Inches(5.5), Inches(0.5), f"• {p}", font_size=11, color=WHITE)
        y += Inches(0.4)
    add_textbox(slide, Inches(6.5), Inches(1.7), Inches(2), Inches(0.3), "МИНУСЫ", font_size=10, bold=True, color=RED)
    y = Inches(2.0)
    for m in minuses:
        add_textbox(slide, Inches(6.7), y, Inches(5.5), Inches(0.5), f"• {m}", font_size=11, color=GRAY)
        y += Inches(0.4)
    add_card(slide, MARGIN, Inches(5.2), Inches(5.8), Inches(1.8), "Для чего", purpose, title_color=WHITE, border_color=color)
    add_card(slide, Inches(6.7), Inches(5.2), Inches(5.8), Inches(1.8), "Тариф", price, title_color=WHITE, border_color=GREEN)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 13 — Фишки моделей
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.4), Inches(12), Inches(0.6), "Зачем именно эта модель?", font_size=32, bold=True, color=WHITE)
features = [
    ("Claude", "4M контекст + минимум галлюцинаций", "Когда нужна точность на длинных документах", BLUE),
    ("GPT-5.4", "Голос + Canvas + всё-в-одном", "Когда нужен универсальный помощник", VIOLET),
    ("Gemini", "Notebook LM + 2M контекст + Google", "Когда работаешь в Google-экосистеме", GREEN),
    ("Perplexity", "Поиск с источниками в реальном времени", "Когда нужны факты, а не домыслы", ORANGE),
    ("Grok", "DeepSearch + Agentic Tasks + доступ к X", "Когда нужны тренды и агенты", PINK),
    ("Kimi", "Agent Swarm + 2M контекст без VPN", "Когда нет VPN и нужны сложные задачи", BLUE),
    ("DeepSeek", "MoE + дёшевый API + DeepThink", "Когда важна экономия и сложные расчёты", VIOLET),
    ("Qwen", "Swarm Mode + Agentic + QwQ-vision", "Когда нужен «всё-в-одном» без VPN", GREEN),
]
for i, (name, feature, reason, color) in enumerate(features):
    col = i % 2
    row = i // 2
    x = MARGIN + col * Inches(6.3)
    y = Inches(1.2) + row * Inches(1.45)
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y + Inches(0.05), Inches(0.15), Inches(0.15))
    dot.fill.solid(); dot.fill.fore_color.rgb = color; dot.line.fill.background()
    add_textbox(slide, x + Inches(0.25), y, Inches(2.5), Inches(0.25), name, font_size=13, bold=True, color=WHITE)
    add_textbox(slide, x + Inches(0.25), y + Inches(0.25), Inches(5.8), Inches(0.25), f"{feature}  →  {reason}", font_size=11, color=GRAY)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 14 — LM Arena
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.5), Inches(12), Inches(0.7), "LM Arena", font_size=40, bold=True, color=WHITE)
add_textbox(slide, MARGIN, Inches(1.2), Inches(8), Inches(0.4), "Бесплатный способ попробовать любую модель", font_size=16, color=GRAY)
add_card(slide, MARGIN, Inches(2), Inches(5.5), Inches(2.5), "Как работает",
         "Вы вводите вопрос → получаете два ответа от анонимных моделей → голосуете за лучший → узнаёте, кто победил.\n\nРейтинг Elo — объективная таблица лидеров. Text Arena, Video Arena, Image Arena — сравнение по типам.",
         title_color=WHITE, border_color=BLUE)
add_card(slide, Inches(6.8), Inches(2), Inches(5.5), Inches(2.5), "Что есть в 2026",
         "Text Arena — текстовые модели.\nVideo Arena — генерация видео (Veo 3, Sora 2, Kling).\nImage Arena — картинки.\nМультимодальные сравнения.",
         title_color=WHITE, border_color=VIOLET)
add_textbox(slide, MARGIN, Inches(5), Inches(12), Inches(0.5), "✓  Регистрация бесплатная. Кредитная карта не нужна.", font_size=14, bold=True, color=GREEN)
add_textbox(slide, MARGIN, Inches(5.5), Inches(12), Inches(0.3), "lmarena.ai", font_size=12, color=DARK_GRAY)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 15 — Robomonkey
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.5), Inches(12), Inches(0.7), "Robomonkey", font_size=40, bold=True, color=WHITE)
add_textbox(slide, MARGIN, Inches(1.2), Inches(8), Inches(0.4), "Автоматизация процессов без программирования", font_size=16, color=GRAY)
add_card(slide, MARGIN, Inches(2), Inches(5.5), Inches(3), "Как работает",
         "Описываете задачу текстом («собирай цены с Ozon каждый день»).\n\nRobomonkey генерирует Chrome-расширение с кодом.\n\nУстанавливаете в браузер — оно работает само.",
         title_color=WHITE, border_color=BLUE)
add_card(slide, Inches(6.8), Inches(2), Inches(5.5), Inches(3), "Альтернативы 2026",
         "Stagehand — для разработчиков (open-source).\nGumloop — no-code платформа для бизнеса.\nBrowser Use — Python для кодеров.\nMake.com / n8n — связка с другими сервисами.",
         title_color=WHITE, border_color=VIOLET)
add_textbox(slide, MARGIN, Inches(5.4), Inches(12), Inches(0.5), "Экономия 90–95% стоимости виртуального ассистента", font_size=14, bold=True, color=GREEN)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 16 — AI-разработка
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.4), Inches(12), Inches(0.6), "AI-разработка без программиста", font_size=32, bold=True, color=WHITE)
dev_tools = [
    ("Lovable", "Генерация веб-приложений и сайтов из текста", "MVP, лендинг, внутренний инструмент", BLUE),
    ("Blink.new", "Создание сайтов с AI-дизайном", "Красивый сайт с нуля за минуты", VIOLET),
    ("Bolt.new", "AI-разработка на Next.js / React", "Настоящий код под капотом (можно доработать)", GREEN),
    ("Hercules.app", "Внутренние бизнес-приложения", "CRM, дашборды, формы без IT-отдела", ORANGE),
]
for i, (name, what, why, color) in enumerate(dev_tools):
    x = MARGIN + i * Inches(3.1)
    add_card(slide, x, Inches(1.3), Inches(2.9), Inches(2.3), name, f"{what}\n\n→ {why}", title_color=color)
add_textbox(slide, MARGIN, Inches(4), Inches(12), Inches(0.8),
            "Принцип: «Сделай сайт для приёма заявок с полями имя, телефон, выбор услуги и отправкой в Telegram» — платформа генерирует работающий сайт. Не нужно уметь кодить.",
            font_size=13, color=GRAY)
add_textbox(slide, MARGIN, Inches(4.8), Inches(12), Inches(0.4),
            "Для бизнеса: прототипы за часы, внутренние инструменты без IT, экономия на фрилансерах.",
            font_size=12, bold=True, color=WHITE)

# ═══════════════════════════════════════════════════════════════
# СЛАЙДЫ 17–24 — Отделы (по 1 слайду на отдел)
# ═══════════════════════════════════════════════════════════════
departments = [
    {
        "name": "БУХГАЛТЕРИЯ",
        "subtitle": "Распознавание, сверка, проверка",
        "color": GREEN,
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
        "color": BLUE,
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
        "color": VIOLET,
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
        "color": ORANGE,
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
        "color": PINK,
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
        "color": AMBER,
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
        "color": CYAN,
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
        "color": GREEN,
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

for dept in departments:
    slide = prs.slides.add_slide(blank_layout)
    add_bg(slide)
    color = dept["color"]
    # Название отдела
    add_textbox(slide, MARGIN, Inches(0.35), Inches(10), Inches(0.6), dept["name"], font_size=36, bold=True, color=WHITE)
    add_textbox(slide, MARGIN, Inches(0.95), Inches(10), Inches(0.3), dept["subtitle"], font_size=13, color=color)
    # Цветная полоса
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, MARGIN, Inches(1.2), Inches(1.5), Inches(0.05))
    bar.fill.solid(); bar.fill.fore_color.rgb = color; bar.line.fill.background()
    
    # ЛЕВАЯ КОЛОНКА: Что может ИИ
    add_textbox(slide, MARGIN, Inches(1.4), Inches(3.8), Inches(0.3), "ЧТО МОЖЕТ ИИ", font_size=10, bold=True, color=color)
    y = Inches(1.7)
    for task in dept["tasks"]:
        add_textbox(slide, MARGIN + Inches(0.15), y, Inches(3.6), Inches(0.35), f"• {task}", font_size=9.5, color=WHITE)
        y += Inches(0.32)
    
    # СРЕДНЯЯ КОЛОНКА: Какую ИИ использовать
    add_textbox(slide, Inches(4.5), Inches(1.4), Inches(4), Inches(0.3), "КАКУЮ ИИ ИСПОЛЬЗОВАТЬ", font_size=10, bold=True, color=color)
    # Платная
    add_textbox(slide, Inches(4.65), Inches(1.7), Inches(3.8), Inches(0.25), "ПЛАТНАЯ:", font_size=9, bold=True, color=GREEN)
    add_textbox(slide, Inches(4.65), Inches(1.95), Inches(3.8), Inches(0.6), dept["paid"], font_size=9, color=GRAY)
    # Бесплатная
    add_textbox(slide, Inches(4.65), Inches(2.65), Inches(3.8), Inches(0.25), "БЕСПЛАТНАЯ:", font_size=9, bold=True, color=GREEN)
    add_textbox(slide, Inches(4.65), Inches(2.9), Inches(3.8), Inches(0.6), dept["free"], font_size=9, color=GRAY)
    
    # ПРАВАЯ КОЛОНКА: Примеры промптов
    add_textbox(slide, Inches(8.8), Inches(1.4), Inches(4.2), Inches(0.3), "ПРИМЕРЫ ПРОМПТОВ", font_size=10, bold=True, color=color)
    y = Inches(1.7)
    for i, prompt in enumerate(dept["prompts"]):
        # Номер
        add_textbox(slide, Inches(8.95), y, Inches(0.3), Inches(0.25), str(i+1), font_size=10, bold=True, color=color)
        # Текст промпта в карточке
        add_textbox(slide, Inches(9.25), y, Inches(3.6), Inches(0.8), f'«{prompt}»', font_size=9, color=GRAY)
        y += Inches(1.05)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 25 — Рекомендации
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.4), Inches(12), Inches(0.6), "Рекомендации по работе с ИИ", font_size=32, bold=True, color=WHITE)

recs = [
    ("01", "Если не уверены — обсудите с другой моделью", "Задайте тот же вопрос Claude, GPT и DeepSeek. Если все три говорят одно — можно доверять.", BLUE),
    ("02", "Формулируйте результат, не задачу", "Плохо: «Вот отчёт, сделай что-нибудь». Хорошо: «Выдели 3 тренда и предложи 2 действия».", VIOLET),
    ("03", "Вначале план, потом реализация", "Сначала составьте план и согласуйте. Только потом выполняйте. Экономит время на переделках.", GREEN),
    ("04", "Заставьте ИИ задать вопросы", "«Есть вопросы? Всё ли понятно?» — лучшие результаты даёт диалог, не монолог.", ORANGE),
    ("05", "Разбивайте сложное на шаги", "Не «напиши бизнес-план». Разбейте: структура → рынок → экономика → риски.", PINK),
    ("06", "Давайте контекст", "«Ты финдиректор, готовишь презентацию для совета директоров» — результат в разы точнее.", BLUE),
    ("07", "Проверяйте факты", "ИИ уверенно выдумывает даты и ссылки. Всегда перепроверяйте.", RED),
    ("08", "Системные промпты для рутины", "«Ты аналитик. Каждый CSV → аномалии, топ-3 тренда, рекомендации» — экономит время.", VIOLET),
    ("09", "Конфиденциальность", "Для чувствительных данных — локальные модели (DeepSeek, Qwen) или корпоративные тарифы.", GREEN),
]

for i, (num, title, body, color) in enumerate(recs):
    col = i % 3
    row = i // 3
    x = MARGIN + col * Inches(4.2)
    y = Inches(1.1) + row * Inches(2.1)
    add_textbox(slide, x, y, Inches(0.8), Inches(0.4), num, font_size=24, bold=True, color=color)
    add_textbox(slide, x + Inches(0.9), y, Inches(3), Inches(0.4), title, font_size=12, bold=True, color=WHITE)
    add_textbox(slide, x + Inches(0.9), y + Inches(0.35), Inches(3), Inches(1.4), body, font_size=10, color=GRAY)

add_textbox(slide, MARGIN, Inches(6.5), Inches(12), Inches(0.4),
            "Главное: ИИ — инструмент. Результат зависит от того, насколько точно вы формулируете задачу.",
            font_size=14, bold=True, color=WHITE)

# ─── СОХРАНЕНИЕ ────────────────────────────────────────────────
prs.save('/root/.openclaw/workspace/AI_Presentation_Full.pptx')
print("✅ PowerPoint сохранён: /root/.openclaw/workspace/AI_Presentation_Full.pptx")
print(f"   Слайдов: {len(prs.slides)}")
