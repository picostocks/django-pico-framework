from django.urls import path
from pico_framework.views import StatsPriceView

urlpatterns = [
    path('stats', StatsPriceView.as_view(),
         name='pico-framework-stats'),
]