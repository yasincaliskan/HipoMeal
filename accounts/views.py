from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from accounts.models import Profile
from .forms import LoginForm, RegisterForm
from meal.models import Meal


def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('meal:home')
    return render(request, 'accounts/form.html', {'form': form, 'title': 'Login'})


# def register_view(request):
#     form = RegisterForm(request.POST or None)
#     if form.is_valid():
#         user = form.save(commit=False)
#         password = form.cleaned_data.get('password1')
#         user.set_password(password)
#         user.save()
#         new_user = authenticate(username=user.username, password=password)
#         login(request, new_user)
#         return redirect('meal:home')
#     return render(request, 'accounts/form.html', {'form': form, 'title': 'Register'})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/form.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('meal:home')


def about_view(request):
    return render(request, 'accounts/about.html')


# def profile_view(request):
#     meals = Meal.objects.filter(user=request.user)
#     profile = Profile.objects.filter(user=request.user)
#     context = {
#         'meals': meals,
#         'profile': profile
#     }
#     return render(request, 'accounts/profile.html', context)
#






