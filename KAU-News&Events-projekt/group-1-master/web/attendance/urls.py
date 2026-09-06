from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_home, name='attendance_home'),
    path('<int:event_id>/attend/', views.attend_event, name='attend_event'),
    path('<int:event_id>/unattend/', views.unattend_event, name='unattend_event'),
]
