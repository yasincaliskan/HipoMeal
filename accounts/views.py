from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, RegisterForm


def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('meal:home')
    return render(request, 'accounts/form.html', {'form': form, 'title': 'Login'})


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