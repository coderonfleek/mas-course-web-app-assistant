NETWORK_SKILL = {
    "name": "network",
    "description": "CORS errors, SSL/TLS certificates, DNS resolution, timeouts, proxy configuration, load balancing, and CDN caching issues",
    "content": """# Network Troubleshooting Guide

## Quick Diagnostic Checklist

1. Can you reach the server? (ping, curl)
2. Is DNS resolving correctly? (nslookup, dig)
3. Are there SSL certificate errors?
4. Check browser Network tab for failed requests
5. Test from different networks/locations

---

## Common Issues and Solutions

### 1. CORS Errors

**Symptoms:** "Access to fetch at 'X' from origin 'Y' has been blocked by CORS policy"

**Understanding CORS:**
```
Browser at http://localhost:3000 
    → requests http://api.example.com/data
    → Server must include CORS headers to allow this
```

**Solution - Server-Side Headers:**

```javascript
// Express.js
const cors = require('cors');

// Allow all origins (development only!)
app.use(cors());

// Production - specific origins
app.use(cors({
  origin: ['https://myapp.com', 'https://www.myapp.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true  // If using cookies
}));
```

```python
# FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

```python
# Django
CORS_ALLOWED_ORIGINS = [
    "https://myapp.com",
]
CORS_ALLOW_CREDENTIALS = True
```

**CORS Preflight Issues:**
```javascript
// Browser sends OPTIONS request first for:
// - Non-simple methods (PUT, DELETE, PATCH)
// - Custom headers
// - Content-Type other than form-data, text/plain, application/x-www-form-urlencoded

// Server must handle OPTIONS
app.options('*', cors());  // Express
```

**CORS with Credentials (Cookies):**
```javascript
// Frontend - must include credentials
fetch('https://api.example.com/data', {
  credentials: 'include'  // Send cookies
});

// Server - must allow credentials
// AND cannot use wildcard origin (*)
Access-Control-Allow-Origin: https://myapp.com  // Specific origin
Access-Control-Allow-Credentials: true
```

### 2. SSL/TLS Certificate Errors

**"NET::ERR_CERT_AUTHORITY_INVALID"**
- Self-signed certificate
- Fix: Use Let's Encrypt for free valid certs

**"NET::ERR_CERT_DATE_INVALID"**
- Certificate expired
- Fix: Renew certificate

**"NET::ERR_CERT_COMMON_NAME_INVALID"**
- Certificate doesn't match domain
- Fix: Generate cert for correct domain(s)

**Debugging SSL:**
```bash
# Check certificate details
openssl s_client -connect example.com:443 -servername example.com

# Check certificate expiration
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates

# Test SSL configuration
curl -vI https://example.com
```

**Let's Encrypt Setup:**
```bash
# Using certbot
sudo certbot --nginx -d example.com -d www.example.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 3. DNS Issues

**"DNS_PROBE_FINISHED_NXDOMAIN"**
- Domain doesn't exist or DNS not propagated

**Diagnostic Commands:**
```bash
# Check DNS resolution
nslookup example.com
dig example.com

# Check specific DNS server
nslookup example.com 8.8.8.8

# Check DNS propagation
dig @8.8.8.8 example.com
dig @1.1.1.1 example.com

# Flush DNS cache
# macOS
sudo dscacheutil -flushcache

# Windows
ipconfig /flushdns

# Linux
sudo systemd-resolve --flush-caches
```

**Common DNS Issues:**
- DNS propagation delay (up to 48 hours)
- Wrong DNS records (A, CNAME, etc.)
- DNS provider issues

### 4. Timeout Errors

**"ETIMEDOUT" / "ESOCKETTIMEDOUT"**

**Diagnostic Steps:**

a) **Test basic connectivity**
```bash
# Check if server is reachable
ping example.com
telnet example.com 443
curl -v --connect-timeout 5 https://example.com
```

b) **Check for slow responses**
```bash
# Time the request
time curl -o /dev/null -s -w "Connect: %{time_connect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" https://example.com
```

c) **Increase timeout settings**
```javascript
// Node.js fetch
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 30000);

fetch(url, { signal: controller.signal });

// Axios
axios.get(url, { timeout: 30000 });
```

```python
# Python requests
requests.get(url, timeout=30)

# aiohttp
async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
    async with session.get(url) as response:
        return await response.text()
```

### 5. Proxy Issues

**Behind Corporate Proxy:**
```bash
# Set proxy environment variables
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1,.company.com

# For npm
npm config set proxy http://proxy.company.com:8080
npm config set https-proxy http://proxy.company.com:8080
```

**Reverse Proxy Configuration (Nginx):**
```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**WebSocket through Proxy:**
```nginx
# Must include these headers for WebSocket
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### 6. Load Balancer Issues

**Health Check Failures:**
```nginx
# Nginx upstream health check
upstream backend {
    server backend1.example.com:3000;
    server backend2.example.com:3000;
    
    # Health check endpoint
    health_check uri=/health interval=5s;
}
```

**Sticky Sessions:**
```nginx
# When sessions must stay on same server
upstream backend {
    ip_hash;  # Route by client IP
    server backend1.example.com:3000;
    server backend2.example.com:3000;
}
```

**502 Bad Gateway:**
- Upstream server is down
- Upstream server is too slow
- Check upstream server logs
- Increase proxy timeout

### 7. CDN/Caching Issues

**Stale Content After Deploy:**
```bash
# Purge CDN cache (varies by provider)
# Cloudflare
curl -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/purge_cache" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

**Cache Headers:**
```javascript
// Express - Prevent caching
app.use((req, res, next) => {
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  next();
});

// Or for specific routes
app.get('/api/data', (req, res) => {
  res.setHeader('Cache-Control', 'max-age=3600');  // Cache 1 hour
  res.json(data);
});
```

**Debugging Cache:**
```bash
# Check cache headers
curl -I https://example.com/static/app.js

# Look for:
# Cache-Control: max-age=31536000
# ETag: "abc123"
# Last-Modified: Wed, 01 Jan 2020 00:00:00 GMT
```

---

## Useful Network Commands

```bash
# Test HTTP request
curl -v https://example.com

# Test specific port
nc -zv example.com 443

# Trace route
traceroute example.com

# Check open ports
nmap -p 1-1000 example.com

# Monitor network traffic
tcpdump -i eth0 port 443

# Check listening ports
netstat -tlnp
ss -tlnp
```

---

## Network Debugging Tips

1. **Start from the client** - Is the request leaving?
2. **Check DNS** - Is the name resolving?
3. **Check connectivity** - Can you reach the IP?
4. **Check the port** - Is the service listening?
5. **Check the response** - What headers/status returned?
6. **Check server logs** - Did the request arrive?
"""
}