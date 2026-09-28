from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_audio_view, name='upload_audio'),
    path('process/<int:call_id>/', views.process_audio_view, name='process_audio'),
    path('result/<int:call_id>/', views.result_view, name='result'),
]
