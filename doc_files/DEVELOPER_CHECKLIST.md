# Developer Checklist - Database Configuration

## ✅ Local Development Setup

- [ ] Copy `example.env` to `.env`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Choose database type in `.env`:
  - [ ] SQLite (default - no additional setup needed)
  - [ ] MySQL (setup instructions below)
  - [ ] PostgreSQL (setup instructions below)
- [ ] Run migrations: `alembic upgrade head`
- [ ] Start development server: `fastapi dev app/main.py`
- [ ] Verify application starts: `curl http://localhost:8000/`

## 🗄️ Database Setup (Choose One)

### SQLite Setup
- [ ] Edit `.env`:
  ```
  DB_TYPE=sqlite
  DB_PATH=app.db
  ```
- [ ] Database file will be created automatically

### MySQL Setup
- [ ] Install MySQL server (or use Docker)
- [ ] Create database: `mysql -u root -p -e "CREATE DATABASE statuscode_tool;"`
- [ ] Edit `.env`:
  ```
  DB_TYPE=mysql
  DB_HOST=localhost
  DB_PORT=3306
  DB_USER=root
  DB_PASSWORD=your_password
  DB_DATABASE=statuscode_tool
  ```
- [ ] Test connection: `mysql -u root -p statuscode_tool -e "SELECT 1;"`

### PostgreSQL Setup
- [ ] Install PostgreSQL server (or use Docker)
- [ ] Create database: `createdb statuscode_tool`
- [ ] Edit `.env`:
  ```
  DB_TYPE=postgresql
  DB_HOST=localhost
  DB_PORT=5432
  DB_USER=postgres
  DB_PASSWORD=your_password
  DB_DATABASE=statuscode_tool
  ```
- [ ] Test connection: `psql -U postgres statuscode_tool -c "SELECT 1;"`

## 🐳 Docker Setup

### Build Docker Image
- [ ] Build with SQLite: `docker build -t moxie:latest .`
- [ ] Build with MySQL: `docker build --build-arg DB_TYPE=mysql ... -t moxie:mysql .`
- [ ] Build with PostgreSQL: `docker build --build-arg DB_TYPE=postgresql ... -t moxie:postgres .`

### Run Docker Container
- [ ] SQLite: `docker run -p 8080:8080 moxie:latest`
- [ ] MySQL: `docker run -e DB_TYPE=mysql -e DB_HOST=mysql_host ... -p 8080:8080 moxie:mysql`
- [ ] PostgreSQL: `docker run -e DB_TYPE=postgresql -e DB_HOST=postgres_host ... -p 8080:8080 moxie:postgres`
- [ ] Verify: `curl http://localhost:8080/`

### Docker Compose
- [ ] Start services: `docker-compose up -d`
- [ ] Check running services: `docker-compose ps`
- [ ] View logs: `docker-compose logs -f moxie-sqlite`
- [ ] Stop services: `docker-compose down`

## 📦 Dependencies

- [ ] Verify all drivers installed: `pip list | grep -E "aiomysql|pymysql|aiosqlite"`
- [ ] Check requirements.txt includes:
  - [ ] `aiomysql>=0.2.0` - Async MySQL
  - [ ] `pymysql>=1.1.0` - MySQL migrations
  - [ ] `aiosqlite>=0.20.0` - Async SQLite
  - [ ] `asyncpg>=0.31.0` - PostgreSQL
  - [ ] `psycopg2>=2.9.11` - PostgreSQL migrations

## 🔄 Database Operations

### Migrations
- [ ] Check current migration: `alembic current`
- [ ] View migration history: `alembic history --all`
- [ ] Create new migration: `alembic revision --autogenerate -m "description"`
- [ ] Apply migrations: `alembic upgrade head`
- [ ] Rollback: `alembic downgrade -1`

### Database Verification
- [ ] View schema: 
  - SQLite: `sqlite3 app.db ".schema"`
  - MySQL: `mysql -u root -p statuscode_tool -e "SHOW TABLES;"`
  - PostgreSQL: `psql -U postgres statuscode_tool -c "\dt"`

## 🧪 Testing

### Unit Tests
- [ ] Run all tests: `pytest`
- [ ] Run with coverage: `pytest --cov`
- [ ] Run specific test: `pytest tests/api/test_rule.py`

### Database Tests
- [ ] Test with SQLite: `DB_TYPE=sqlite pytest`
- [ ] Test with MySQL: `DB_TYPE=mysql pytest`
- [ ] Test with PostgreSQL: `DB_TYPE=postgresql pytest`

### Integration Tests
- [ ] Test with docker-compose: `docker-compose up && docker-compose exec moxie-sqlite pytest`

## 📝 Code Quality

- [ ] Linting: `flake8 app/`
- [ ] Type checking: `mypy app/`
- [ ] Formatting: `isort app/`
- [ ] All files compile: `python -m py_compile app/core/config.py app/core/session.py`

## 🚀 Before Commit

- [ ] All tests pass
- [ ] Code passes linting
- [ ] Database migrations are versioned
- [ ] `.env` is in `.gitignore`
- [ ] `example.env` is updated with new variables
- [ ] Documentation is updated

## 🚀 Before Production Deploy

- [ ] Backup production database
- [ ] Test migrations on staging
- [ ] Review all pending migrations
- [ ] Verify database user permissions
- [ ] Test with production-like data volume
- [ ] Monitor first deployment closely
- [ ] Have rollback plan ready

## 📚 Documentation Checklist

- [ ] Read QUICKSTART.md
- [ ] Review DATABASE_CONFIG.md
- [ ] Study MIGRATION_GUIDE.md
- [ ] Check IMPLEMENTATION_SUMMARY.md
- [ ] Review DATABASE_SUPPORT.md

## 🆘 Troubleshooting Checklist

If something breaks:
- [ ] Check `.env` file exists and is readable
- [ ] Verify database credentials in `.env`
- [ ] Confirm database service is running
- [ ] Check database user has correct permissions
- [ ] Review logs: `docker-compose logs moxie-sqlite`
- [ ] Test database connection directly
- [ ] Run migrations in isolation: `alembic upgrade head`
- [ ] Clear any cached data or containers
- [ ] Consult relevant documentation file

## 🔒 Security Checklist

- [ ] Never commit `.env` file
- [ ] Use strong passwords for production
- [ ] Don't store passwords in code
- [ ] Use environment variables for secrets
- [ ] Rotate database passwords regularly
- [ ] Use separate databases for dev/test/prod
- [ ] Enable database authentication
- [ ] Use SSL/TLS for remote databases
- [ ] Limit database user permissions
- [ ] Audit database access logs

---

**Status**: Ready for Development
**Last Updated**: March 2026

