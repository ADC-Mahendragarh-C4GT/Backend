from django.contrib import admin
from .models import *

@admin.register(Road)
class RoadAdmin(admin.ModelAdmin):
    list_display = ("id", "road_name", "unique_code", "isActive")
    list_filter = ("isActive",)
    search_fields = ("road_name", "unique_code")

admin.site.register(Contractor)
admin.site.register(InfraWork)
admin.site.register(Update)
admin.site.register(Comments)
admin.site.register(OtherDepartmentRequest)