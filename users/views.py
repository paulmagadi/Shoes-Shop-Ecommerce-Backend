
# def register_user(request):
#     if request.method == 'POST':
#         form = CustomUserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False 
#             user.save()

#             messages.success(request, 'Registration successful!')
#             return redirect('login')
#         else:
#             messages.error(request, "Unsuccessful registration. Invalid information.")
#     else:
#         form = CustomUserRegistrationForm()
#     return render(request, 'users/register-user.html', {'form': form,})
    


# def login_user(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)

#                 messages.info(request, 'Login successful!')
#                 return redirect('home')  
#             else:
#                 messages.error(request, "Invalid username or password.")
#         else:
#             messages.error(request, "Invalid username or password.")
#     else:
#         form = AuthenticationForm()
#     return render(request, 'users/login_user.html', {'form': form})


from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout

from django.utils.http import url_has_allowed_host_and_scheme


def login_user(request):
    # Next URL validation
    next_url = request.GET.get('next') or request.POST.get('next', '/')  
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = '/' 
    
    # Redirect if already authenticated
    if request.user.is_authenticated:
        return redirect(next_url)
    
    form = AuthenticationForm(request, data=request.POST or None)
    email_entered = ""

    if request.method == 'POST':
        if form.is_valid():
            email_entered = form.cleaned_data.get('username')  # this is 'email' in our case
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email_entered, password=password)

            if user is not None:
                if not user.is_active or not user.is_email_verified:
                    messages.warning(request, "Your account is not verified yet.")
                    return render(request, 'users/login_user.html', {
                        'form': form,
                        'show_resend_button': True,
                        'resend_email': email_entered
                    })
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect(next_url)  
            else:
                messages.error(request, "Invalid credentials.")
    return render(request, 'users/login_user.html', {'form': form, 'next': next_url,})

 

def logout_user(request):
    logout(request)
    messages.success(request, ('You have been logged out!!!'))
    return redirect('home')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UpdateUserForm
from django.contrib import messages

@login_required
def dashboard_view(request):
    return render(request, 'users/user_account.html', {'user': request.user})


@login_required
def update_profile_view(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('account')
    else:
        form = UpdateUserForm(instance=request.user)
    return render(request, 'users/profile_update.html', {'form': form})
