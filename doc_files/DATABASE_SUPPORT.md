# Database Support Enhancement - Complete Feature Overview

## 🎯 Summary

The Moxie project now supports **three database backends** with seamless switching and Docker configuration:
- **SQLite** (Default) - Zero-configuration development
- **MySQL** - Production-grade relational database
- **PostgreSQL** - Full-featured relational database

## 🚀 Quick Start

### Option 1: SQLite (Fastest, No Setup Required)
```bash
cp example.env .env
pip install -r requirements.txt
alembic upgrade head
fastapi dev app/main.py
```

### Option 2: Docker with SQLite
```bash
docker build -t moxie .
docker run -p 8080:8080 moxie
```

### Option 3: Docker Compose (All Databases)
```bash
docker-compose up
```

## 📋 Configuration

### Environment Variables

| Variable | Default | Options |
|----------|---------|---------|
| `DB_TYPE` | `sqlite` | `sqlite`, `mysql`, `postgresql` |
| `DB_PATH` | `app.db` | Any file path (SQLite only) |
| `DB_HOST` | - | Hostname/IP |
| `DB_PORT` | - | Port number |
| `DB_USER` | - | Database user |
| `DB_PASSWORD` | - | Database password |
| `DB_DATABASE` | - | Database name |

### Example Configurations

**SQLite (default)**:
```env
DB_TYPE=sqlite
DB_PATH=app.db
```

**MySQL**:
```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_DATABASE=statuscode_tool
```

**PostgreSQL**:
```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_DATABASE=statuscode_tool
```

## 🐳 Docker Usage

### Building Images

```bash
# SQLite (default)
docker build -t moxie:sqlite .

# MySQL with migrations
docker build \
  --build-arg DB_TYPE=mysql \
  --build-arg DB_HOST=mysql_host \
  --build-arg DB_USER=root \
  --build-arg DB_PASSWORD=password \
  --build-arg DB_DATABASE=statuscode_tool \
  --build-arg RUN_MIGRATIONS=true \
  -t moxie:mysql .

# PostgreSQL with migrations
docker build \
  --build-arg DB_TYPE=postgresql \
  --build-arg DB_HOST=postgres_host \
  --build-arg DB_USER=postgres \
  --build-arg DB_PASSWORD=password \
  --build-arg DB_DATABASE=statuscode_tool \
  --build-arg RUN_MIGRATIONS=true \
  -t moxie:postgres .
```

### Running Containers

```bash
# SQLite
docker run -p 8080:8080 moxie:sqlite

# MySQL
docker run \
  -e DB_TYPE=mysql \
  -e DB_HOST=mysql_host \
  -e DB_USER=root \
  -e DB_PASSWORD=password \
  -p 8080:8080 \
  moxie:mysql

# PostgreSQL
docker run \
  -e DB_TYPE=postgresql \
  -e DB_HOST=postgres_host \
  -e DB_USER=postgres \
  -e DB_PASSWORD=password \
  -p 8080:8080 \
  moxie:postgres
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Fast setup guide
- **[DATABASE_CONFIG.md](DATABASE_CONFIG.md)** - Detailed configuration reference
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migration and deployment guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## 🔄 Switching Databases

### From SQLite to MySQL

1. **Update environment**:
```bash
# Edit .env
DB_TYPE=mysql
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_DATABASE=statuscode_tool
```

2. **Create database**:
```bash
mysql -u root -p -e "CREATE DATABASE statuscode_tool;"
```

3. **Run migrations**:
```bash
alembic upgrade head
```

### From SQLite to PostgreSQL

1. **Update environment**:
```bash
# Edit .env
DB_TYPE=postgresql
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=password
DB_DATABASE=statuscode_tool
```

2. **Create database**:
```bash
createdb statuscode_tool
```

3. **Run migrations**:
```bash
alembic upgrade head
```

## ✨ Key Features

- ✅ **Zero Configuration Development** - SQLite needs no external setup
- ✅ **Flexible Database Selection** - Choose the right database for your use case
- ✅ **Docker Build-time Configuration** - Set database details during image build
- ✅ **Runtime Configuration** - Override settings via environment variables
- ✅ **Automatic Migrations** - Optional automatic migrations during Docker build
- ✅ **Backward Compatible** - Existing PostgreSQL setups continue to work
- ✅ **Docker Compose Ready** - Test multiple databases simultaneously

## 🛠 What Changed

### Files Modified
- `pyproject.toml` - Added database drivers
- `app/core/config.py` - Multi-database configuration
- `app/core/session.py` - Database-specific session setup
- `alembic/env.py` - Migration support for all databases
- `Dockerfile` - Configurable build arguments
- `example.env` - Configuration template
- `requirements.txt` - Auto-generated with new dependencies

### Files Created
- `docker-compose.yml` - Complete Docker Compose setup
- `DATABASE_CONFIG.md` - Configuration guide
- `QUICKSTART.md` - Quick reference
- `MIGRATION_GUIDE.md` - Deployment guide
- `IMPLEMENTATION_SUMMARY.md` - Technical overview

## 📦 New Dependencies

```
aiomysql>=0.2.0      # Async MySQL driver
pymysql>=1.1.0       # Sync MySQL driver for migrations
aiosqlite>=0.20.0    # Async SQLite driver
```

All existing dependencies remain unchanged.

## 🧪 Testing

```bash
# With SQLite
DB_TYPE=sqlite pytest

# With MySQL
DB_TYPE=mysql DB_HOST=localhost pytest

# With PostgreSQL  
DB_TYPE=postgresql DB_HOST=localhost pytest

# Using Docker Compose
docker-compose up
# Then run tests against different database URLs
```

## 🚨 Important Notes

1. **SQLite** - Ideal for development and testing; limited concurrent writes
2. **MySQL** - Good for production; widely supported and scalable
3. **PostgreSQL** - Best for production; advanced features and reliability
4. **Migrations** - Always test migrations on a backup before production

## 📈 Production Recommendations

- Use **PostgreSQL** for critical production systems
- Use **MySQL** for high-volume applications
- Use **SQLite** only for single-server, low-concurrency systems
- Always backup database before migrations
- Use separate databases for development, testing, and production
- Monitor migration execution time for performance
- Consider read replicas for PostgreSQL in high-traffic scenarios

## 🆘 Troubleshooting

### Connection Refused
- Verify database service is running
- Check credentials are correct
- Ensure network connectivity between services

### Migration Fails
- Verify database exists and is accessible
- Check database user has appropriate permissions
- Review migration files for compatibility

### SQLite File Permissions
- Ensure app has write access to directory
- Use volume mounts in Docker for persistence

## 🎓 Learning Resources

- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Migration Documentation](https://alembic.sqlalchemy.org/)
- [MySQL Async Python Drivers](https://github.com/aiomysql/aiomysql)
- [SQLite Async Python Drivers](https://github.com/omnilib/aiosqlite)

## 📞 Support

For issues or questions:
1. Check relevant documentation files
2. Review configuration in `example.env`
3. Test with `docker-compose.yml`
4. Check Alembic migration status with `alembic current`

---

**Last Updated**: March 2026
**Status**: ✅ Production Ready
**Compatibility**: Python 3.13+, SQLAlchemy 2.0.48+, Alembic 1.18.4+

