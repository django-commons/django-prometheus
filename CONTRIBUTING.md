# Contributing

## Git

Feel free to send pull requests, even for the tiniest things. Watch
for Travis' opinion on them ([![Build
Status](https://travis-ci.org/korfuri/django-prometheus.svg?branch=master)](https://travis-ci.org/korfuri/django-prometheus)).

Travis will also make sure your code is pep8 compliant, and it's a
good idea to run flake8 as well (on django_prometheus/ and on
tests/). The code contains "unused" imports on purpose so flake8 isn't
run automatically.

## Tests

Please write unit tests for your change. There are two kinds of tests:

* Regular unit tests that test the code directly, without loading
  Django. This is limited to pieces of the code that don't depend on
  Django, since a lot of the Django code will require a full Django
  environment (anything that interacts with models, for instance,
  needs a full database configuration).
* End-to-end tests are Django unit tests in a test application. The
  test application doubles as an easy way to interactively test your
  changes. It uses most of the basic Django features and a few
  advanced features, so you can test things for yourself.

### Running all tests

```shell
python -m pytest django_prometheus/tests
cd tests/end2end/ &&  PYTHONPATH=../.. ./manage.py test
```

The former runs the regular unit tests, the latter runs the Django
unit test.

To avoid setting PYTHONPATH every time, you can also run `python -m
pip install .`.

### Running the test Django app

```shell
cd tests/end2end/ &&  PYTHONPATH=../.. ./manage.py runserver
```

By default, this will start serving on http://localhost:8000/. Metrics
are available at `/metrics`.

## Running Prometheus

See <http://prometheus.io/docs/> for instructions on installing
Prometheus. Once you have Prometheus installed, you can use the
example rules and dashboard in `examples/prometheus/`. See
`examples/prometheus/README.md` to run Prometheus and view the example
dashboard.
