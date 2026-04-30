BACKEND_SKILL = {
    "name": "backend",
    "description": "Server errors, API failures, HTTP status codes, stack traces, Express/FastAPI/Django debugging, middleware, and routing issues",
    "content": """# Backend Troubleshooting Guide

## Quick Diagnostic Checklist

1. Check server logs for error messages
2. Verify the HTTP status code returned
3. Test the endpoint with curl or Postman
4. Check if the service is running (ps aux, systemctl status)
5. Verify environment variables are loaded

---

## HTTP Status Codes Reference

### 4xx Client Errors

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 400 | Bad Request | Invalid JSON, missing required fields |
| 401 | Unauthorized | Missing or invalid auth token |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Wrong URL, resource doesn't exist |
| 405 | Method Not Allowed | GET instead of POST, etc. |
| 409 | Conflict | Duplicate resource, version mismatch |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limited |

### 5xx Server Errors

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 500 | Internal Server Error | Unhandled exception in code |
| 502 | Bad Gateway | Upstream server down |
| 503 | Service Unavailable | Server overloaded or in maintenance |
| 504 | Gateway Timeout | Upstream server too slow |

---

## Common Issues and Solutions

### 1. 500 Internal Server Error

**Diagnostic Steps:**

a) **Check Server Logs**
```bash
# Node.js/Express
tail -f logs/error.log
# Or check console output

# Python/Django
tail -f /var/log/django/error.log

# Check system logs
journalctl -u myapp -f
```

b) **Enable Detailed Errors (Development Only!)**
```javascript
// Express
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: err.message,
    stack: process.env.NODE_ENV === 'development' ? err.stack : undefined
  });
});
```

```python
# Django settings.py
DEBUG = True  # Only in development!
```

c) **Common Causes:**
- Null pointer / undefined access
- Database connection failed
- Missing environment variable
- Unhandled promise rejection
- Syntax error in production build

### 2. 404 Not Found (But Route Exists)

**Diagnostic Steps:**

a) **Check Route Registration**
```javascript
// Express - Order matters!
app.use('/api', apiRouter);  // Must be before catch-all
app.get('*', (req, res) => res.sendFile('index.html'));
```

```python
# Django - Check urls.py
urlpatterns = [
    path('api/', include('api.urls')),  # Check path matches
]
```

b) **Check HTTP Method**
```bash
# Are you using the right method?
curl -X POST http://localhost:3000/api/users  # Not GET
```

c) **Check for Typos**
- Case sensitivity: /api/Users vs /api/users
- Trailing slashes: /api/users vs /api/users/
- Query params in path: /api/users?id=1 vs /api/users/1

### 3. Request Body is Empty/Undefined

**Express.js**
```javascript
// MUST add body parsing middleware BEFORE routes
const express = require('express');
const app = express();

app.use(express.json());  // For JSON bodies
app.use(express.urlencoded({ extended: true }));  // For form data

// NOW define routes
app.post('/api/users', (req, res) => {
  console.log(req.body);  // Now it works
});
```

**FastAPI**
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str

@app.post("/users")
async def create_user(user: User):  # Pydantic handles parsing
    return user
```

**Check Content-Type Header**
```bash
# Must match body format
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John"}'
```

### 4. Authentication/Authorization Failures

**401 Unauthorized**
```javascript
// Check token is being sent
// Header: Authorization: Bearer <token>

// Express middleware
const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};
```

**403 Forbidden**
```javascript
// User is authenticated but lacks permission
const adminOnly = (req, res, next) => {
  if (req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Admin access required' });
  }
  next();
};
```

### 5. Middleware Not Executing

**Express - Order Matters!**
```javascript
// WRONG - middleware after route
app.get('/api/data', handler);
app.use(authMiddleware);  // Never runs for /api/data

// CORRECT - middleware before route
app.use(authMiddleware);
app.get('/api/data', handler);
```

**Check Middleware Chain**
```javascript
// Must call next() to continue
const myMiddleware = (req, res, next) => {
  console.log('Middleware running');
  next();  // Don't forget this!
};
```

### 6. Async/Await Errors Not Caught

**Express**
```javascript
// WRONG - error disappears
app.get('/api/data', async (req, res) => {
  const data = await fetchData();  // If this throws, no response
  res.json(data);
});

// CORRECT - wrap in try/catch
app.get('/api/data', async (req, res, next) => {
  try {
    const data = await fetchData();
    res.json(data);
  } catch (err) {
    next(err);  // Pass to error handler
  }
});

// OR use express-async-errors package
require('express-async-errors');
```

**FastAPI - Automatic handling**
```python
@app.get("/data")
async def get_data():
    # FastAPI handles async errors automatically
    data = await fetch_data()
    return data
```

---

## Debugging Techniques

### Logging Best Practices

```javascript
// Structured logging
const logger = require('pino')();

logger.info({ userId: user.id, action: 'login' }, 'User logged in');
logger.error({ err, requestId: req.id }, 'Database query failed');
```

### Request Tracing

```javascript
// Add request ID for tracing
const { v4: uuidv4 } = require('uuid');

app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] || uuidv4();
  res.setHeader('x-request-id', req.id);
  next();
});
```

### Testing Endpoints

```bash
# Basic GET
curl http://localhost:3000/api/users

# POST with JSON
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com"}'

# With auth header
curl http://localhost:3000/api/protected \
  -H "Authorization: Bearer eyJhbGc..."

# Verbose output (see headers)
curl -v http://localhost:3000/api/users
```

---

## Framework-Specific Issues

### Express.js

- Check middleware order
- Verify body parsers are configured
- Use error handling middleware
- Check for unhandled promise rejections

### FastAPI

- Validate Pydantic models
- Check async/await usage
- Verify dependency injection
- Check OpenAPI docs at /docs

### Django

- Check URL patterns in urls.py
- Verify view function/class setup
- Check middleware order in settings.py
- Run migrations if model-related
"""
}
