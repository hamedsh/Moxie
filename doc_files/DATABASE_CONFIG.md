# Database Configuration Guide

This project now supports SQLite, MySQL, and PostgreSQL databases with configurable settings.

## Database Types

### SQLite (Default)
- **Best for**: Development, testing, and small deployments
- **No external dependencies**: Works out of the box
- **Configuration**:
  ```env
  DB_TYPE=sqlite
  DB_PATH=app.db
  ```

### MySQL
- **Best for**: Production environments with multiple connections
- **Requirements**: MySQL 5.7+ server
- **Configuration**:
  ```env
  DB_TYPE=mysql
  DB_HOST=localhost
  DB_PORT=3306
  DB_USER=root
  DB_PASSWORD=your_password
  DB_DATABASE=statuscode_tool
  ```

### PostgreSQL
- **Best for**: Production environments with advanced features
- **Requirements**: PostgreSQL 12+ server
- **Configuration**:
  ```env
  DB_TYPE=postgresql
  DB_HOST=postgres
  DB_PORT=5432
  DB_USER=postgres
  DB_PASSWORD=your_password
  DB_DATABASE=statuscode_tool
  ```

## Environment Variables

### Application Database
- `DB_TYPE`: Database type (sqlite, mysql, postgresql) - Default: `sqlite`
- `DB_PATH`: SQLite database file path - Default: `app.db`
- `DB_HOST`: Database server hostname
- `DB_PORT`: Database server port
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_DATABASE`: Database name

### Test Database
- `TEST_DB_TYPE`: Test database type - Default: `sqlite`
- `TEST_DB_PATH`: Test SQLite database file path - Default: `test_app.db`
- `TEST_DB_HOST`: Test database server hostname
- `TEST_DB_PORT`: Test database server port
- `TEST_DB_USER`: Test database username
- `TEST_DB_PASSWORD`: Test database password
- `TEST_DB_DATABASE`: Test database name

## Docker Usage

### Build with SQLite (Default)
```bash
docker build -t moxie:latest .
```

### Build with MySQL
```bash
docker build \
  --build-arg DB_TYPE=mysql \
  --build-arg DB_HOST=mysql_host \
  --build-arg DB_PORT=3306 \
  --build-arg DB_USER=root \
  --build-arg DB_PASSWORD=password \
  --build-arg DB_DATABASE=statuscode_tool \
  -t moxie:mysql .
```

### Build with PostgreSQL
```bash
docker build \
  --build-arg DB_TYPE=postgresql \
  --build-arg DB_HOST=postgres_host \
  --build-arg DB_PORT=5432 \
  --build-arg DB_USER=postgres \
  --build-arg DB_PASSWORD=password \
  --build-arg DB_DATABASE=statuscode_tool \
  -t moxie:postgres .
```

### Run Migrations During Docker Build
```bash
docker build \
  --build-arg RUN_MIGRATIONS=true \
  --build-arg DB_TYPE=sqlite \
  -t moxie:latest .
```

### Set Environment Variables at Runtime

If you need to override database settings at runtime, you can pass them when running the container:

```bash
docker run \
  -e DB_TYPE=mysql \
  -e DB_HOST=mysql_host \
  -e DB_PORT=3306 \
  -e DB_USER=root \
  -e DB_PASSWORD=password \
  -e DB_DATABASE=statuscode_tool \
  -p 8080:8080 \
  moxie:latest
```

## Running Migrations Locally

### Using Alembic directly

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### With SQLite
```bash
DB_TYPE=sqlite DB_PATH=app.db alembic upgrade head
```

### With MySQL
```bash
DB_TYPE=mysql DB_HOST=localhost DB_PORT=3306 DB_USER=root DB_PASSWORD=password DB_DATABASE=statuscode_tool alembic upgrade head
```

### With PostgreSQL
```bash
DB_TYPE=postgresql DB_HOST=localhost DB_PORT=5432 DB_USER=postgres DB_PASSWORD=password DB_DATABASE=statuscode_tool alembic upgrade head
```

## Example .env File

```env
# Database Type: sqlite, mysql, postgresql
DB_TYPE=sqlite

# SQLite Configuration
DB_PATH=app.db

# MySQL Configuration (uncomment and fill for MySQL)
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=your_password
# DB_DATABASE=statuscode_tool

# PostgreSQL Configuration (uncomment and fill for PostgreSQL)
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_DATABASE=statuscode_tool

# Test Database
TEST_DB_TYPE=sqlite
TEST_DB_PATH=test_app.db
```

## Development Setup

1. Copy `example.env` to `.env`:
   ```bash
   cp example.env .env
   ```

2. Choose your database type in `.env`:
   - For SQLite (default): No additional setup needed
   - For MySQL: Install MySQL and configure connection details
   - For PostgreSQL: Install PostgreSQL and configure connection details

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the development server:
   ```bash
   fastapi dev app/main.py
   ```

## Production Recommendations

- **Use PostgreSQL** for production environments with high concurrency
- **Enable connection pooling** for MySQL
- **Regular backups** of your database
- **Use strong passwords** and secure connection strings
- **Keep database versions updated** for security patches

## Troubleshooting

### SQLite Issues
- File permissions: Ensure the application has write permissions to the directory
- Concurrent access: SQLite is limited for concurrent writes; consider upgrading to PostgreSQL

### MySQL Issues
- Connection refused: Check MySQL is running and credentials are correct
- Character encoding: Ensure MySQL is using UTF-8

### PostgreSQL Issues
- Connection refused: Check PostgreSQL is running and credentials are correct
- SSL errors: Verify SSL configuration in connection string if needed

