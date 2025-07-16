from django.urls import path
from . import views
from django.views.generic import TemplateView

from .skyapi_endpoints import skyapi_authorize, skyapi_callback, skyapi_token

urlpatterns = [
    path('', views.donate_form, name='donate_form'),
    path('donate_finalize', views.donate_finalize, name='donate_finalize'),
    path('webhooks/bbms', views.bbms_webhook, name='bbms_webhook'),
    path('test-email/', views.test_send_email, name='test_send_email'),
    path('sky-addin', TemplateView.as_view(template_name='sky-addin/index.html')),
    path('skyapi/authorize', skyapi_authorize, name='skyapi_authorize'),
    path('skyapi/oath/callback', skyapi_callback, name='skyapi_callback'),
    path('skyapi/token', skyapi_token, name='sky_token'),
]