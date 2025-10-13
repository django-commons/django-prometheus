import re

from setuptools import find_packages, setup

with open("README.md") as fl:
    LONG_DESCRIPTION = fl.read()


def get_version():
    version_file = open("django_prometheus/__init__.py").read()
    version_match = re.search(
        r'^__version__ = [\'"]([^\'"]*)[\'"]',
        version_file,
        re.MULTILINE,
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="django-prometheus",
    version=get_version(),
    author="Uriel Corfa",
    author_email="uriel@corfa.fr",
    description=("Django middlewares to monitor your application with Prometheus.io."),
    license="Apache",
    keywords="django monitoring prometheus",
    url="http://github.com/korfuri/django-prometheus",
    project_urls={
        "Changelog": "https://github.com/korfuri/django-prometheus/blob/master/CHANGELOG.md",
        "Documentation": "https://github.com/korfuri/django-prometheus/blob/master/README.md",
        "Source": "https://github.com/korfuri/django-prometheus",
        "Tracker": "https://github.com/korfuri/django-prometheus/issues",
    },
    packages=find_packages(
        exclude=[
            "tests",
        ],
    ),
    test_suite="django_prometheus.tests",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    tests_require=["pytest", "pytest-django"],
    setup_requires=["pytest-runner"],
    options={"bdist_wheel": {"universal": "1"}},
    install_requires=[
        "Django>=4.2,<5.3,!=5.0.*",
        "prometheus-client>=0.7",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.14t",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.1",
        "Framework :: Django :: 5.2",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: Apache Software License",
    ],
)
