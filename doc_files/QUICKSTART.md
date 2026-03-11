# Quick Start Guide - Database Configuration

This guide shows the fastest way to get started with different database backends.

## Quickest Setup (SQLite - Recommended for Development)

```bash
# 1. Copy example config
cp example.env .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
alembic upgrade head

# 4. Start the app
fastapi dev app/main.py
```

That's it! SQLite is the default and needs no external setup.

## Docker Quick Start

### With SQLite (Single container)
```bash
docker build -t moxie:latest .
docker run -p 8080:8080 moxie:latest
```

### With PostgreSQL + Docker Compose
```bash
docker-compose up -d
# App available at http://localhost:8001
# Database: postgres://postgres:111111@localhost:5432/statuscode_tool
```

### With MySQL + Docker Compose
```bash
docker-compose up -d mysql moxie-mysql
# App available at http://localhost:8002
# Database: mysql://moxie_user:moxie_password@localhost:3306/statuscode_tool
```

## Database Type Cheat Sheet

| Database | Setup Time | Concurrency | External Service | Best For |
|----------|-----------|------------|-------------------|----------|
| SQLite | Instant | Low | No | Development |
| MySQL | 5 mins | High | Yes | Production |
| PostgreSQL | 5 mins | High | Yes | Production |

## Switching Databases

### SQLite to PostgreSQL

1. Update `.env`:
```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_DATABASE=statuscode_tool
```

2. Reset and migrate:
```bash
alembic upgrade head
```

### SQLite to MySQL

1. Update `.env`:
```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_DATABASE=statuscode_tool
```

2. Reset and migrate:
```bash
alembic upgrade head
```

## Docker Build with Migrations

Run migrations during Docker build:

```bash
docker build \
  --build-arg DB_TYPE=mysql \
  --build-arg DB_HOST=mysql_db \
  --build-arg DB_USER=root \
  --build-arg DB_PASSWORD=password \
  --build-arg DB_DATABASE=statuscode_tool \
  --build-arg RUN_MIGRATIONS=true \
  -t moxie:mysql .
```

## Troubleshooting

**Port already in use?**
```bash
docker run -p 8888:8080 moxie:latest  # Use different port
```

**Need to reset database?**
```bash
# For SQLite
rm app.db test_app.db
alembic upgrade head

# For MySQL/PostgreSQL
# Drop and recreate the database, then run:
alembic upgrade head
```

**Connection refused?**
- SQLite: Check file permissions
- MySQL/PostgreSQL: Ensure service is running and credentials are correct

## Next Steps

- See [DATABASE_CONFIG.md](DATABASE_CONFIG.md) for detailed configuration
- See [DOCKER_EXAMPLES.md](DOCKER_EXAMPLES.md) for advanced Docker usage (in progress)
- Check `example.env` for all available configuration options

