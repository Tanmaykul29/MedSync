from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("logout", views.logout_view, name="logout"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),

    path('speech-to-text/', views.speech_to_text, name='speech_to_text'),
    path("patient_history", views.patient_history, name="patient_history"),
    path('health_analyzer/', views.health_analyzer, name='health_analyzer'),
    path('patient_management', views.patient_management, name='patient_management'),
    path('medication_tracker', views.medication_tracker, name='medication_tracker'),
    path('patient_med_tracker', views.patient_med_tracker, name='patient_med_tracker'),
]