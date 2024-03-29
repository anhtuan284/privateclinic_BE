import datetime
import enum
from datetime import date
from django.db import models
from django.utils import timezone

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from django.db.models import Max


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "PATIENT", 'Patient'
        ADMIN = "ADMIN", 'Admin'
        DOCTOR = "DOCTOR", 'Doctor'
        NURSE = "NURSE", 'Nurse'

    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    birth_date = models.DateField(null=True)
    sex = models.CharField(max_length=10, choices=SEX, null=True)
    phone_nb = models.CharField(max_length=30, null=True)
    avatar = CloudinaryField('avatar', null=True)
    role = models.CharField(max_length=50, choices=Role, default=Role.PATIENT)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.username

    @property
    def name(self):
        return self.role.name + " " + self.get_full_name()


class Patient(models.Model):
    user_info = models.OneToOneField(User, related_name="patient", null=False, primary_key=True, on_delete=models.CASCADE)
    weight = models.IntegerField(null=True)
    allergies = models.CharField(max_length=200, null=True)

    def __str__(self):
        return "Pt. " + self.user_info.first_name + " " + self.user_info.last_name


class Doctor(models.Model):
    user_info = models.OneToOneField(User, related_name="doctor", null=False, primary_key=True, on_delete=models.CASCADE)

    class Specialty(models.TextChoices):
        GENERAL_PRACTICE = 'General practice', 'General practice'
        CLINICAL_RADIOLOGY = 'Clinical radiology', 'Clinical radiology'  # X quang lam san
        ANAESTHESIA = 'Anaesthesia', 'Anaesthesia'  # Gay te
        OPHTHALMOLOGY = 'Ophthalmology', 'Ophthalmology'  # Eye

    salary = models.FloatField()
    specialty = models.CharField(max_length=200, choices=Specialty, default=Specialty.GENERAL_PRACTICE)
    exp_year = models.PositiveIntegerField(default=3)
    patients = models.PositiveIntegerField(default=5)

    def __str__(self):
        return "Dr. " + self.user_info.first_name + " " + self.user_info.last_name


class Nurse(models.Model):
    user_info = models.OneToOneField(User, related_name="nurse", null=False, primary_key=True, on_delete=models.CASCADE)
    salary = models.FloatField(null=True)

    def __str__(self):
        return "Nr. " + self.user_info.first_name + " " + self.user_info.last_name


class BaseModel(models.Model):
    created_date = models.DateField(auto_now_add=True, null=True)
    updated_date = models.DateField(auto_now=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Department(BaseModel):
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.name


class DepartmentSchedule(BaseModel):
    date = models.DateField(null=False)
    department = models.ForeignKey(Department, related_name='schedules', on_delete=models.CASCADE)
    doctor = models.ManyToManyField(Doctor, related_name='schedules')
    nurse = models.ManyToManyField(Nurse, related_name='schedules')

    class Meta:
        unique_together = ('date', 'department')

    def __str__(self):
        return str(self.date) + ' | ' + str(self.department)


class Medicine(BaseModel):
    class MedicineUnit(models.TextChoices):
        TABLET = "TABLET", "Tablet"
        CAPSULE = "CAPSULE", "Capsule"
        LIQUID = "LIQUID", "Liquid"
        INJECTION = "INJECTION", "Injection"
        CREAM = "CREAM", "Cream"
        OINTMENT = "OINTMENT", "Ointment"
        DROPS = "DROPS", "Drops"
        POWDER = "POWDER", "Powder"
        OTHER = "OTHER", "Other"

    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50, choices=MedicineUnit, default=MedicineUnit.TABLET)
    price = models.IntegerField(null=False)  # have to add unit, unit_price
    manufacturer = models.CharField(max_length=100, null=True)
    weight = models.FloatField()
    # Shell: m.prescription_set.all()

    def __str__(self):
        return str(self.name) + " [" + str(self.weight) + "mg]"


class Service(BaseModel):
    name = models.CharField(max_length=25, null=False)
    price = models.IntegerField(null=False)

    def __str__(self):
        return self.name


class Appointment(BaseModel):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        CANCELLED = 'cancelled', 'Cancelled'

    patient = models.ForeignKey(Patient, related_name="appointments", on_delete=models.CASCADE)
    scheduled_date = models.DateField(null=False)
    status = models.CharField(max_length=20, choices=StatusChoices, default=StatusChoices.PENDING)
    order_number = models.PositiveIntegerField(default=None, null=True)


    def __str__(self):
        return "Appointment for " + str(self.patient)


class PrescriptionMedicine(models.Model):
    prescription = models.ForeignKey('Prescription', related_name='dosages', on_delete=models.CASCADE)
    medicine = models.ForeignKey('Medicine', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    dosage = models.CharField(max_length=50)

    class Meta:
        unique_together = ("prescription", "medicine")


class Prescription(BaseModel):
    patient = models.ForeignKey(Patient, related_name="prescription", null=False, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name="prescription", null=False, on_delete=models.CASCADE)
    symptoms = models.TextField(max_length=500)
    diagnosis = models.TextField(max_length=500)
    pay_status = models.BooleanField(default=False)
    medicines = models.ManyToManyField(Medicine, through=PrescriptionMedicine)
    services = models.ManyToManyField(Service)

    def __str__(self):
        return self.patient.user_info.first_name + " " + self.patient.user_info.last_name + " " + str(self.created_date)


class Receipt(models.Model):
    nurse = models.ForeignKey(Nurse, related_name='receipt_confirmed', on_delete=models.SET_NULL, null=True)
    prescription = models.OneToOneField(Prescription, related_name='receipt', primary_key=True, on_delete=models.CASCADE)
    total = models.IntegerField()
    created_date = models.DateField(auto_now_add=True)
    paid = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.prescription.__str__()


class Notification(models.Model):
    user = models.ForeignKey('User', related_name='notifications', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=False, default='Notification 1}')
    notice = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notify_{self.id}_of_{self.user.username}'

