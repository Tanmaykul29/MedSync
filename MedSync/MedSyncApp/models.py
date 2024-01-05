from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class SpeechData(models.Model):
    patient_id = models.IntegerField()
    patient_name = models.TextField()
    patient_age = models.IntegerField()
    patient_sex = models.TextField()
    doctor_username = models.CharField(max_length=256)
    doctor_id = models.IntegerField()
    speech_data = models.CharField(max_length=256)
    date = models.DateTimeField()


class Patients(models.Model):
    patient_id = models.IntegerField()
    patient_name = models.CharField(max_length=256)
    patient_age = models.IntegerField()
    patient_sex = models.CharField(max_length=256)
    patient_illness = models.CharField(max_length=256)
    patient_medication = models.CharField(max_length=256)
    patient_doctor_id = models.IntegerField()
    patient_visit_date = models.DateTimeField()
    patient_weight = models.FloatField()
    patient_doctor_notes = models.CharField(max_length=256)
    patient_diabeter_level = models.FloatField()
    patient_choleterol_level = models.FloatField()
    patient_bp_sys = models.IntegerField()
    patient_bp_dias = models.IntegerField()


class SOAP_format_data(models.Model):
    patient_id = models.IntegerField()
    patient_name = models.TextField()
    patient_age = models.IntegerField()
    patient_sex = models.TextField()
    doctor_id = models.IntegerField()
    soap_data = models.TextField()
    date = models.DateTimeField()


class HealthAnalyzer(models.Model):
    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    patient_age = models.IntegerField()
    patient_sex = models.CharField(max_length=256)
    heart_rate = models.IntegerField()
    blood_pressure = models.CharField(max_length=20)
    respiratory_rate = models.IntegerField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    analysis_comments = models.TextField()
    analysis_date = models.DateTimeField()



class PatientHealthData(models.Model):
    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    patient_name = models.TextField()
    patient_sex = models.CharField(max_length=256)
    patient_age = models.IntegerField()
    patient_weight = models.IntegerField()
    heart_rate = models.IntegerField()
    bp_systolic = models.IntegerField()
    bp_diastolic = models.IntegerField()
    oxy_rate = models.IntegerField()
    cholesterol = models.CharField(max_length=256)
    diabetes = models.CharField(max_length=256)


class Tests(models.Model):
    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    patient_name = models.CharField(max_length=256)
    patient_age = models.IntegerField()
    patient_sex = models.CharField(max_length=256)
    patient_weight = models.IntegerField()
    patient_illness = models.CharField(max_length=256)
    patient_medication = models.CharField(max_length=256)
    patient_test_ordered = models.CharField(max_length=256)
    visit_date = models.DateTimeField()
    smart_insights = models.TextField()
