from django.urls import path
from . import views

urlpatterns = [
    path('predict/<int:call_id>/', views.predict_behavior_view, name='predict_behavior'),
    path('result/<int:prediction_id>/', views.prediction_result_view, name='prediction_result'),
    path('history/', views.prediction_history_view, name='prediction_history'),
]
