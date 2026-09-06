from django.urls import path
from . import views as calendar_views 



urlpatterns = [
    #path('<int:year>/<str:month>/', calendar_views.CalendarEvents_view, name='calendarevents_view'),
    path('', calendar_views.CalendarEvents_view, name='calendarevents_view'),
    path('<int:year>/<str:month>/', calendar_views.CalendarEvents_view_previous_or_next, name='calendarevents_view_next_previous'),
   # path('calendarevents/<int:year>/<str:month>/', calendar_views.CalendarEvents_view, name='calendarevents_view'),


]