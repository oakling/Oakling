from django.contrib import admin
from models import Pane

class PaneAdmin(admin.ModelAdmin):
        pass
admin.site.register(Pane, PaneAdmin)
