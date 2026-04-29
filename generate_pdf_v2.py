#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fpdf import FPDF

class SlidePDF(FPDF):
    def __init__(self):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.set_auto_page_break(False)
        self.margin = 14
        self.content_w = 297 - 2*self.margin
        self.content_h = 210 - 2*self.margin
        self.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", uni=True)
        self.add_font("DejaVu", "I", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Oblique.ttf", uni=True)
        self.add_font("DejaVu", "BI", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-BoldOblique.ttf", uni=True)
        self.dark = (25, 30, 48)
        self.accent = (59, 130, 246)
        self.accent2 = (139, 92, 246)
        self.text = (51, 65, 85)
        self.light = (148, 163, 184)
        self.white = (255, 255, 255)
        self.card_bg = (248, 250, 252)
        self.green = (16, 185, 129)
        self.orange = (245, 158, 11)
        self.red = (239, 68, 68)

    def new_slide(self, title, subtitle=""):
        self.add_page()
        # Градиент-фон
        self.set_fill_color(250, 251, 253)
        self.rect(0, 0, 297, 210, style='F')
        # Боковая цветная полоса
        self.set_fill_color(*self.accent)
        self.rect(0, 0, 6, 210, style='F')
        # Заголовочная плашка
        self.set_fill_color(*self.dark)
        self.rect(6, 0, 291, 18, style='F')
        # Номер слайда
        self.set_xy(280, 5)
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(*self.white)
        self.cell(10, 8, str(self.page_no()-1), align='R')
        # Текст заголовка
        self.set_xy(self.margin, 4)
        self.set_font("DejaVu", "B", 15)
        self.set_text_color(*self.white)
        self.cell(0, 10, title, ln=1)
        if subtitle:
            self.set_xy(self.margin, 14)
            self.set_font("DejaVu", "", 9)
            self.set_text_color(180, 190, 210)
            self.cell(0, 6, subtitle, ln=1)
        self.set_xy(self.margin, 22)
        self.set_text_color(*self.text)

    def card(self, x, y, w, h, title, body, title_color=None, icon=""):
        # Карточка с тенью
        self.set_fill_color(235, 238, 242)
        self.rounded_rect(x+0.5, y+0.5, w, h, 3, style='F')
        self.set_fill_color(*self.white)
        self.rounded_rect(x, y, w, h, 3, style='F')
        # Цветной левый бордюр
        c = title_color or self.accent
        self.set_fill_color(*c)
        self.rounded_rect(x, y, 1.2, h, 1.2, style='F')
        # Иконка + заголовок
        self.set_xy(x + 4, y + 3)
        self.set_font("DejaVu", "B", 10)
        self.set_text_color(*c)
        self.cell(0, 5, f"{icon}  {title}", ln=1)
        # Тело
        self.set_xy(x + 4, y + 9)
        self.set_font("DejaVu", "", 9)
        self.set_text_color(*self.text)
        self.multi_cell(w - 7, 4.2, body)

    def rounded_rect(self, x, y, w, h, r, style=''):
        """Рисует прямоугольник со скруглёнными углами"""
        self.set_draw_color(*self.white)
        self.set_line_width(0.3)
        # Верхняя линия
        self.line(x+r, y, x+w-r, y)
        # Нижняя линия
        self.line(x+r, y+h, x+w-r, y+h)
        # Левая линия
        self.line(x, y+r, x, y+h-r)
        # Правая линия
        self.line(x+w, y+r, x+w, y+h-r)
        # Углы (упрощённо — прямоугольник)
        self.rect(x, y, w, h, style=style)

    def bullet(self, text, size=10, icon="▸", color=None):
        c = color or self.accent
        self.set_font("DejaVu", "B", size)
        self.set_text_color(*c)
        x = self.get_x()
        self.cell(5, 5, icon, ln=0)
        self.set_font("DejaVu", "", size)
        self.set_text_color(*self.text)
        self.multi_cell(self.content_w - 5, 5, text)
        self.ln(1.5)

    def body_text(self, text, size=10, bold=False, color=None):
        self.set_font("DejaVu", "B" if bold else "", size)
        if color:
            self.set_text_color(*color)
        else:
            self.set_text_color(*self.text)
        self.multi_cell(self.content_w, 5, text)
        self.ln(1)

    def mini_table(self, headers, rows, col_widths=None, font_size=9, header_color=None):
        hc = header_color or self.accent
        if col_widths is None:
            n = len(headers)
            col_widths = [self.content_w / n] * n
        # Заголовки
        self.set_font("DejaVu", "B", font_size)
        self.set_fill_color(*hc)
        self.set_text_color(*self.white)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 6, h, border=0, align='C', fill=True)
        self.ln()
        # Строки
        self.set_font("DejaVu", "", font_size)
        self.set_text_color(*self.text)
        self.set_fill_color(*self.card_bg)
        alt = False
        for row in rows:
            max_h = 6
            for i, cell in enumerate(row):
                lines = self.multi_cell(col_widths[i], 4.8, str(cell), split_only=True, dry_run=True, output="LINES")
                h = len(lines) * 4.8
                if h > max_h: max_h = h
            x_start = self.get_x()
            y_start = self.get_y()
            if alt:
                self.set_fill_color(240, 243, 247)
            else:
                self.set_fill_color(*self.white)
            self.rect(x_start, y_start, sum(col_widths), max_h, style='F')
            for i, cell in enumerate(row):
                self.set_xy(x_start + sum(col_widths[:i]), y_start)
                self.multi_cell(col_widths[i], 4.8, str(cell), border=0, align='L')
            self.set_xy(x_start, y_start + max_h)
            alt = not alt
        self.ln(2)

    def highlight_box(self, text, color=None):
        c = color or self.green
        self.set_fill_color(*c)
        self.set_text_color(*self.white)
        self.set_font("DejaVu", "B", 10)
        h = 7
        w = self.get_string_width(text) + 10
        x = self.get_x()
        y = self.get_y()
        self.rounded_rect(x, y, w, h, 2, style='F')
        self.set_xy(x + 5, y + 1.5)
        self.cell(w - 10, 4, text, align='C')
        self.ln(h + 2)
        self.set_text_color(*self.text)

pdf = SlidePDF()

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 1 — Титульный
# ═══════════════════════════════════════════════════════════════
pdf.add_page()
pdf.set_fill_color(*pdf.dark)
pdf.rect(0, 0, 297, 210, style='F')
# Декоративный круг
pdf.set_fill_color(59, 130, 246)
pdf.ellipse(220, -30, 120, 120, style='F')
pdf.set_fill_color(139, 92, 246)
pdf.ellipse(-40, 120, 100, 100, style='F')
# Заголовок
pdf.set_y(65)
pdf.set_font("DejaVu", "B", 32)
pdf.set_text_color(*pdf.white)
pdf.cell(297, 16, "Нейросети и ИИ", align='C', ln=1)
pdf.set_font("DejaVu", "B", 20)
pdf.set_text_color(180, 190, 210)
pdf.cell(297, 10, "как использовать в работе", align='C', ln=1)
pdf.ln(15)
pdf.set_font("DejaVu", "", 13)
pdf.set_text_color(148, 163, 184)
pdf.cell(297, 8, "Доклад для сотрудников компании", align='C', ln=1)
pdf.set_font("DejaVu", "B", 13)
pdf.set_text_color(*pdf.accent)
pdf.cell(297, 8, "2026", align='C', ln=1)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 2 — Что такое ИИ
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("2. Что такое ИИ", "Как работает и что может воспринимать")
pdf.body_text("Искусственный интеллект — программа, которая учится на данных и делает выводы, которые раньше требовали человека.", 10.5)
pdf.set_font("DejaVu", "B", 11)
pdf.set_text_color(*pdf.accent)
pdf.cell(0, 6, "Как работает:", ln=1)
pdf.set_text_color(*pdf.text)
pdf.bullet("Обучение — модель «читает» огромные массивы текста/кода/изображений и запоминает закономерности")
pdf.bullet("Инференс — при получении запроса предсказывает наиболее вероятный ответ")
pdf.bullet("Токены — текст разбивается на маленькие кусочки. 1 токен ≈ 0.75 слова")
pdf.ln(1)
pdf.set_font("DejaVu", "B", 11)
pdf.set_text_color(*pdf.accent2)
pdf.cell(0, 6, "Модальности — что модель может воспринимать на вход:", ln=1)
pdf.set_text_color(*pdf.text)
# Карточки модальностей в 2 колонки
modalities = [
    ("📝 Текст", "Написать письмо, проанализировать документ, ответить на вопрос", pdf.accent),
    ("💻 Код", "Написать скрипт, исправить баг, объяснить чужой код", pdf.accent2),
    ("🖼 Изображение", "Скриншот → прочитать цифры. Фото товара → найти аналоги. Скан → извлечь текст", pdf.green),
    ("🎙 Аудио", "Запись совещания → расшифровка и action items. Голосовое → в текст", pdf.orange),
    ("🎬 Видео", "Ролик → расшифровка, ключевые моменты, summary", pdf.red),
    ("📄 Документы", "Договор → найти риски. Отчёт → тренды. Таблица → ошибки", pdf.accent),
    ("🔀 Многомодальность", "Скинуть скриншот «почему упали продажи?» → модель увидит график и даст анализ", pdf.accent2),
]
start_y = pdf.get_y()
for i, (title, body, color) in enumerate(modalities):
    col = i % 2
    row = i // 2
    x = pdf.margin + col * 135
    y = start_y + row * 20
    pdf.card(x, y, 130, 18, title, body, title_color=color, icon="")
pdf.set_y(start_y + 4*20 + 5)
pdf.body_text("Ключевое: модель не «думает» — она статистически предсказывает. Чётко формулируйте задачу и проверяйте результат.", 9.5, bold=True, color=pdf.red)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 3 — Сравнительная таблица
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("3. Сравнительная таблица моделей", "Claude, GPT, Gemini, Perplexity, Grok, Kimi, DeepSeek, Qwen")
headers = ["Модель", "Разраб.", "VPN", "Текст", "Код", "Картинки", "Аудио", "Видео", "Документы", "Беспл. лимит", "Платный тариф"]
rows = [
    ["Claude 4.7", "Anthropic", "Да", "✓", "✓", "✓", "—", "—", "✓", "~45к/3ч", "Pro $18–30"],
    ["GPT-5.4", "OpenAI", "Да", "✓", "✓", "✓", "✓", "✓", "✓", "~40–80/3ч", "Plus $20"],
    ["Gemini 3.1", "Google", "Да", "✓", "✓", "✓", "✓", "✓", "✓", "~60/мин", "Pro $20"],
    ["Perplexity", "Perplexity", "Да", "✓", "✓", "—", "—", "—", "✓", "~20/ч", "Pro $20"],
    ["Grok 4", "xAI", "Да", "✓", "✓", "✓", "✓", "✓", "✓", "~25/2ч", "SuperGrok $30"],
    ["Kimi 2.6", "Moonshot", "Нет", "✓", "✓", "✓", "—", "—", "✓", "~100/мин", "API по расходу"],
    ["DeepSeek V4", "DeepSeek", "Нет", "✓", "✓", "✓", "—", "—", "✓", "Неогранич.", "API дёшево"],
    ["Qwen 3.6", "Alibaba", "Нет", "✓", "✓", "✓", "✓", "✓", "✓", "~120/мин", "API по расходу"],
]
w = [30, 30, 20, 18, 18, 22, 18, 18, 22, 38, 40]
pdf.mini_table(headers, rows, col_widths=w, font_size=8.5, header_color=pdf.dark)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 4 — Claude
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("4. Claude 4.7 (Anthropic)", "Лидер Arena #1 по тексту")
pdf.bullet("Минимум галлюцинаций — если не знает, скажет «не уверен»", icon="✅", color=pdf.green)
pdf.bullet("Огромный контекст — до 4M токенов (можно скормить целую книгу)", icon="📚", color=pdf.accent)
pdf.bullet("Отлично понимает инструкции и форматы. Самый «человечный» стиль", icon="🎯", color=pdf.accent2)
pdf.ln(2)
pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(*pdf.red)
pdf.cell(0, 6, "Минусы:", ln=1)
pdf.set_text_color(*pdf.text)
pdf.bullet("Нет видео и аудио на входе. Дорогой API. Нужен VPN", icon="⚠️", color=pdf.orange)
pdf.bullet("Бесплатно — 45 тыс токенов каждые 3 часа (хватает на 1–2 больших задачи)", icon="⚠️", color=pdf.orange)
pdf.ln(2)
pdf.card(pdf.margin, pdf.get_y(), 130, 18, "Для чего", "Анализ длинных документов и договоров. Написание сложных текстов. Разработка. Задачи, где важна точность и не нужна «выдумка».", pdf.accent, "🎯")
pdf.card(pdf.margin + 140, pdf.get_y() - 18, 130, 18, "Платный тариф", "Pro $18–30/мес — больше лимитов, ранний доступ к новым моделям, приоритет при загрузке.", pdf.green, "💰")

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 5 — GPT
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("5. GPT-5.4 / ChatGPT (OpenAI)", "Самая известная модель в мире")
pdf.bullet("Универсальность: текст, код, картинки, видео, голос — всё в одном", icon="✅", color=pdf.green)
pdf.bullet("Огромная экосистема: плагины, GPTs, интеграции везде", icon="🌐", color=pdf.accent)
pdf.bullet("Голосовой режим — разговаривайте как с человеком. Canvas — совместное редактирование", icon="🎙", color=pdf.accent2)
pdf.ln(2)
pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(*pdf.red)
pdf.cell(0, 6, "Минусы:", ln=1)
pdf.set_text_color(*pdf.text)
pdf.bullet("Галлюцинирует чаще, чем Claude. Нужен VPN", icon="⚠️", color=pdf.orange)
pdf.bullet("Бесплатно ограниченно (40–80 сообщений/3ч). Дорогой API", icon="⚠️", color=pdf.orange)
pdf.ln(2)
pdf.card(pdf.margin, pdf.get_y(), 130, 18, "Для чего", "Универсальные задачи: от письма до кода. Генерация изображений. Голосовые диалоги. Быстрые ответы. Работа с Canvas.", pdf.accent, "🎯")
pdf.card(pdf.margin + 140, pdf.get_y() - 18, 130, 18, "Платный тариф", "Plus $20/мес — GPT-5.4 без лимитов, Canvas, приоритетный доступ, DALL-E.", pdf.green, "💰")

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 6 — Gemini
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("6. Gemini 3.1 (Google)", "Тесная интеграция с Google-экосистемой")
pdf.bullet("Многомодальность: текст + картинки + видео + аудио + документы", icon="✅", color=pdf.green)
pdf.bullet("2M контекст — можно скормить 1500 страниц. Notebook LM — аудио-обзоры из документов", icon="📚", color=pdf.accent)
pdf.bullet("Интеграция с Google Docs, Sheets, Drive, Gmail. Дешевле Claude/OpenAI", icon="🔗", color=pdf.accent2)
pdf.ln(2)
pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(*pdf.red)
pdf.cell(0, 6, "Минусы:", ln=1)
pdf.set_text_color(*pdf.text)
pdf.bullet("Нужен VPN. Иногда «врёт» увереннее других", icon="⚠️", color=pdf.orange)
pdf.ln(2)
pdf.card(pdf.margin, pdf.get_y(), 130, 18, "Для чего", "Работа с Google-экосистемой. Анализ видео. Notebook LM. Задачи, где нужен большой контекст.", pdf.accent, "🎯")
pdf.card(pdf.margin + 140, pdf.get_y() - 18, 130, 18, "Платный тариф", "Pro $20/мес — Gemini 3.1 Pro, больше запросов, интеграции, ранний доступ.", pdf.green, "💰")

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 7 — Perplexity
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("7. Perplexity", "Поисковик с ИИ — не чатбот")
pdf.bullet("Ищет в интернете в реальном времени. Каждый ответ — со ссылками на оригинал", icon="✅", color=pdf.green)
pdf.bullet("Минимум галлюцинаций (опирается на факты). Pro Search — поиск по документам", icon="🎯", color=pdf.accent)
pdf.bullet("Pro API — 3000 запросов/сутки. Spaces для организации исследований", icon="🔌", color=pdf.accent2)
pdf.ln(2)
pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(*pdf.red)
pdf.cell(0, 6, "Минусы:", ln=1)
pdf.set_text_color(*pdf.text)
pdf.bullet("Не умеет картинки/видео/аудио на входе. Контекст меньше. Нужен VPN", icon="⚠️", color=pdf.orange)
pdf.bullet("Бесплатно ~20 запросов/час", icon="⚠️", color=pdf.orange)
pdf.ln(2)
pdf.card(pdf.margin, pdf.get_y(), 130, 18, "Для чего", "Поиск актуальной информации. Фактчекинг. Исследования. Работа с внутренними документами.", pdf.accent, "🎯")
pdf.card(pdf.margin + 140, pdf.get_y() - 18, 130, 18, "Платный тариф", "Pro $20/мес — Pro Search, API, больше запросов, приоритет.", pdf.green, "💰")

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 8 — Grok
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("8. Grok 4 (xAI / Илон Маск)", "Доступ к X/Twitter в реальном времени")
pdf.bullet("DeepSearch — поиск по интернету + X/Twitter. Agentic Tasks — модель сама выполняет задачи", icon="✅", color=pdf.green)
pdf.bullet("Мем-режим и неформальный стиль. Voice Mode", icon="🎙", color=pdf.accent)
pdf.bullet("SuperGrok — ранний доступ к экспериментальным фичам", icon="🔬", color=pdf.accent2)
pdf.ln(2)
pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(*pdf.red)
pdf.cell(0, 6, "Минусы:", ln=1)
pdf.set_text_color(*pdf.text)
pdf.bullet("Нужен VPN. Бесплатно мало токенов (25/2ч). Менее надёжен для серьёзных задач", icon="⚠️", color=pdf.orange)
pdf.ln(2)
pdf.card(pdf.margin, pdf.get_y(), 130, 18, "Для чего", "Мониторинг трендов в X/Twitter. Быстрые задачи с агентами. DeepSearch для актуальной инфы.", pdf.accent, "🎯")
pdf.card(pdf.margin + 140, pdf.get_y() - 18, 130, 18, "Платный тариф", "SuperGrok $30/мес — больше токенов, ранний доступ, приоритет, Big Brain Mode.", pdf.green, "💰")

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 9 — Kimi
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("9. Kimi 2.6 (Moonshot AI)", "Лучший выбор без VPN")
pdf.bullet("Не нужен VPN — работает из России напрямую", icon="🌐", color=pdf.green)
pdf.bullet("Огромный контекст — 2M токенов (целая книга за раз)", icon="📚", color=pdf.accent)
pdf.bullet("Agent Swarm — модель запускает несколько агентов параллельно для сложных задач", icon="🤖", color=pdf.accent2)
pdf.bullet("Long-Context Inferencing — уникальная технология. Бесплатно щедро (~100/мин)", icon="⚡", color=pdf.accent)
pdf.ln(2)
pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(*pdf.red)
pdf.cell(0, 6, "Минусы:", ln=1)
pdf.set_text_color(*pdf.text)
pdf.bullet("Нет видео и аудио. Интерфейс на китайском/английском. Меньше интеграций", icon="⚠️", color=pdf.orange)
pdf.ln(2)
pdf.card(pdf.margin, pdf.get_y(), 130, 18, "Для чего", "Работа с длинными документами. Сложные параллельные задачи. Программирование. Когда нет VPN.", pdf.accent, "🎯")
pdf.card(pdf.margin + 140, pdf.get_y() - 18, 130, 18, "Платный тариф", "Нет фиксированного — только API по использованию. Очень доступно.", pdf.green, "💰")

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 10 — DeepSeek
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("10. DeepSeek V4", "Лидер по соотношению цена/качество")
pdf.bullet("Не нужен VPN. Почти бесплатный API — в 20–50 раз дешевле Claude/OpenAI", icon="💰", color=pdf.green)
pdf.bullet("#2 в Arena по тексту. Mixture-of-Experts: 1.2 трлн параметров, активны 32 млрд", icon="🏆", color=pdf.accent)
pdf.bullet("Неограниченный бесплатный чат. DeepThink — режим глубокого рассуждения", icon="🧠", color=pdf.accent2)
pdf.ln(2)
pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(*pdf.red)
pdf.cell(0, 6, "Минусы:", ln=1)
pdf.set_text_color(*pdf.text)
pdf.bullet("Нет видео и аудио. Спартанский интерфейс. Цензура на политические темы", icon="⚠️", color=pdf.orange)
pdf.ln(2)
pdf.card(pdf.margin, pdf.get_y(), 130, 18, "Для чего", "Разработка и API-интеграции (дешево!). Сложные математические задачи (DeepThink). Много запросов за минимальные деньги.", pdf.accent, "🎯")
pdf.card(pdf.margin + 140, pdf.get_y() - 18, 130, 18, "Платный тариф", "API платное, но дёшево: ~$0.25–0.50 за 1M токенов (против $5–15 у западных).", pdf.green, "💰")

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 11 — Qwen
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("11. Qwen 3.6 (Alibaba)", "Самая универсальная китайская модель")
pdf.bullet("Не нужен VPN. Мультимодальность: текст + код + картинки + видео + аудио", icon="🌐", color=pdf.green)
pdf.bullet("Agentic Mode — модель сама выполняет задачи в интернете. Swarm Mode — параллельные агенты", icon="🤖", color=pdf.accent)
pdf.bullet("QwQ-vision — мультимодальное рассуждение. 2.56M контекст. Бесплатно ~120/мин", icon="👁", color=pdf.accent2)
pdf.ln(2)
pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(*pdf.red)
pdf.cell(0, 6, "Минусы:", ln=1)
pdf.set_text_color(*pdf.text)
pdf.bullet("Интерфейс на китайском/английском. Качество видео/аудио уступает западным", icon="⚠️", color=pdf.orange)
pdf.ln(2)
pdf.card(pdf.margin, pdf.get_y(), 130, 18, "Для чего", "Универсальные задачи без VPN. Работа с изображениями/видео. Задачи с агентами.", pdf.accent, "🎯")
pdf.card(pdf.margin + 140, pdf.get_y() - 18, 130, 18, "Платный тариф", "Нет фиксированного — API по использованию. Очень доступно.", pdf.green, "💰")

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 12 — Фишки моделей
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("12. Фишки моделей — зачем именно ей?", "Уникальные возможности каждой модели")
headers = ["Модель", "Уникальная фишка", "Зачем использовать именно её"]
rows = [
    ["Claude", "4M контекст + минимум галлюцинаций", "Когда нужна точность на длинных документах"],
    ["GPT-5.4", "Голос + Canvas + всё-в-одном", "Когда нужен универсальный помощник"],
    ["Gemini", "Notebook LM + 2M контекст + Google", "Когда работаешь в Google-экосистеме"],
    ["Perplexity", "Поиск с источниками в реальном времени", "Когда нужны факты, а не домыслы"],
    ["Grok", "DeepSearch + Agentic Tasks + доступ к X", "Когда нужны тренды и агенты"],
    ["Kimi", "Agent Swarm + 2M контекст без VPN", "Когда нет VPN и нужны сложные задачи"],
    ["DeepSeek", "MoE + дёшевый API + DeepThink", "Когда важна экономия и сложные расчёты"],
    ["Qwen", "Swarm Mode + Agentic + QwQ-vision", "Когда нужен «всё-в-одном» без VPN"],
]
pdf.mini_table(headers, rows, col_widths=[30, 100, 137], font_size=9.5, header_color=pdf.accent)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 13 — LM Arena
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("13. LM Arena — бесплатный способ попробовать", "lmarena.ai")
pdf.body_text("Платформа от UC Berkeley. Модели соревнуются вслепую — вы судите по качеству, не по бренду.", 11)
pdf.ln(2)
pdf.card(pdf.margin, pdf.get_y(), 130, 22, "Как работает", "Вводите вопрос → получаете два ответа от анонимных моделей → голосуете за лучший → узнаёте, кто победил. Рейтинг Elo — объективная таблица лидеров.", pdf.accent, "🥊")
pdf.card(pdf.margin + 140, pdf.get_y() - 22, 130, 22, "Что есть в 2026", "Text Arena — текстовые модели. Video Arena — генерация видео (Veo 3, Sora 2, Kling). Image Arena — картинки. Мультимодальные сравнения.", pdf.accent2, "📊")
pdf.ln(25)
pdf.set_font("DejaVu", "B", 12)
pdf.set_text_color(*pdf.green)
pdf.cell(0, 8, "✅ Регистрация бесплатная. Кредитная карта не нужна.", ln=1)
pdf.set_font("DejaVu", "", 10)
pdf.set_text_color(*pdf.light)
pdf.cell(0, 6, "lmarena.ai", ln=1)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 14 — Robomonkey
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("14. Автоматизация — Robomonkey", "No-code инструмент для браузера")
pdf.body_text("Описываете задачу текстом → Robomonkey генерирует Chrome-расширение → работает само.", 11)
pdf.ln(1)
pdf.bullet("Сбор данных с сайтов (парсинг)", icon="📊", color=pdf.accent)
pdf.bullet("Автозаполнение форм", icon="📝", color=pdf.accent)
pdf.bullet("Мониторинг цен и наличия", icon="💰", color=pdf.accent)
pdf.bullet("Экспорт данных в таблицы", icon="📤", color=pdf.accent)
pdf.ln(2)
pdf.card(pdf.margin, pdf.get_y(), 130, 20, "Альтернативы 2026", "Stagehand — для разработчиков (open-source). Gumloop — no-code платформа для бизнеса. Browser Use — Python для кодеров. Make.com / n8n — связка с другими сервисами.", pdf.accent2, "🔧")
pdf.ln(22)
pdf.set_font("DejaVu", "B", 11)
pdf.set_text_color(*pdf.green)
pdf.cell(0, 7, "💡 Вывод: даже без навыков программирования можно автоматизировать рутину.", ln=1)
pdf.set_text_color(*pdf.text)
pdf.set_font("DejaVu", "", 10)
pdf.cell(0, 6, "Экономия 90–95% стоимости виртуального ассистента.", ln=1)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 15 — AI-разработка
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("15. AI-разработка без программиста", "Lovable, Blink, Bolt, Hercules")
headers = ["Платформа", "Что делает", "Для чего"]
rows = [
    ["Lovable", "Генерация веб-приложений и сайтов из текста", "Быстро создать MVP, лендинг, внутренний инструмент"],
    ["Blink.new", "Создание сайтов с AI-дизайном", "Красивый сайт с нуля за минуты"],
    ["Bolt.new", "AI-разработка на Next.js / React", "Настоящий код под капотом (можно доработать)"],
    ["Hercules.app", "Внутренние бизнес-приложения", "CRM, дашборды, формы без IT-отдела"],
]
pdf.mini_table(headers, rows, col_widths=[35, 110, 122], font_size=9.5, header_color=pdf.accent2)
pdf.ln(3)
pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(*pdf.accent)
pdf.cell(0, 6, "Общий принцип:", ln=1)
pdf.set_text_color(*pdf.text)
pdf.set_font("DejaVu", "", 10)
pdf.multi_cell(pdf.content_w, 5, "«Сделай сайт для приёма заявок с полями имя, телефон, выбор услуги и отправкой в Telegram» — платформа генерирует работающий сайт. Не нужно уметь кодить.")
pdf.ln(2)
pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(*pdf.green)
pdf.cell(0, 6, "Для бизнеса: прототипы за часы, внутренние инструменты без IT, экономия на фрилансерах.", ln=1)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 16 — Задачи по отделам
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("16. Задачи по отделам", "Что ИИ может делать в каждом отделе")
headers = ["Отдел", "Что может делать ИИ", "Примеры"]
rows = [
    ["Бухгалтерия", "Распознавание документов, сверка, проверка проводок", "100 сканов счетов → сводная таблица. Сверка 1С с банковской выпиской"],
    ["Финансы", "Прогнозирование, бюджеты, сценарное моделирование", "3 сценария при росте 10/20/30%. Проверить Excel-модель"],
    ["Юристы", "Анализ договоров, выявление рисков, сравнение редакций", "Договор → неблагоприятные пункты. Сравнить две редакции NDA"],
    ["Продакты", "Анализ отзывов, user stories, исследование конкурентов", "500 отзывов → топ-10 проблем. Написать ТЗ на интеграцию"],
    ["Коммерческий", "Скрипты, КП, анализ воронки, реактивация", "5 писем для реактивации клиентов, не купивших 90 дней"],
    ["Топы", "Стратегия, due diligence, структурирование мыслей", "3 варианта выхода на рынок с рисками и бюджетом"],
    ["Аналитики", "Обработка данных, SQL, визуализация, прогнозирование", "CSV → аномалии. SQL для сложного отчёта"],
    ["HR", "Вакансии, скрининг, планы адаптации", "50 резюме → топ-10. План адаптации на 30 дней"],
]
pdf.mini_table(headers, rows, col_widths=[30, 80, 157], font_size=8.5, header_color=pdf.dark)
pdf.ln(2)
pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(*pdf.red)
pdf.cell(0, 6, "⚠️ Важно: ИИ — ассистент, не замена. Проверяйте финальные решения, особенно в юридических и финансовых вопросах.", ln=1)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 17 — Рекомендации 1–5
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("17. Рекомендации по работе с ИИ", "Часть 1 — подход и методология")
recs1 = [
    ("1. Если не уверены — обсудите с другой моделью", "Не доверяйте одному ответу на критические вопросы. Задайте тот же вопрос Claude, GPT и DeepSeek. Если все три говорят одно — можно доверять.", pdf.accent),
    ("2. Важнее не входные данные, а результат", "Плохой запрос: «Вот отчёт, сделай что-нибудь». Хороший: «Выдели 3 тренда за квартал и предложи 2 действия». Формулируйте результат.", pdf.accent2),
    ("3. Вначале план, потом реализация", "Сначала попросите составить план и согласуйте его. Только потом выполнять. Экономит время на переделках.", pdf.green),
    ("4. Заставьте ИИ задать уточняющие вопросы", "«Есть вопросы? Всё ли понятно?» — лучшие результаты даёт диалог, не монолог.", pdf.orange),
    ("5. Разбивайте сложное на шаги", "Не «напиши бизнес-план». Разбейте: 1) структура, 2) рынок, 3) экономика, 4) риски. Каждый шаг отдельно.", pdf.accent),
]
start_y = pdf.get_y()
for i, (title, body, color) in enumerate(recs1):
    col = i % 2
    row = i // 2
    x = pdf.margin + col * 135
    y = start_y + row * 32
    pdf.card(x, y, 130, 30, title, body, title_color=color, icon="")
pdf.set_y(start_y + 3*32 + 5)

# ═══════════════════════════════════════════════════════════════
# СЛАЙД 18 — Рекомендации 6–9
# ═══════════════════════════════════════════════════════════════
pdf.new_slide("18. Рекомендации по работе с ИИ", "Часть 2 — качество и безопасность")
recs2 = [
    ("6. Давайте контекст", "«Ты финансовый директор, готовишь презентацию для совета директоров. Объясни, почему кассовый разрыв вырос на 20%» — результат в разы точнее.", pdf.accent),
    ("7. Проверяйте факты", "ИИ уверенно выдумывает даты, ссылки и данные. Всегда перепроверяйте фактчекингом или поиском.", pdf.red),
    ("8. Системные промпты для рутины", "«Ты аналитик. Каждый раз, когда я кидаю CSV, выделяй: аномалии, топ-3 тренда, рекомендации» — экономит время.", pdf.accent2),
    ("9. Конфиденциальность", "Для чувствительных данных используйте локальные модели (DeepSeek, Qwen) или корпоративные тарифы с гарантиями неиспользования данных для обучения.", pdf.green),
]
start_y = pdf.get_y()
for i, (title, body, color) in enumerate(recs2):
    col = i % 2
    row = i // 2
    x = pdf.margin + col * 135
    y = start_y + row * 38
    pdf.card(x, y, 130, 36, title, body, title_color=color, icon="")
pdf.set_y(start_y + 2*38 + 5)
pdf.set_font("DejaVu", "B", 12)
pdf.set_text_color(*pdf.accent)
pdf.cell(0, 8, "🎯 Главное: ИИ — инструмент. Результат зависит от того, насколько точно вы формулируете задачу.", ln=1)

pdf.output("/root/.openclaw/workspace/AI_Presentation_v2.pdf")
print("✅ PDF сохранён: /root/.openclaw/workspace/AI_Presentation_v2.pdf")
