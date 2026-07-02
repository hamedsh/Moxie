# API Documentation

## Overview

Moxie API provides endpoints for:
1. **Gateway** (`/api/api_v1/api_gateway/*`) - Transparent request proxying with rule-based interception
2. **Management** (`/api/api_v1/api_management/*`) - Rule CRUD and testing
3. **Health Checks** (`/api/v1/healthcheck/*`) - Service health and readiness probes

## Interactive API Documentation

Access the Swagger UI at: `http://localhost:8080/`

This provides an interactive interface to test all endpoints.

---

## Rule Management API

### Create a Rule

**Endpoint:** `POST /api/api_v1/api_management/rule`

**Description:** Create a new rule for intercepting and manipulating API requests.

**Request Body:**
```json
{
  "method": "GET",
  "url": "api.customer.io/v1/activities",
  "call_backend": false,
  "status_code": 429,
  "response": "{\"error\": \"Too Many Requests\"}",
  "enable": true,
  "mock_count": 5,
  "response_delay": 2,
  "response_media_type": "application/json",
  "custom_headers": {
    "X-Custom-Header": "value"
  }
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "method": "GET",
  "url": "api.customer.io/v1/activities",
  "call_backend": false,
  "status_code": 429,
  "response": "{\"error\": \"Too Many Requests\"}",
  "enable": true,
  "mock_count": 5,
  "response_delay": 2,
  "response_media_type": "application/json",
  "custom_headers": {"X-Custom-Header": "value"},
  "created_at": "2026-07-02T10:00:00Z",
  "updated_at": "2026-07-02T10:00:00Z"
}
```

---

### Get All Rules

**Endpoint:** `GET /api/api_v1/api_management/rules`

**Description:** Retrieve all configured rules.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "method": "GET",
    "url": "api.customer.io/v1/activities",
    "call_backend": false,
    "status_code": 429,
    "response": "{\"error\": \"Too Many Requests\"}",
    "enable": true,
    "mock_count": 5,
    "response_delay": 2,
    "response_media_type": "application/json",
    "custom_headers": {}
  }
]
```

---

### Test Rule Regex

**Endpoint:** `POST /api/api_v1/api_management/rule/test`

**Description:** Test a URL pattern against a sample URL to verify regex matching without saving.

**Request Body:**
```json
{
  "method": "GET",
  "url_pattern": "api.customer.io/v1/activities",
  "test_url": "api.customer.io/v1/activities"
}
```

**Response:** `200 OK`
```json
{
  "method": "GET",
  "url_pattern": "api.customer.io/v1/activities",
  "test_url": "api.customer.io/v1/activities",
  "matches": true,
  "message": "Pattern 'api.customer.io/v1/activities' matches 'api.customer.io/v1/activities'"
}
```

---

### Check for Conflicting Rules

**Endpoint:** `POST /api/api_v1/api_management/rule/check-conflicts`

**Description:** Check if a new rule would conflict with existing rules (overlapping patterns).

**Request Body:**
```json
{
  "method": "POST",
  "url": "track.customer.io/api/v1/customers/.*/unsuppress",
  "call_backend": false,
  "status_code": 429,
  "response": "{}",
  "enable": true,
  "mock_count": -1,
  "response_delay": 0,
  "response_media_type": "application/json",
  "custom_headers": {}
}
```

**Response:** `200 OK`
```json
[
  {
    "rule_id": 2,
    "method": "POST",
    "url_pattern": "track.customer.io/api/v1/customers/.*/unsuppress",
    "conflicting_rule_ids": [2],
    "conflict_severity": "warning",
    "message": "Rule 2 has overlapping pattern: track.customer.io/api/v1/customers/.*/unsuppress"
  }
]
```

---

### Enable/Disable a Rule

**Endpoint:** `PATCH /api/api_v1/api_management/rule/{rule_id}/status`

**Description:** Enable or disable a rule.

**Request Body:**
```json
{
  "enable": false
}
```

**Response:** `200 OK` (returns updated rule)

---

### Update Rule Mock Count

**Endpoint:** `PATCH /api/api_v1/api_management/rule/{rule_id}/mock_count`

**Description:** Update how many times a rule should be applied.

**Request Body:**
```json
{
  "mock_count": 10
}
```

**Response:** `200 OK` (returns updated rule)

---

### Delete a Rule

**Endpoint:** `DELETE /api/api_v1/api_management/rule/{rule_id}`

**Description:** Delete a rule by ID.

**Response:** `204 No Content`

---

### Export All Rules

**Endpoint:** `POST /api/api_v1/api_management/rules/export`

**Description:** Export all current rules as JSON for backup or sharing.

**Response:** `200 OK`
```json
{
  "version": "1.0",
  "rules": [
    {
      "method": "GET",
      "url": "api.customer.io/v1/activities",
      "call_backend": false,
      "status_code": 429,
      "response": "{}",
      "enable": true,
      "mock_count": 5,
      "response_delay": 0,
      "response_media_type": "application/json",
      "custom_headers": {}
    }
  ],
  "metadata": {
    "rule_count": 1
  }
}
```

---

### Import Rules

**Endpoint:** `POST /api/api_v1/api_management/rules/import`

**Description:** Import multiple rules from a JSON export file. Existing rules are not affected.

**Request Body:** (RuleExport object from export endpoint)
```json
{
  "version": "1.0",
  "rules": [
    {
      "method": "GET",
      "url": "api.example.com/.*",
      "call_backend": false,
      "status_code": 500,
      "response": "{\"error\": \"Internal Server Error\"}",
      "enable": true,
      "mock_count": -1,
      "response_delay": 0,
      "response_media_type": "application/json",
      "custom_headers": {}
    }
  ],
  "metadata": {}
}
```

**Response:** `201 Created`
```json
{
  "imported": 1,
  "failed": 0,
  "failed_details": []
}
```

---

## Health Check API

### Health Status

**Endpoint:** `GET /api/v1/healthcheck/`

**Description:** Simple health check - returns OK if service is running.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "message": "Service is running"
}
```

---

### Readiness Probe

**Endpoint:** `GET /api/v1/healthcheck/ready`

**Description:** Check if service is ready to accept requests (includes database connectivity).

**Response:** `200 OK` (if ready)
```json
{
  "status": "ready",
  "database": "connected",
  "message": "Service is ready to accept requests"
}
```

**Response:** `503 Service Unavailable` (if database is unreachable)
```json
{
  "detail": "Database is unreachable. Service is not ready."
}
```

---

### Liveness Probe

**Endpoint:** `GET /api/v1/healthcheck/live`

**Description:** Check if service process is alive (for Kubernetes liveness probes).

**Response:** `200 OK`
```json
{
  "status": "alive",
  "message": "Service process is running"
}
```

---

## Gateway API

### Proxy Request

**Endpoint:** `GET|POST|PUT|PATCH|DELETE /api/api_v1/api_gateway/{url_path:path}`

**Description:** Transparent proxy endpoint. Matches against rules and either:
- Returns mocked response (if rule matches and call_backend=false)
- Proxies to backend with custom headers (if rule matches and call_backend=true)
- Proxies to backend as-is (if no rule matches)

**Example:**
```bash
curl -X GET "http://localhost:8080/api/api_v1/api_gateway/api.customer.io/v1/activities"
```

If a rule matches:
- Returns the rule's status_code, response, and response_delay
- Adds custom_headers to the request

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|----------|
| 200 | OK | GET /rules succeeded |
| 201 | Created | POST /rule succeeded |
| 204 | No Content | DELETE /rule succeeded |
| 400 | Bad Request | Invalid regex pattern, negative rule ID |
| 404 | Not Found | Rule with given ID doesn't exist |
| 503 | Service Unavailable | Database is unreachable |
| 500 | Internal Server Error | Unexpected server error (check Sentry) |

### Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

---

## Example Workflows

### Setup: Create Test Rules

```bash
# 1. Test regex pattern before creating
curl -X POST "http://localhost:8080/api/api_v1/api_management/rule/test" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "url_pattern": "api.cloudflare.com/client/v4/zones/.*/ssl/universal/settings",
    "test_url": "api.cloudflare.com/client/v4/zones/abc123/ssl/universal/settings"
  }'

# 2. Check for conflicts
curl -X POST "http://localhost:8080/api/api_v1/api_management/rule/check-conflicts" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "url": "api.cloudflare.com/client/v4/zones/.*/ssl/universal/settings",
    "call_backend": false,
    "status_code": 429,
    "response": "{}",
    "enable": true,
    "mock_count": -1,
    "response_delay": 1,
    "response_media_type": "application/json",
    "custom_headers": {}
  }'

# 3. Create the rule
curl -X POST "http://localhost:8080/api/api_v1/api_management/rule" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "url": "api.cloudflare.com/client/v4/zones/.*/ssl/universal/settings",
    "call_backend": false,
    "status_code": 429,
    "response": "{\"success\": false}",
    "enable": true,
    "mock_count": -1,
    "response_delay": 1,
    "response_media_type": "application/json",
    "custom_headers": {}
  }'
```

### Backup and Share Rules

```bash
# Export all rules
curl -X POST "http://localhost:8080/api/api_v1/api_management/rules/export" \
  > rules_backup.json

# Import on another instance
curl -X POST "http://localhost:8080/api/api_v1/api_management/rules/import" \
  -H "Content-Type: application/json" \
  -d @rules_backup.json
```

---

## Kubernetes Integration

Use health check endpoints for orchestration:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: moxie
spec:
  containers:
  - name: moxie
    image: moxie:latest
    livenessProbe:
      httpGet:
        path: /api/v1/healthcheck/live
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /api/v1/healthcheck/ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
```
