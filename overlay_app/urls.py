from django.urls import path
from .views import onboarding, upload_images

urlpatterns = [
    path('', onboarding, name='onboarding'),
    path('upload', upload_images, name='restaurant'),
]
