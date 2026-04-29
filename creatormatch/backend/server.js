const express = require('express');
const pg = require('pg');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';
const YOOKASSA_SHOP_ID = process.env.YOOKASSA_SHOP_ID || '';
const YOOKASSA_SECRET_KEY = process.env.YOOKASSA_SECRET_KEY || '';
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || '';

// ===== DB =====
const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// ===== MIDDLEWARE =====
app.use(helmet());
app.use(cors({ origin: true, credentials: true }));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

const limiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 200 });
app.use('/api/', limiter);

const authLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 20 });
app.use('/api/auth/', authLimiter);

// ===== AUTH MIDDLEWARE =====
const authenticate = async (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) return res.status(401).json({ error: 'No token' });
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    const user = await pool.query('SELECT * FROM users WHERE id = $1', [decoded.id]);
    if (!user.rows.length || !user.rows[0].is_active) return res.status(401).json({ error: 'User not found' });
    req.user = user.rows[0];
    next();
  } catch { res.status(401).json({ error: 'Invalid token' }); }
};

const requireRole = (...roles) => (req, res, next) => {
  if (!roles.includes(req.user.role)) return res.status(403).json({ error: 'Forbidden' });
  next();
};

// ===== HELPERS =====
const hashPw = async (p) => bcrypt.hash(p, 12);
const checkPw = async (p, h) => bcrypt.compare(p, h);
const signToken = (id) => jwt.sign({ id }, JWT_SECRET, { expiresIn: '7d' });
const ok = (res, data) => res.json({ success: true, data });

// ===== AUTH =====
app.post('/api/auth/register', async (req, res) => {
  const { email, password, name, role, phone, company_name, bio } = req.body;
  if (!email || !password || !name || !role) return res.status(400).json({ error: 'Missing fields' });
  if (!['seller', 'creator'].includes(role)) return res.status(400).json({ error: 'Invalid role' });
  
  try {
    const exists = await pool.query('SELECT 1 FROM users WHERE email = $1', [email]);
    if (exists.rows.length) return res.status(409).json({ error: 'Email exists' });
    
    const hash = await hashPw(password);
    const userRes = await pool.query(
      `INSERT INTO users (email, password_hash, role, name, phone) VALUES ($1,$2,$3,$4,$5) RETURNING *`,
      [email, hash, role, name, phone || null]
    );
    const user = userRes.rows[0];
    
    if (role === 'seller') {
      await pool.query('INSERT INTO seller_profiles (user_id, company_name) VALUES ($1,$2)', [user.id, company_name || name]);
    } else {
      await pool.query('INSERT INTO creator_profiles (user_id, bio) VALUES ($1,$2)', [user.id, bio || null]);
    }
    
    ok(res, { token: signToken(user.id), user: { id: user.id, email, name, role } });
  } catch (e) { console.error(e); res.status(500).json({ error: 'Server error' }); }
});

app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const r = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (!r.rows.length || !await checkPw(password, r.rows[0].password_hash)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    const u = r.rows[0];
    ok(res, { token: signToken(u.id), user: { id: u.id, email: u.email, name: u.name, role: u.role } });
  } catch (e) { res.status(500).json({ error: 'Server error' }); }
});

app.get('/api/auth/me', authenticate, async (req, res) => {
  const u = req.user;
  let profile = null;
  if (u.role === 'seller') {
    const p = await pool.query('SELECT * FROM seller_profiles WHERE user_id = $1', [u.id]);
    profile = p.rows[0];
  } else if (u.role === 'creator') {
    const p = await pool.query('SELECT * FROM creator_profiles WHERE user_id = $1', [u.id]);
    profile = p.rows[0];
  }
  ok(res, { user: { id: u.id, email: u.email, name: u.name, role: u.role, phone: u.phone, avatar_url: u.avatar_url }, profile });
});

// ===== USER =====
app.patch('/api/users/me', authenticate, async (req, res) => {
  const { name, phone, bio, company_name, website, description, social_links, skills } = req.body;
  const u = req.user;
  try {
    if (name || phone) {
      await pool.query('UPDATE users SET name = COALESCE($1, name), phone = COALESCE($2, phone) WHERE id = $3', [name, phone, u.id]);
    }
    if (u.role === 'seller' && (company_name || website || description)) {
      await pool.query(
        'UPDATE seller_profiles SET company_name = COALESCE($1, company_name), website = COALESCE($2, website), description = COALESCE($3, description) WHERE user_id = $4',
        [company_name, website, description, u.id]
      );
    }
    if (u.role === 'creator' && (bio || social_links || skills)) {
      await pool.query(
        'UPDATE creator_profiles SET bio = COALESCE($1, bio), social_links = COALESCE($2, social_links), skills = COALESCE($3, skills) WHERE user_id = $4',
        [bio, JSON.stringify(social_links || []), JSON.stringify(skills || []), u.id]
      );
    }
    ok(res, { message: 'Updated' });
  } catch (e) { res.status(500).json({ error: 'Update failed' }); }
});

// ===== TASKS =====
app.get('/api/tasks', authenticate, async (req, res) => {
  const { status, my } = req.query;
  const u = req.user;
  try {
    let q, params;
    if (u.role === 'seller' && my === '1') {
      q = 'SELECT t.*, (SELECT COUNT(*) FROM applications WHERE task_id = t.id) as applicants FROM tasks t WHERE t.seller_id = $1 ORDER BY t.created_at DESC';
      params = [u.id];
    } else if (u.role === 'creator') {
      q = `SELECT t.*, (SELECT COUNT(*) FROM applications WHERE task_id = t.id AND creator_id = $1) as my_applications 
           FROM tasks t WHERE t.status = 'active' ORDER BY t.created_at DESC`;
      params = [u.id];
    } else {
      q = "SELECT t.*, u.name as seller_name FROM tasks t JOIN users u ON t.seller_id = u.id WHERE t.status = 'active' ORDER BY t.created_at DESC";
      params = [];
    }
    const r = await pool.query(q, params);
    ok(res, r.rows);
  } catch (e) { res.status(500).json({ error: 'Failed' }); }
});

app.get('/api/tasks/:id', authenticate, async (req, res) => {
  try {
    const r = await pool.query('SELECT t.*, u.name as seller_name, u.avatar_url as seller_avatar FROM tasks t JOIN users u ON t.seller_id = u.id WHERE t.id = $1', [req.params.id]);
    if (!r.rows.length) return res.status(404).json({ error: 'Not found' });
    ok(res, r.rows[0]);
  } catch (e) { res.status(500).json({ error: 'Failed' }); }
});

app.post('/api/tasks', authenticate, requireRole('seller'), async (req, res) => {
  const { title, description, product_name, product_url, requirements, content_type, platform, reward_type, reward_amount, reward_percent, budget_total, max_creators, deadline } = req.body;
  if (!title || !description || !requirements || !content_type || !platform || !reward_type) {
    return res.status(400).json({ error: 'Missing fields' });
  }
  try {
    const r = await pool.query(
      `INSERT INTO tasks (seller_id, title, description, product_name, product_url, requirements, content_type, platform, reward_type, reward_amount, reward_percent, budget_total, max_creators, deadline, status)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,'active') RETURNING *`,
      [req.user.id, title, description, product_name, product_url, requirements, content_type, platform, reward_type, reward_amount, reward_percent, budget_total, max_creators, deadline]
    );
    ok(res, r.rows[0]);
  } catch (e) { console.error(e); res.status(500).json({ error: 'Failed' }); }
});

app.patch('/api/tasks/:id', authenticate, requireRole('seller'), async (req, res) => {
  const taskRes = await pool.query('SELECT seller_id FROM tasks WHERE id = $1', [req.params.id]);
  if (!taskRes.rows.length || taskRes.rows[0].seller_id !== req.user.id) return res.status(403).json({ error: 'Not yours' });
  const fields = req.body;
  const allowed = ['title', 'description', 'product_name', 'product_url', 'requirements', 'content_type', 'platform', 'reward_type', 'reward_amount', 'reward_percent', 'budget_total', 'max_creators', 'deadline', 'status'];
  const keys = Object.keys(fields).filter(k => allowed.includes(k));
  if (!keys.length) return res.status(400).json({ error: 'No valid fields' });
  const setClause = keys.map((k, i) => `${k} = $${i + 2}`).join(', ');
  const values = keys.map(k => fields[k]);
  await pool.query(`UPDATE tasks SET ${setClause} WHERE id = $1`, [req.params.id, ...values]);
  ok(res, { message: 'Updated' });
});

// ===== APPLICATIONS =====
app.post('/api/applications', authenticate, requireRole('creator'), async (req, res) => {
  const { task_id, cover_letter, proposed_price } = req.body;
  try {
    const task = await pool.query("SELECT * FROM tasks WHERE id = $1 AND status = 'active'", [task_id]);
    if (!task.rows.length) return res.status(404).json({ error: 'Task not found' });
    
    const existing = await pool.query('SELECT 1 FROM applications WHERE task_id = $1 AND creator_id = $2', [task_id, req.user.id]);
    if (existing.rows.length) return res.status(409).json({ error: 'Already applied' });
    
    const r = await pool.query(
      'INSERT INTO applications (task_id, creator_id, cover_letter, proposed_price) VALUES ($1,$2,$3,$4) RETURNING *',
      [task_id, req.user.id, cover_letter, proposed_price]
    );
    ok(res, r.rows[0]);
  } catch (e) { res.status(500).json({ error: 'Failed' }); }
});

app.get('/api/applications', authenticate, async (req, res) => {
  const u = req.user;
  try {
    let q, params;
    if (u.role === 'creator') {
      q = `SELECT a.*, t.title as task_title, t.reward_type, t.reward_amount, u.name as seller_name 
           FROM applications a JOIN tasks t ON a.task_id = t.id JOIN users u ON t.seller_id = u.id 
           WHERE a.creator_id = $1 ORDER BY a.created_at DESC`;
      params = [u.id];
    } else {
      q = `SELECT a.*, t.title as task_title, u.name as creator_name, u.avatar_url as creator_avatar, p.rating as creator_rating
           FROM applications a JOIN tasks t ON a.task_id = t.id JOIN users u ON a.creator_id = u.id 
           LEFT JOIN creator_profiles p ON p.user_id = a.creator_id
           WHERE t.seller_id = $1 ORDER BY a.created_at DESC`;
      params = [u.id];
    }
    const r = await pool.query(q, params);
    ok(res, r.rows);
  } catch (e) { res.status(500).json({ error: 'Failed' }); }
});

app.patch('/api/applications/:id', authenticate, async (req, res) => {
  const { status, seller_notes } = req.body;
  const u = req.user;
  try {
    const appRes = await pool.query('SELECT a.*, t.seller_id FROM applications a JOIN tasks t ON a.task_id = t.id WHERE a.id = $1', [req.params.id]);
    if (!appRes.rows.length) return res.status(404).json({ error: 'Not found' });
    const app = appRes.rows[0];
    
    if (u.role === 'seller' && app.seller_id !== u.id) return res.status(403).json({ error: 'Not yours' });
    if (u.role === 'creator' && app.creator_id !== u.id && status !== 'submitted') return res.status(403).json({ error: 'Forbidden' });
    
    const updates = [];
    const vals = [req.params.id];
    if (status) { updates.push(`status = $${updates.length + 2}`); vals.push(status); }
    if (seller_notes) { updates.push(`seller_notes = $${updates.length + 2}`); vals.push(seller_notes); }
    if (!updates.length) return res.status(400).json({ error: 'Nothing to update' });
    
    await pool.query(`UPDATE applications SET ${updates.join(', ')} WHERE id = $1`, vals);
    ok(res, { message: 'Updated' });
  } catch (e) { res.status(500).json({ error: 'Failed' }); }
});

// ===== SUBMISSIONS =====
app.post('/api/submissions', authenticate, requireRole('creator'), async (req, res) => {
  const { application_id, content_urls, caption, platform_post_url } = req.body;
  try {
    const app = await pool.query('SELECT * FROM applications WHERE id = $1 AND creator_id = $2', [application_id, req.user.id]);
    if (!app.rows.length) return res.status(403).json({ error: 'Not your application' });
    if (app.rows[0].status !== 'approved' && app.rows[0].status !== 'revision') {
      return res.status(400).json({ error: 'Application not approved' });
    }
    
    const r = await pool.query(
      'INSERT INTO submissions (application_id, content_urls, caption, platform_post_url) VALUES ($1,$2,$3,$4) RETURNING *',
      [application_id, JSON.stringify(content_urls || []), caption, platform_post_url]
    );
    await pool.query("UPDATE applications SET status = 'submitted' WHERE id = $1", [application_id]);
    ok(res, r.rows[0]);
  } catch (e) { res.status(500).json({ error: 'Failed' }); }
});

app.patch('/api/submissions/:id', authenticate, requireRole('seller'), async (req, res) => {
  const { status, admin_notes } = req.body;
  try {
    const sub = await pool.query(
      'SELECT s.*, t.seller_id FROM submissions s JOIN applications a ON s.application_id = a.id JOIN tasks t ON a.task_id = t.id WHERE s.id = $1',
      [req.params.id]
    );
    if (!sub.rows.length || sub.rows[0].seller_id !== req.user.id) return res.status(403).json({ error: 'Not yours' });
    
    await pool.query('UPDATE submissions SET status = $1, admin_notes = $2, reviewed_at = NOW() WHERE id = $3', [status, admin_notes, req.params.id]);
    
    const appId = sub.rows[0].application_id;
    let newAppStatus = 'submitted';
    if (status === 'approved') newAppStatus = 'completed';
    if (status === 'revision_requested') newAppStatus = 'revision';
    if (status === 'rejected') newAppStatus = 'cancelled';
    await pool.query('UPDATE applications SET status = $1 WHERE id = $2', [newAppStatus, appId]);
    
    ok(res, { message: 'Reviewed' });
  } catch (e) { res.status(500).json({ error: 'Failed' }); }
});

// ===== PAYMENTS / YOOKASSA =====
app.post('/api/payments/deposit', authenticate, async (req, res) => {
  const { amount, description } = req.body;
  if (!amount || amount < 100) return res.status(400).json({ error: 'Min 100 RUB' });
  if (!YOOKASSA_SHOP_ID || !YOOKASSA_SECRET_KEY) return res.status(503).json({ error: 'Payments not configured' });
  
  const idempotenceKey = uuidv4();
  try {
    const payment = await fetch('https://api.yookassa.ru/v3/payments', {
      method: 'POST',
      headers: {
        'Authorization': 'Basic ' + Buffer.from(`${YOOKASSA_SHOP_ID}:${YOOKASSA_SECRET_KEY}`).toString('base64'),
        'Idempotence-Key': idempotenceKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        amount: { value: parseFloat(amount).toFixed(2), currency: 'RUB' },
        capture: true,
        confirmation: { type: 'redirect', return_url: `${req.headers.origin || 'https://localhost'}/dashboard/payments` },
        description: description || `Deposit ${amount} RUB`,
        metadata: { user_id: req.user.id, type: 'deposit' }
      })
    });
    const data = await payment.json();
    if (!payment.ok) return res.status(502).json({ error: data.description || 'Payment error' });
    
    await pool.query(
      'INSERT INTO payments (user_id, type, amount, status, yookassa_payment_id, yookassa_status, description, metadata) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)',
      [req.user.id, 'deposit', amount, 'pending', data.id, data.status, description || 'Deposit', JSON.stringify({ return_url: data.confirmation?.confirmation_url })]
    );
    
    ok(res, { confirmation_url: data.confirmation?.confirmation_url, payment_id: data.id });
  } catch (e) { console.error(e); res.status(500).json({ error: 'Payment failed' }); }
});

app.post('/api/payments/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  try {
    const body = JSON.parse(req.body);
    const paymentId = body.object?.id;
    const status = body.object?.status;
    if (!paymentId) return res.status(400).send('Bad request');
    
    const local = await pool.query('SELECT * FROM payments WHERE yookassa_payment_id = $1', [paymentId]);
    if (!local.rows.length) return res.status(404).send('Not found');
    const p = local.rows[0];
    
    if (status === 'succeeded' && p.status !== 'completed') {
      await pool.query('UPDATE payments SET status = $1, yookassa_status = $2, completed_at = NOW() WHERE id = $3', ['completed', status, p.id]);
      if (p.type === 'deposit') {
        await pool.query('UPDATE seller_profiles SET balance = balance + $1 WHERE user_id = $2', [p.amount, p.user_id]);
      }
    }
    if (status === 'canceled') {
      await pool.query('UPDATE payments SET status = $1, yookassa_status = $2 WHERE id = $3', ['cancelled', status, p.id]);
    }
    res.status(200).send('OK');
  } catch (e) { console.error('Webhook error:', e); res.status(500).send('Error'); }
});

app.get('/api/payments', authenticate, async (req, res) => {
  try {
    const r = await pool.query('SELECT * FROM payments WHERE user_id = $1 ORDER BY created_at DESC', [req.user.id]);
    ok(res, r.rows);
  } catch (e) { res.status(500).json({ error: 'Failed' }); }
});

app.get('/api/payments/stats', authenticate, async (req, res) => {
  try {
    const r = await pool.query(
      `SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE user_id = $1 AND status = 'completed' AND type IN ('deposit', 'task_payment')`,
      [req.user.id]
    );
    ok(res, { total_spent: r.rows[0].total });
  } catch (e) { res.status(500).json({ error: 'Failed' }); }
});

// ===== AI / OPENROUTER =====
app.post('/api/ai/generate-brief', authenticate, requireRole('seller'), async (req, res) => {
  const { product_name, platform, content_type, requirements } = req.body;
  if (!OPENROUTER_API_KEY) return res.status(503).json({ error: 'AI not configured' });
  
  const prompt = `Create a detailed content brief for ${content_type} on ${platform} for product "${product_name}". 
Requirements: ${requirements || 'None'}

Generate:
1. Content concept / hook
2. Key talking points (5-7 bullets)
3. Recommended format and duration
4. Call to action
5. Hashtags / keywords
6. Do's and Don'ts

Respond in Russian.`;

  try {
    const r = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://creatormatch.ru',
        'X-Title': 'CreatorHub'
      },
      body: JSON.stringify({
        model: 'openai/gpt-4o-mini',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.7
      })
    });
    const data = await r.json();
    ok(res, { brief: data.choices?.[0]?.message?.content || 'No response' });
  } catch (e) { res.status(500).json({ error: 'AI failed' }); }
});

app.post('/api/ai/generate-description', authenticate, requireRole('seller'), async (req, res) => {
  const { product_name, features, target_audience, platform } = req.body;
  if (!OPENROUTER_API_KEY) return res.status(503).json({ error: 'AI not configured' });
  
  const prompt = `Write an SEO-optimized product description for "${product_name}" targeting ${target_audience || 'general audience'} on ${platform || 'marketplace'}.
Features: ${features || 'None specified'}

Requirements:
- Include keywords naturally
- Highlight benefits, not just features
- Add emotional appeal
- 200-400 words
- Russian language

Also provide 5 keyword suggestions.`;

  try {
    const r = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'openai/gpt-4o-mini',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.7
      })
    });
    const data = await r.json();
    ok(res, { description: data.choices?.[0]?.message?.content || 'No response' });
  } catch (e) { res.status(500).json({ error: 'AI failed' }); }
});

// ===== ADMIN =====
app.get('/api/admin/users', authenticate, requireRole('admin'), async (req, res) => {
  try {
    const r = await pool.query('SELECT id, email, name, role, is_active, created_at FROM users ORDER BY created_at DESC');
    ok(res, r.rows);
  } catch (e) { res.status(500).json({ error: 'Failed' }); }
});

app.get('/api/admin/stats', authenticate, requireRole('admin'), async (req, res) => {
  try {
    const users = await pool.query('SELECT role, COUNT(*) FROM users GROUP BY role');
    const tasks = await pool.query('SELECT status, COUNT(*) FROM tasks GROUP BY status');
    const apps = await pool.query('SELECT status, COUNT(*) FROM applications GROUP BY status');
    const revenue = await pool.query("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'completed' AND type IN ('deposit', 'subscription')");
    ok(res, { users: users.rows, tasks: tasks.rows, applications: apps.rows, total_revenue: revenue.rows[0].sum });
  } catch (e) { res.status(500).json({ error: 'Failed' }); }
});

// ===== PUBLIC / LANDING =====
app.get('/api/public/stats', async (req, res) => {
  try {
    const sellers = await pool.query('SELECT COUNT(*) FROM seller_profiles');
    const creators = await pool.query('SELECT COUNT(*) FROM creator_profiles');
    const tasks = await pool.query("SELECT COUNT(*) FROM tasks WHERE status = 'active'");
    ok(res, { sellers: sellers.rows[0].count, creators: creators.rows[0].count, active_tasks: tasks.rows[0].count });
  } catch (e) { res.status(500).json({ error: 'Failed' }); }
});

// ===== ERROR HANDLER =====
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal error' });
});

// ===== START =====
app.listen(PORT, () => {
  console.log(`[CreatorHub] API running on port ${PORT}`);
  console.log(`[CreatorHub] DB: ${process.env.DATABASE_URL?.replace(/:.+@/, ':****@')}`);
  console.log(`[CreatorHub] YooKassa: ${YOOKASSA_SHOP_ID ? 'configured' : 'NOT configured'}`);
  console.log(`[CreatorHub] OpenRouter: ${OPENROUTER_API_KEY ? 'configured' : 'NOT configured'}`);
});
