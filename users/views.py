from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout

from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import login

from .forms import CustomUserRegistrationForm
from .models import CustomUser
from .tokens import email_verification_token


def register_user(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Prevent login before email verification
            user.save()

            # Email verification
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = email_verification_token.make_token(user)
            activation_link = f"{request.scheme}://{current_site.domain}/activate/{uid}/{token}/"

            subject = 'Activate your Shoe Shop account'
            message = render_to_string('users/activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            messages.success(request, 'Account created! Please check your email to activate your account.')
            return redirect('login')  # Adjust this if you have a named login URL
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'users/register_user.html', {'form': form})


from django.contrib.auth import login
from django.contrib.auth import get_backends

def activate_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and email_verification_token.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True
        user.save()

        # ✅ FIX: set the backend manually
        backend = get_backends()[0]
        user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

        login(request, user)
        messages.success(request, 'Email verified successfully. You are now logged in.')
        return redirect('home')  # or home
    else:
        messages.error(request, 'Invalid or expired activation link.')
        return redirect('login')

    
    
from .forms import ResendActivationEmailForm
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import email_verification_token
from django.contrib.sites.shortcuts import get_current_site

def resend_activation_user(request):
    if request.method == 'POST':
        form = ResendActivationEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                if user.is_email_verified:
                    messages.info(request, "This account is already verified. You can log in.")
                    return redirect('login')

                current_site = get_current_site(request)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = email_verification_token.make_token(user)
                activation_link = f"{request.scheme}://{current_site.domain}/activate/{uid}/{token}/"

                subject = 'Activate your Shoe Shop account (Resent)'
                message = render_to_string('users/activation_email.html', {
                    'user': user,
                    'activation_link': activation_link,
                })

                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                messages.success(request, "A new activation email has been sent.")
                return redirect('login')
            except CustomUser.DoesNotExist:
                messages.error(request, "No account found with that email.")
    else:
        form = ResendActivationEmailForm()

    return render(request, 'users/resend_activation.html', {'form': form})




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

def login_user(request):
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
                return redirect('home')  # adjust as needed
            else:
                messages.error(request, "Invalid credentials.")
    return render(request, 'users/login_user.html', {'form': form})

 

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
    return render(request, 'users/dashboard.html', {'user': request.user})


@login_required
def update_profile_view(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('dashboard')
    else:
        form = UpdateUserForm(instance=request.user)
    return render(request, 'users/profile_update.html', {'form': form})
