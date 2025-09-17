# SQL Server MCP Server - Deployment Guide

This guide covers deployment options, configuration, and operational considerations for the SQL Server MCP Server in various environments.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [Deployment Options](#deployment-options)
- [Production Considerations](#production-considerations)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10/11, Ubuntu 18.04+, CentOS 7+, macOS 10.15+
- **Python**: 3.8 or higher
- **Memory**: 512 MB RAM minimum, 2 GB recommended
- **Storage**: 100 MB for application, additional space for logs
- **Network**: Access to SQL Server instance

### Recommended Requirements

- **Operating System**: Windows Server 2019+, Ubuntu 20.04+, CentOS 8+
- **Python**: 3.11 or higher
- **Memory**: 4 GB RAM or more
- **Storage**: SSD with 1 GB+ available space
- **Network**: Low-latency connection to SQL Server

### SQL Server Requirements

- **SQL Server**: 2016 or higher
- **Authentication**: Windows Authentication or SQL Server Authentication
- **ODBC Driver**: ODBC Driver 17 for SQL Server or higher
- **Permissions**: Appropriate database access permissions

## Installation Methods

### 1. PyPI Installation (Recommended)

```bash
# Install from PyPI
pip install sqlserver-mcp-server

# Install with development dependencies
pip install sqlserver-mcp-server[dev]
```

### 2. Source Installation

```bash
# Clone repository
git clone https://github.com/your-org/sqlserver-mcp-server.git
cd sqlserver-mcp-server

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### 3. Docker Installation

```bash
# Pull Docker image
docker pull sqlserver-mcp-server:latest

# Run container
docker run -d \
  --name sqlserver-mcp \
  -p 8000:8000 \
  -e SQLSERVER_MCP_SERVER_HOST=0.0.0.0 \
  -e SQLSERVER_MCP_SERVER_PORT=8000 \
  sqlserver-mcp-server:latest
```

### 4. System Package Installation

#### Ubuntu/Debian

```bash
# Add repository (when available)
curl -fsSL https://packages.sqlserver-mcp.com/ubuntu/gpg | sudo apt-key add -
echo "deb https://packages.sqlserver-mcp.com/ubuntu/ focal main" | sudo tee /etc/apt/sources.list.d/sqlserver-mcp.list

# Install package
sudo apt update
sudo apt install sqlserver-mcp-server
```

#### CentOS/RHEL

```bash
# Add repository (when available)
sudo yum-config-manager --add-repo https://packages.sqlserver-mcp.com/centos/sqlserver-mcp.repo

# Install package
sudo yum install sqlserver-mcp-server
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SQLSERVER_MCP_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO | No |
| `SQLSERVER_MCP_SERVER_HOST` | Server host address | 127.0.0.1 | No |
| `SQLSERVER_MCP_SERVER_PORT` | Server port | 8000 | No |
| `SQLSERVER_MCP_CONFIG_FILE` | Configuration file path | config.json | No |
| `SQLSERVER_MCP_LOG_FILE` | Log file path | logs/mcp-server.log | No |

### Configuration File

Create `config.json`:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8000,
    "workers": 4
  },
  "logging": {
    "level": "INFO",
    "file": "logs/mcp-server.log",
    "max_size": "10MB",
    "backup_count": 5,
    "format": "json"
  },
  "database": {
    "default_timeout": 30,
    "max_pool_size": 10,
    "min_pool_size": 2,
    "pool_timeout": 30
  },
  "security": {
    "encrypt_connections": true,
    "trust_server_certificate": false,
    "connection_timeout": 30
  },
  "performance": {
    "query_timeout": 300,
    "max_result_rows": 10000,
    "enable_caching": true,
    "cache_ttl": 3600
  }
}
```

### Connection Configuration

#### Windows Authentication

```json
{
  "connections": {
    "default": {
      "server": "localhost",
      "database": "master",
      "trusted_connection": true,
      "encrypt": true
    }
  }
}
```

#### SQL Server Authentication

```json
{
  "connections": {
    "default": {
      "server": "localhost",
      "database": "master",
      "username": "sa",
      "password": "your_password",
      "trusted_connection": false,
      "encrypt": true
    }
  }
}
```

## Deployment Options

### 1. Standalone Deployment

#### Windows Service

```powershell
# Install as Windows Service
sc create "SQL Server MCP Server" binPath="C:\Python\Scripts\sqlserver-mcp.exe" start=auto
sc start "SQL Server MCP Server"
```

#### Linux Systemd Service

Create `/etc/systemd/system/sqlserver-mcp.service`:

```ini
[Unit]
Description=SQL Server MCP Server
After=network.target

[Service]
Type=simple
User=mcp-server
Group=mcp-server
WorkingDirectory=/opt/sqlserver-mcp-server
ExecStart=/opt/sqlserver-mcp-server/venv/bin/python -m src.mcp_tools
Restart=always
RestartSec=10
Environment=SQLSERVER_MCP_LOG_LEVEL=INFO
Environment=SQLSERVER_MCP_CONFIG_FILE=/etc/sqlserver-mcp-server/config.json

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl enable sqlserver-mcp
sudo systemctl start sqlserver-mcp
sudo systemctl status sqlserver-mcp
```

### 2. Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config.json .

# Create non-root user
RUN useradd -m -u 1000 mcp-server
USER mcp-server

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "-m", "src.mcp_tools"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  sqlserver-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SQLSERVER_MCP_LOG_LEVEL=INFO
      - SQLSERVER_MCP_SERVER_HOST=0.0.0.0
      - SQLSERVER_MCP_SERVER_PORT=8000
    volumes:
      - ./config.json:/app/config.json:ro
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: SQL Server for testing
  sqlserver:
    image: mcr.microsoft.com/mssql/server:2019-latest
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=YourStrong@Passw0rd
    ports:
      - "1433:1433"
    volumes:
      - sqlserver_data:/var/opt/mssql

volumes:
  sqlserver_data:
```

### 3. Kubernetes Deployment

#### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sqlserver-mcp-server
  labels:
    app: sqlserver-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sqlserver-mcp-server
  template:
    metadata:
      labels:
        app: sqlserver-mcp-server
    spec:
      containers:
      - name: sqlserver-mcp-server
        image: sqlserver-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: SQLSERVER_MCP_LOG_LEVEL
          value: "INFO"
        - name: SQLSERVER_MCP_SERVER_HOST
          value: "0.0.0.0"
        - name: SQLSERVER_MCP_SERVER_PORT
          value: "8000"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: sqlserver-mcp-server-service
spec:
  selector:
    app: sqlserver-mcp-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 4. Cloud Deployment

#### AWS ECS

```json
{
  "family": "sqlserver-mcp-server",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "sqlserver-mcp-server",
      "image": "your-account.dkr.ecr.region.amazonaws.com/sqlserver-mcp-server:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "SQLSERVER_MCP_LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/sqlserver-mcp-server",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

## Production Considerations

### Performance Optimization

1. **Connection Pooling**
   ```json
   {
     "database": {
       "max_pool_size": 20,
       "min_pool_size": 5,
       "pool_timeout": 30
     }
   }
   ```

2. **Caching Configuration**
   ```json
   {
     "performance": {
       "enable_caching": true,
       "cache_ttl": 3600,
       "max_cache_size": "100MB"
     }
   }
   ```

3. **Query Optimization**
   ```json
   {
     "performance": {
       "query_timeout": 300,
       "max_result_rows": 10000,
       "enable_query_plan_caching": true
     }
   }
   ```

### High Availability

1. **Load Balancing**
   - Use multiple instances behind a load balancer
   - Configure health checks
   - Implement graceful shutdown

2. **Database Redundancy**
   - Use SQL Server Always On Availability Groups
   - Configure automatic failover
   - Monitor connection health

3. **Monitoring**
   - Set up comprehensive monitoring
   - Configure alerts for critical metrics
   - Implement log aggregation

### Security Hardening

1. **Network Security**
   - Use TLS/SSL for all connections
   - Implement firewall rules
   - Use VPN or private networks

2. **Authentication**
   - Use Windows Authentication when possible
   - Implement strong password policies
   - Use service accounts with minimal privileges

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Use encrypted connections
   - Implement audit logging

## Monitoring and Maintenance

### Health Checks

#### HTTP Health Endpoint

```bash
# Check server health
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "timestamp": "2025-01-27T14:17:00Z",
  "uptime_seconds": 3600,
  "active_connections": 5,
  "total_queries": 1250
}
```

#### CLI Health Check

```bash
# Check connection health
sqlserver-mcp connection health <connection-id>

# Check server status
sqlserver-mcp server status
```

### Logging

#### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General information about operations
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations

#### Log Rotation

```json
{
  "logging": {
    "file": "logs/mcp-server.log",
    "max_size": "10MB",
    "backup_count": 5,
    "rotation": "daily"
  }
}
```

### Metrics Collection

#### Key Metrics

- **Connection Metrics**: Active connections, pool utilization
- **Query Metrics**: Execution time, success rate, error rate
- **Performance Metrics**: Memory usage, CPU utilization
- **Business Metrics**: Queries per second, response time

#### Prometheus Integration

```python
# Example metrics endpoint
from prometheus_client import Counter, Histogram, generate_latest

query_counter = Counter('sqlserver_mcp_queries_total', 'Total queries executed')
query_duration = Histogram('sqlserver_mcp_query_duration_seconds', 'Query execution time')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

## Troubleshooting

### Common Issues

#### Connection Issues

**Problem**: Cannot connect to SQL Server
```bash
# Check connection string
sqlserver-mcp connection test --server localhost --database master

# Check ODBC driver
odbcinst -q -d -n "ODBC Driver 17 for SQL Server"
```

**Solution**:
1. Verify SQL Server is running
2. Check network connectivity
3. Verify authentication credentials
4. Ensure ODBC driver is installed

#### Performance Issues

**Problem**: Slow query execution
```bash
# Check query performance
sqlserver-mcp query profile <connection-id> "SELECT * FROM large_table"
```

**Solution**:
1. Optimize SQL queries
2. Increase connection pool size
3. Enable query caching
4. Check database indexes

#### Memory Issues

**Problem**: High memory usage
```bash
# Check memory usage
sqlserver-mcp server stats
```

**Solution**:
1. Reduce connection pool size
2. Limit result set sizes
3. Enable result streaming
4. Monitor for memory leaks

### Debug Mode

Enable debug logging:

```bash
export SQLSERVER_MCP_LOG_LEVEL=DEBUG
python -m src.mcp_tools
```

### Log Analysis

```bash
# Search for errors
grep "ERROR" logs/mcp-server.log

# Monitor real-time logs
tail -f logs/mcp-server.log

# Analyze performance
grep "execution_time" logs/mcp-server.log | awk '{print $NF}' | sort -n
```

## Security Considerations

### Network Security

1. **Firewall Configuration**
   ```bash
   # Allow only necessary ports
   ufw allow 8000/tcp
   ufw allow 1433/tcp  # SQL Server
   ```

2. **TLS/SSL Configuration**
   ```json
   {
     "security": {
       "tls_enabled": true,
       "tls_cert_file": "/path/to/cert.pem",
       "tls_key_file": "/path/to/key.pem"
     }
   }
   ```

### Authentication Security

1. **Service Account Configuration**
   - Use dedicated service accounts
   - Grant minimal required permissions
   - Rotate credentials regularly

2. **Connection Security**
   ```json
   {
     "security": {
       "encrypt_connections": true,
       "trust_server_certificate": false,
       "connection_timeout": 30
     }
   }
   ```

### Data Protection

1. **Sensitive Data Handling**
   - Never log passwords or sensitive data
   - Use environment variables for secrets
   - Implement data encryption

2. **Audit Logging**
   ```json
   {
     "audit": {
       "enabled": true,
       "log_queries": true,
       "log_connections": true,
       "retention_days": 90
     }
   }
   ```

---

*Deployment Guide Version: 1.0.0 | Last Updated: 2025-01-27*
