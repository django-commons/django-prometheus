"""PostgreSQL database backend with AWS Advanced Python Wrapper integration.

This backend provides automatic failover capabilities for Amazon RDS clusters
while maintaining comprehensive Prometheus metrics collection.

Usage in Django settings:

    DATABASES = {
        'default': {
            'ENGINE': 'django_prometheus.db.backends.postgresql_aws',
            'HOST': 'database.cluster-xyz.us-east-1.rds.amazonaws.com',
            'NAME': 'mydb',
            'USER': 'myuser',
            'PASSWORD': 'mypassword',
            'PORT': '5432',
            'OPTIONS': {
                'aws_plugins': 'failover,host_monitoring',
                'connect_timeout': 30,
                'socket_timeout': 30,
            },
        }
    }

The backend automatically handles:
- Database failover for RDS clusters
- Connection monitoring and health checks  
- Prometheus metrics for all database operations
- Query retry on successful failover
- Proper error handling for failed failovers
"""