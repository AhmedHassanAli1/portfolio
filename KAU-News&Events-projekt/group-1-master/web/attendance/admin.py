from django.contrib import admin
from attendance.models import EventAttendance
from custom_admin.admin import admin_site

class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'User_role', 'Event_Departments', 'Event_Tags', 'timestamp')
    search_fields = ('event__EventTitle', 'user__username', 'user__email')
    list_filter = (
        'event','event__Department','event__Tag','user__is_superuser','user__is_staff','user__is_active',)

    def get_count_event(self, request):
        return EventAttendance.objects.count()

    def Event_Departments(self, obj):
        return ", ".join([d.DepName for d in obj.event.Department.all()])

    def Event_Tags(self, obj):
        return ", ".join([t.TagName for t in obj.event.Tag.all()])

    def User_role(self, obj):
        if obj.user.is_superuser:
            return "Admin"
        elif obj.user.is_staff:
            return "Publisher"
        else:
            return "User"

admin_site.register(EventAttendance, EventAttendanceAdmin)
