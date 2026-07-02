# Database Connection Pool Configuration Guide

## What is Connection Pooling?
Connection pooling maintains a set of reusable database connections, reducing the overhead of creating new connections for each request.

## Configuration Parameters

### DB_POOL_SIZE (default: 20)
- Number of connections to keep ready in the pool
- Increase for high-concurrency applications
- Recommended: 20-50 for typical APIs
- Too high can exhaust database resources

### DB_POOL_MAX_OVERFLOW (default: 10)
- Maximum additional connections beyond DB_POOL_SIZE when demand is high
- Total max connections = DB_POOL_SIZE + DB_POOL_MAX_OVERFLOW
- These temporary connections are closed when demand decreases
- Set to 0 to enforce strict pool size limit

### DB_POOL_RECYCLE (default: 3600 seconds = 1 hour)
- Automatically recycle connections after this duration
- Useful to handle database server timeouts and idle connection cleanup
- Set to -1 to disable recycling
- Typical values: 3600 (1 hour), 1800 (30 min), 900 (15 min)

### DB_POOL_PRE_PING (default: True)
- Send a test query before using a connection from the pool
- Catches connections that have been closed or timed out
- Slight performance overhead but prevents "connection lost" errors
- Disable only if you're confident connections won't be stale

### DB_ECHO (default: False)
- Log all SQL statements to help with debugging
- Enable only during development or troubleshooting
- Disable in production for performance

## Recommended Configurations

### Development (SQLite)
```
DB_TYPE=sqlite
DB_POOL_SIZE=1
DB_POOL_MAX_OVERFLOW=0
DB_ECHO=True
```

### Small Production (PostgreSQL/MySQL, <50 concurrent requests)
```
DB_TYPE=postgresql
DB_POOL_SIZE=20
DB_POOL_MAX_OVERFLOW=10
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=True
DB_ECHO=False
```

### Medium Production (100-200 concurrent requests)
```
DB_TYPE=postgresql
DB_POOL_SIZE=50
DB_POOL_MAX_OVERFLOW=20
DB_POOL_RECYCLE=1800
DB_POOL_PRE_PING=True
DB_ECHO=False
```

### High Concurrency (>200 concurrent requests)
```
DB_TYPE=postgresql
DB_POOL_SIZE=100
DB_POOL_MAX_OVERFLOW=50
DB_POOL_RECYCLE=900
DB_POOL_PRE_PING=True
DB_ECHO=False
```

## Troubleshooting

### "Too many connections" error
- Decrease DB_POOL_SIZE or DB_POOL_MAX_OVERFLOW
- Check database max_connections setting
- Ensure connections are being released properly

### "Connection timeout" errors
- Increase DB_POOL_SIZE
- Increase DB_POOL_MAX_OVERFLOW
- Check if connection wait time is acceptable

### Stale connection errors
- Enable DB_POOL_PRE_PING
- Decrease DB_POOL_RECYCLE
- Check database idle timeout settings

### Performance degradation
- Enable DB_ECHO to identify slow queries
- Check DB_POOL_PRE_PING overhead
- Consider using connection monitoring tools
