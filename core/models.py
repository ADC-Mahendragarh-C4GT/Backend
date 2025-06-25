from django.db import models

class Road(models.Model):
    unique_code = models.CharField(max_length=50, unique=True)
    road_name = models.CharField(max_length=100)
    ward_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    length_km = models.DecimalField(max_digits=5, decimal_places=2)
    

class Vendor(models.Model):
    vendor_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

class InfraWork(models.Model):
    road = models.ForeignKey(Road, on_delete=models.CASCADE)
    phase = models.CharField(max_length=50)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    progress_percent = models.IntegerField()
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)

class Update(models.Model):
    work = models.ForeignKey(InfraWork, on_delete=models.CASCADE)
    update_date = models.DateField(auto_now_add=True)
    status_note = models.TextField()
    progress_percent = models.IntegerField()

