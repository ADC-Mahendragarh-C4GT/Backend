from django.contrib import admin
from .models import *

admin.site.register(UserAuditLog)
admin.site.register(RoadAuditLog)
admin.site.register(ContracterAuditLog)
admin.site.register(InfraWorkAuditLog)
admin.site.register(UpdateAuditLog) 
admin.site.register(CommentAuditLog)
