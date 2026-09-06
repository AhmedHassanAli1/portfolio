import time
from django.contrib.auth import logout
from django.contrib import messages

class loginTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            login_time = request.session.get('login_time')
            if login_time:
                elapsed = time.time() - login_time
                if request.user.is_staff:
                    timeout_seconds = 18000 #18 000 sekunder = 5 timmar, sen loggas ut, om staff/admin
                else:
                    timeout_seconds = 36000 #36 000 sekunder = 10 timmar sen loggas ut, om student/organization
                if elapsed > timeout_seconds:
                    messages.error(request, 'Logged out due to inactivity')     
                    logout(request)
                    request.session['session_expired'] = True
 
        return self.get_response(request)
