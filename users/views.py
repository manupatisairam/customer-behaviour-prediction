from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm

def home_view(request):
    return render(request, 'home.html')

def about_view(request):
    return render(request, 'about.html')

def login_view(request):
    if request.user.is_authenticated and not request.GET.get('reauth'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to the AI Call Center System!")
            return redirect('dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('home')

@login_required(login_url='login')
def dashboard_view(request):
    from speech_analytics.models import CallData
    from prediction.models import Prediction
    recent_calls = CallData.objects.filter(user=request.user).order_by('-created_at')[:5]
    recent_predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')[:5]
    latest_prediction = recent_predictions.first()
    return render(request, 'dashboard.html', {
        'recent_calls': recent_calls,
        'recent_predictions': recent_predictions,
        'latest_prediction': latest_prediction
    })

def admin_login_view(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN':
        return redirect('admin_panel:admin_panel_dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_staff or user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'ADMIN'):
                    login(request, user)
                    messages.success(request, f"Welcome to Admin Terminal, {username}.")
                    return redirect('admin_panel:admin_panel_dashboard')
                else:
                    messages.error(request, "Access Denied. You do not have administrative privileges.")
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "Invalid credentials.")
    
    form = AuthenticationForm()
    return render(request, 'admin_login.html', {'form': form})

@login_required(login_url='admin_login')
def admin_dashboard_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
        messages.error(request, "Unauthorized access. Administrative profile required.")
        return redirect('home')
    
    from .models import Profile, Role
    from django.contrib.auth.models import User
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        if user_id and new_role:
            target_user = User.objects.get(id=user_id)
            target_user.profile.role = new_role
            target_user.profile.save()
            messages.success(request, f"Role for {target_user.username} updated to {new_role}.")
            return redirect('admin_dashboard')

    users = User.objects.all().select_related('profile')
    roles = Role.choices
    return render(request, 'admin_dashboard.html', {'all_users': users, 'roles': roles})
