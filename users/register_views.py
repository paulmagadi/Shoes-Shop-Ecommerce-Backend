from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserRegistrationForm

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from .models import CustomUser
from .tokens import email_verification_token
from django.contrib.auth import login
from django.contrib.auth import get_backends

from .forms import ResendActivationEmailForm


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
            return redirect('login') 
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'users/register_user.html', {'form': form})



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

        backend = get_backends()[0]
        user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

        login(request, user)
        messages.success(request, 'Email verified successfully. You are now logged in.')
        return redirect('home')  
    else:
        messages.error(request, 'Invalid or expired activation link.')
        return redirect('login')

    
    

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