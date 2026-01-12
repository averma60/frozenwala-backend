from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.cache import never_cache
from .forms import CustomAuthenticationForm  # Assuming you have a custom authentication form
AUTH_USER_MODEL = 'backendlogin.BackendCustomUser'
from ecomApp.models import CustomUser
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
class CustomUserBackend(BaseBackend):
    def authenticate(self, request, phone_number=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password,is_staff=True,is_influencer=False)

            if user is not None and  user.is_staff and not user.is_influencer:
                login(request, user)
                next_url = request.GET.get('next', reverse('backend/dashboard'))
                return redirect(next_url)
            else:
                return render(request, 'backend/login.html', {'form': form, 'error': 'Invalid login credentials'})
    else:
        form = CustomAuthenticationForm()
    if request.session.get('logged_out'):
        del request.session['logged_out']

    return render(request, 'backend/login.html', {'form': form, 'error': 'Invalid login credentials'})



def logout_view(request):
    if request.user.is_authenticated and request.user.is_staff and not request.user.is_influencer:
        request.session['logged_out'] = True  # Set session variable to indicate logout
        logout(request)
    return redirect('backend/login')
# @login_required(login_url='backend/login')
# def dashboard(request):
#     return render(request, 'backend/dashboard.html')