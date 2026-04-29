# CreatorHub — SaaS-платформа для UGC-контента

**Бизнес-модель:** Маркетплейс для селлеров и контент-креаторов. Селлеры публикуют задания, креаторы выполняют, платформа берёт комиссию / подписку.

**Целевая выручка:** 500 000 ₽/мес = 50–100 клиентов на тарифе 5 000–15 000 ₽/мес.

---

## Архитектура

| Компонент | Технология |
|-----------|------------|
| Frontend | React + Vite + vanilla CSS (тёмная тема) |
| Backend | Node.js + Express |
| Database | PostgreSQL 15 |
| AI | OpenRouter API (GPT-4o-mini и др.) |
| Payments | ЮKassa (Яндекс.Касса) |
| Reverse Proxy | Nginx (внутри frontend-контейнера) |
| Orchestration | Docker Compose |

---

## Быстрый старт

### 1. Требования
- Docker + Docker Compose
- Домен + HTTPS (для production)
- Аккаунт ЮKassa (для приёма платежей)
- OpenRouter API Key (для AI-генерации)

### 2. Настройка

```bash
# 1. Клонируй / распакуй проект
cd creatormatch

# 2. Скопируй env
mv .env.example .env

# 3. Заполни .env
nano .env
# DB_PASSWORD=your-secure-password
# JWT_SECRET=$(openssl rand -base64 32)
# YOOKASSA_SHOP_ID=your-shop-id
# YOOKASSA_SECRET_KEY=your-secret-key
# OPENROUTER_API_KEY=sk-or-v1-your-key

# 4. Запусти
docker compose up --build -d

# 5. Создай первого селлера через регистрацию
# Админ уже есть: admin@creatormatch.ru / admin123
```

### 3. Доступ
- **Сайт:** http://localhost (или твой домен)
- **API:** http://localhost:3000/api
- **Админ:** логин `admin@creatormatch.ru`, пароль `admin123`

---

## Бизнес-модель и ценообразование

### Тарифы для селлеров

| Тариф | Цена | Задания | Креаторы | AI | Аналитика |
|-------|------|---------|----------|----|-----------|
| **Стартер** | 5 000 ₽/мес | 5 активных | 50 | Брифы | Базовая |
| **Про** | 15 000 ₽/мес | Безлимит | Безлимит | Брифы + описания | Полная |
| **Агентство** | 50 000 ₽/мес | Безлимит | Безлимит | Всё + API | White-label |

### Для креаторов
- Регистрация бесплатная
- Выплаты за выполненные задания
- Комиссия платформы: 10% (настраивается)

### Как достичь 500к/мес
- 40 селлеров на тарифе «Про» = 600 000 ₽
- Или: 80 селлеров на «Стартер» + 10 на «Про» = 550 000 ₽
- Или: 30 «Про» + 20 «Стартер» + комиссия с креаторов (~50к) = 550 000 ₽

---

## Структура проекта

```
creatormatch/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── package.json
│   ├── init.sql          -- Схема БД + default admin
│   └── server.js         -- Express API (~600 строк)
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── nginx.conf
│   └── src/
│       ├── main.jsx
│       ├── App.jsx       -- Router + все страницы
│       ├── api.js        -- Fetch helper
│       └── styles.css    -- Тёмная тема
```

---

## API Endpoints

### Auth
- `POST /api/auth/register` — регистрация (seller/creator)
- `POST /api/auth/login` — вход
- `GET /api/auth/me` — текущий пользователь

### Tasks
- `GET /api/tasks` — список заданий
- `POST /api/tasks` — создать задание (seller)
- `GET /api/tasks/:id` — детали задания
- `PATCH /api/tasks/:id` — обновить задание

### Applications
- `POST /api/applications` — откликнуться (creator)
- `GET /api/applications` — мои заявки / отклики
- `PATCH /api/applications/:id` — одобрить/отклонить

### Submissions
- `POST /api/submissions` — загрузить контент
- `PATCH /api/submissions/:id` — модерация

### Payments (ЮKassa)
- `POST /api/payments/deposit` — создать платёж
- `POST /api/payments/webhook` — webhook от ЮKassa
- `GET /api/payments` — история

### AI (OpenRouter)
- `POST /api/ai/generate-brief` — AI-бриф для креатора
- `POST /api/ai/generate-description` — SEO-описание товара

### Admin
- `GET /api/admin/users`
- `GET /api/admin/stats`

---

## Подключение ЮKassa

1. Регистрация: https://yookassa.ru
2. Получи `shopId` и `secretKey` в личном кабинете
3. Укажи в `.env`
4. Настрой webhook URL: `https://your-domain.com/api/payments/webhook`
5. Для тестов используй тестовые карты ЮKassa

---

## Деплой на VPS

```bash
# 1. На сервере
git clone <repo> /opt/creatormatch
cd /opt/creatormatch

# 2. Настрой .env и запусти
docker compose up --build -d

# 3. Nginx / Caddy для HTTPS (рекомендуется Caddy)
# Caddyfile:
# your-domain.com {
#     reverse_proxy localhost:80
# }
```

---

## Что дальше (дорожная карта)

### MVP (сейчас)
- ✅ Регистрация, задания, отклики, модерация
- ✅ AI-брифы и SEO-описания
- ✅ ЮKassa пополнение
- ✅ Админ-панель

### v1.1 (2 недели)
- Подписки и тарифы (автоматическое списание)
- Email-уведомления (SendGrid / UniSender)
- Верификация креаторов

### v1.2 (1 месяц)
- Автоматические выплаты креаторам
- Интеграция Ozon API (отслеживание продаж по UGC)
- Интеграция Wildberries API
- White-label для агентств

### v2.0
- Мобильное приложение
- Маркетплейс готовых креаторов (портфолио)
- A/B тестирование карточек товаров
- Видео-редактор в браузере

---

## Лицензия
MIT — делай что хочешь, это твой бизнес.

**Контакты:** Саша → CreatorHub → 500к/мес ❤️‍🔥
