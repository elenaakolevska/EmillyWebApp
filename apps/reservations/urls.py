from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('create/', views.create_reservation, name='create'),
    path('confirmation/<int:reservation_id>/', views.reservation_confirmation, name='reservation_confirmation'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
]

