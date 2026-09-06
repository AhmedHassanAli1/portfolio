from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from authuser.models import CustomUser, Department, Tag
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from custom_admin.admin import admin_site

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('DepName','publisher_count','user_count',)
    fieldsets = (
        (None, {'fields': ('DepName','staff',)}),
    )

    def publisher_count(self,obj):
        return obj.staff.filter(role=2).count()
    
    def user_count(self,obj):
        return obj.staff.filter(role=3).count()

# Used to display departments when viewing a custom user
class DepartmentInLine(admin.TabularInline): 
    model = CustomUser.departments.through

class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    # List display : fields to show when viewing a table
    list_display = ( 'username','email', 'is_active',
                    'is_staff', 'is_superuser','get_departments','role','last_login')
    # List filer : fields to filter by when viewing a table
    list_filter = ('is_active', 'is_staff', 'is_superuser','departments','role',)

    # Fieldsets to display when in "Change user" view in admin
    fieldsets = (
        (None, {'fields': ('username','fullname','email', 'password','role',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active','is_superuser',)}),
        ('Dates', {'fields': ('last_login',)})
    )
    # Add fieldsets : fields to display when adding user in database
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email','role', 'password1', 'password2', 'is_superuser','is_staff', 'is_active',)}
         ),
    )

    search_fields = ('username',)
    
    ordering = ('username',)

    inlines = [
        DepartmentInLine,
    ]

    # Used to view departments in list_display
    def get_departments(self, obj):
        return ", ".join([departments.DepName for departments in obj.departments.all()])



# Register model and model admin in admin_site
admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(Department,DepartmentAdmin)
admin_site.register(Tag)