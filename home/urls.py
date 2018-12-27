from django.urls import path
from .views import contact_me

urlpatterns = [
    path('contact-me/', contact_me),
]
