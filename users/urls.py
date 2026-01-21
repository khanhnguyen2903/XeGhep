from django.urls import path
from .views import login_view, reset_pass

urlpatterns = [
    path('', login_view, name='login_view'),
    path('reset-password', reset_pass, name='reset_pass'),
    
]
