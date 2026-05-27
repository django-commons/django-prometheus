# Exports

## Default: exporting /metrics as a Django view

/metrics can be exported as a Django view very easily. Simply
include('django_prometheus.urls') with no prefix like so:

```python
urlpatterns = [
    ...
    path('', include('django_prometheus.urls')),
]
```

This will reserve the /metrics path on your server. This may be a
problem for you, so you can use a prefix. For instance, the following
will export the metrics at `/monitoring/metrics` instead. You will
need to configure Prometheus to use that path instead of the default.

```python
urlpatterns = [
    ...
    path('monitoring/', include('django_prometheus.urls')),
]
```

## Exporting /metrics in a dedicated thread

To ensure that issues in your Django app do not affect the monitoring,
it is recommended to export /metrics in an HTTPServer running in a
daemon thread. This will prevent that problems such as thread
starvation or low-level bugs in Django do not affect the export of
your metrics, which may be more needed than ever if these problems
occur.

It can be enabled by adding the following line in your `settings.py`:

```python
PROMETHEUS_METRICS_EXPORT_PORT = 8001
PROMETHEUS_METRICS_EXPORT_ADDRESS = ''  # all addresses
```

However, by default this mechanism is disabled, because it is not
compatible with Django's autoreloader. The autoreloader is the feature
that allows you to edit your code and see the changes
immediately. This works by forking multiple processes of Django, which
would compete for the port. As such, this code will assert-fail if the
autoreloader is active.

You can run Django without the autoreloader by passing `-noreload` to
`manage.py`. If you decide to enable the thread-based exporter in
production, you may wish to modify your manage.py to ensure that this
option is always active:

```python
    execute_from_command_line(sys.argv + ['--noreload'])
```

## Exporting /metrics in a WSGI application with multiple processes per process

If you're using WSGI (e.g. with uwsgi or with gunicorn) and multiple
Django processes, using either option above won't work, as requests
using the Django view would just go to an inconsistent backend each
time, and exporting on a single port doesn't work.

The following settings can be used instead:

```python
PROMETHEUS_METRICS_EXPORT_PORT_RANGE = range(8001, 8050)
```

This will make Django-Prometheus try to export /metrics on port
8001. If this fails (i.e. the port is in use), it will try 8002, then
8003, etc.

You can then configure Prometheus to collect metrics on as many
targets as you have workers, using each port separately.

This approach requires the application to be loaded into each child process.
uWSGI and Gunicorn typically load the application into the master process before forking the child processes.
Set the [lazy-apps option](https://uwsgi-docs.readthedocs.io/en/latest/Options.html#lazy-apps) to `true` (uWSGI)
or the [preload-app option](https://docs.gunicorn.org/en/stable/settings.html#preload-app) to `false` (Gunicorn)
to change this behaviour.

For using port ranges on uWSGI, you should also set the [enable-threads](https://uwsgi-docs.readthedocs.io/en/latest/Options.html#enable-threads) to `true`. HTTP servers of different ports start on their own
threads and without that option, threads will not run. (Having the [threads](https://uwsgi-docs.readthedocs.io/en/latest/Options.html#threads) will automatically enable that flag.)


## Exporting /metrics in a WSGI application with multiple processes globally

In some WSGI applications, workers are short lived (less than a minute), so some
are never scraped by prometheus by default. Prometheus client already provides
a nice system to aggregate them using the env variable: `PROMETHEUS_MULTIPROC_DIR`
which will configure the directory where metrics will be stored as files per process.

Configuration in uwsgi would look like:

```ini
env = PROMETHEUS_MULTIPROC_DIR=/path/to/django_metrics
```

You can also set this environment variable elsewhere such as in a kubernetes manifest.

Setting this will create four files (one for counters, one for summaries, ...etc)
for each pid used. In uwsgi, the number of different pids used can be quite large
(the pid change every time a worker respawn). To prevent having thousand of files
created, it's possible to create file using worker ids rather than pids.

You can change the function used for identifying the process to use the uwsgi worker_id.
Modify this in settings before any metrics are created:

```python
try:
    import prometheus_client
    import uwsgi
    prometheus_client.values.ValueClass = prometheus_client.values.MultiProcessValue(
        process_identifier=uwsgi.worker_id)
except ImportError:
    pass  # not running in uwsgi
```

Note that this code uses internal interfaces of prometheus_client.
The underlying implementation may change.

The number of resulting files will be:
number of processes * 4 (counter, histogram, gauge, summary)

Be aware that by default this will generate a large amount of file descriptors:
Each worker will keep 3 file descriptors for each files it created.

Since these files will be written often, you should consider mounting this directory
as a `tmpfs` or using a subdir of an existing one such as `/run/` or `/var/run/`.

If uwsgi is not using lazy-apps (lazy-apps = true), there will be a
file descriptors leak (tens to hundreds of fds on a single file) due
to the way uwsgi forks processes to create workers.
