# HTTP Request/Response Metrics

The following table lists and explains the HTTP request and response metrics produced by the `django_prometheus` project
middleware, which are relevant for monitoring the API endpoints in your Django application.

| Metric Name                                                        | Type      | Labels                        | Description                                                                                                              |
|--------------------------------------------------------------------|-----------|-------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| `django_http_requests_before_middlewares_total`                    | Counter   | *(none)*                      | Total number of HTTP requests received before middlewares run.                                                           |
| `django_http_responses_before_middlewares_total`                   | Counter   | *(none)*                      | Total number of HTTP responses before middlewares run.                                                                   |
| `django_http_requests_latency_including_middlewares_seconds`       | Histogram | *(none)*                      | Histogram of request processing time (including middleware processing time).                                             |
| `django_http_requests_unknown_latency_including_middlewares_total` | Counter   | *(none)*                      | Number of requests for which the latency was unknown (for `django_http_requests_latency_including_middlewares_seconds`). |
| `django_http_requests_latency_seconds_by_view_method`              | Histogram | `view`, `method`              | Histogram of request processing time labeled by view name and HTTP method.                                               |
| `django_http_requests_unknown_latency_total`                       | Counter   | *(none)*                      | Number of requests for which the latency was unknown.                                                                    |
| `django_http_ajax_requests_total`                                  | Counter   | *(none)*                      | Number of AJAX requests (`X-Requested-With: XMLHttpRequest`).                                                            |
| `django_http_requests_total_by_method`                             | Counter   | `method`                      | Number of requests split by HTTP method (e.g., GET, POST).                                                               |
| `django_http_requests_total_by_transport`                          | Counter   | `transport`                   | Number of requests split by transport protocol (`http` or `https`).                                                      |
| `django_http_requests_total_by_view_transport_method`              | Counter   | `view`, `transport`, `method` | Number of requests by view name, transport protocol, and HTTP method.                                                    |
| `django_http_requests_body_total_bytes`                            | Histogram | *(none)*                      | Histogram distribution of incoming HTTP request body sizes (in bytes).                                                   |
| `django_http_responses_total_by_templatename`                      | Counter   | `templatename`                | Number of responses broken out by template name used for rendering.                                                      |
| `django_http_responses_total_by_status`                            | Counter   | `status`                      | Number of responses by HTTP status code (e.g., 200, 404).                                                                |
| `django_http_responses_total_by_status_view_method`                | Counter   | `status`, `view`, `method`    | Number of responses split by HTTP status, view name, and HTTP method.                                                    |
| `django_http_responses_body_total_bytes`                           | Histogram | *(none)*                      | Histogram distribution of outgoing HTTP response body sizes (in bytes).                                                  |
| `django_http_responses_total_by_charset`                           | Counter   | `charset`                     | Number of responses split by charset (e.g., utf-8).                                                                      |
| `django_http_responses_streaming_total`                            | Counter   | *(none)*                      | Number of streaming responses served.                                                                                    |
| `django_http_exceptions_total_by_type`                             | Counter   | `type`                        | Number of exceptions occurring, labeled by the exception object (class) type.                                            |
| `django_http_exceptions_total_by_view`                             | Counter   | `view`                        | Number of exceptions broken down by view name.                                                                           |

## Labels

- `view`: Name of the Django view (or `<unnamed view>` if not resolved).
- `method`: HTTP method (`GET`, `POST`, etc.).
- `transport`: `http` or `https`, per request scheme.
- `status`: HTTP status code as string.
- `templatename`: Name of the template used, if applicable.
- `charset`: Character set of the response.
- `type`: Exception class name.

## Notes

- Metrics with no labels provide cumulative totals or global histograms.
- **Latency metrics** (`requests_latency_*`) record how long requests take. Separate metrics exist for end-to-end (
  before middlewares, by view/method, etc.).
- **Body size metrics** record the distributions of incoming/outgoing body sizes in powers-of-two buckets.

# Database Metrics

| Metric Name                             | Type      | Labels                    | Description                                                                         |
|-----------------------------------------|-----------|---------------------------|-------------------------------------------------------------------------------------|
| `django_db_new_connections_total`       | Counter   | `alias`, `vendor`         | Number of created connections by database and by vendor.                            |
| `django_db_new_connection_errors_total` | Counter   | `alias`, `vendor`         | Number of connection failures by database and by vendor.                            |
| `django_db_execute_total`               | Counter   | `alias`, `vendor`         | Number of executed statements by database and by vendor, including bulk executions. |
| `django_db_execute_many_total`          | Counter   | `alias`, `vendor`         | Number of executed statements in bulk operations by database and by vendor.         |
| `django_db_errors_total`                | Counter   | `alias`, `vendor`, `type` | Number of execution errors by database, vendor and exception type.                  |
| `django_db_query_duration_seconds`      | Histogram | `alias`, `vendor`         | Histogram of query duration by database and vendor.                                 |

## Labels

- `alias`: The Django database alias, which identifies the specific configured database connection.
- `vendor`: The database engine/vendor (e.g., "postgresql", "mysql", "sqlite") used for the connection.
- `type`: The type of error or exception encountered during database operations.

# Cache Metrics

| Metric Name                       | Type    | Labels   | Description                                                               |
|-----------------------------------|---------|----------|---------------------------------------------------------------------------|
| `django_cache_get_total`          | Counter | *(none)* | Total number of cache `get` operations attempted.                         |
| `django_cache_get_hits_total`     | Counter | *(none)* | Total number of cache `get` operations that resulted in a cache hit.      |
| `django_cache_get_misses_total`   | Counter | *(none)* | Total number of cache `get` operations that resulted in a cache miss.     |
| `django_cache_get_fail_total`     | Counter | *(none)* | Total number of cache `get` operations that failed (e.g., backend error). |

# Django Model Metrics

| Metric Name                  | Type    | Labels  | Description                           |
|------------------------------|---------|---------|---------------------------------------|
| `django_model_inserts_total` | Counter | `model` | Number of insert operations by model. |
| `django_model_updates_total` | Counter | `model` | Number of update operations by model. |
| `django_model_deletes_total` | Counter | `model` | Number of delete operations by model. |
