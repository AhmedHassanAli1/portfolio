from django.contrib import admin
from Publication.models import Publication_Event, Publication_News
from custom_admin.admin import admin_site

class EventAdmin(admin.ModelAdmin):
    list_display = ('EventTitle','Organization','is_approved')

class NewsAdmin(admin.ModelAdmin):
    list_display = ('NewsTitle','Organization','is_approved')

admin_site.register(Publication_Event,EventAdmin)
admin_site.register(Publication_News,NewsAdmin)