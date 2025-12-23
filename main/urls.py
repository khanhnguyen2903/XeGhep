from django.urls import path
from .views import home, manage_coin, calculate_payout, calculate_payment

urlpatterns = [
    path('home/', home, name='home'),
    path('manage-coin/', manage_coin, name='manage_coin'),
    path('calculate-payout/<str:phone>/', calculate_payout, name='calculate_payout'),
    path('calculate-payment/<str:phone>/', calculate_payment, name='calculate_payment'),
]
