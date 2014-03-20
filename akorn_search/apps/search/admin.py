from django.contrib import admin
from models import Search

class SearchAdmin(admin.ModelAdmin):
        pass
admin.site.register(Search, SearchAdmin)
