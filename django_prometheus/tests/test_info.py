from django import VERSION, get_version
from django_prometheus.info import django_info

def test_info_metric():
    major, minor, patch = VERSION[:3]
    assert django_info._name == "django"
    assert django_info._documentation == "Django version information"
    assert django_info._value == {"major": str(major), 
                                  "minor": str(minor), 
                                  "patchlevel": str(patch), 
                                  "version": get_version(),
                                  }
