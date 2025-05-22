from django.urls import path
from . import views

urlpatterns = [
path('', views.donate_form, name='donate_form'),
path('finalize', views.donate_finalize, name='donate_finalize'),
path('webhooks/bbms', views.bbms_webhook, name='bbms_webhook'),
]