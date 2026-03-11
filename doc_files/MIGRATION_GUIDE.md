# Migration & Deployment Guide

## Running Migrations Locally

### SQLite (Default)
```bash
# Ensure DB_PATH is set in .env or environment
DB_TYPE=sqlite DB_PATH=app.db alembic upgrade head

# Or with .env file present:
alembic upgrade head
```

### MySQL
```bash
export DB_TYPE=mysql
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=your_password
export DB_DATABASE=statuscode_tool

alembic upgrade head
```

### PostgreSQL
```bash
export DB_TYPE=postgresql
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_DATABASE=statuscode_tool

alembic upgrade head
```

## Creating New Migrations

```bash
# Auto-generate migration based on model changes
alembic revision --autogenerate -m "description of changes"

# Or create empty migration template
alembic revision -m "description of changes"
```

## Viewing Migration Status

```bash
# Show current revision
alembic current

# Show all revisions
alembic history --all

# Show pending migrations
alembic heads
```

## Rollback Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade ae92739891d7

# Rollback all
alembic downgrade base
```

## Docker Build with Migrations

### Build and Run Migrations in One Step

```bash
# SQLite
docker build \
  --build-arg DB_TYPE=sqlite \
  --build-arg RUN_MIGRATIONS=true \
  -t moxie:sqlite .

# MySQL
docker build \
  --build-arg DB_TYPE=mysql \
  --build-arg DB_HOST=mysql_db \
  --build-arg DB_PORT=3306 \
  --build-arg DB_USER=root \
  --build-arg DB_PASSWORD=password \
  --build-arg DB_DATABASE=statuscode_tool \
  --build-arg RUN_MIGRATIONS=true \
  -t moxie:mysql .

# PostgreSQL
docker build \
  --build-arg DB_TYPE=postgresql \
  --build-arg DB_HOST=postgres_db \
  --build-arg DB_PORT=5432 \
  --build-arg DB_USER=postgres \
  --build-arg DB_PASSWORD=password \
  --build-arg DB_DATABASE=statuscode_tool \
  --build-arg RUN_MIGRATIONS=true \
  -t moxie:postgres .
```

### Run Migrations After Container Startup

If you prefer to run migrations after the container starts:

```bash
# Build without migrations
docker build -t moxie:latest .

# Run container
docker run -d \
  -e DB_TYPE=mysql \
  -e DB_HOST=mysql_host \
  -e DB_USER=root \
  -e DB_PASSWORD=password \
  -e DB_DATABASE=statuscode_tool \
  --name moxie \
  -p 8080:8080 \
  moxie:latest

# Run migrations inside container
docker exec moxie alembic upgrade head
```

## Production Deployment Scenarios

### Scenario 1: MySQL on Separate Server

```bash
# Build image without migrations
docker build \
  --build-arg DB_TYPE=mysql \
  --build-arg DB_HOST=mysql.prod.example.com \
  --build-arg DB_USER=app_user \
  --build-arg DB_PASSWORD=secure_password \
  --build-arg DB_DATABASE=moxie_prod \
  -t moxie:1.0 .

# Run migrations before deploying new instances
docker run --rm \
  -e DB_TYPE=mysql \
  -e DB_HOST=mysql.prod.example.com \
  -e DB_USER=app_user \
  -e DB_PASSWORD=secure_password \
  -e DB_DATABASE=moxie_prod \
  moxie:1.0 \
  alembic upgrade head

# Deploy new instances
docker service update \
  --image moxie:1.0 \
  moxie_service
```

### Scenario 2: PostgreSQL with Kubernetes

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: moxie-migrations
spec:
  template:
    spec:
      containers:
      - name: moxie
        image: moxie:latest
        env:
        - name: DB_TYPE
          value: postgresql
        - name: DB_HOST
          value: postgres.default.svc.cluster.local
        - name: DB_PORT
          value: "5432"
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-creds
              key: user
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-creds
              key: password
        - name: DB_DATABASE
          value: moxie_prod
        command: ["alembic", "upgrade", "head"]
      restartPolicy: Never
  backoffLimit: 3
```

### Scenario 3: SQLite for Single-Instance Deployment

```bash
# Build with SQLite
docker build -t moxie:latest .

# Create volume for persistent storage
docker volume create moxie_data

# Run container
docker run -d \
  -v moxie_data:/app \
  -p 8080:8080 \
  --name moxie \
  moxie:latest

# Migrations will use embedded SQLite
```

## Troubleshooting Migrations

### Connection Error During Migration

**Problem**: `Can't connect to database server`

**Solution**:
```bash
# Verify database is running
mysql -h localhost -u root -p -e "SELECT 1;"

# Or for PostgreSQL
psql -h localhost -U postgres -c "SELECT 1;"

# Then retry migration
alembic upgrade head
```

### Migration File Conflict

**Problem**: Multiple migration files at same timestamp

**Solution**:
```bash
# Delete problematic auto-generated migrations
rm alembic/versions/xxxx_*.py

# Regenerate
alembic revision --autogenerate -m "description"
```

### Cannot Create Database

**Problem**: `Database does not exist`

**Solution for MySQL**:
```bash
mysql -h localhost -u root -p -e "CREATE DATABASE statuscode_tool;"
alembic upgrade head
```

**Solution for PostgreSQL**:
```bash
createdb -h localhost -U postgres statuscode_tool
alembic upgrade head
```

## Verifying Migrations

After running migrations, verify they were applied:

```bash
# Check current database schema
sqlite3 app.db ".schema"          # SQLite
mysql -e "SHOW TABLES;"            # MySQL
psql -l                            # PostgreSQL

# Check migration status
alembic current
alembic history --all
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Database Migrations

on:
  push:
    branches: [main]

jobs:
  migrate:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: statuscode_tool
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run migrations
        env:
          DB_TYPE: mysql
          DB_HOST: localhost
          DB_USER: root
          DB_PASSWORD: root
          DB_DATABASE: statuscode_tool
        run: alembic upgrade head
```

## Backup & Recovery

### Before Major Changes

```bash
# SQLite - simple file copy
cp app.db app.db.backup

# MySQL - dump database
mysqldump -u root -p statuscode_tool > backup.sql

# PostgreSQL - dump database
pg_dump -U postgres statuscode_tool > backup.sql
```

### Recovery

```bash
# SQLite - restore from backup
cp app.db.backup app.db

# MySQL - restore from dump
mysql -u root -p statuscode_tool < backup.sql

# PostgreSQL - restore from dump
psql -U postgres statuscode_tool < backup.sql
```

## Best Practices

1. **Always backup before migrations**: Especially in production
2. **Test migrations locally first**: Use docker-compose for testing
3. **Keep migration files in version control**: Include alembic/versions/
4. **Review auto-generated migrations**: Check for unintended changes
5. **Use consistent database names**: Across dev, test, and prod
6. **Document significant migrations**: Add comments in migration files
7. **Monitor migration execution time**: Long migrations may need optimization

