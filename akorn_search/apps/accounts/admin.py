from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AkornUser
from .forms import AkornUserChangeForm, AkornUserCreationForm

class AkornUserAdmin(UserAdmin):
    add_form = AkornUserCreationForm
    form = AkornUserChangeForm

    list_display = ('email', 'is_staff', 'settings')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    fieldsets = (
            (None, {'fields': ('email', 'password')}),
            ('Personal info', {'fields':
                ('settings',)}),
            ('Permissions', {'fields': ('is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',)}),
            ('Important dates', {'fields': ('last_login',)}),
        )

admin.site.register(AkornUser, AkornUserAdmin)
