from django.contrib import admin
from .models import Road, Contractor, InfraWork, Update

admin.site.register(Road)
admin.site.register(Contractor)
admin.site.register(InfraWork)
admin.site.register(Update)
