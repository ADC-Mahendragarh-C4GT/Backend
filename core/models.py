from django.db import models

ROAD_CATEGORY_CHOICES = (
    ('ColonyStreet', 'Colony Street'),
    ('Road', 'Road')
)

ROAD_TYPE_CHOICES = (
    ('IV', 'Road Type IV'),
    ('VI', 'Road Type VI'),
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

class Contractor(models.Model):
    contractor_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

class InfraWork(models.Model):
    road = models.ForeignKey(Road, on_delete=models.CASCADE)
    phase = models.CharField(max_length=500)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    progress_percent = models.IntegerField()
    cost = models.DecimalField(max_digits=1000, decimal_places=2)
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True)

class Update(models.Model):
    work = models.ForeignKey(InfraWork, on_delete=models.CASCADE)
    update_date = models.DateField(auto_now_add=True)
    status_note = models.TextField()
    progress_percent = models.IntegerField()

