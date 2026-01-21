from django.urls import path
from .views import create_trip, list_trip, list_trip_receiving, list_trip_completed, list_trip_created, accept_trip, finish_trip, cancel_trip, logout

urlpatterns = [
    path('create-trip/', create_trip, name='create_trip'),
    path('list-trip/', list_trip, name='list_trip'),
    path('list-trip-receiving/', list_trip_receiving, name='list_trip_receiving'),
    path('list-trip-completed/', list_trip_completed, name='list_trip_completed'),
    path('list-trip-created/', list_trip_created, name='list_trip_created'),
    path('accept-trip/<str:trip_id>/', accept_trip, name='accept_trip'),
    path('finish-trip/<str:trip_id>/', finish_trip, name='finish_trip'),
    path('cancel-trip/<str:trip_id>/', cancel_trip, name='cancel_trip'),
    path('logout/', logout, name='logout'),
]