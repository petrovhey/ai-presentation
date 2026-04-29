#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PREMIUM LIGHT THEME — High Level Design
Светлая тема, крупная типографика, плотная компоновка, цветные акценты
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ═══════════════════════════════════════════════════════════════
# ЦВЕТА — СВЕТЛАЯ ПРЕМИУМ ТЕМА
# ═══════════════════════════════════════════════════════════════
BG = RGBColor(250, 251, 253)           # почти белый
WHITE = RGBColor(255, 255, 255)
DARK = RGBColor(15, 23, 42)            # slate-900 — основной текст
DARK_MED = RGBColor(51, 65, 85)        # slate-700
GRAY = RGBColor(100, 116, 139)         # slate-500
LIGHT_GRAY = RGBColor(203, 213, 225)   # slate-300

ACCENT_BLUE = RGBColor(37, 99, 235)      # яркий синий
ACCENT_VIOLET = RGBColor(124, 58, 237)   # фиолетовый
ACCENT_PINK = RGBColor(236, 72, 153)     # розовый
ACCENT_GREEN = RGBColor(34, 197, 94)     # зелёный
ACCENT_ORANGE = RGBColor(245, 158, 11)   # оранжевый
ACCENT_RED = RGBColor(239, 68, 68)       # красный
ACCENT_CYAN = RGBColor(6, 182, 212)     # циан
ACCENT_AMBER = RGBColor(251, 191, 36)   # янтарный

# Фон карточек
CARD_BG = RGBColor(241, 245, 249)      # slate-100
CARD_BORDER = RGBColor(226, 232, 240)   # slate-200

# ═══════════════════════════════════════════════════════════════
# РАЗМЕРЫ
# ═══════════════════════════════════════════════════════════════
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
M = Inches(0.45)  # отступ от края

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
blank_layout = prs.slide_layouts[6]

# ═══════════════════════════════════════════════════════════════
# УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════
def add_bg(slide, color=BG):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    spTree = slide.shapes._spTree
    sp = shape._element
    spTree.remove(sp)
    spTree.insert(2, sp)

def add_text(slide, left, top, width, height, text, size=16, bold=False, color=DARK, align=PP_ALIGN.LEFT, font="Calibri"):
    tx = slide.shapes.add_textbox(left, top, width, height)
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font
    p.alignment = align
    return tx

def add_card(slide, left, top, width, height, title, body, accent=ACCENT_BLUE, title_size=15, body_size=13):
    """Карточка с цветным левым бордюром"""
    # Фон
    bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE
    bg.line.color.rgb = CARD_BORDER
    bg.line.width = Pt(1)
    # Цветной бордюр слева
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(0.08), height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = accent
    bar.line.fill.background()
    # Тень (имитация — серый прямоугольник позади)
    shadow = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.03), top + Inches(0.03), width, height)
    shadow.fill.solid()
    shadow.fill.fore_color.rgb = RGBColor(220, 225, 232)
    shadow.line.fill.background()
    spTree = slide.shapes._spTree
    sp = shadow._element
    spTree.remove(sp)
    spTree.insert(3, sp)  # позади фона карточки
    
    # Заголовок
    add_text(slide, left + Inches(0.2), top + Inches(0.12), width - Inches(0.35), Inches(0.4),
             title, size=title_size, bold=True, color=accent)
    # Тело
    add_text(slide, left + Inches(0.2), top + Inches(0.48), width - Inches(0.35), height - Inches(0.6),
             body, size=body_size, color=DARK_MED)

def add_badge(slide, left, top, text, bg_color=ACCENT_GREEN):
    """Цветной бейдж с текстом"""
    # Подложка
    pad = Inches(0.15)
    w = Inches(2.5)
    h = Inches(0.35)
    bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, w, h)
    bg.fill.solid()
    bg.fill.fore_color.rgb = bg_color
    bg.line.fill.background()
    # Текст
    add_text(slide, left + pad, top + Inches(0.04), w - pad*2, Inches(0.25),
             text, size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    return w

def add_colored_bar(slide, left, top, width, height, color):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()

def add_bullet(slide, left, top, width, items, size=13, color=DARK, spacing=Inches(0.28)):
    y = top
    for item in items:
        # Цветная точка
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, y + Inches(0.04), Inches(0.08), Inches(0.08))
        dot.fill.solid()
        dot.fill.fore_color.rgb = ACCENT_BLUE
        dot.line.fill.background()
        # Текст
        add_text(slide, left + Inches(0.15), y, width - Inches(0.2), Inches(0.45),
                 item, size=size, color=color)
        y += spacing

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 1 — ТИТУЛЬНЫЙ
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide, WHITE)

# Градиентные декоративные блоки (имитация через прямоугольники)
for i, (x, y, w, h, c) in enumerate([
    (Inches(9.5), Inches(-1.5), Inches(5), Inches(5), ACCENT_BLUE),
    (Inches(-1.5), Inches(4), Inches(4), Inches(4), ACCENT_VIOLET),
    (Inches(10.5), Inches(5.5), Inches(3), Inches(3), ACCENT_PINK),
]):
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = c
    shape.line.fill.background()
    # Отправляем на задний план
    spTree = slide.shapes._spTree
    sp = shape._element
    spTree.remove(sp)
    spTree.insert(2, sp)

# Главный заголовок
add_text(slide, M, Inches(2.2), Inches(9), Inches(1), 
         "Нейросети и ИИ", size=60, bold=True, color=DARK)
add_text(slide, M, Inches(3.2), Inches(9), Inches(0.6), 
         "как использовать в работе", size=28, color=DARK_MED)

# Подчёркивающая полоса
bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, M, Inches(3.95), Inches(2.5), Inches(0.08))
bar.fill.solid()
bar.fill.fore_color.rgb = ACCENT_BLUE
bar.line.fill.background()

add_text(slide, M, Inches(4.3), Inches(8), Inches(0.4), 
         "Доклад для сотрудников компании  •  2026", size=16, color=GRAY)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 2 — Что такое ИИ
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)

add_text(slide, M, Inches(0.35), Inches(10), Inches(0.7), 
         "Что такое ИИ", size=42, bold=True, color=DARK)
add_text(slide, M, Inches(0.95), Inches(10), Inches(0.4), 
         "Программа, которая учится на данных и делает выводы", size=18, color=DARK_MED)

# Три колонки с цветными акцентами
cols = [
    ("01", "Обучение", "Модель «читает» огромные массивы текста, кода, изображений — и запоминает закономерности. Это как если бы человек прочитал миллионы книг за одну ночь.", ACCENT_BLUE),
    ("02", "Инференс", "При получении запроса модель предсказывает наиболее вероятный ответ, основываясь на том, что выучила. Не думает — считает вероятности.", ACCENT_VIOLET),
    ("03", "Токены", "Текст разбивается на маленькие кусочки. 1 токен ≈ 0.75 слова. Контекстное окно = сколько токенов модель помнит одновременно.", ACCENT_PINK),
]
for i, (num, title, body, color) in enumerate(cols):
    x = M + i * Inches(4.25)
    # Цветной круг с цифрой
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, Inches(1.8), Inches(0.7), Inches(0.7))
    circle.fill.solid()
    circle.fill.fore_color.rgb = color
    circle.line.fill.background()
    add_text(slide, x, Inches(1.92), Inches(0.7), Inches(0.5), num, size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    # Заголовок
    add_text(slide, x + Inches(0.9), Inches(1.85), Inches(3.2), Inches(0.4), title, size=22, bold=True, color=DARK)
    # Текст
    add_text(slide, x, Inches(2.7), Inches(4), Inches(2.2), body, size=15, color=DARK_MED)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 3 — Модальности
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)

add_text(slide, M, Inches(0.35), Inches(10), Inches(0.7), 
         "Модальности", size=42, bold=True, color=DARK)
add_text(slide, M, Inches(0.95), Inches(10), Inches(0.4), 
         "Что модель может воспринимать на вход — для рабочих задач", size=18, color=DARK_MED)

mods = [
    ("Текст", "Письма, документы, анализ, ответы", ACCENT_BLUE),
    ("Код", "Скрипты, баги, ревью, объяснение", ACCENT_VIOLET),
    ("Изображение", "Скриншот → цифры. Фото → аналоги. Скан → текст", ACCENT_PINK),
    ("Аудио", "Записи совещаний → расшифровка. Голосовые → текст", ACCENT_GREEN),
    ("Видео", "Ролики → summary, ключевые моменты", ACCENT_ORANGE),
    ("Документы", "Договоры → риски. Отчёты → тренды. Таблицы → ошибки", ACCENT_BLUE),
    ("Многомодальность", "Скрин + вопрос = анализ. Всё вместе", ACCENT_VIOLET),
]
for i, (title, body, color) in enumerate(mods):
    col = i % 4
    row = i // 4
    x = M + col * Inches(3.2)
    y = Inches(1.6) + row * Inches(2.8)
    add_card(slide, x, y, Inches(3), Inches(2.5), title, body, accent=color, title_size=16, body_size=13)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 4 — Сравнительная таблица
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)

add_text(slide, M, Inches(0.3), Inches(12), Inches(0.7), 
         "Сравнительная таблица моделей", size=38, bold=True, color=DARK)

rows, cols = 9, 11
table = slide.shapes.add_table(rows, cols, M, Inches(1), Inches(12.4), Inches(6)).table

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

accent_colors = [ACCENT_BLUE, ACCENT_VIOLET, ACCENT_PINK, ACCENT_GREEN, ACCENT_ORANGE, ACCENT_CYAN, ACCENT_AMBER, ACCENT_RED]

for i, row_data in enumerate(table_data):
    for j, cell_text in enumerate(row_data):
        cell = table.cell(i, j)
        cell.text = cell_text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(10.5 if i == 0 else 10)
            paragraph.font.bold = (i == 0)
            paragraph.font.color.rgb = WHITE if i == 0 else DARK_MED
            paragraph.alignment = PP_ALIGN.CENTER if j > 1 else PP_ALIGN.LEFT
        if i == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = DARK
        else:
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if i % 2 == 1 else CARD_BG
            # Цветной левый бордюр для первой колонки
            if j == 0:
                # Нельзя сделать границу отдельной ячейки, но можно цвет текста
                for paragraph in cell.text_frame.paragraphs:
                    paragraph.font.color.rgb = accent_colors[i-1]
                    paragraph.font.bold = True

col_widths = [Inches(1.35), Inches(1.25), Inches(0.7), Inches(0.6), Inches(0.6), 
              Inches(0.85), Inches(0.6), Inches(0.6), Inches(0.7), Inches(1.15), Inches(1.05)]
for i, w in enumerate(col_widths):
    table.columns[i].width = w

# ═══════════════════════════════════════════════════════════════
# СЛАЙДЫ 5–12 — Модели
# ═══════════════════════════════════════════════════════════════
models = [
    ("Claude 4.7", "Anthropic", "Лидер Arena #1", ACCENT_BLUE,
     ["Минимум галлюцинаций — скажет «не уверен»",
      "Контекст до 4M токенов (целая книга за раз)",
      "Отлично понимает инструкции. Самый «человечный» стиль"],
     ["Нет видео и аудио. Дорогой API. Нужен VPN",
      "Бесплатно — 45к токенов каждые 3 часа"],
     "Анализ длинных документов и договоров. Написание сложных текстов. Разработка.",
     "$18–30/мес — больше лимитов, ранний доступ"),
    ("GPT-5.4", "OpenAI", "Самая известная модель", ACCENT_VIOLET,
     ["Всё-в-одном: текст, код, картинки, видео, голос",
      "Экосистема: плагины, GPTs, интеграции везде",
      "Голосовой режим. Canvas — совместное редактирование"],
     ["Галлюцинирует чаще, чем Claude. Нужен VPN",
      "Бесплатно 40–80 сообщений/3ч. Дорогой API"],
     "Универсальные задачи. Генерация изображений. Голосовые диалоги.",
     "$20/мес — GPT-5.4 без лимитов, Canvas"),
    ("Gemini 3.1", "Google", "Google-экосистема", ACCENT_PINK,
     ["Многомодальность: текст + картинки + видео + аудио",
      "2M контекст — 1500 страниц. Notebook LM",
      "Интеграция с Docs, Sheets, Drive, Gmail"],
     ["Нужен VPN. Иногда «врёт» увереннее других"],
     "Работа с Google-экосистемой. Анализ видео. Notebook LM.",
     "$20/мес — Gemini 3.1 Pro"),
    ("Perplexity", "Perplexity", "Поисковик с ИИ", ACCENT_GREEN,
     ["Ищет в интернете в реальном времени. Ответы со ссылками",
      "Минимум галлюцинаций (опирается на факты)",
      "Pro Search по документам. Pro API — 3000/сутки"],
     ["Не умеет картинки/видео/аудио. Меньше контекста. VPN",
      "Бесплатно ~20 запросов/час"],
     "Поиск актуальной информации. Фактчекинг. Исследования.",
     "$20/мес — Pro Search, API"),
    ("Grok 4", "xAI", "Доступ к X/Twitter", ACCENT_ORANGE,
     ["DeepSearch — поиск + X/Twitter в реальном времени",
      "Agentic Tasks — модель сама выполняет задачи",
      "Voice Mode. SuperGrok — ранний доступ"],
     ["Нужен VPN. Бесплатно мало токенов (25/2ч)",
      "Менее надёжен для серьёзных задач"],
     "Мониторинг трендов в X/Twitter. Быстрые задачи с агентами.",
     "$30/мес — больше токенов, ранний доступ"),
    ("Kimi 2.6", "Moonshot AI", "Без VPN", ACCENT_CYAN,
     ["Не нужен VPN — работает из России",
      "2M контекст. Agent Swarm — параллельные агенты",
      "Long-Context Inferencing. ~100 запросов/мин"],
     ["Нет видео и аудио. Интерфейс китайский/английский"],
     "Длинные документы. Сложные параллельные задачи. Программирование.",
     "Нет фиксированного — API по расходу"),
    ("DeepSeek V4", "DeepSeek", "Цена/качество #1", ACCENT_AMBER,
     ["Не нужен VPN. API в 20–50 раз дешевле западных",
      "#2 в Arena. MoE: 1.2T параметров, активны 32B",
      "Неограниченный бесплатный чат. DeepThink"],
     ["Нет видео и аудио. Спартанский интерфейс. Цензура"],
     "Разработка и API-интеграции. Сложные расчёты (DeepThink).",
     "API ~$0.25–0.50 за 1M токенов"),
    ("Qwen 3.6", "Alibaba", "Универсальная (без VPN)", ACCENT_RED,
     ["Не нужен VPN. Мультимодальность: всё-в-одном",
      "Agentic Mode + Swarm Mode. QwQ-vision",
      "2.56M контекст. ~120 запросов/мин"],
     ["Интерфейс китайский/английский. Видео/аудио уступает"],
     "Универсальные задачи без VPN. Изображения/видео. Агенты.",
     "Нет фиксированного — API по расходу"),
]

for idx, (name, company, tagline, color, pluses, minuses, purpose, price) in enumerate(models):
    slide = prs.slides.add_slide(blank_layout)
    add_bg(slide)
    
    # Цветная шапка
    header_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(1.3))
    header_bg.fill.solid()
    header_bg.fill.fore_color.rgb = color
    header_bg.line.fill.background()
    spTree = slide.shapes._spTree
    sp = header_bg._element
    spTree.remove(sp)
    spTree.insert(2, sp)
    
    # Название модели на шапке
    add_text(slide, M, Inches(0.25), Inches(8), Inches(0.7), name, size=38, bold=True, color=WHITE)
    add_text(slide, M, Inches(0.75), Inches(8), Inches(0.4), f"{company}  •  {tagline}", size=16, color=WHITE)
    
    # Номер слайда в правом верхнем углу
    add_text(slide, Inches(11.5), Inches(0.35), Inches(1.5), Inches(0.4), f"{idx+5}/25", size=14, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)
    
    # Две колонки: плюсы / минусы
    add_text(slide, M, Inches(1.5), Inches(2), Inches(0.35), "ПЛЮСЫ", size=13, bold=True, color=ACCENT_GREEN)
    y = Inches(1.85)
    for p in pluses:
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, M + Inches(0.1), y + Inches(0.05), Inches(0.1), Inches(0.1))
        dot.fill.solid()
        dot.fill.fore_color.rgb = ACCENT_GREEN
        dot.line.fill.background()
        add_text(slide, M + Inches(0.3), y, Inches(5.5), Inches(0.45), p, size=15, color=DARK)
        y += Inches(0.42)
    
    add_text(slide, Inches(6.5), Inches(1.5), Inches(2), Inches(0.35), "МИНУСЫ", size=13, bold=True, color=ACCENT_RED)
    y = Inches(1.85)
    for m in minuses:
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(6.6), y + Inches(0.05), Inches(0.1), Inches(0.1))
        dot.fill.solid()
        dot.fill.fore_color.rgb = ACCENT_RED
        dot.line.fill.background()
        add_text(slide, Inches(6.8), y, Inches(5.5), Inches(0.45), m, size=15, color=DARK_MED)
        y += Inches(0.42)
    
    # Карточки снизу
    add_card(slide, M, Inches(4.5), Inches(5.8), Inches(1.9), "Для чего использовать", purpose, accent=color, title_size=16, body_size=14)
    add_card(slide, Inches(6.7), Inches(4.5), Inches(5.8), Inches(1.9), "Платный тариф", price, accent=ACCENT_GREEN, title_size=16, body_size=14)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 13 — Фишки моделей
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)

add_text(slide, M, Inches(0.3), Inches(12), Inches(0.7), 
         "Зачем именно эта модель?", size=38, bold=True, color=DARK)

features = [
    ("Claude", "4M контекст + минимум галлюцинаций", "Когда нужна точность на длинных документах", ACCENT_BLUE),
    ("GPT-5.4", "Голос + Canvas + всё-в-одном", "Когда нужен универсальный помощник", ACCENT_VIOLET),
    ("Gemini", "Notebook LM + 2M контекст + Google", "Когда работаешь в Google-экосистеме", ACCENT_PINK),
    ("Perplexity", "Поиск с источниками в реальном времени", "Когда нужны факты, а не домыслы", ACCENT_GREEN),
    ("Grok", "DeepSearch + Agentic Tasks + доступ к X", "Когда нужны тренды и агенты", ACCENT_ORANGE),
    ("Kimi", "Agent Swarm + 2M контекст без VPN", "Когда нет VPN и нужны сложные задачи", ACCENT_CYAN),
    ("DeepSeek", "MoE + дёшевый API + DeepThink", "Когда важна экономия и сложные расчёты", ACCENT_AMBER),
    ("Qwen", "Swarm Mode + Agentic + QwQ-vision", "Когда нужен «всё-в-одном» без VPN", ACCENT_RED),
]

for i, (name, feature, reason, color) in enumerate(features):
    col = i % 2
    row = i // 2
    x = M + col * Inches(6.4)
    y = Inches(1.1) + row * Inches(1.5)
    # Цветная точка
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y + Inches(0.06), Inches(0.18), Inches(0.18))
    dot.fill.solid()
    dot.fill.fore_color.rgb = color
    dot.line.fill.background()
    # Название
    add_text(slide, x + Inches(0.3), y, Inches(2.5), Inches(0.3), name, size=17, bold=True, color=DARK)
    # Описание
    add_text(slide, x + Inches(0.3), y + Inches(0.3), Inches(5.8), Inches(0.3), 
             f"{feature}  →  {reason}", size=13, color=DARK_MED)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 14 — LM Arena
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)

# Цветная шапка
hb = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(1.2))
hb.fill.solid()
hb.fill.fore_color.rgb = ACCENT_BLUE
hb.line.fill.background()
spTree = slide.shapes._spTree
sp = hb._element
spTree.remove(sp)
spTree.insert(2, sp)

add_text(slide, M, Inches(0.25), Inches(10), Inches(0.7), "LM Arena", size=40, bold=True, color=WHITE)
add_text(slide, M, Inches(0.75), Inches(10), Inches(0.4), "Бесплатный способ попробовать любую модель", size=16, color=WHITE)

add_card(slide, M, Inches(1.5), Inches(5.8), Inches(2.4), "Как работает",
         "Вводите вопрос → получаете два ответа от анонимных моделей → голосуете за лучший → узнаёте, кто победил.\n\nРейтинг Elo — объективная таблица лидеров.",
         accent=ACCENT_BLUE, title_size=17, body_size=14)

add_card(slide, Inches(6.7), Inches(1.5), Inches(5.8), Inches(2.4), "Что есть в 2026",
         "Text Arena — текстовые модели.\nVideo Arena — генерация видео.\nImage Arena — картинки.\nМультимодальные сравнения.",
         accent=ACCENT_VIOLET, title_size=17, body_size=14)

add_badge(slide, M, Inches(4.2), "✓  Регистрация бесплатная. Карта не нужна.", ACCENT_GREEN)
add_text(slide, M + Inches(0.1), Inches(4.7), Inches(4), Inches(0.3), "lmarena.ai", size=14, color=GRAY)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 15 — Robomonkey
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)

hb = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(1.2))
hb.fill.solid()
hb.fill.fore_color.rgb = ACCENT_VIOLET
hb.line.fill.background()
spTree = slide.shapes._spTree
sp = hb._element
spTree.remove(sp)
spTree.insert(2, sp)

add_text(slide, M, Inches(0.25), Inches(10), Inches(0.7), "Robomonkey", size=40, bold=True, color=WHITE)
add_text(slide, M, Inches(0.75), Inches(10), Inches(0.4), "Автоматизация процессов без программирования", size=16, color=WHITE)

add_card(slide, M, Inches(1.5), Inches(5.8), Inches(2.8), "Как работает",
         "Описываете задачу текстом → Robomonkey генерирует Chrome-расширение → устанавливаете в браузер → работает само.\n\nСбор данных, парсинг, автозаполнение форм, мониторинг цен.",
         accent=ACCENT_VIOLET, title_size=17, body_size=14)

add_card(slide, Inches(6.7), Inches(1.5), Inches(5.8), Inches(2.8), "Альтернативы 2026",
         "Stagehand — для разработчиков (open-source).\nGumloop — no-code для бизнеса.\nBrowser Use — Python для кодеров.\nMake.com / n8n — связка сервисов.",
         accent=ACCENT_PINK, title_size=17, body_size=14)

add_badge(slide, M, Inches(4.5), "Экономия 90–95% стоимости виртуального ассистента", ACCENT_GREEN)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 16 — AI-разработка
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)

add_text(slide, M, Inches(0.3), Inches(12), Inches(0.7), 
         "AI-разработка без программиста", size=38, bold=True, color=DARK)

dev_tools = [
    ("Lovable", "Генерация веб-приложений и сайтов из текста", "MVP, лендинг, внутренний инструмент", ACCENT_BLUE),
    ("Blink.new", "Создание сайтов с AI-дизайном", "Красивый сайт за минуты", ACCENT_VIOLET),
    ("Bolt.new", "AI-разработка на Next.js / React", "Настоящий код под капотом", ACCENT_GREEN),
    ("Hercules.app", "Внутренние бизнес-приложения", "CRM, дашборды, формы без IT", ACCENT_ORANGE),
]
for i, (name, what, why, color) in enumerate(dev_tools):
    x = M + i * Inches(3.2)
    add_card(slide, x, Inches(1.2), Inches(3), Inches(2.6), name, f"{what}\n\n→ {why}", accent=color, title_size=17, body_size=13)

add_text(slide, M, Inches(4.1), Inches(12), Inches(0.7),
         "Принцип: «Сделай сайт для приёма заявок с полями имя, телефон, выбор услуги и отправкой в Telegram» — платформа генерирует работающий сайт. Не нужно уметь кодить.",
         size=15, color=DARK_MED)
add_badge(slide, M, Inches(4.9), "Для бизнеса: прототипы за часы, внутренние инструменты без IT", ACCENT_BLUE)

# ═══════════════════════════════════════════════════════════════
# ДАННЫЕ ПО ОТДЕЛАМ
# ═══════════════════════════════════════════════════════════════
departments = [
    {
        "name": "БУХГАЛТЕРИЯ",
        "subtitle": "Распознавание, сверка, проверка",
        "color": ACCENT_GREEN,
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
        "color": ACCENT_BLUE,
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
        "color": ACCENT_VIOLET,
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
        "color": ACCENT_ORANGE,
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
        "color": ACCENT_PINK,
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
        "color": ACCENT_AMBER,
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
        "color": ACCENT_CYAN,
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
        "color": ACCENT_GREEN,
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

# ═══════════════════════════════════════════════════════════════
# СЛАЙДЫ ОТДЕЛОВ (17–24)
# ═══════════════════════════════════════════════════════════════
for dept in departments:
    slide = prs.slides.add_slide(blank_layout)
    add_bg(slide)
    color = dept["color"]
    
    # ЦВЕТНАЯ ШАПКА
    hb = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(1.1))
    hb.fill.solid()
    hb.fill.fore_color.rgb = color
    hb.line.fill.background()
    spTree = slide.shapes._spTree
    sp = hb._element
    spTree.remove(sp)
    spTree.insert(2, sp)
    
    # Название отдела
    add_text(slide, M, Inches(0.15), Inches(10), Inches(0.6), dept["name"], size=36, bold=True, color=WHITE)
    add_text(slide, M, Inches(0.65), Inches(10), Inches(0.3), dept["subtitle"], size=14, color=WHITE)
    
    # КОЛОНКА 1 — ЗАДАЧИ (левая, 4.2")
    add_text(slide, M, Inches(1.25), Inches(2), Inches(0.3), "ЗАДАЧИ", size=12, bold=True, color=color)
    y = Inches(1.55)
    for task in dept["tasks"]:
        # Цветной маркер
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, M, y + Inches(0.05), Inches(0.06), Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = color
        bar.line.fill.background()
        # Текст
        add_text(slide, M + Inches(0.12), y, Inches(3.9), Inches(0.5), task, size=12.5, color=DARK)
        y += Inches(0.35)
    
    # КОЛОНКА 2 — ИИ (средняя, 4.2")
    x2 = Inches(4.7)
    add_text(slide, x2, Inches(1.25), Inches(2), Inches(0.3), "КАКУЮ ИИ ИСПОЛЬЗОВАТЬ", size=12, bold=True, color=color)
    
    # Платная карточка
    add_card(slide, x2, Inches(1.55), Inches(4), Inches(1.35), "Платные", dept["paid"], accent=ACCENT_GREEN, title_size=14, body_size=11.5)
    # Бесплатная карточка
    add_card(slide, x2, Inches(3.05), Inches(4), Inches(1.35), "Бесплатные", dept["free"], accent=ACCENT_BLUE, title_size=14, body_size=11.5)
    
    # КОЛОНКА 3 — ПРОМПТЫ (правая, 4.2")
    x3 = Inches(9.1)
    add_text(slide, x3, Inches(1.25), Inches(2), Inches(0.3), "ПРИМЕРЫ ПРОМПТОВ", size=12, bold=True, color=color)
    y = Inches(1.55)
    for i, prompt in enumerate(dept["prompts"]):
        # Номер в кружке
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, x3, y + Inches(0.02), Inches(0.28), Inches(0.28))
        circle.fill.solid()
        circle.fill.fore_color.rgb = color
        circle.line.fill.background()
        add_text(slide, x3, y + Inches(0.04), Inches(0.28), Inches(0.2), str(i+1), size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        # Текст промпта
        add_text(slide, x3 + Inches(0.35), y, Inches(3.7), Inches(0.85), f'«{prompt}»', size=11.5, color=DARK_MED)
        y += Inches(0.95)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 25 — Рекомендации
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)

add_text(slide, M, Inches(0.3), Inches(12), Inches(0.7), 
         "Рекомендации по работе с ИИ", size=38, bold=True, color=DARK)

recs = [
    ("01", "Если не уверены — обсудите с другой моделью", "Задайте тот же вопрос Claude, GPT и DeepSeek. Если все три говорят одно — можно доверять.", ACCENT_BLUE),
    ("02", "Формулируйте результат, не задачу", "Плохо: «Вот отчёт, сделай что-нибудь». Хорошо: «Выдели 3 тренда и предложи 2 действия».", ACCENT_VIOLET),
    ("03", "Вначале план, потом реализация", "Сначала составьте план и согласуйте его. Только потом выполняйте.", ACCENT_GREEN),
    ("04", "Заставьте ИИ задать вопросы", "«Есть вопросы? Всё ли понятно?» — лучшие результаты даёт диалог, не монолог.", ACCENT_ORANGE),
    ("05", "Разбивайте сложное на шаги", "Не «напиши бизнес-план». Разбейте: структура → рынок → экономика → риски.", ACCENT_PINK),
    ("06", "Давайте контекст", "«Ты финдиректор, готовишь презентацию для совета директоров» — результат в разы точнее.", ACCENT_BLUE),
    ("07", "Проверяйте факты", "ИИ уверенно выдумывает даты и ссылки. Всегда перепроверяйте.", ACCENT_RED),
    ("08", "Системные промпты для рутины", "«Ты аналитик. Каждый CSV → аномалии, топ-3 тренда, рекомендации» — экономит время.", ACCENT_VIOLET),
    ("09", "Конфиденциальность", "Для чувствительных данных — локальные модели (DeepSeek, Qwen) или корпоративные тарифы.", ACCENT_GREEN),
]

for i, (num, title, body, color) in enumerate(recs):
    col = i % 3
    row = i // 3
    x = M + col * Inches(4.3)
    y = Inches(1.1) + row * Inches(2.05)
    # Круг с номером
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, Inches(0.45), Inches(0.45))
    circle.fill.solid()
    circle.fill.fore_color.rgb = color
    circle.line.fill.background()
    add_text(slide, x, y + Inches(0.08), Inches(0.45), Inches(0.3), num, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    # Заголовок
    add_text(slide, x + Inches(0.55), y, Inches(3.5), Inches(0.35), title, size=14, bold=True, color=DARK)
    # Текст
    add_text(slide, x + Inches(0.55), y + Inches(0.32), Inches(3.5), Inches(1.2), body, size=12, color=DARK_MED)

add_text(slide, M, Inches(6.6), Inches(12), Inches(0.4),
         "Главное: ИИ — инструмент. Результат зависит от того, насколько точно вы формулируете задачу.",
         size=16, bold=True, color=DARK)

# ─── СОХРАНЕНИЕ ────────────────────────────────────────────────
prs.save('/root/.openclaw/workspace/AI_Presentation_Premium.pptx')
print("✅ PowerPoint сохранён: /root/.openclaw/workspace/AI_Presentation_Premium.pptx")
print(f"   Слайдов: {len(prs.slides)}")
