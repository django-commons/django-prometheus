# Changelog

## v2.5.0 - UNRELEASED

* Drop support for Django 5.0 (EOL)
* Add support for Python 3.13, 3.14, and free threaded 3.14t.

## v2.4.1 - June 25th, 2025

* Add Django version to install requirements.

## v2.4.0 - June 18th, 2025

* Add support for Django 5.0 and Python 3.12.
* Replace black, flake8 and isort with Ruff
* Drop support for Django 3.2 (Python 3.7), 4.0 and 4.1
* Project moved to the [Django Commons](https://github.com/django-commons) GitHub organization.
* Add pyupgrade and yamlfmt pre-commit hooks

## v2.3.1 - May 2nd, 2023

* Fix postgresql provider import, Thanks [@wilsonehusin](https://github.com/korfuri/django-prometheus/pull/402)

## v2.3.0 - May 2nd, 2023

* Remove support for Python 3.6, Django versions older tha than 3.2
* Fix two latency metrics not using PROMETHEUS_LATENCY_BUCKETS setting, Thanks [@AleksaC](https://github.com/korfuri/django-prometheus/pull/343)
* Support new cache backend names in newer Django versions, Thanks [@tneuct](https://github.com/korfuri/django-prometheus/pull/329)
* Make export of migrations False by default, Thanks [@kaypee90](https://github.com/korfuri/django-prometheus/pull/313)
* Add support for Django 4.1, Python 3.11
* Add support for Django 4.2 and Psycopg 3

## v2.2.0 - December 19, 2021

* Switch to Github Actions CI, remove travis-ci.
* Add support for Django 3.2 & 4.0 and Python 3.9 & 3.10

## v2.1.0 - August 22, 2020

* Remove support for older django and python versions
* Add support for Django 3.0 and Django 3.1
* Add support for [PostGIS](https://github.com/korfuri/django-prometheus/pull/221), Thanks [@EverWinter23](https://github.com/EverWinter23)

## v2.0.0 - Jan 20, 2020

* Added support for newer Django and Python versions
* Added an extensibility that applications to add their own labels to middleware (request/response) metrics
* Allow overriding and setting custom bucket values for request/response latency histogram metric
* Internal improvements:
  * use tox
  * Use pytest
  * use Black
  * Automate pre-releases on every commit ot master
  * Fix flaky tests.

## v1.1.0 -  Sep 28, 2019

* maintenance release that updates this library to support recent and supported version of python & Django
