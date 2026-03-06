"""
Tests for PostgreSQL AWS backend integration.
"""

import unittest
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured

from django_prometheus.db import (
    connections_total,
    connection_errors_total,
    aws_failover_success_total,
    aws_failover_failed_total,
    aws_transaction_resolution_unknown_total,
)


class PostgreSQLAWSBackendTest(TestCase):
    """Test the PostgreSQL AWS backend."""

    def setUp(self):
        """Set up test fixtures."""
        self.database_config = {
            'ENGINE': 'django_prometheus.db.backends.postgresql_aws',
            'HOST': 'test-cluster.cluster-xyz.us-east-1.rds.amazonaws.com',
            'NAME': 'testdb',
            'USER': 'testuser',
            'PASSWORD': 'testpass',
            'PORT': '5432',
            'OPTIONS': {
                'aws_plugins': 'failover,host_monitoring',
                'connect_timeout': 30,
                'socket_timeout': 30,
            },
        }

    @patch('django_prometheus.db.backends.postgresql_aws.base.psycopg')
    @patch('django_prometheus.db.backends.postgresql_aws.base.AwsWrapperConnection')
    def test_import_backend(self, mock_aws_wrapper, mock_psycopg):
        """Test that the backend can be imported without AWS wrapper."""
        try:
            from django_prometheus.db.backends.postgresql_aws.base import DatabaseWrapper
            self.assertIsNotNone(DatabaseWrapper)
        except ImportError:
            self.fail("Backend import should not fail when AWS wrapper is available")

    def test_import_error_without_aws_wrapper(self):
        """Test that backend raises ImproperlyConfigured without AWS wrapper."""
        with patch.dict('sys.modules', {'aws_advanced_python_wrapper': None}):
            with self.assertRaises(ImproperlyConfigured) as cm:
                from django_prometheus.db.backends.postgresql_aws.base import DatabaseWrapper
            self.assertIn("AWS Advanced Python Wrapper is required", str(cm.exception))

    @patch('django_prometheus.db.backends.postgresql_aws.base.psycopg')
    @patch('django_prometheus.db.backends.postgresql_aws.base.AwsWrapperConnection')
    def test_database_wrapper_initialization(self, mock_aws_wrapper, mock_psycopg):
        """Test DatabaseWrapper initialization with configuration options."""
        from django_prometheus.db.backends.postgresql_aws.base import DatabaseWrapper
        
        wrapper = DatabaseWrapper(self.database_config, alias='default')
        
        self.assertEqual(wrapper.aws_plugins, 'failover,host_monitoring')
        self.assertEqual(wrapper.connect_timeout, 30)
        self.assertEqual(wrapper.socket_timeout, 30)

    @patch('django_prometheus.db.backends.postgresql_aws.base.psycopg')
    @patch('django_prometheus.db.backends.postgresql_aws.base.AwsWrapperConnection')
    def test_default_configuration(self, mock_aws_wrapper, mock_psycopg):
        """Test DatabaseWrapper with default configuration."""
        from django_prometheus.db.backends.postgresql_aws.base import DatabaseWrapper
        
        config_without_options = self.database_config.copy()
        config_without_options.pop('OPTIONS')
        
        wrapper = DatabaseWrapper(config_without_options, alias='default')
        
        self.assertEqual(wrapper.aws_plugins, 'failover,host_monitoring')
        self.assertEqual(wrapper.connect_timeout, 30)
        self.assertEqual(wrapper.socket_timeout, 30)

    @patch('django_prometheus.db.backends.postgresql_aws.base.logger')
    @patch('django_prometheus.db.backends.postgresql_aws.base.psycopg')
    @patch('django_prometheus.db.backends.postgresql_aws.base.AwsWrapperConnection')
    def test_connection_creation_success(self, mock_aws_wrapper, mock_psycopg, mock_logger):
        """Test successful connection creation."""
        from django_prometheus.db.backends.postgresql_aws.base import DatabaseWrapper
        
        # Mock successful connection
        mock_connection = MagicMock()
        mock_aws_wrapper.connect.return_value = mock_connection
        
        wrapper = DatabaseWrapper(self.database_config, alias='default')
        
        conn_params = {
            'host': 'test-cluster.cluster-xyz.us-east-1.rds.amazonaws.com',
            'port': 5432,
            'database': 'testdb',
            'user': 'testuser',
            'password': 'testpass',
            'options': {}
        }
        
        # Record initial metric value
        initial_connections = connections_total.labels('default', 'postgresql')._value.get() or 0
        
        connection = wrapper.get_new_connection(conn_params)
        
        # Verify connection was created
        self.assertIsNotNone(connection)
        mock_aws_wrapper.connect.assert_called_once()
        
        # Verify metrics were updated
        final_connections = connections_total.labels('default', 'postgresql')._value.get()
        self.assertEqual(final_connections, initial_connections + 1)
        
        # Verify logging
        mock_logger.info.assert_called_with(
            "Successfully created AWS wrapper connection to test-cluster.cluster-xyz.us-east-1.rds.amazonaws.com:5432"
        )

    @patch('django_prometheus.db.backends.postgresql_aws.base.logger')
    @patch('django_prometheus.db.backends.postgresql_aws.base.psycopg')
    @patch('django_prometheus.db.backends.postgresql_aws.base.AwsWrapperConnection')
    def test_connection_creation_failure(self, mock_aws_wrapper, mock_psycopg, mock_logger):
        """Test connection creation failure."""
        from django_prometheus.db.backends.postgresql_aws.base import DatabaseWrapper
        
        # Mock connection failure
        mock_aws_wrapper.connect.side_effect = Exception("Connection failed")
        
        wrapper = DatabaseWrapper(self.database_config, alias='default')
        
        conn_params = {
            'host': 'test-cluster.cluster-xyz.us-east-1.rds.amazonaws.com',
            'port': 5432,
            'database': 'testdb',
            'user': 'testuser',
            'password': 'testpass',
            'options': {}
        }
        
        # Record initial metric values
        initial_connections = connections_total.labels('default', 'postgresql')._value.get() or 0
        initial_errors = connection_errors_total.labels('default', 'postgresql')._value.get() or 0
        
        with self.assertRaises(Exception):
            wrapper.get_new_connection(conn_params)
        
        # Verify metrics were updated
        final_connections = connections_total.labels('default', 'postgresql')._value.get()
        final_errors = connection_errors_total.labels('default', 'postgresql')._value.get()
        
        self.assertEqual(final_connections, initial_connections + 1)  # Connection attempt counted
        self.assertEqual(final_errors, initial_errors + 1)  # Error counted
        
        # Verify error logging
        mock_logger.error.assert_called_with("Failed to create AWS wrapper connection: Connection failed")

    @patch('django_prometheus.db.backends.postgresql_aws.base.psycopg')
    @patch('django_prometheus.db.backends.postgresql_aws.base.AwsWrapperConnection')
    def test_failover_success_metrics(self, mock_aws_wrapper, mock_psycopg):
        """Test that failover success metrics are recorded."""
        from django_prometheus.db.backends.postgresql_aws.base import AwsPrometheusCursor
        from aws_advanced_python_wrapper.errors import FailoverSuccessError
        
        # Create cursor instance
        mock_connection = MagicMock()
        cursor = AwsPrometheusCursor(mock_connection, 'default', 'postgresql')
        
        # Mock the parent execute to raise FailoverSuccessError on first call
        with patch.object(cursor.__class__.__bases__[0], 'execute') as mock_execute:
            mock_execute.side_effect = [FailoverSuccessError(), None]  # Fail then succeed
            
            # Record initial metric value
            initial_failovers = aws_failover_success_total.labels('default', 'postgresql')._value.get() or 0
            
            # Execute query
            cursor.execute("SELECT 1")
            
            # Verify metrics were updated
            final_failovers = aws_failover_success_total.labels('default', 'postgresql')._value.get()
            self.assertEqual(final_failovers, initial_failovers + 1)

    @patch('django_prometheus.db.backends.postgresql_aws.base.psycopg')
    @patch('django_prometheus.db.backends.postgresql_aws.base.AwsWrapperConnection')
    def test_failover_failed_metrics(self, mock_aws_wrapper, mock_psycopg):
        """Test that failover failure metrics are recorded."""
        from django_prometheus.db.backends.postgresql_aws.base import AwsPrometheusCursor
        from aws_advanced_python_wrapper.errors import FailoverFailedError
        
        # Create cursor instance
        mock_connection = MagicMock()
        cursor = AwsPrometheusCursor(mock_connection, 'default', 'postgresql')
        
        # Mock the parent execute to raise FailoverFailedError
        with patch.object(cursor.__class__.__bases__[0], 'execute') as mock_execute:
            mock_execute.side_effect = FailoverFailedError("Failover failed")
            
            # Record initial metric value
            initial_failures = aws_failover_failed_total.labels('default', 'postgresql')._value.get() or 0
            
            # Execute query and expect exception
            with self.assertRaises(FailoverFailedError):
                cursor.execute("SELECT 1")
            
            # Verify metrics were updated
            final_failures = aws_failover_failed_total.labels('default', 'postgresql')._value.get()
            self.assertEqual(final_failures, initial_failures + 1)

    @patch('django_prometheus.db.backends.postgresql_aws.base.psycopg')
    @patch('django_prometheus.db.backends.postgresql_aws.base.AwsWrapperConnection')
    def test_transaction_resolution_unknown_metrics(self, mock_aws_wrapper, mock_psycopg):
        """Test that transaction resolution unknown metrics are recorded."""
        from django_prometheus.db.backends.postgresql_aws.base import AwsPrometheusCursor
        from aws_advanced_python_wrapper.errors import TransactionResolutionUnknownError
        
        # Create cursor instance
        mock_connection = MagicMock()
        cursor = AwsPrometheusCursor(mock_connection, 'default', 'postgresql')
        
        # Mock the parent execute to raise TransactionResolutionUnknownError
        with patch.object(cursor.__class__.__bases__[0], 'execute') as mock_execute:
            mock_execute.side_effect = TransactionResolutionUnknownError("Unknown transaction state")
            
            # Record initial metric value
            initial_unknown = aws_transaction_resolution_unknown_total.labels('default', 'postgresql')._value.get() or 0
            
            # Execute query and expect exception
            with self.assertRaises(TransactionResolutionUnknownError):
                cursor.execute("SELECT 1")
            
            # Verify metrics were updated
            final_unknown = aws_transaction_resolution_unknown_total.labels('default', 'postgresql')._value.get()
            self.assertEqual(final_unknown, initial_unknown + 1)


if __name__ == '__main__':
    unittest.main()