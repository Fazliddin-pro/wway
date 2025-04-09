from django.urls import path
from .views import CustomAuthToken

urlpatterns = [
    path('token/', CustomAuthToken.as_view(), name='custom-token-auth'),
]
