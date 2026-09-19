from django import VERSION, get_version
from prometheus_client import Info
from django_prometheus.conf import NAMESPACE

major, minor, patch = VERSION[:3]
version = get_version()
django_info = Info("django", 
                   "Django version information", 
                   namespace=NAMESPACE)
django_info.info({"major": str(major), 
                  "minor": str(minor), 
                  "patchlevel": str(patch), 
                  "version": version})