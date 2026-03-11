# SQLite & MySQL Support - Quick Reference Card

## 🚀 Quick Start (Choose One)

### Option 1: SQLite (Fastest, No Setup)
```bash
cp example.env .env
pip install -r requirements.txt
alembic upgrade head
fastapi dev app/main.py
```

### Option 2: Docker
```bash
docker build -t moxie .
docker run -p 8080:8080 moxie
```

### Option 3: Docker Compose (All Databases)
```bash
docker-compose up
# SQLite: http://localhost:8000
# PostgreSQL: http://localhost:8001
# MySQL: http://localhost:8002
```

---

## ⚙️ Configuration

### In `.env` File

**SQLite (Default - No Setup Required)**
```env
DB_TYPE=sqlite
DB_PATH=app.db
```

**MySQL**
```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_DATABASE=statuscode_tool
```

**PostgreSQL**
```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_DATABASE=statuscode_tool
```

---

## 🐳 Docker Build Examples

### SQLite
```bash
docker build -t moxie:sqlite .
```

### MySQL with Migrations
```bash
docker build \
  --build-arg DB_TYPE=mysql \
  --build-arg DB_HOST=mysql_host \
  --build-arg DB_USER=root \
  --build-arg DB_PASSWORD=password \
  --build-arg DB_DATABASE=statuscode_tool \
  --build-arg RUN_MIGRATIONS=true \
  -t moxie:mysql .
```

### PostgreSQL with Migrations
```bash
docker build \
  --build-arg DB_TYPE=postgresql \
  --build-arg DB_HOST=postgres_host \
  --build-arg DB_USER=postgres \
  --build-arg DB_PASSWORD=password \
  --build-arg DB_DATABASE=statuscode_tool \
  --build-arg RUN_MIGRATIONS=true \
  -t moxie:postgres .
```

---

## 🔄 Database Operations

### Run Migrations
```bash
alembic upgrade head
```

### Create New Migration
```bash
alembic revision --autogenerate -m "description"
```

### Rollback
```bash
alembic downgrade -1
```

### Check Status
```bash
alembic current
alembic history --all
```

---

## 📚 Documentation Files

| File | Purpose | Time |
|------|---------|------|
| [QUICKSTART.md](QUICKSTART.md) | Fast setup guide | 5 min |
| [DATABASE_CONFIG.md](DATABASE_CONFIG.md) | Full configuration | 20 min |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | Deployments | 30 min |
| [DEVELOPER_CHECKLIST.md](DEVELOPER_CHECKLIST.md) | Task list | 10 min |
| [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) | Navigation | 5 min |

---

## 🆘 Troubleshooting

### Database Connection Error
```bash
# For MySQL
mysql -h localhost -u root -p -e "SELECT 1;"

# For PostgreSQL
psql -h localhost -U postgres -c "SELECT 1;"
```

### Reset Database (SQLite Only)
```bash
rm app.db test_app.db
alembic upgrade head
```

### Clear Docker
```bash
docker system prune
docker-compose down -v
```

---

## 📦 New Dependencies

- `aiomysql>=0.2.0` - Async MySQL
- `pymysql>=1.1.0` - MySQL migrations
- `aiosqlite>=0.20.0` - Async SQLite

---

## 🎯 Key Features

✅ Zero-config SQLite development
✅ MySQL production support
✅ PostgreSQL production support
✅ Docker build-time configuration
✅ Runtime environment override
✅ Optional automatic migrations
✅ Full Docker Compose support
✅ Complete documentation

---

## 💻 System Requirements

- Python 3.13+
- SQLAlchemy 2.0.48+
- Alembic 1.18.4+
- Docker (optional)
- Docker Compose (optional)

---

## 📋 Files Modified

1. `pyproject.toml` - Added database drivers
2. `app/core/config.py` - Multi-database config
3. `app/core/session.py` - Database-specific setup
4. `alembic/env.py` - Migration support
5. `Dockerfile` - Configurable builds
6. `example.env` - Configuration template
7. `requirements.txt` - Updated dependencies

---

## 📄 Files Created

1. `docker-compose.yml` - Multi-database testing
2. 8 documentation files - Guides and references

---

## 🔗 Quick Links

- **Start Here**: [QUICKSTART.md](QUICKSTART.md)
- **Navigation**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- **Configuration**: [DATABASE_CONFIG.md](DATABASE_CONFIG.md)
- **Deployment**: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Checklist**: [DEVELOPER_CHECKLIST.md](DEVELOPER_CHECKLIST.md)

---

## ✨ You're Ready!

Everything is set up and ready to use. Start with [QUICKSTART.md](QUICKSTART.md) and you'll be running in 5 minutes.

**Status**: ✅ Complete & Tested

