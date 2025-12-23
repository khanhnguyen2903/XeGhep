from django.urls import path
from .views import add_driver_view, list_driver_view, edit_driver, delete_driver

urlpatterns = [
    path('add-driver/', add_driver_view, name='add_driver'),
    path('list-driver/', list_driver_view, name='list_driver'),
    path('edit-driver/<str:id>', edit_driver, name='edit_driver'),
    path('delete-driver/<str:id>', delete_driver, name='delete_driver'),
]
