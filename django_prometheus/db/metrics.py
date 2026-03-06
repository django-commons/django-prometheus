from prometheus_client import Counter, Histogram

from django_prometheus.conf import NAMESPACE, PROMETHEUS_LATENCY_BUCKETS

connections_total = Counter(
    "django_db_new_connections_total",
    "Counter of created connections by database and by vendor.",
    ["alias", "vendor"],
    namespace=NAMESPACE,
)

connection_errors_total = Counter(
    "django_db_new_connection_errors_total",
    "Counter of connection failures by database and by vendor.",
    ["alias", "vendor"],
    namespace=NAMESPACE,
)

execute_total = Counter(
    "django_db_execute_total",
    ("Counter of executed statements by database and by vendor, including bulk executions."),
    ["alias", "vendor"],
    namespace=NAMESPACE,
)


execute_many_total = Counter(
    "django_db_execute_many_total",
    ("Counter of executed statements in bulk operations by database and by vendor."),
    ["alias", "vendor"],
    namespace=NAMESPACE,
)


errors_total = Counter(
    "django_db_errors_total",
    ("Counter of execution errors by database, vendor and exception type."),
    ["alias", "vendor", "type"],
    namespace=NAMESPACE,
)

query_duration_seconds = Histogram(
    "django_db_query_duration_seconds",
    ("Histogram of query duration by database and vendor."),
    ["alias", "vendor"],
    buckets=PROMETHEUS_LATENCY_BUCKETS,
    namespace=NAMESPACE,
)

# AWS Advanced Wrapper specific metrics
aws_failover_success_total = Counter(
    "django_db_aws_failover_success_total",
    "Counter of successful AWS database failovers by database and vendor.",
    ["alias", "vendor"],
    namespace=NAMESPACE,
)

aws_failover_failed_total = Counter(
    "django_db_aws_failover_failed_total",
    "Counter of failed AWS database failovers by database and vendor.",
    ["alias", "vendor"],
    namespace=NAMESPACE,
)

aws_transaction_resolution_unknown_total = Counter(
    "django_db_aws_transaction_resolution_unknown_total",
    "Counter of AWS database transactions with unknown resolution status.",
    ["alias", "vendor"],
    namespace=NAMESPACE,
)
