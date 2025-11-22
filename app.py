// server.js (Node.js / Express) — example for 2025
import express from 'express';
import session from 'express-session';
import Redis from 'ioredis';
import connectRedis from 'connect-redis';
import helmet from 'helmet';
import csrf from 'csurf';
import dotenv from 'dotenv';

dotenv.config();
const app = express();
app.use(helmet());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Redis setup (production: use auth, TLS where available)
const redisClient = new Redis(process.env.REDIS_URL);
const RedisStore = connectRedis(session);

app.set('trust proxy', 1); // if behind proxy/load balancer and using secure cookies

app.use(session({
  store: new RedisStore({ client: redisClient }),
  name: process.env.SESSION_COOKIE_NAME || 'sid', // don't use default name in prod
  secret: process.env.SESSION_SECRET,             // strong secret from env
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,             // JS cannot access cookie
    secure: process.env.NODE_ENV === 'production', // only send over HTTPS
    sameSite: 'lax',            // CSRF protection balance
    maxAge: 1000 * 60 * 60 * 24 // 1 day
  }
}));

// CSRF protection for state-changing requests
const csurfProtection = csrf({ cookie: false });
app.use((req, res, next) => {
  // optionally skip CSRF for API routes used by trusted clients
  next();
});

// Example login route (do NOT store password in cookie)
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  // authenticate user (example only)
  const user = await fakeAuth(username, password);
  if (!user) return res.status(401).json({ error: 'Unauthorized' });

  // regenerate session to prevent fixation
  req.session.regenerate((err) => {
    if (err) return res.status(500).json({ error: 'Session error' });
    req.session.userId = user.id;
    // don't store sensitive info in session cookie
    res.json({ ok: true });
  });
});

app.post('/logout', (req, res) => {
  req.session.destroy(err => {
    res.clearCookie(process.env.SESSION_COOKIE_NAME || 'sid', {
      path: '/'
    });
    res.json({ ok: true });
  });
});

// Serve frontend (which will include CMP script / cookie banner)
app.get('/', (req, res) => {
  res.sendFile('/path/to/your/index.html'); // serve your SPA / page
});

// fake auth for example
async function fakeAuth(u, p) {
  if (u === 'demo' && p === 'demo') return { id: 1 };
  return null;
}

app.listen(process.env.PORT || 3000, () => console.log('Server running'));
