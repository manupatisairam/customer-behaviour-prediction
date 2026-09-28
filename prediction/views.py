from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from speech_analytics.models import CallData
from .models import Prediction
import random

@login_required(login_url='login')
def predict_behavior_view(request, call_id):
    call_data = get_object_or_404(CallData, id=call_id, user=request.user)
    
    # Check if prediction already exists
    existing_prediction = Prediction.objects.filter(call=call_data).first()
    if existing_prediction:
        return redirect('prediction_result', prediction_id=existing_prediction.id)

    # Prediction Logic
    emotion = call_data.emotion
    sentiment = call_data.sentiment_score # 0-100
    
    behavior = "Neutral"
    confidence = 0.0
    
    # Rules-based prediction (can be replaced with actual ML model)
    if emotion in ['Angry', 'Frustrated', 'Negative']:
        behavior = "Negative"
        confidence = random.uniform(85, 98)
    elif emotion in ['Happy', 'Joy', 'Positive']:
        behavior = "Positive"
        confidence = random.uniform(88, 99)
    else:
        if sentiment > 70:
            behavior = "Positive"
            confidence = random.uniform(70, 85)
        elif sentiment < 30:
            behavior = "Negative"
            confidence = random.uniform(70, 85)
        else:
            behavior = "Neutral"
            confidence = random.uniform(90, 95)

    # Recommendation Engine
    recommendations = []
    if behavior == "Negative":
        recommendations = [
            "Use calm, low-pitched tone and empathetic language.",
            "Acknowledge the frustration immediately: 'I understand why you're upset.'",
            "Avoid interrupting; let the customer vent before providing solutions.",
            "Escalate to a Senior Supervisor if the customer demands it."
        ]
    elif behavior == "Neutral":
        recommendations = [
            "Engage more actively; use the customer's name to build rapport.",
            "Clarify concerns by summarizing: 'Just to confirm, you need help with...'",
            "Provide detailed, step-by-step solutions to prevent follow-up calls.",
            "Ask if there is anything else you can assist with today."
        ]
    else: # Positive
        recommendations = [
            "Maintain an enthusiastic and friendly tone.",
            "This is a high-potential cross-sell moment. Offer the 'Premium Support' add-on.",
            "Thank the customer for their loyalty and positive energy.",
            "Request a formal review or referral if appropriate."
        ]

    recommendation_text = "\n".join(recommendations)

    prediction = Prediction.objects.create(
        user=request.user,
        call=call_data,
        behavior=behavior,
        confidence_score=confidence,
        recommendation=recommendation_text
    )

    messages.success(request, "Behavior prediction generated successfully.")
    return redirect('prediction_result', prediction_id=prediction.id)

@login_required(login_url='login')
def prediction_result_view(request, prediction_id):
    prediction = get_object_or_404(Prediction, id=prediction_id, user=request.user)
    recommendations = prediction.recommendation.split('\n')
    return render(request, 'prediction/result.html', {
        'prediction': prediction,
        'recommendations': recommendations
    })

@login_required(login_url='login')
def prediction_history_view(request):
    predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'prediction/history.html', {'predictions': predictions})
