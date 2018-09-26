"""
URLConf for test suite.
"""

from django.urls import path, include

from pico_framework import urls


urlpatterns = [
    path('pico_framework/', include(urls.urlpatterns))
]