# Augments MCP API Guide

## 🚀 Quick Start

### Base URL
```
https://mcp.augments.dev/api/v1
```

### Authentication
All API requests require an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" https://mcp.augments.dev/api/v1/frameworks
```

### API Key Tiers
- **Demo**: `demo_*` keys - Limited rate limits, perfect for testing
- **Premium**: Contact us for premium access with 10x rate limits

## 📚 API Endpoints

### List Frameworks
Get all available frameworks, optionally filtered by category.

```http
GET /frameworks?category=web
```

**Parameters:**
- `category` (optional): Filter by category (web, backend, mobile, ai-ml, design, tools, data-platforms)

**Example Response:**
```json
{
  "success": true,
  "data": {
    "frameworks": [
      {
        "name": "react",
        "display_name": "React",
        "category": "web",
        "type": "library",
        "description": "JavaScript library for building user interfaces"
      }
    ]
  },
  "request_id": "1234567890_abc123"
}
```

### Get Framework Info
Get detailed information about a specific framework.

```http
GET /frameworks/{framework}
```

**Example:**
```bash
curl -H "X-API-Key: demo_test" \
  https://mcp.augments.dev/api/v1/frameworks/tailwindcss
```

### Search Frameworks
Search for frameworks by name, features, or keywords.

```http
POST /frameworks/search
Content-Type: application/json

{
  "query": "react component library",
  "limit": 10
}
```

### Get Documentation
Retrieve comprehensive documentation for a framework.

```http
POST /documentation
Content-Type: application/json

{
  "framework": "nextjs",
  "section": "app-router",
  "use_cache": true
}
```

**Parameters:**
- `framework` (required): Framework name
- `section` (optional): Specific documentation section
- `use_cache` (optional): Use cached data if available (default: true)

### Search Documentation
Search within a framework's documentation.

```http
POST /documentation/search
Content-Type: application/json

{
  "framework": "tailwindcss",
  "query": "responsive design",
  "limit": 10
}
```

### Get Multi-Framework Context
Get combined context from multiple frameworks for a specific task.

```http
POST /context
Content-Type: application/json

{
  "frameworks": ["nextjs", "tailwindcss", "shadcn-ui"],
  "task_description": "Building a responsive dashboard with dark mode"
}
```

### Analyze Code Compatibility
Check code for framework compatibility issues.

```http
POST /analyze
Content-Type: application/json

{
  "code": "const App = () => { return <div className='p-4'>Hello</div> }",
  "frameworks": ["react", "tailwindcss"]
}
```

**Note:** Code size is limited to 50KB for security reasons.

### Cache Statistics
Get cache performance metrics (useful for monitoring).

```http
GET /cache/stats
```

### Refresh Cache
Force refresh cached documentation (Premium only).

```http
POST /cache/refresh
Content-Type: application/json

{
  "framework": "react",
  "use_cache": false
}
```

## 🔒 Rate Limits

### Demo Tier
- 100 requests per minute
- 1,000 requests per hour
- Per-IP additional limiting

### Premium Tier
- 1,000 requests per minute
- 10,000 requests per hour
- Priority queue access

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 🛠️ Error Handling

All errors follow a consistent format:

```json
{
  "error": "Framework not found",
  "detail": "The framework 'invalid-framework' does not exist",
  "request_id": "1234567890_abc123"
}
```

### Common Error Codes
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (framework doesn't exist)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

## 💻 Client Examples

### JavaScript/TypeScript
```javascript
const AUGMENTS_API_KEY = 'demo_test123';
const BASE_URL = 'https://mcp.augments.dev/api/v1';

async function getFrameworkDocs(framework) {
  const response = await fetch(`${BASE_URL}/documentation`, {
    method: 'POST',
    headers: {
      'X-API-Key': AUGMENTS_API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      framework: framework,
      use_cache: true
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

// Usage
const docs = await getFrameworkDocs('react');
console.log(docs.data);
```

### Python
```python
import requests

AUGMENTS_API_KEY = 'demo_test123'
BASE_URL = 'https://mcp.augments.dev/api/v1'

def get_framework_docs(framework: str):
    response = requests.post(
        f'{BASE_URL}/documentation',
        headers={'X-API-Key': AUGMENTS_API_KEY},
        json={
            'framework': framework,
            'use_cache': True
        }
    )
    response.raise_for_status()
    return response.json()

# Usage
docs = get_framework_docs('fastapi')
print(docs['data'])
```

### cURL
```bash
# List all web frameworks
curl -H "X-API-Key: demo_test123" \
  "https://mcp.augments.dev/api/v1/frameworks?category=web"

# Get React documentation
curl -X POST \
  -H "X-API-Key: demo_test123" \
  -H "Content-Type: application/json" \
  -d '{"framework": "react", "use_cache": true}' \
  https://mcp.augments.dev/api/v1/documentation

# Search within Tailwind docs
curl -X POST \
  -H "X-API-Key: demo_test123" \
  -H "Content-Type: application/json" \
  -d '{"framework": "tailwindcss", "query": "dark mode", "limit": 5}' \
  https://mcp.augments.dev/api/v1/documentation/search
```

## 🏃 Best Practices

1. **Cache Wisely**: Use `use_cache: true` for stable content
2. **Batch Requests**: Combine multiple frameworks in context requests
3. **Handle Rate Limits**: Implement exponential backoff
4. **Monitor Usage**: Track your API usage via cache stats
5. **Error Handling**: Always check response status and handle errors

## 🔄 Webhooks (Coming Soon)

Subscribe to documentation updates:
```json
{
  "url": "https://your-app.com/webhook",
  "frameworks": ["react", "nextjs"],
  "events": ["documentation_updated", "new_version"]
}
```

## 📊 Response Headers

All responses include helpful headers:
```
X-Request-ID: Unique request identifier
X-Process-Time: Processing time in seconds
X-Cache-Hit: Whether response was served from cache
X-RateLimit-*: Rate limiting information
```

## 🆘 Support

- **API Status**: https://status.augments.dev
- **Documentation**: https://docs.augments.dev
- **Issues**: https://github.com/augments/mcp-server/issues
- **Premium Access**: contact@augments.dev

## 🚀 SDK (Coming Soon)

Official SDKs planned for:
- JavaScript/TypeScript
- Python
- Go
- Ruby
- PHP

Stay tuned for updates!