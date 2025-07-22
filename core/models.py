from django.db import models
from accounts.models import CustomUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# Define choices for road categories, types, and material types
ROAD_CATEGORY_CHOICES = (
    ('ColonyStreet', 'Colony Street'),
    ('Road', 'Road')
)

user_type_choices = settings.USER_TYPE_CHOICES

ROAD_TYPE_CHOICES = (
    ('IV', 'Road Type IV'),
    ('VI', 'Road Type VI'),
    ('others', 'Other Road Type')
)

MATERIAL_TYPE_CHOICES = (
    ('CC', 'Material Type CC'),
    ('IPB', 'Material Type IPB'),
    ('Bitumin', 'Material Type Bitumin'),
    ('Other', 'Other'),
)


class Road(models.Model):
    unique_code = models.CharField(max_length=500, unique=True)
    road_name = models.CharField()
    ward_number = models.CharField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    length_km = models.DecimalField(decimal_places=4, max_digits=200, default=0.0)
    width_m = models.DecimalField(decimal_places=4, max_digits=200, default=0.0)
    road_type = models.CharField( choices=ROAD_TYPE_CHOICES, default='IV')
    material_type = models.CharField( choices=MATERIAL_TYPE_CHOICES, default='CC')
    road_category = models.CharField( choices=ROAD_CATEGORY_CHOICES, default='Road')
    area_name = models.CharField(default='Gumanpura', blank=True, null=True)
    district = models.CharField(default='Kota', blank=True, null= True)
    state = models.CharField(default='Rajasthan', blank=True, null=True)

    def __str__(self):
        return f"{self.unique_code} ({self.road_type}) ({self.road_name})"

class Contractor(models.Model):
    contractor_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):  
        return self.contractor_name

class InfraWork(models.Model):
    road = models.ForeignKey(Road, on_delete=models.CASCADE)
    phase = models.CharField(max_length=500)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    progress_percent = models.IntegerField()
    cost = models.DecimalField(max_digits=1000, decimal_places=2)
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True)
    completedOrpending = models.CharField(max_length=20, choices=[('Completed', 'Completed'), ('Pending', 'Pending')], default='Pending')
    defect_liability_period = models.IntegerField(help_text="Defect Liability Period in months", default=0, null=True, blank=True)
    def __str__(self):
        return f"{self.road.road_name} - {self.phase} ({self.start_date} to {self.end_date})"

class Update(models.Model):
    work = models.ForeignKey(InfraWork, on_delete=models.CASCADE)
    update_date = models.DateField(auto_now_add=True)
    status_note = models.TextField()
    progress_percent = models.IntegerField()

    def __str__(self):
        return f"Update on {self.update_date} for {self.work.road.road_name}: {self.status_note[:50]}..."


@receiver(post_save, sender=Update)
def update_infra_work_progress(sender, instance, created, **kwargs):
    if created:
        if(instance.progress_percent == 100):
            instance.work.completedOrpending = 'Completed' 
        infra_work = instance.work
        # set InfraWork.progress_percent = latest update's progress_percent
        infra_work.progress_percent = instance.progress_percent
        infra_work.save()

class Comments(models.Model):
    update = models.ForeignKey(Update, on_delete=models.CASCADE)
    infra_work = models.ForeignKey(InfraWork, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    commenter = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter.first_name} {self.commenter.last_name} {self.commenter.user_type} on {self.update.update_date}: {self.comment_text[:50]}..."
        

class OtherDepartmentRequest(models.Model):
    department_name = models.CharField(max_length=255)
    road = models.ForeignKey(Road, on_delete=models.CASCADE)
    work_description = models.TextField()
    requested_by = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    response_by = models.CharField(max_length=255, null=True, blank=True)
    response_date = models.DateTimeField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.road.road_name} - {self.requested_by} - {self.department_name} ({self.status})"