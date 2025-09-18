from django.urls import path
from .views import whatsapp_webhook
from django.urls import include

urlpatterns = [
    path("webhook/", whatsapp_webhook, name="whatsapp_webhook"),
    path("", include("django_whatsapp_api_wrapper.templates.urls")),
]
