from django.urls import path
from .views import (
    make_reservation, table_detail, edit_reservation, delete_reservation, 
    saloon_list, saloon_tables, table_history, restaurant_home
)

urlpatterns = [
    path('home/', restaurant_home, name='restaurant_home'),
    path('reservation/<int:table_id>/new/', make_reservation, name='make_reservation'),
    path('table/<int:table_id>/', table_detail, name='table_detail'),
    path('reservation/<int:reservation_id>/edit/', edit_reservation, name='edit_reservation'),
    path('reservation/<int:reservation_id>/delete/', delete_reservation, name='delete_reservation'),
    path('saloons/', saloon_list, name='saloon_list'),
    path('saloons/<int:saloon_id>/tables/', saloon_tables, name='saloon_tables'),
    path('history/', table_history, name='table_history'),
]
