"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from Registration import views as reg_views
from custom_admin.admin import admin_site
from login import views as login_views
from Publication import views as publi_views
from staffuser import views as staff_views
from django.conf import settings
from django.conf.urls.static import static
from attendance import views as attend_views

urlpatterns = [
    path('admin/', admin_site.urls),
    path("register/", reg_views.registration_view, name = "register"), # Connect the register view from Registration app, i.e the function register in views.py for website.com/register
    path("login/", login_views.login_view, name='login'),
    path("logout/", login_views.logout_view, name='logout'),
    path('', include('frontpage.urls')),
    path ("publication_events/", publi_views.publication_event_view, name='publication_events'),
    path ("publication_news/", publi_views.publication_news_view, name='publication_news'), 
    path("staffuser/", include('staffuser.urls')),
    path("attendance/", include("attendance.urls")),
    
    path("calendarevents/", include('CalenderEvents.urls')),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                        document_root=settings.MEDIA_ROOT)
