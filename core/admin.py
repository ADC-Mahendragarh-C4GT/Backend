from django.contrib import admin
from .models import *

@admin.register(Road)
class RoadAdmin(admin.ModelAdmin):
    list_display = ("id", "road_name", "unique_code", "isActive")
    list_filter = ("isActive",)
    search_fields = ("road_name", "unique_code")

@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ("id", "contractor_name", "contractor_name", "isActive")
    list_filter = ("isActive",)
    search_fields = ("contractor_name", "unique_code")

@admin.register(InfraWork)
class InfraWorkAdmin(admin.ModelAdmin):
    list_display = ("id","road","description", "defect_liability_period", "isActive")
    list_filter = ("isActive",)
    search_fields = ("work_name", "unique_code")

@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "work", "update_date", "status_note", "progress_percent", "isActive")
    list_filter = ("isActive",)
    search_fields = ("work__road__road_name", "status_note")

@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ("id", "update", "commenter", "comment_date", "isActive")
    list_filter = ("isActive",)
    search_fields = ("update__work__road__road_name", "commenter__first_name", "commenter__last_name")

@admin.register(OtherDepartmentRequest)
class OtherDepartmentRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "road", "work_description", "requested_by", "status", "isActive")
    list_filter = ("isActive",)
    search_fields = ("road__road_name", "requested_by", "department_name")