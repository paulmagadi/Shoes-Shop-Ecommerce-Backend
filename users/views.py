from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout


def register_user(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False 
            user.save()

            messages.success(request, 'Registration successful!')
            return redirect('login')
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'users/register-user.html', {'form': form,})
    


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                messages.info(request, 'Login successful!')
                return redirect('home')  
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login_user.html', {'form': form})
 

def logout_user(request):
    logout(request)
    messages.success(request, ('You have been logged out!!!'))
    return redirect('home')