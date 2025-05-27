from django.urls import path
from . import views

urlpatterns = [
    path('', views.donate_form, name='donate_form'),
    path('donate_finalize', views.donate_finalize, name='donate_finalize'),
    path('webhooks/bbms', views.bbms_webhook, name='bbms_webhook'),
    path('test-email/', views.test_send_email, name='test_send_email'),

]