# Moxie

Moxie is a high-performance network mediator that sits at the edge of your internal infrastructure, giving you total control over outbound API traffic. By acting as a transparent bridge or a sophisticated interceptor, Moxie lets you:

- **Simulate Reality:** Return custom JSON or XML payloads and status codes to validate how internal systems handle specific API behaviors.
- **Engineer Chaos:** Inject precision latency and custom error states to test system resilience and timeout configurations under pressure.
- **Bridge the Gap:** Maintain full transparency for standard traffic while selectively intercepting specific endpoints for debugging or local development.

version: 0.1

![diagram.png](doc_files%2Fdiagram.png)

Some of our services require external APIs like Cloudflare and customer.io. These services sometimes return exception codes like 429, which can interrupt our service's reliability. To cope with these exceptions, we use BackOff mechanisms. However, we're unable to test those in DEV or STG environments because any interruption to our outgoing gateway affects all services.

For this purpose, we implemented our custom API gateway. This gateway works in transparent mode and passes every request to the destination. Based on test requirements, we can add a rule to change status_code or response without affecting real traffic.

## Quick Start

### Local Development

**Prerequisites:**
- Python 3.13+
- pip or uv package manager

**Installation:**
```bash
pip install -r requirements.txt
```

**Configuration:**

Create a `.env` file (see `example.env` for all options):

```bash
cp example.env .env
```

For PostgreSQL:
```env
DB_TYPE=postgresql
DB_HOST=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_DATABASE=statuscode_tool
```

**Run migrations:**
```bash
alembic upgrade head
```

**Start the server:**
```bash
uvicorn app.main:app --reload --port 8080
```

Access Swagger UI: http://localhost:8080/

### Docker

**Using Docker Compose (includes PostgreSQL):**
```bash
docker-compose up
```

**Access:** http://localhost:8080/

## Usage

### Interactive API Documentation

The Swagger UI is available at the root path: `http://localhost:8080/`

For detailed API documentation, see [docs/API.md](docs/API.md)

### Example: Create a Test Rule

1. **Test your URL pattern first:**

```bash
curl -X POST "http://localhost:8080/api/api_v1/api_management/rule/test" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "url_pattern": "api.customer.io/v1/activities",
    "test_url": "api.customer.io/v1/activities"
  }'
```

2. **Check for conflicts with existing rules:**

```bash
curl -X POST "http://localhost:8080/api/api_v1/api_management/rule/check-conflicts" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "url": "api.customer.io/v1/activities",
    "call_backend": false,
    "status_code": 429,
    "response": "{}",
    "enable": true,
    "mock_count": -1,
    "response_delay": 0,
    "response_media_type": "application/json",
    "custom_headers": {}
  }'
```

3. **Create the rule:**

```bash
curl -X POST "http://localhost:8080/api/api_v1/api_management/rule" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "url": "api.customer.io/v1/activities",
    "call_backend": false,
    "status_code": 429,
    "response": "{\"error\": \"Too Many Requests\"}",
    "enable": true,
    "mock_count": 3,
    "response_delay": 0,
    "response_media_type": "application/json",
    "custom_headers": {}
  }'
```

4. **View all rules:**

```bash
curl http://localhost:8080/api/api_v1/api_management/rules
```

5. **Enable/disable a rule:**

```bash
curl -X PATCH "http://localhost:8080/api/api_v1/api_management/rule/1/status" \
  -H "Content-Type: application/json" \
  -d '{"enable": false}'
```

6. **Delete a rule:**

```bash
curl -X DELETE "http://localhost:8080/api/api_v1/api_management/rule/1"
```

### Backup and Share Rules

**Export all rules:**
```bash
curl -X POST "http://localhost:8080/api/api_v1/api_management/rules/export" \
  > my_rules.json
```

**Import rules on another instance:**
```bash
curl -X POST "http://localhost:8080/api/api_v1/api_management/rules/import" \
  -H "Content-Type: application/json" \
  -d @my_rules.json
```

## Rule Structure

### Fields

- **method** (string, required): HTTP method (GET, POST, PUT, PATCH, DELETE)
- **url** (string, regex, required): URL pattern to match (without http:// or https://)
  - Examples:
    - `api.customer.io/v1/activities` - exact match
    - `api.customer.io/v1/activities.*` - prefix match
    - `track.customer.io/api/v1/customers/.*/unsuppress` - dynamic segments
- **call_backend** (boolean): Whether to still call the actual backend after applying rule
- **status_code** (integer): HTTP status code to return (e.g., 429, 500, 200)
- **response** (string, JSON): Response body as string
- **enable** (boolean): Whether this rule is active
- **mock_count** (integer): How many times to apply this rule
  - `-1`: unlimited (default)
  - `0`: never apply
  - `> 0`: apply exactly N times, then disable
- **response_delay** (integer): Delay in seconds before returning response
- **response_media_type** (string): Content-Type header (default: `application/json`)
- **custom_headers** (object): Custom headers to add to the request

### Examples

**Simulate 429 Rate Limit (3 times):**
```json
{
  "method": "POST",
  "url": "track.customer.io/api/v1/customers/.*/unsuppress",
  "call_backend": false,
  "custom_headers": {},
  "status_code": 429,
  "response": "{\"key\": \"value\"}",
  "enable": true,
  "mock_count": 3,
  "response_delay": 0,
  "response_media_type": "application/json"
}
```

**Return Mocked Cloudflare Response (unlimited):**
```json
{
  "method": "GET",
  "url": "api.cloudflare.com/client/v4/zones/.*/ssl/universal/settings",
  "call_backend": false,
  "custom_headers": {},
  "status_code": 200,
  "response": "{\"errors\":[],\"messages\":[],\"result\":{\"enabled\":true},\"success\":true}",
  "enable": true,
  "mock_count": -1,
  "response_delay": 1,
  "response_media_type": "application/json"
}
```

**Return XML Response:**
```json
{
  "method": "GET",
  "url": "test_url.com/xml_response",
  "call_backend": false,
  "custom_headers": {},
  "status_code": 200,
  "response": "<studentsList><student id=\"1\"><firstName>Greg</firstName><lastName>Dean</lastName></student></studentsList>",
  "enable": true,
  "mock_count": -1,
  "response_delay": 1,
  "response_media_type": "application/xml"
}
```

**Pass Through to Backend with Custom Headers:**
```json
{
  "method": "GET",
  "url": "api.example.com/.*",
  "call_backend": true,
  "custom_headers": {"X-Custom-Header": "custom-value"},
  "status_code": 200,
  "response": "{}",
  "enable": true,
  "mock_count": -1,
  "response_delay": 0,
  "response_media_type": "application/json"
}
```

## Health Checks

Moxie provides three health check endpoints for monitoring and orchestration:

```bash
# Simple health check (service is running)
curl http://localhost:8080/api/v1/healthcheck/

# Readiness probe (service is ready, database connected)
curl http://localhost:8080/api/v1/healthcheck/ready

# Liveness probe (process is alive)
curl http://localhost:8080/api/v1/healthcheck/live
```

Use these for Kubernetes probes or load balancer health checks.

## Development

### Auto-generate Alembic Migration
```bash
alembic revision --autogenerate -m 'migration_name'
```

### Run Migrations
```bash
alembic upgrade head
```

### Local Development Server
```bash
uvicorn app.main:app --reload --port 8080
```

### Run Tests
```bash
pytest
```

## Configuration

See [docs/CONNECTION_POOL_CONFIG.md](docs/CONNECTION_POOL_CONFIG.md) for detailed database connection pool tuning.

## Deployment

### Environment Variables

Key configuration via environment variables:

```env
# Database
DB_TYPE=postgresql              # sqlite, mysql, postgresql
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=secure_password
DB_DATABASE=statuscode_tool
DB_PORT=5432

# Connection Pool (see CONNECTION_POOL_CONFIG.md)
DB_POOL_SIZE=20
DB_POOL_MAX_OVERFLOW=10
DB_POOL_RECYCLE=3600

# Error Tracking (optional)
SENTRY_DSN=https://key@sentry.io/project

# Environment
ENV=production
RELEASE=0.1.0
```

### Docker

Build and run:
```bash
docker build -t moxie:latest .
docker run -p 8080:8080 --env-file .env moxie:latest
```

### Kubernetes

See [docs/API.md](docs/API.md#kubernetes-integration) for example deployment with health probes.

## Roadmap

- [x] Rule creation and management
- [x] Response mocking (JSON and XML)
- [x] Rule conflict detection
- [x] Rule import/export
- [x] Health checks and readiness probes
- [x] Connection pool configuration
- [ ] Response templates with dynamic values
- [ ] Rule grouping and state machines
- [ ] Metrics and analytics dashboard
- [ ] Webhook support for custom actions

## License

MIT
