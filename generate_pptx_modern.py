#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Современная презентация в PowerPoint
Темный фон, яркие акценты, минимализм
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import nsmap
from pptx.oxml import parse_xml

# ─── ЦВЕТА ─────────────────────────────────────────────────────
BG = RGBColor(15, 23, 42)         # slate-900
CARD = RGBColor(30, 41, 59)       # slate-800
BLUE = RGBColor(59, 130, 246)     # blue-500
VIOLET = RGBColor(139, 92, 246)   # violet-500
PINK = RGBColor(236, 72, 153)     # pink-500
GREEN = RGBColor(16, 185, 129)    # emerald-500
ORANGE = RGBColor(245, 158, 11)   # amber-500
RED = RGBColor(239, 68, 68)       # red-500
WHITE = RGBColor(248, 250, 252)   # slate-50
GRAY = RGBColor(148, 163, 184)    # slate-400
DARK_GRAY = RGBColor(71, 85, 105) # slate-600

# ─── РАЗМЕРЫ ─────────────────────────────────────────────────
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MARGIN = Inches(0.6)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
blank_layout = prs.slide_layouts[6]  # Blank

def add_bg(slide, color=BG):
    """Темный фон слайда"""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    # Отправляем на задний план
    spTree = slide.shapes._spTree
    sp = shape._element
    spTree.remove(sp)
    spTree.insert(2, sp)

def add_textbox(slide, left, top, width, height, text, font_size=14, 
                bold=False, color=WHITE, align=PP_ALIGN.LEFT, font_name="Calibri"):
    """Добавить текстовый блок"""
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
             title_color=BLUE, border_color=None, icon=""):
    """Карточка с заголовком и текстом"""
    # Фон карточки
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD
    shape.line.color.rgb = border_color or RGBColor(51, 65, 85)
    shape.line.width = Pt(1)
    
    # Заголовок
    title_text = f"{icon} {title}" if icon else title
    title_box = add_textbox(slide, left + Inches(0.15), top + Inches(0.1), 
                            width - Inches(0.3), Inches(0.4), 
                            title_text, font_size=13, bold=True, color=title_color)
    
    # Текст
    add_textbox(slide, left + Inches(0.15), top + Inches(0.45), 
                width - Inches(0.3), height - Inches(0.55), 
                body, font_size=10.5, color=GRAY)

def add_badge(slide, left, top, text, color=GREEN):
    """Цветной бейдж"""
    width = Inches(0.01)  # будет пересчитано
    txBox = slide.shapes.add_textbox(left, top, Inches(2), Inches(0.3))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = WHITE
    # Подложка
    w = txBox.width + Inches(0.2)
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, w, Inches(0.28))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    # Отправляем текст поверх
    spTree = slide.shapes._spTree
    sp = txBox._element
    spTree.remove(sp)
    spTree.append(sp)
    return w

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 1 — ТитульНЫЙ
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)

# Декоративные круги (полупрозрачные)
c1 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9), Inches(-2), Inches(6), Inches(6))
c1.fill.solid()
c1.fill.fore_color.rgb = BLUE
c1.line.fill.background()
c2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-2), Inches(4), Inches(5), Inches(5))
c2.fill.solid()
c2.fill.fore_color.rgb = VIOLET
c2.line.fill.background()

# Градиент полоса
bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(2.8), Inches(3), Inches(0.15))
bar.fill.solid()
bar.fill.fore_color.rgb = BLUE
bar.line.fill.background()

add_textbox(slide, Inches(0.6), Inches(2.5), Inches(10), Inches(1.2),
            "Нейросети и ИИ", font_size=54, bold=True, color=WHITE)
add_textbox(slide, Inches(0.6), Inches(3.5), Inches(10), Inches(0.6),
            "как использовать в работе", font_size=28, color=GRAY)
add_textbox(slide, Inches(0.6), Inches(4.3), Inches(8), Inches(0.4),
            "Доклад для сотрудников компании  •  2026", font_size=14, color=DARK_GRAY)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 2 — Что такое ИИ
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.5), Inches(12), Inches(0.7),
            "Что такое ИИ", font_size=36, bold=True, color=WHITE)
add_textbox(slide, MARGIN, Inches(1.1), Inches(12), Inches(0.4),
            "Программа, которая учится на данных и делает выводы, которые раньше требовали человека",
            font_size=14, color=GRAY)

# Три колонки
cols = [
    ("01", "Обучение", "Модель «читает» огромные массивы текста, кода, изображений — и запоминает закономерности. Это как если бы человек прочитал миллионы книг за одну ночь.", BLUE),
    ("02", "Инференс", "При получении запроса модель предсказывает наиболее вероятный ответ, основываясь на том, что выучила. Не думает — считает вероятности.", VIOLET),
    ("03", "Токены", "Текст разбивается на маленькие кусочки. 1 токен ≈ 0.75 слова. Контекстное окно = сколько токенов модель помнит «в голове» одновременно.", PINK),
]
for i, (num, title, body, color) in enumerate(cols):
    x = MARGIN + i * Inches(4.2)
    # Цифра
    add_textbox(slide, x, Inches(2), Inches(1), Inches(0.6), num, font_size=48, bold=True, color=color)
    # Заголовок
    add_textbox(slide, x, Inches(2.7), Inches(3.8), Inches(0.4), title, font_size=18, bold=True, color=WHITE)
    # Текст
    add_textbox(slide, x, Inches(3.2), Inches(3.6), Inches(2.5), body, font_size=12, color=GRAY)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 3 — Модальности
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.5), Inches(12), Inches(0.7),
            "Модальности", font_size=36, bold=True, color=WHITE)
add_textbox(slide, MARGIN, Inches(1.1), Inches(12), Inches(0.4),
            "Что модель может воспринимать на вход — для рабочих задач",
            font_size=14, color=GRAY)

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
add_textbox(slide, MARGIN, Inches(0.4), Inches(12), Inches(0.6),
            "Сравнительная таблица моделей", font_size=32, bold=True, color=WHITE)

# Таблица через PowerPoint native table
rows, cols = 9, 12
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

# Цвета строк
for i, row_data in enumerate(table_data):
    for j, cell_text in enumerate(row_data):
        cell = table.cell(i, j)
        cell.text = cell_text
        # Форматирование
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(9.5 if i == 0 else 9)
            paragraph.font.bold = (i == 0)
            paragraph.font.color.rgb = WHITE if i == 0 else GRAY
            paragraph.alignment = PP_ALIGN.CENTER if j > 1 else PP_ALIGN.LEFT
        # Фон
        if i == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(51, 65, 85)
        else:
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD if i % 2 == 1 else BG

# Ширины колонок
col_widths = [Inches(1.3), Inches(1.2), Inches(0.7), Inches(0.6), Inches(0.6), 
              Inches(0.9), Inches(0.6), Inches(0.6), Inches(0.7), Inches(1.1), Inches(1.0)]
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
    
    # Название модели (большое)
    add_textbox(slide, MARGIN, Inches(0.4), Inches(8), Inches(0.7),
                name, font_size=40, bold=True, color=WHITE)
    # Компания + теглайн
    add_textbox(slide, MARGIN, Inches(1.1), Inches(8), Inches(0.35),
                f"{company}  •  {tagline}", font_size=13, color=color)
    
    # Цветная полоса под заголовком
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, MARGIN, Inches(1.45), Inches(2), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()
    
    # Плюсы (левая колонка)
    add_textbox(slide, MARGIN, Inches(1.7), Inches(2), Inches(0.3), "ПЛЮСЫ", font_size=10, bold=True, color=GREEN)
    y = Inches(2.0)
    for p in pluses:
        add_textbox(slide, MARGIN + Inches(0.2), y, Inches(5.5), Inches(0.5),
                    f"• {p}", font_size=11, color=WHITE)
        y += Inches(0.4)
    
    # Минусы (правая колонка)
    add_textbox(slide, Inches(6.5), Inches(1.7), Inches(2), Inches(0.3), "МИНУСЫ", font_size=10, bold=True, color=RED)
    y = Inches(2.0)
    for m in minuses:
        add_textbox(slide, Inches(6.7), y, Inches(5.5), Inches(0.5),
                    f"• {m}", font_size=11, color=GRAY)
        y += Inches(0.4)
    
    # Карточки снизу
    add_card(slide, MARGIN, Inches(5.2), Inches(5.8), Inches(1.8), 
             "Для чего", purpose, title_color=WHITE, border_color=color)
    add_card(slide, Inches(6.7), Inches(5.2), Inches(5.8), Inches(1.8), 
             "Тариф", price, title_color=WHITE, border_color=GREEN)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 13 — Фишки моделей
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.4), Inches(12), Inches(0.6),
            "Зачем именно эта модель?", font_size=32, bold=True, color=WHITE)

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
    # Цветная точка
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y + Inches(0.05), Inches(0.15), Inches(0.15))
    dot.fill.solid()
    dot.fill.fore_color.rgb = color
    dot.line.fill.background()
    # Текст
    add_textbox(slide, x + Inches(0.25), y, Inches(2.5), Inches(0.25),
                name, font_size=13, bold=True, color=WHITE)
    add_textbox(slide, x + Inches(0.25), y + Inches(0.25), Inches(5.8), Inches(0.25),
                f"{feature}  →  {reason}", font_size=11, color=GRAY)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 14 — LM Arena
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.5), Inches(12), Inches(0.7),
            "LM Arena", font_size=40, bold=True, color=WHITE)
add_textbox(slide, MARGIN, Inches(1.2), Inches(8), Inches(0.4),
            "Бесплатный способ попробовать любую модель", font_size=16, color=GRAY)

# Центральный блок
add_card(slide, MARGIN, Inches(2), Inches(5.5), Inches(2.5),
         "Как работает",
         "Вы вводите вопрос → получаете два ответа от анонимных моделей → голосуете за лучший → узнаёте, кто победил.\n\nРейтинг Elo — объективная таблица лидеров. Text Arena, Video Arena, Image Arena — сравнение по типам.",
         title_color=WHITE, border_color=BLUE)

add_card(slide, Inches(6.8), Inches(2), Inches(5.5), Inches(2.5),
         "Что есть в 2026",
         "Text Arena — текстовые модели.\nVideo Arena — генерация видео (Veo 3, Sora 2, Kling).\nImage Arena — картинки.\nМультимодальные сравнения.",
         title_color=WHITE, border_color=VIOLET)

add_textbox(slide, MARGIN, Inches(5), Inches(12), Inches(0.5),
            "✓  Регистрация бесплатная. Кредитная карта не нужна.", font_size=14, bold=True, color=GREEN)
add_textbox(slide, MARGIN, Inches(5.5), Inches(12), Inches(0.3),
            "lmarena.ai", font_size=12, color=DARK_GRAY)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 15 — Robomonkey
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.5), Inches(12), Inches(0.7),
            "Robomonkey", font_size=40, bold=True, color=WHITE)
add_textbox(slide, MARGIN, Inches(1.2), Inches(8), Inches(0.4),
            "Автоматизация процессов без программирования", font_size=16, color=GRAY)

add_card(slide, MARGIN, Inches(2), Inches(5.5), Inches(3),
         "Как работает",
         "Описываете задачу текстом («собирай цены с Ozon каждый день»).\n\nRobomonkey генерирует Chrome-расширение с кодом.\n\nУстанавливаете в браузер — оно работает само.",
         title_color=WHITE, border_color=BLUE)

add_card(slide, Inches(6.8), Inches(2), Inches(5.5), Inches(3),
         "Альтернативы 2026",
         "Stagehand — для разработчиков (open-source).\nGumloop — no-code платформа для бизнеса.\nBrowser Use — Python для кодеров.\nMake.com / n8n — связка с другими сервисами.",
         title_color=WHITE, border_color=VIOLET)

add_textbox(slide, MARGIN, Inches(5.4), Inches(12), Inches(0.5),
            "Экономия 90–95% стоимости виртуального ассистента", font_size=14, bold=True, color=GREEN)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 16 — AI-разработка
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.4), Inches(12), Inches(0.6),
            "AI-разработка без программиста", font_size=32, bold=True, color=WHITE)

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
# СЛАЙД 17 — Задачи по отделам
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.4), Inches(12), Inches(0.6),
            "Задачи по отделам", font_size=32, bold=True, color=WHITE)

departments = [
    ("Бухгалтерия", "Распознавание документов, сверка, проверка проводок", BLUE),
    ("Финансы", "Прогнозирование, бюджеты, сценарное моделирование", VIOLET),
    ("Юристы", "Анализ договоров, риски, сравнение редакций", GREEN),
    ("Продакты", "Анализ отзывов, user stories, конкуренты", ORANGE),
    ("Коммерческий", "Скрипты, КП, воронка, реактивация", PINK),
    ("Топы", "Стратегия, due diligence, структурирование", BLUE),
    ("Аналитики", "Обработка данных, SQL, визуализация", VIOLET),
    ("HR", "Вакансии, скрининг, планы адаптации", GREEN),
]

for i, (dept, tasks, color) in enumerate(departments):
    col = i % 4
    row = i // 4
    x = MARGIN + col * Inches(3.1)
    y = Inches(1.2) + row * Inches(2.6)
    add_card(slide, x, y, Inches(2.9), Inches(2.3), dept, tasks, title_color=color)

add_textbox(slide, MARGIN, Inches(6.3), Inches(12), Inches(0.4),
            "⚠  ИИ — ассистент, не замена. Проверяйте финальные решения, особенно в юридических и финансовых вопросах.",
            font_size=12, bold=True, color=RED)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 18 — Рекомендации
# ═══════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_bg(slide)
add_textbox(slide, MARGIN, Inches(0.4), Inches(12), Inches(0.6),
            "Рекомендации по работе с ИИ", font_size=32, bold=True, color=WHITE)

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
    # Номер
    add_textbox(slide, x, y, Inches(0.8), Inches(0.4), num, font_size=24, bold=True, color=color)
    # Заголовок
    add_textbox(slide, x + Inches(0.9), y, Inches(3), Inches(0.4), title, font_size=12, bold=True, color=WHITE)
    # Текст
    add_textbox(slide, x + Inches(0.9), y + Inches(0.35), Inches(3), Inches(1.4), body, font_size=10, color=GRAY)

add_textbox(slide, MARGIN, Inches(6.5), Inches(12), Inches(0.4),
            "Главное: ИИ — инструмент. Результат зависит от того, насколько точно вы формулируете задачу.",
            font_size=14, bold=True, color=WHITE)

# ─── СОХРАНЕНИЕ ────────────────────────────────────────────────
prs.save('/root/.openclaw/workspace/AI_Presentation_Modern.pptx')
print("✅ PowerPoint сохранён: /root/.openclaw/workspace/AI_Presentation_Modern.pptx")
print(f"   Слайдов: {len(prs.slides)}")
