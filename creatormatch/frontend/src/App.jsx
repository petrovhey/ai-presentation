import { useState, useEffect } from 'react'
import { Routes, Route, Link, useNavigate, useParams } from 'react-router-dom'
import { get, post, patch, isAuth, getUser, logout } from './api.js'

/* ===== LAYOUT ===== */
function Layout({ children }) {
  const user = getUser();
  const nav = useNavigate();
  return (
    <div className="app">
      <nav className="navbar">
        <Link to="/" className="logo"
003e🐵 CreatorHub</Link>
        <div className="nav-links">
          {!isAuth() ? (
            <>
              <Link to="/login">Войти</Link>
              <Link to="/register" className="btn-nav">Регистрация</Link>
            </>
          ) : (
            <>
              <Link to="/dashboard">Dashboard</Link>
              <Link to="/tasks">Задания</Link>
              {user.role === 'seller' && <Link to="/ai">AI</Link>}
              <Link to="/applications">{user.role === 'seller' ? 'Отклики' : 'Мои заявки'}</Link＞
              <Link to="/payments">Баланс</Link＞
              <button onClick={logout} className="btn-link">Выйти</button＞
            </>
          )}
        </div＞
      </nav＞
      <main className="main">{children}</main＞
    </div＞
  );
}

/* ===== LANDING ===== */
function Landing() {
  const [stats, setStats] = useState({ sellers: 0, creators: 0, active_tasks: 0 });
  useEffect(() => {
    fetch('/api/public/stats').then(r => r.json()).then(d => setStats(d.data || {})).catch(() => {});
  }, []);
  return (
    <div className="landing">
      <section className="hero">
        <h1＞UGC-контент на автопилоте</h1＞
        <p＞Наймите креаторов, управляйте кампаниями и масштабируйте продажи через нативный контент — всё в одной платформе.</p＞
        <div className="hero-btns">
          <Link to="/register" className="btn-primary">Начать бесплатно</Link＞
          <Link to="/register?role=creator" className="btn-secondary">Я креатор</Link＞
        </div＞
        <div className="stats-row">
          <div＞<strong＞{stats.sellers}</strong＞<span＞Брендов</span＞</div＞
          <div＞<strong＞{stats.creators}</strong＞<span＞Креаторов</span＞</div＞
          <div＞<strong＞{stats.active_tasks}</strong＞<span＞Активных заданий</span＞</div＞
        </div＞
      </section＞

      <section className="features">
        <h2＞Возможности</h2＞
        <div className="feature-grid">
          <div className="feature-card">
            <div className="feature-icon">🎯</div＞
            <h3＞Публикация заданий</h3＞
            <p＞Создавайте кампании с чёткими требованиями, бюджетом и дедлайнами.</p＞
          </div＞
          <div className="feature-card">
            <div className="feature-icon">🤖</div＞
            <h3＞AI-брифы</h3＞
            <p＞Генерация контент-планов, сценариев и SEO-описаний через OpenRouter.</p＞
          </div＞
          <div className="feature-card">
            <div className="feature-icon">⚡</div＞
            <h3＞Автоматизация</h3＞
            <p＞Модерация контента, выплаты креаторам и аналитика в одном окне.</p＞
          </div＞
          <div className="feature-card">
            <div className="feature-icon">💰</div＞
            <h3＞Прозрачная оплата</h3＞
            <p＞Пополнение через ЮKassa. Выплаты по факту одобренного контента.</p＞
          </div＞
        </div＞
      </section＞

      <section className="pricing">
        <h2＞Тарифы</h2＞
        <div className="pricing-grid">
          <div className="pricing-card">
            <h3＞Стартер</h3＞
            <div className="price">5 000 ₽/мес</div＞
            <ul＞<li＞5 активных заданий</li＞<li＞50 креаторов в базе</li＞<li＞AI-генерация брифов</li＞<li＞Email-уведомления</li＞</ul＞
            <Link to="/register" className="btn-secondary">Выбрать</Link＞
          </div＞
          <div className="pricing-card popular">
            <h3＞Про</h3＞
            <div className="price">15 000 ₽/мес</div＞
            <ul＞<li＞Безлимит заданий</li＞<li＞Безлимит креаторов</li＞<li＞AI-описания товаров</li＞<li＞Приоритетная поддержка</li＞<li＞Аналитика кампаний</li＞</ul＞
            <Link to="/register" className="btn-primary">Выбрать</Link＞
          </div＞
          <div className="pricing-card">
            <h3＞Агентство</h3＞
            <div className="price">50 000 ₽/мес</div＞
            <ul＞<li＞White-label</li＞<li＞API-доступ</li＞<li＞Персональный менеджер</li＞<li＞Custom-интеграции</li＞</ul＞
            <Link to="/register" className="btn-secondary">Связаться</Link＞
          </div＞
        </div＞
      </section＞
    </div＞
  );
}

/* ===== AUTH ===== */
function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ email: '', password: '', name: '', role: 'seller', phone: '', company_name: '', bio: '' });
  const [err, setErr] = useState('');
  const nav = useNavigate();
  const params = new URLSearchParams(window.location.search);
  const defaultRole = params.get('role') || 'seller';

  useEffect(() => setForm(f => ({ ...f, role: defaultRole })), [defaultRole]);

  const submit = async (e) => {
    e.preventDefault(); setErr('');
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const body = isLogin ? { email: form.email, password: form.password } : form;
      const res = await fetch(`/api${endpoint}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      localStorage.setItem('token', data.data.token);
      localStorage.setItem('user', JSON.stringify(data.data.user));
      window.location = '/dashboard';
    } catch (e) { setErr(e.message); }
  };

  return (
    <div className="auth-page">
      <div className="auth-box">
        <h2＞{isLogin ? 'Вход' : 'Регистрация'}</h2＞
        {err && <div className="error">{err}</div＞}
        <form onSubmit={submit}>
          {!isLogin && (
            <>
              <input placeholder="Имя" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
              <select value={form.role} onChange={e => setForm({...form, role: e.target.value})}>
                <option value="seller">Я бренд / селлер</option＞
                <option value="creator">Я креатор</option＞
              </select＞
              {form.role === 'seller' && <input placeholder="Название компании" value={form.company_name} onChange={e => setForm({...form, company_name: e.target.value})} />}
              {form.role === 'creator' && <input placeholder="О себе (кратко)" value={form.bio} onChange={e => setForm({...form, bio: e.target.value})} />}
            </>
          )}
          <input type="email" placeholder="Email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} required />
          <input type="password" placeholder="Пароль" value={form.password} onChange={e => setForm({...form, password: e.target.value})} required minLength={6} />
          <button type="submit" className="btn-primary">{isLogin ? 'Войти' : 'Создать аккаунт'}</button＞
        </form＞
        <p className="toggle-auth">
          {isLogin ? 'Нет аккаунта? ' : 'Уже есть? '}
          <button onClick={() => setIsLogin(!isLogin)} className="link-btn">{isLogin ? 'Регистрация' : 'Вход'}</button＞
        </p＞
      </div＞
    </div＞
  );
}

/* ===== DASHBOARD ===== */
function Dashboard() {
  const user = getUser();
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState({});
  useEffect(() => {
    get('/auth/me').then(d => setProfile(d.profile));
    if (user.role === 'seller') {
      get('/tasks?my=1').then(t => setStats(s => ({ ...s, myTasks: t?.length || 0 })));
      get('/applications').then(a => setStats(s => ({ ...s, applications: a?.length || 0 })));
      get('/payments/stats').then(p => setStats(s => ({ ...s, spent: p?.total_spent || 0 })));
    } else {
      get('/applications').then(a => setStats(s => ({ ...s, myApps: a?.length || 0 })));
      get('/tasks').then(t => setStats(s => ({ ...s, available: t?.length || 0 })));
    }
  }, []);

  return (
    <div＞
      <h1＞Dashboard</h1＞
      <div className="dashboard-grid">
        <div className="dash-card">
          <h3＞{user.role === 'seller' ? 'Баланс' : 'Заработок'}</h3＞
          <div className="dash-number">{profile?.balance || profile?.total_earnings || 0} ₽</div＞
        </div＞
        {user.role === 'seller' ? (
          <>
            <div className="dash-card"><h3＞Мои задания</h3＞<div className="dash-number">{stats.myTasks || 0}</div＞</div＞
            <div className="dash-card"><h3＞Откликов</h3＞<div className="dash-number">{stats.applications || 0}</div＞</div＞
            <div className="dash-card"><h3＞Потрачено</h3＞<div className="dash-number">{stats.spent || 0} ₽</div＞</div＞
          </>
        ) : (
          <>
            <div className="dash-card"><h3＞Мои заявки</h3＞<div className="dash-number">{stats.myApps || 0}</div＞</div＞
            <div className="dash-card"><h3＞Доступно заданий</h3＞<div className="dash-number">{stats.available || 0}</div＞</div＞
            <div className="dash-card"><h3＞Рейтинг</h3＞<div className="dash-number">{profile?.rating || 5.0} ⭐</div＞</div＞
          </>
        )}
      </div＞
    </div＞
  );
}

/* ===== TASKS ===== */
function Tasks() {
  const user = getUser();
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('');
  const nav = useNavigate();

  useEffect(() => {
    get(user.role === 'seller' ? '/tasks?my=1' : '/tasks').then(setTasks).catch(() => setTasks([]));
  }, []);

  const filtered = tasks.filter(t => (t.title + t.product_name).toLowerCase().includes(filter.toLowerCase()));

  return (
    <div＞
      <div className="page-header">
        <h1＞{user.role === 'seller' ? 'Мои задания' : 'Доступные задания'}</h1＞
        {user.role === 'seller' && <button className="btn-primary" onClick={() => nav('/tasks/new')}>+ Новое задание</button＞}
      </div＞
      <input className="search-input" placeholder="Поиск..." value={filter} onChange={e => setFilter(e.target.value)} />
      <div className="task-list">
        {filtered.map(t => (
          <div key={t.id} className="task-card" onClick={() => nav(`/tasks/${t.id}`)}>
            <div className="task-header">
              <span className={`status-badge ${t.status}`}>{t.status}</span＞
              <span className="task-reward">{t.reward_type === 'fixed' ? `${t.reward_amount} ₽` : t.reward_type === 'percent' ? `${t.reward_percent}%` : 'Продукт'}</span＞
            </div＞
            <h3＞{t.title}</h3＞
            <p className="task-meta">{t.product_name} • {t.platform} • {t.content_type}</p＞
            <p className="task-desc">{t.description?.slice(0, 120)}...</p＞
            {user.role === 'seller' && <span className="task-applicants">👥 {t.applicants || 0} откликов</span＞}
          </div＞
        ))}
        {filtered.length === 0 && <div className="empty">Ничего не найдено</div＞}
      </div＞
    </div＞
  );
}

/* ===== TASK DETAIL / CREATE ===== */
function TaskDetail() {
  const { id } = useParams();
  const user = getUser();
  const nav = useNavigate();
  const [task, setTask] = useState(null);
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);

  const isNew = id === 'new';

  useEffect(() => {
    if (isNew) { setLoading(false); return; }
    get(`/tasks/${id}`).then(t => { setTask(t); return get(`/applications?task_id=${id}`); }).then(a => setApps(a || [])).catch(() => {}).finally(() => setLoading(false));
  }, [id]);

  const createTask = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = Object.fromEntries(fd.entries());
    body.reward_amount = body.reward_amount ? parseFloat(body.reward_amount) : null;
    body.reward_percent = body.reward_percent ? parseInt(body.reward_percent) : null;
    body.budget_total = body.budget_total ? parseFloat(body.budget_total) : null;
    body.max_creators = body.max_creators ? parseInt(body.max_creators) : 1;
    try {
      const t = await post('/tasks', body);
      nav(`/tasks/${t.id}`);
    } catch (e) { alert(e.message); }
  };

  const apply = async () => {
    try {
      await post('/applications', { task_id: id, cover_letter: 'Заинтересован в сотрудничестве', proposed_price: task.reward_amount });
      alert('Заявка отправлена');
    } catch (e) { alert(e.message); }
  };

  const reviewApp = async (appId, status) => {
    try {
      await patch(`/applications/${appId}`, { status });
      setApps(apps.map(a => a.id === appId ? { ...a, status } : a));
    } catch (e) { alert(e.message); }
  };

  if (loading) return <div className="empty">Загрузка...</div＞;

  if (isNew) {
    return (
      <div className="task-form">
        <h1＞Новое задание</h1＞
        <form onSubmit={createTask}>
          <input name="title" placeholder="Название задания" required />
          <input name="product_name" placeholder="Название продукта" />
          <input name="product_url" placeholder="Ссылка на продукт" />
          <textarea name="description" placeholder="Описание задачи" rows="4" required />
          <textarea name="requirements" placeholder="Требования к контенту" rows="3" required />
          <select name="content_type" required><option value="video">Видео</option＞<option value="photo">Фото</option＞<option value="story">Сторис</option＞<option value="review">Отзыв</option＞<option value="unboxing">Анбоксинг</option＞</select＞
          <select name="platform" required><option value="tiktok">TikTok</option＞<option value="vk">VK</option＞<option value="youtube">YouTube</option＞<option value="instagram">Instagram</option＞<option value="any">Любая</option＞</select＞
          <select name="reward_type" required><option value="fixed">Фикс</option＞<option value="percent">Процент</option＞<option value="product">Продукт</option＞<option value="mixed">Смешанное</option＞</select＞
          <input name="reward_amount" type="number" placeholder="Сумма вознаграждения (₽)" />
          <input name="budget_total" type="number" placeholder="Общий бюджет кампании (₽)" />
          <input name="max_creators" type="number" placeholder="Макс. креаторов" defaultValue="1" />
          <input name="deadline" type="date" />
          <button type="submit" className="btn-primary">Создать задание</button＞
        </form＞
      </div＞
    );
  }

  if (!task) return <div className="empty">Задание не найдено</div＞;

  return (
    <div className="task-detail">
      <div className="task-detail-header">
        <h1＞{task.title}</h1＞
        <span className={`status-badge ${task.status}`}>{task.status}</span＞
      </div＞
      <div className="task-info">
        <p＞<strong＞Продукт:</strong＞ {task.product_name}</p＞
        <p＞<strong＞Тип:</strong＞ {task.content_type} для {task.platform}</p＞
        <p＞<strong＞Вознаграждение:</strong＞ {task.reward_type === 'fixed' ? `${task.reward_amount} ₽` : `${task.reward_percent}%`}</p＞
        <p＞<strong＞Дедлайн:</strong＞ {task.deadline ? new Date(task.deadline).toLocaleDateString('ru') : 'Не указан'}</p＞
      </div＞
      <div className="task-description">
        <h3＞Описание</h3＞
        <p＞{task.description}</p＞
        <h3＞Требования</h3＞
        <p＞{task.requirements}</p＞
      </div＞

      {user.role === 'creator' && task.status === 'active' && (
        <button className="btn-primary" onClick={apply}>Откликнуться</button＞
      )}

      {user.role === 'seller' && (
        <div className="applications-section">
          <h3＞Отклики ({apps.length})</h3＞
          {apps.map(a => (
            <div key={a.id} className="app-card">
              <div className="app-header">
                <strong＞{a.creator_name || 'Креатор'}</strong＞
                <span className={`status-badge ${a.status}`}>{a.status}</span＞
              </div＞
              <p＞{a.cover_letter}</p＞
              {a.status === 'pending' && (
                <div className="app-actions">
                  <button className="btn-sm btn-primary" onClick={() => reviewApp(a.id, 'approved')}>Одобрить</button＞
                  <button className="btn-sm btn-secondary" onClick={() => reviewApp(a.id, 'rejected')}>Отклонить</button＞
                </div＞
              )}
            </div＞
          ))}
        </div＞
      )}
    </div＞
  );
}

/* ===== APPLICATIONS ===== */
function Applications() {
  const user = getUser();
  const [apps, setApps] = useState([]);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    get('/applications').then(a => setApps(a || [])).catch(() => {});
  }, []);

  const filtered = apps.filter(a => (a.task_title + a.creator_name).toLowerCase().includes(filter.toLowerCase()));

  return (
    <div＞
      <h1＞{user.role === 'seller' ? 'Отклики на мои задания' : 'Мои заявки'}</h1＞
      <input className="search-input" placeholder="Поиск..." value={filter} onChange={e => setFilter(e.target.value)} />
      <div className="app-list">
        {filtered.map(a => (
          <div key={a.id} className="app-card">
            <div className="app-header">
              <strong＞{a.task_title}</strong＞
              <span className={`status-badge ${a.status}`}>{a.status}</span＞
            </div＞
            <p className="app-meta">{user.role === 'seller' ? a.creator_name : a.seller_name} • {new Date(a.created_at).toLocaleDateString('ru')}</p＞
            <p＞{a.cover_letter}</p＞
          </div＞
        ))}
        {filtered.length === 0 && <div className="empty">Нет заявок</div＞}
      </div＞
    </div＞
  );
}

/* ===== AI TOOLS ===== */
function AI() {
  const [mode, setMode] = useState('brief');
  const [input, setInput] = useState({ product_name: '', platform: 'tiktok', content_type: 'video', requirements: '', features: '', target_audience: '' });
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true);
    try {
      const endpoint = mode === 'brief' ? '/ai/generate-brief' : '/ai/generate-description';
      const body = mode === 'brief'
        ? { product_name: input.product_name, platform: input.platform, content_type: input.content_type, requirements: input.requirements }
        : { product_name: input.product_name, features: input.features, target_audience: input.target_audience, platform: input.platform };
      const res = await post(endpoint, body);
      setResult(mode === 'brief' ? res.brief : res.description);
    } catch (e) { setResult('Ошибка: ' + e.message); }
    setLoading(false);
  };

  return (
    <div className="ai-page">
      <h1＞🤖 AI-ассистент</h1＞
      <div className="ai-tabs">
        <button className={mode === 'brief' ? 'active' : ''} onClick={() => setMode('brief')}>Контент-бриф</button＞
        <button className={mode === 'desc' ? 'active' : ''} onClick={() => setMode('desc')}>SEO-описание</button＞
      </div＞
      <div className="ai-form">
        <input placeholder="Название продукта" value={input.product_name} onChange={e => setInput({...input, product_name: e.target.value})} />
        <select value={input.platform} onChange={e => setInput({...input, platform: e.target.value})}>
          <option value="tiktok">TikTok</option＞<option value="vk">VK</option＞<option value="youtube">YouTube</option＞<option value="instagram">Instagram</option＞<option value="ozon">Ozon</option＞<option value="wildberries">Wildberries</option＞
        </select＞
        {mode === 'brief' ? (
          <>
            <select value={input.content_type} onChange={e => setInput({...input, content_type: e.target.value})}>
              <option value="video">Видео</option＞<option value="photo">Фото</option＞<option value="story">Сторис</option＞<option value="review">Отзыв</option＞
            </select＞
            <textarea placeholder="Требования / пожелания" rows="3" value={input.requirements} onChange={e => setInput({...input, requirements: e.target.value})} />
          </>
        ) : (
          <>
            <textarea placeholder="Особенности продукта (через запятую)" rows="2" value={input.features} onChange={e => setInput({...input, features: e.target.value})} />
            <input placeholder="Целевая аудитория" value={input.target_audience} onChange={e => setInput({...input, target_audience: e.target.value})} />
          </>
        )}
        <button className="btn-primary" onClick={generate} disabled={loading}>{loading ? 'Генерация...' : 'Сгенерировать'}</button＞
      </div＞
      {result && (
        <div className="ai-result">
          <pre＞{result}</pre＞
          <button className="btn-secondary" onClick={() => navigator.clipboard.writeText(result)}>📋 Копировать</button＞
        </div＞
      )}
    </div＞
  );
}

/* ===== PAYMENTS ===== */
function Payments() {
  const [amount, setAmount] = useState('');
  const [payments, setPayments] = useState([]);
  const user = getUser();

  useEffect(() => {
    get('/payments').then(setPayments).catch(() => {});
  }, []);

  const deposit = async () => {
    try {
      const res = await post('/payments/deposit', { amount: parseFloat(amount), description: 'Пополнение баланса' });
      if (res.confirmation_url) window.location = res.confirmation_url;
    } catch (e) { alert(e.message); }
  };

  return (
    <div className="payments-page">
      <h1＞💰 Баланс и платежи</h1＞
      {user.role === 'seller' && (
        <div className="deposit-box">
          <h3＞Пополнить баланс</h3＞
          <input type="number" placeholder="Сумма (₽)" value={amount} onChange={e => setAmount(e.target.value)} />
          <button className="btn-primary" onClick={deposit}>Перейти к оплате (ЮKassa)</button＞
        </div＞
      )}
      <h3＞История</h3＞
      <div className="payments-list">
        {payments.map(p => (
          <div key={p.id} className="payment-row">
            <span＞{new Date(p.created_at).toLocaleDateString('ru')}</span＞
            <span className={`type-${p.type}`}>{p.type}</span＞
            <span className={`status-${p.status}`}>{p.status}</span＞
            <span className="amount">{p.amount} ₽</span＞
          </div＞
        ))}
        {payments.length === 0 && <div className="empty">Нет операций</div＞}
      </div＞
    </div＞
  );
}

/* ===== APP ROUTER ===== */
export default function App() {
  return (
    <Routes＞
      <Route path="/" element={<Layout><Landing /></Layout>} />
      <Route path="/login" element={<Layout><Auth /></Layout>} />
      <Route path="/register" element={<Layout><Auth /></Layout>} />
      <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
      <Route path="/tasks" element={<Layout><Tasks /></Layout>} />
      <Route path="/tasks/:id" element={<Layout><TaskDetail /></Layout>} />
      <Route path="/applications" element={<Layout><Applications /></Layout>} />
      <Route path="/ai" element={<Layout><AI /></Layout>} />
      <Route path="/payments" element={<Layout><Payments /></Layout>} />
    </Routes＞
  );
}
