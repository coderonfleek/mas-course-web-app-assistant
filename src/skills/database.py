DATABASE_SKILL = {
    "name": "database",
    "description": "Connection pools, query failures, N+1 problems, deadlocks, migrations, ORM debugging, and indexing issues for PostgreSQL, MySQL, and MongoDB",
    "content": """# Database Troubleshooting Guide

## Quick Diagnostic Checklist

1. Can you connect to the database manually? (psql, mysql, mongosh)
2. Check connection string format and credentials
3. Verify database server is running
4. Check for connection pool exhaustion
5. Look at slow query logs

---

## Common Issues and Solutions

### 1. Connection Failures

**"Connection refused" / "ECONNREFUSED"**

a) **Check if database is running**
```bash
# PostgreSQL
sudo systemctl status postgresql
pg_isready -h localhost -p 5432

# MySQL
sudo systemctl status mysql
mysqladmin ping -h localhost

# MongoDB
sudo systemctl status mongod
mongosh --eval "db.adminCommand('ping')"
```

b) **Check connection string format**
```javascript
// PostgreSQL
postgresql://user:password@localhost:5432/dbname

// MySQL
mysql://user:password@localhost:3306/dbname

// MongoDB
mongodb://user:password@localhost:27017/dbname
```

c) **Check firewall / network**
```bash
# Test port connectivity
telnet localhost 5432
nc -zv localhost 5432

# Check listening ports
sudo netstat -tlnp | grep 5432
```

d) **Check pg_hba.conf (PostgreSQL)**
```
# Allow local connections
host    all    all    127.0.0.1/32    md5
host    all    all    ::1/128         md5
```

### 2. Connection Pool Exhaustion

**Symptoms:** "too many connections", timeouts, slow responses

**Diagnostic Steps:**

a) **Check current connections**
```sql
-- PostgreSQL
SELECT count(*) FROM pg_stat_activity;
SELECT * FROM pg_stat_activity WHERE state = 'active';

-- MySQL
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Threads_connected';
```

b) **Check pool configuration**
```javascript
// Node.js with pg
const pool = new Pool({
  max: 20,  // Max connections in pool
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```

```python
# SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections
)
```

c) **Common Fixes:**
- Close connections after use (use context managers)
- Increase pool size
- Add connection timeouts
- Implement connection retry logic

### 3. N+1 Query Problem

**Symptoms:** Hundreds of queries for simple operations

**Example Problem:**
```python
# BAD - N+1 queries
users = User.query.all()
for user in users:
    print(user.posts)  # Each access = 1 query!
```

**Solutions:**

```python
# SQLAlchemy - Eager loading
users = User.query.options(joinedload(User.posts)).all()

# Django - select_related (foreign key)
users = User.objects.select_related('profile').all()

# Django - prefetch_related (many-to-many)
users = User.objects.prefetch_related('posts').all()
```

```javascript
// Prisma
const users = await prisma.user.findMany({
  include: { posts: true }
});

// Sequelize
const users = await User.findAll({
  include: [{ model: Post }]
});
```

### 4. Slow Queries

**Diagnostic Steps:**

a) **Enable slow query logging**
```sql
-- PostgreSQL (postgresql.conf)
log_min_duration_statement = 1000  -- Log queries > 1s

-- MySQL
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

b) **Analyze query execution**
```sql
-- PostgreSQL
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- MySQL
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
```

c) **Look for:**
- Seq Scan (full table scan) - needs index
- High row estimates
- Nested loops with large tables

d) **Add indexes**
```sql
-- Single column index
CREATE INDEX idx_users_email ON users(email);

-- Composite index (order matters!)
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Partial index (PostgreSQL)
CREATE INDEX idx_active_users ON users(email) WHERE active = true;
```

### 5. Deadlocks

**Symptoms:** Queries hang, then fail with deadlock error

**Diagnostic:**
```sql
-- PostgreSQL - View locks
SELECT * FROM pg_locks WHERE NOT granted;

-- MySQL - View locks
SHOW ENGINE INNODB STATUS;
SELECT * FROM information_schema.innodb_locks;
```

**Solutions:**

a) **Consistent ordering**
```python
# Always lock in same order
# If updating users 1 and 2, always lock 1 first
users = User.query.filter(User.id.in_([1, 2])).order_by(User.id).with_for_update()
```

b) **Reduce transaction scope**
```python
# Keep transactions short
with db.session.begin():
    # Do minimal work here
    user.balance -= amount
# Release lock quickly
```

c) **Use appropriate isolation levels**
```python
# Lower isolation if acceptable
with db.session.begin():
    db.session.execute(text("SET TRANSACTION ISOLATION LEVEL READ COMMITTED"))
```

### 6. Migration Failures

**Common Issues:**

a) **Migration conflict**
```bash
# Django - Check migration history
python manage.py showmigrations

# Create fresh migration
python manage.py makemigrations --merge
```

b) **Locked table during migration**
```sql
-- PostgreSQL - Add column without lock (if possible)
ALTER TABLE users ADD COLUMN new_col VARCHAR(255);
-- This locks briefly

-- For large tables, consider:
-- 1. Add nullable column
-- 2. Backfill in batches
-- 3. Add constraints after
```

c) **Data migration fails**
```python
# Always handle None/NULL values
def migrate_data(apps, schema_editor):
    User = apps.get_model('app', 'User')
    for user in User.objects.filter(new_field__isnull=True):
        user.new_field = calculate_default(user)
        user.save()
```

### 7. ORM-Specific Issues

**SQLAlchemy - DetachedInstanceError**
```python
# Object accessed outside session
user = session.query(User).first()
session.close()
print(user.posts)  # Error! Session closed

# Solution 1: Eager load
user = session.query(User).options(joinedload(User.posts)).first()

# Solution 2: Keep session open
# Solution 3: Expire on commit = False
```

**Django - OperationalError: database is locked (SQLite)**
```python
# SQLite can't handle concurrent writes
# Solution: Use PostgreSQL for production

# Or increase timeout
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}
```

**Prisma - Connection pool timeout**
```javascript
// Increase pool timeout
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL + "?connection_limit=5&pool_timeout=10"
    }
  }
});
```

---

## Performance Tips

### Indexing Strategy
```sql
-- Index columns used in:
-- WHERE clauses
-- JOIN conditions
-- ORDER BY
-- Foreign keys

-- Check index usage (PostgreSQL)
SELECT indexrelname, idx_scan, idx_tup_read 
FROM pg_stat_user_indexes;
```

### Query Optimization
```sql
-- Use LIMIT for large results
SELECT * FROM logs ORDER BY created_at DESC LIMIT 100;

-- Avoid SELECT *
SELECT id, name, email FROM users;

-- Use EXISTS instead of COUNT for existence checks
SELECT EXISTS(SELECT 1 FROM users WHERE email = 'test@test.com');
```

### Connection Best Practices
```python
# Always use connection pooling
# Always close connections (use context managers)
# Implement retry logic for transient failures
# Monitor connection count in production
```
"""
}
