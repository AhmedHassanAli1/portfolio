from django.urls import path, re_path
from . import views as staff_views



urlpatterns = [
    path('', staff_views.staffuser_home, name='staffuser_home'),
    path('view_request/<int:id>/', staff_views.view_request, name='view_request'),
]