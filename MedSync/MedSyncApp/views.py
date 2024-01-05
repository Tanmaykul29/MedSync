from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import requests
from django.db import IntegrityError
from django.urls import reverse
from .models import *
from django.contrib.auth.hashers import make_password
import speech_recognition as sr
from datetime import datetime
from openai import OpenAI
import numpy as np
from itertools import groupby
from operator import itemgetter

# openai.api_key = "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"
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="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",
)


def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmPassword"]

        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")

def speech_to_text(request):
    if request.method == 'POST':
        text = request.POST.get('converted_text', '')

        patient_id = request.POST.get('patient_id')
        patient_name = request.POST.get('patient_name')
        patient_age = request.POST.get('patient_age')
        patient_sex = request.POST.get('patient_sex')
        doctor_username = request.user.username
        doctor_id = request.user.id
        date = datetime.now()

        SpeechData.objects.create(
            patient_id=patient_id,
            patient_name=patient_name,
            patient_age=patient_age,
            patient_sex=patient_sex,
            doctor_username=doctor_username,
            doctor_id=doctor_id,
            speech_data=text,
            date=date
        )
        speechData_to_SOAP(text, patient_id, doctor_id, patient_name, patient_age, patient_sex)
        return redirect('index')

    return render(request, 'speech_to_text.html')


def speechData_to_SOAP(text, patient_id, doctor_id, patient_name,patient_age, patient_sex):
    message = "Convert the patient data to SOAP format: "
    message += text
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message}
        ]
    )
    reply = completion.choices[0].message.content.strip()
    date = datetime.now()
    patient_id=patient_id
    patient_name=patient_name
    patient_age = patient_age
    patient_sex = patient_sex
    doctor_id=doctor_id
    SOAP_format_data.objects.create(
        patient_id=patient_id,
        patient_name=patient_name,
        patient_age=patient_age,
        patient_sex = patient_sex,
        doctor_id = doctor_id,
        soap_data = reply,
        date = date
    )


def patient_history(request):
    doc_id = request.user.id
    my_patients = SOAP_format_data.objects.filter(doctor_id=doc_id)
    result_dict = {}
    for patient in my_patients:
        patient_id = patient.patient_id
        print(patient)
        if patient_id not in result_dict:
            result_dict[patient_id] = [patient]
        else:
            result_dict[patient_id].append(patient)


    return render(request, "patient_history.html",{
        "result_dict":result_dict
    })



def health_analyzer(request):
    doc_id = request.user.id
    all_patients = PatientHealthData.objects.all()
    my_patients = PatientHealthData.objects.filter(doctor_id=doc_id)

    age_cat = ["10-20","21-30","31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100"]
    heart_rate_data = [0,0,0,0,0,0,0,0,0]
    age_heart_rate_values = []
    age_bp_diastolic_values = []
    diabetes_data = [0, 0, 0, 0]
    diabetes_cat = ['low', 'normal', 'borderline_high', 'high']
    cholesterol_data = [0, 0, 0, 0, 0]
    cholesterol_cat = ['low', 'borderline_low', 'normal', 'borderline_high', 'high']

    for patient in all_patients:
        age_bp_diastolic_values.append({'x':patient.patient_age, 'y':patient.bp_diastolic,  'sex': patient.patient_sex})

    for patient in all_patients:
        age_heart_rate_values.append({'x':patient.patient_age, 'y':patient.heart_rate, 'sex': patient.patient_sex})

    for patient in all_patients:
        if patient.diabetes == 'low':
            diabetes_data[0]+=1
        elif patient.diabetes == 'normal':
            diabetes_data[1]+=1
        elif patient.diabetes == 'borderline_high':
            diabetes_data[2]+=1
        elif patient.diabetes == 'high':
            diabetes_data[3]+=1

    for patient in all_patients:
        if patient.cholesterol == 'low':
            cholesterol_data[0]+=1
        elif patient.cholesterol == 'borderline_low':
            cholesterol_data[1]+=1
        elif patient.cholesterol == 'normal':
            cholesterol_data[2]+=1
        elif patient.cholesterol == 'borderline_high':
            cholesterol_data[3]+=1
        elif patient.cholesterol == 'high':
            cholesterol_data[4]+=1



    for patient in all_patients:
        if patient.patient_age>=10 and patient.patient_age<=20:
            heart_rate_data[0]+=1
        elif patient.patient_age>=21 and patient.patient_age<=30:
            heart_rate_data[1]+=1
        elif patient.patient_age>=31 and patient.patient_age<=40:
            heart_rate_data[2]+=1
        elif patient.patient_age>=41 and patient.patient_age<=50:
            heart_rate_data[3]+=1
        elif patient.patient_age>=51 and patient.patient_age<=60:
            heart_rate_data[4]+=1
        elif patient.patient_age>=61 and patient.patient_age<=70:
            heart_rate_data[5]+=1
        elif patient.patient_age>=71 and patient.patient_age<=80:
            heart_rate_data[6]+=1
        elif patient.patient_age>=81 and patient.patient_age<=90:
            heart_rate_data[7]+=1
        elif patient.patient_age>=91 and patient.patient_age<=100:
            heart_rate_data[8]+=1

    age_bp_sex_values = []

    for patient in all_patients:
        age_bp_sex_values.append({'x': patient.patient_age, 'y': patient.bp_systolic, 'sex': patient.patient_sex})

    return render(request, 'health_analyzer.html', {
        "my_patients": my_patients,
        "all_patients": all_patients,
        "heart_rate_data": heart_rate_data,
        "age_cat": age_cat,
        "age_heart_rate_values": age_heart_rate_values,
        "age_bp_diastolic_values": age_bp_diastolic_values,
        "age_bp_sex_values": age_bp_sex_values,
        "diabetes_cat":diabetes_cat,
        "diabetes_data":diabetes_data,
        "cholesterol_cat":cholesterol_cat,
        "cholesterol_data":cholesterol_data
    })


def patient_management(request):
    if request.method=="POST":
        patientdata = PatientHealthData.objects.all()

        patient_id = len(patientdata)+1
        doctor_id = request.user.id
        patient_name = request.POST.get('patient_name')
        patient_sex = request.POST.get('patient_sex')
        patient_age = request.POST.get('patient_age')
        patient_weight = request.POST.get('patient_weight')
        heart_rate = request.POST.get('heart_rate')
        bp_systolic = request.POST.get('bp_systolic')
        bp_diastolic = request.POST.get('bp_diastolic')
        oxy_rate = request.POST.get('oxy_rate')
        cholesterol = request.POST.get('cholesterol')
        diabetes = request.POST.get('diabetes')
        PatientHealthData.objects.create(
            id = patient_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            patient_name=patient_name,
            patient_sex=patient_sex,
            patient_age=patient_age,
            patient_weight=patient_weight,
            heart_rate=heart_rate,
            bp_systolic=bp_systolic,
            bp_diastolic=bp_diastolic,
            oxy_rate=oxy_rate,
            cholesterol=cholesterol,
            diabetes=diabetes
        )
        return redirect('index')

    else:
        doc_id = request.user.id
        my_patients = PatientHealthData.objects.filter(doctor_id=doc_id)
        data_size = len(my_patients)
        return render(request, "patient_management.html", {
            "my_patients":my_patients
        })


def medication_tracker(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient_id")
        patient_name = request.POST.get("patient_name")
        patient_age = request.POST.get("patient_age")
        patient_sex = request.POST.get("patient_sex")
        patient_illness = request.POST.get("patient_illness")
        patient_medication = request.POST.get("patient_medication")
        patient_doctor_id = request.user.id
        patient_visit_date = datetime.now()
        patient_weight = request.POST.get("patient_weight")
        patient_doctor_notes = request.POST.get("patient_doctor_notes")
        patient_diabeter_level = request.POST.get("patient_diabeter_level")
        patient_choleterol_level = request.POST.get("patient_choleterol_level")
        patient_bp_sys = request.POST.get("patient_bp_sys")
        patient_bp_dias = request.POST.get("patient_bp_dias")
        Patients.objects.create(
            patient_id=patient_id,
            patient_name=patient_name,
            patient_age=patient_age,
            patient_sex=patient_sex,
            patient_illness=patient_illness,
            patient_medication=patient_medication,
            patient_doctor_id=patient_doctor_id,
            patient_visit_date=patient_visit_date,
            patient_weight=patient_weight,
            patient_doctor_notes=patient_doctor_notes,
            patient_diabeter_level=patient_diabeter_level,
            patient_choleterol_level=patient_choleterol_level,
            patient_bp_sys=patient_bp_sys,
            patient_bp_dias=patient_bp_dias
        )
        return redirect('index')
    else:
        doc_id = request.user.id
        my_patients = PatientHealthData.objects.filter(doctor_id=doc_id)
        return render(request, "medication_tracker.html",{
            "my_patients":my_patients
        })


def patient_med_tracker(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient_id")
        patient_data = Patients.objects.filter(patient_id=patient_id)
        pname = ""
        visit_dates = []
        diabetes, cholesterol, bp_sys, bp_dia = [], [], [], []
        for data in patient_data:
            pname=data.patient_name
            page=data.patient_age
            psex=data.patient_sex
            diabetes.append(data.patient_diabeter_level)
            day = str(data.patient_visit_date.day) + "-" + str(data.patient_visit_date.month) + "-" + str(data.patient_visit_date.year)
            visit_dates.append(day)
            cholesterol.append(data.patient_choleterol_level)
            bp_sys.append(data.patient_bp_sys)
            bp_dia.append(data.patient_bp_dias)

        if len(patient_data)!=0:
            message = "Provide smart notes and trends based on patient data: diabetes (mg/dL)" +str(diabetes)+  ", cholesterol (mg/dL) " +str(cholesterol)+" , Bp systolic (mmHg): " + str(bp_sys)+" , Bp diastolic (mmHg): "+str(bp_dia)+" for "+pname+" a "+str(page)+" old "+psex
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": message}
                ]
            )
            reply = completion.choices[0].message.content.strip()


        return render(request, "patient_info.html", {
            "patient_data": patient_data,
            "diabetes": diabetes,
            "cholesterol": cholesterol,
            "bp_sys": bp_sys,
            "bp_dia": bp_dia,
            "visit_dates": visit_dates,
            "smart_notes":reply
        })


def tests(request):
    doc_id = request.user.id
    my_patients = PatientHealthData.objects.filter(doctor_id=doc_id)
    return render(request, "tests.html",{
        "my_patients":my_patients
    })


def patient_test(request, id):
    if request.method == "POST":
        doc_id = request.user.id
        pat_id = id
        patient = PatientHealthData.objects.filter(patient_id=pat_id)

        pname=patient[0].patient_name
        psex=patient[0].patient_sex
        page=request.POST.get("patient_age")
        pweight=request.POST.get("patient_weight")
        pDiag=request.POST.get("patient_illness")
        pTreat=request.POST.get("patient_medication")
        pTests = request.POST.get("patient_test_ordered")

        message = "generate smart insights on reason of test ordered and why other test are not ordered for patient data: name= "+pname+" age: "+page+" with weight: "+pweight+" sex:"+psex+" , Diagnosis: "+pDiag+", Treatment: "+pTreat+", Tests ordered: "+pTests
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        reply = completion.choices[0].message.content.strip()


        Tests.objects.create(
            patient_id=pat_id,
            doctor_id = doc_id,
            patient_name = pname,
            patient_age = page,
            patient_sex = psex,
            patient_weight = pweight,
            patient_illness = pDiag,
            patient_medication = pTreat,
            patient_test_ordered = pTests,
            visit_date = datetime.now(),
            smart_insights = reply
        )
        return redirect('index')
    else:
        doc_id = request.user.id
        pat_tests = Tests.objects.filter(patient_id=id, doctor_id=doc_id)
        return render(request, "patient_test.html", {
            "pat_tests": pat_tests,
            "patient_id":id
        })
