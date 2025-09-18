# 🛡️ Django CFG Middleware

Custom Django middleware components for Django CFG applications.

## 📋 Contents

- [UserActivityMiddleware](#useractivitymiddleware) - User activity tracking
- [PublicEndpointsMiddleware](#publicendpointsmiddleware) - Ignore invalid JWT tokens on public endpoints

## UserActivityMiddleware

Middleware for automatic user activity tracking by updating the `last_login` field on API requests.

### ✨ Features

- ✅ Automatic `last_login` update on API requests
- ✅ Smart API request detection (JSON, DRF, REST methods)
- ✅ 5-minute update interval to prevent database spam
- ✅ In-memory caching for performance optimization
- ✅ Only works when `accounts` app is enabled
- ✅ KISS principle - no configuration needed

### 🚀 Automatic Integration

The middleware is automatically included when `enable_accounts = True`:

```python
class MyConfig(DjangoConfig):
    enable_accounts = True  # UserActivityMiddleware will be auto-included
```

### 🎯 API Request Detection

The middleware intelligently detects API requests using:

1. **JSON Content-Type or Accept header**
   ```
   Content-Type: application/json
   Accept: application/json
   ```

2. **DRF format parameter**
   ```
   ?format=json
   ?format=api
   ```

3. **REST methods** (POST, PUT, PATCH, DELETE) on non-admin paths

4. **Configured API prefixes**
   - Django Revolution API: `/{api_prefix}/` (from config)
   - Django CFG API: `/cfg/` (always)

### 📊 Statistics

Get middleware statistics:

```python
from django_cfg.middleware import UserActivityMiddleware

# In view or management command
middleware = UserActivityMiddleware()
stats = middleware.get_activity_stats()

print(stats)
# {
#     'tracked_users': 42,
#     'update_interval': 300,
#     'api_only': True,
#     'accounts_enabled': True,
#     'middleware_active': True
# }
```

### 🔍 Logging

The middleware logs activity at DEBUG level:

```python
# settings.py
LOGGING = {
    'loggers': {
        'django_cfg.middleware.user_activity': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

### 🎛️ Manual Integration

If you need to include the middleware manually:

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'django_cfg.middleware.UserActivityMiddleware',
]
```

### 🔧 Performance

- **Caching**: Last update times are cached in memory
- **Batch updates**: Uses `update()` instead of `save()` for optimization
- **Auto-cleanup**: Cache automatically cleans up when exceeding 1000 users
- **Graceful errors**: Errors don't break request processing

### 🎯 Admin Integration

The `last_login` field is automatically displayed in accounts admin:

- ✅ In user list view (`last_login_display`)
- ✅ In user detail view
- ✅ With human-readable time format

### 🚨 Important Notes

1. **Accounts only**: Middleware only works when `enable_accounts = True`
2. **Authentication**: Only tracks authenticated users
3. **Performance**: 5-minute interval prevents database spam
4. **Safety**: Middleware doesn't break requests on errors

### 📈 Monitoring

For user activity monitoring:

```python
# In Django admin or management command
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Active users in the last hour
active_users = User.objects.filter(
    last_login__gte=timezone.now() - timedelta(hours=1)
).count()

# Online users (last 5 minutes)
online_users = User.objects.filter(
    last_login__gte=timezone.now() - timedelta(minutes=5)
).count()
```

### 💡 Usage Examples

The middleware works automatically with no configuration needed:

```python
# Your DjangoConfig
class MyProjectConfig(DjangoConfig):
    enable_accounts = True  # That's it! Middleware is active

# API requests will automatically update last_login:
# POST /cfg/accounts/profile/
# GET /api/users/?format=json
# PUT /cfg/newsletter/subscribe/
```

## PublicEndpointsMiddleware

Middleware that temporarily removes invalid JWT tokens from public endpoints to prevent authentication errors.

### ✨ Features

- ✅ **Automatic activation** - No configuration needed, works out of the box
- ✅ **Smart endpoint detection** - Configurable regex patterns for public endpoints
- ✅ **JWT token detection** - Only processes requests with Bearer tokens
- ✅ **Temporary removal** - Auth headers are restored after request processing
- ✅ **Performance optimized** - Compiled regex patterns for fast matching
- ✅ **Detailed logging** - Debug information for troubleshooting
- ✅ **Statistics tracking** - Monitor middleware usage and effectiveness

### 🎯 Problem Solved

When a frontend sends an invalid/expired JWT token to a public endpoint (like OTP request), Django's authentication middleware tries to authenticate the user and fails with "User not found" errors, even though the endpoint has `AllowAny` permissions.

This middleware temporarily removes the `Authorization` header for public endpoints, allowing them to work without authentication errors.

### 🚀 Automatic Integration

The middleware is **automatically included** in all Django CFG projects:

```python
class MyConfig(DjangoConfig):
    # No configuration needed - PublicEndpointsMiddleware is always active
    pass
```

### 🎯 Default Public Endpoints

The middleware protects these endpoints by default:

```python
DEFAULT_PUBLIC_PATTERNS = [
    r'^/api/accounts/otp/',           # OTP endpoints (request, verify)
    r'^/cfg/accounts/otp/',           # CFG OTP endpoints
    r'^/api/accounts/token/refresh/', # Token refresh
    r'^/cfg/accounts/token/refresh/', # CFG Token refresh
    r'^/api/health/',                 # Health check endpoints
    r'^/cfg/api/health/',             # CFG Health check endpoints
    r'^/admin/login/',                # Django admin login
    r'^/api/schema/',                 # API schema endpoints
    r'^/api/docs/',                   # API documentation
]
```

### ⚙️ Custom Configuration

You can customize public endpoint patterns in your Django settings:

```python
# settings.py (optional)
PUBLIC_ENDPOINT_PATTERNS = [
    r'^/api/accounts/otp/',
    r'^/api/public/',
    r'^/api/webhooks/',
    # Add your custom patterns here
]
```

### 🔍 How It Works

1. **Request Processing**: Middleware checks if the request path matches public endpoint patterns
2. **Token Detection**: If a Bearer token is present, it's temporarily removed
3. **Request Handling**: Django processes the request without authentication
4. **Token Restoration**: The original Authorization header is restored after processing

### 📊 Statistics

Get middleware statistics for monitoring:

```python
from django_cfg.middleware import PublicEndpointsMiddleware

# In your view or management command
middleware = PublicEndpointsMiddleware()
stats = middleware.get_stats()

print(stats)
# {
#     'requests_processed': 1250,
#     'tokens_ignored': 45,
#     'public_endpoints_hit': 120,
#     'public_patterns_count': 9,
#     'middleware_active': True
# }
```

### 🔍 Logging

The middleware logs activity at DEBUG level:

```python
# settings.py
LOGGING = {
    'loggers': {
        'django_cfg.middleware.public_endpoints': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

### 🎛️ Manual Integration

If you need to include the middleware manually (not recommended):

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django_cfg.middleware.PublicEndpointsMiddleware',  # Add early in stack
    # ... other middleware
]
```

### 🚨 Important Notes

1. **Always Active**: Middleware is included by default in all Django CFG projects
2. **Performance**: Uses compiled regex patterns for fast endpoint matching
3. **Safety**: Only removes Authorization headers temporarily, restores them after processing
4. **Logging**: All actions are logged for debugging and monitoring

### 💡 Usage Examples

The middleware works automatically with no configuration needed:

```python
# Your DjangoConfig
class MyProjectConfig(DjangoConfig):
    # PublicEndpointsMiddleware is automatically active
    pass

# These requests will work even with invalid tokens:
# POST /api/accounts/otp/request/ (with expired Bearer token)
# POST /cfg/accounts/otp/verify/ (with invalid Bearer token)
# GET /api/health/ (with any Bearer token)
```

### 🔧 Frontend Integration

Perfect companion to frontend error handling:

```typescript
// Frontend automatically clears invalid tokens on 401/403
// Middleware ensures public endpoints work during token cleanup
const response = await api.requestOTP({
  identifier: "user@example.com",
  channel: "email"
});
// ✅ Works even if localStorage has invalid token
```
