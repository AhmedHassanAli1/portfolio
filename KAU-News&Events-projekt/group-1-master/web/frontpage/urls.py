from django.urls import path
from Registration import views as reg_views
from login import views as login_views
from staffuser import views as staff_views
from attendance import views as attendance_views

from CalenderEvents import views as calendar_views

# importing views from views..py
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('publish_events/', views.publication_events, name='publication_events'),
    path('publish_news/', views.publication_news, name='publication_news'),
    path('login/', views.index4, name='index4'),
    path('admin/', views.admin_index, name='admin_index'),
    path('staffuser/', staff_views.staffuser_home, name='staffuser'),
    path('read_more/<int:id>/', views.read_more, name='read_more'),
    path('attendance/', attendance_views.attendance_home, name='attendance_home'),
    path('att_list/<int:id>/', views.att_list, name='att_list'),
    path("calendarevents/", calendar_views.CalendarEvents_view, name='calendarevents_view'),
    path('delete_publication/<int:id>/', views.delete_publication, name='delete_publication'),
]
