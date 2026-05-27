# Database Backends

This directory contains Django database backends with Prometheus metrics integration.

## Available Backends

### Standard Backends

- **postgresql/** - PostgreSQL backend with Prometheus metrics
- **mysql/** - MySQL backend with Prometheus metrics  
- **sqlite3/** - SQLite3 backend with Prometheus metrics
- **postgis/** - PostGIS (PostgreSQL + GIS) backend with Prometheus metrics
- **spatialite/** - SpatiaLite (SQLite + GIS) backend with Prometheus metrics

### Enhanced Backends

- **postgresql_aws/** - PostgreSQL backend with AWS Advanced Python Wrapper integration

## PostgreSQL AWS Backend

The `postgresql_aws` backend extends the standard PostgreSQL backend with AWS Advanced Python Wrapper integration, providing automatic failover capabilities for Amazon RDS clusters while maintaining comprehensive Prometheus metrics collection.

### Features

- **Automatic Failover**: Seamlessly handles RDS cluster failovers using AWS Advanced Python Wrapper
- **Prometheus Metrics**: Collects all standard database metrics plus AWS-specific failover metrics
- **Connection Monitoring**: Built-in health checks and connection monitoring
- **Query Retry**: Automatically retries queries after successful failover
- **Error Handling**: Proper handling for failed failovers and transaction resolution issues

### AWS-Specific Metrics

The backend adds these additional Prometheus metrics:

- `django_db_aws_failover_success_total` - Counter of successful database failovers
- `django_db_aws_failover_failed_total` - Counter of failed database failovers  
- `django_db_aws_transaction_resolution_unknown_total` - Counter of transactions with unknown resolution status

### Usage

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.postgresql_aws',
        'HOST': 'database.cluster-xyz.us-east-1.rds.amazonaws.com',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'PORT': '5432',
        'OPTIONS': {
            'aws_plugins': 'failover,host_monitoring',  # AWS wrapper plugins
            'connect_timeout': 30,  # Connection timeout in seconds
            'socket_timeout': 30,   # Socket timeout in seconds
            # Additional psycopg connection options can be added here
        },
    }
}
```

### Prerequisites

1. Install the AWS Advanced Python Wrapper:
   ```bash
   pip install aws-advanced-python-wrapper
   ```

2. Configure your RDS cluster for failover (reader/writer endpoints)

3. Ensure proper IAM permissions for RDS cluster access

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `aws_plugins` | `'failover,host_monitoring'` | Comma-separated list of AWS wrapper plugins |
| `connect_timeout` | `30` | Connection timeout in seconds |
| `socket_timeout` | `30` | Socket timeout in seconds |

### Monitoring

The backend automatically logs failover events and metrics. Monitor these key indicators:

- Connection success/failure rates
- Failover frequency and success rates
- Query execution times during normal operation vs. failover
- Transaction resolution status

### Best Practices

1. **Connection Pooling**: Use with Django's database connection pooling
2. **Health Checks**: Monitor the failover metrics to detect cluster issues
3. **Timeout Configuration**: Tune timeout values based on your application requirements
4. **Testing**: Test failover scenarios in a staging environment
5. **Monitoring**: Set up alerts for failover events and failures

### Troubleshooting

- **ImportError**: Ensure `aws-advanced-python-wrapper` is installed
- **Connection Issues**: Verify RDS cluster configuration and IAM permissions
- **Slow Queries**: Monitor query duration metrics during failover events
- **Transaction Issues**: Check transaction resolution unknown metrics for application logic issues

For more information, see the [AWS Advanced Python Wrapper documentation](https://github.com/aws/aws-advanced-python-wrapper).

---

# Adding new database wrapper types

Unfortunately, I don't have the resources to create wrappers for all
database vendors. Doing so should be straightforward, but testing that
it works and maintaining it is a lot of busywork, or is impossible for
me for commercial databases.

This document should be enough for people who wish to implement a new
database wrapper.

## Structure

A database engine in Django requires 3 classes (it really requires 2,
but the 3rd one is required for our purposes):

* A DatabaseFeatures class, which describes what features the database
  supports. For our usage, we can simply extend the existing
  DatabaseFeatures class without any changes.
* A DatabaseWrapper class, which abstracts the interface to the
  database.
* A CursorWrapper class, which abstracts the interface to a cursor. A
  cursor is the object that can execute SQL statements via an open
  connection.

An easy example can be found in the sqlite3 module. Here are a few tips:

* The `self.alias` and `self.vendor` properties are present in all
  DatabaseWrappers.
* The CursorWrapper doesn't have access to the alias and vendor, so we
  generate the class in a function that accepts them as arguments.
* Most methods you overload should just increment a counter, forward
  all arguments to the original method and return the
  result. `execute` and `execute_many` should also wrap the call to
  the parent method in a `try...except` block to increment the
  `errors_total` counter as appropriate.
