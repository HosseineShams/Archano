from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, ProfileForm, NameForm
from .models import Profile
from django.contrib import messages
from django.db import IntegrityError
from django import forms
import random
from django.conf import settings
import ghasedakpack
from django.contrib.auth.models import User  


def entry_view(request):
    return render(request, 'accounts/entry.html')

def login_signup_view(request):
    error_message = None  # Initialize the error message

    if request.method == 'POST':
        # Handle login case
        if 'phone_number' in request.POST and 'password' in request.POST:
            phone_number = request.POST.get('phone_number').strip()
            password = request.POST.get('password').strip()

            # Authenticate using phone number (which is set as the username)
            user = authenticate(request, username=phone_number, password=password)

            if user is not None:
                login(request, user)
                return redirect('saloon_list')
            else:
                error_message = 'Incorrect phone number or password.'

            # Return the same page with error message for login
            return render(request, 'accounts/login.html', {
                'signup_form': SignUpForm(),
                'error': error_message
            })

        # Handle signup case
        else:
            signup_form = SignUpForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                if user is not None:
                    login(request, user)
                    return redirect('login')
            # If form is invalid or save fails, re-render the form with errors
            return render(request, 'accounts/login.html', {
                'signup_form': signup_form,
                'error': None
            })
    else:
        # GET request, show the login/signup page with an empty signup form
        signup_form = SignUpForm()

    return render(request, 'accounts/login.html', {'signup_form': signup_form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    profile = user.profile  # Access the profile associated with the user

    # Handle POST request
    if request.method == 'POST':
        name_form = NameForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if name_form.is_valid() and profile_form.is_valid():
            name_form.save()
            profile_form.save()
            return redirect('restaurant_home')  # Redirect to a success page

    # Handle GET request
    else:
        name_form = NameForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'name_form': name_form,
        'profile_form': profile_form,
        'phone_number': profile.phone_number,
        'email': profile.email
    })


def generate_otp():
    digits = '0123456789'
    otp = ''.join(random.choice(digits) for i in range(6))
    return otp

def login_signup_view(request):
    error_message = None  # Initialize the error message

    if request.method == 'POST':
        # Handle login case
        if 'phone_number' in request.POST and 'password' in request.POST:
            phone_number = request.POST.get('phone_number').strip()
            password = request.POST.get('password').strip()

            # Authenticate using phone number (which is set as the username)
            user = authenticate(request, username=phone_number, password=password)

            if user is not None:
                login(request, user)
                return redirect('saloon_list')
            else:
                error_message = 'Incorrect phone number or password.'

            # Return the same page with error message for login
            return render(request, 'accounts/login.html', {
                'signup_form': SignUpForm(),
                'error': error_message
            })

        # Handle signup case
        else:
            signup_form = SignUpForm(request.POST)
            if signup_form.is_valid():
                phone_number = signup_form.cleaned_data.get('phone_number')

                # Check if phone number is already registered
                if User.objects.filter(username=phone_number).exists():
                    messages.error(request, 'A user with this phone number already exists.')
                    return redirect('login')

                # Generate OTP and send it via Ghasedak API
                otp = generate_otp()
                try:
                    ghasedak = ghasedakpack.Ghasedak(settings.GHASEDAK_API_KEY)
                    ghasedak.verification({
                        'receptor': phone_number,
                        'type': '1',
                        'template': 'Archano',
                        'param1': otp
                    })
                except Exception as e:
                    messages.error(request, 'Failed to send OTP. Please try again later.')
                    return redirect('signup')

                # Save OTP and phone number in session for verification
                request.session['phone_number'] = phone_number
                request.session['otp'] = otp
                request.session['signup_data'] = signup_form.cleaned_data  # Temporarily store form data

                return redirect('verify_otp')  # Redirect to OTP verification page

            # If form is invalid or save fails, re-render the form with errors
            return render(request, 'accounts/login.html', {
                'signup_form': signup_form,
                'error': None
            })

    else:
        # GET request, show the login/signup page with an empty signup form
        signup_form = SignUpForm()

    return render(request, 'accounts/login.html', {'signup_form': signup_form})


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.db import IntegrityError
from django.contrib import messages
from .models import User, Profile

def verify_otp(request):
    # Retrieve the phone number from the session
    phone_number = request.session.get('phone_number')
    
    # If no phone number is found in the session, redirect to the signup page
    if not phone_number:
        return redirect('signup')

    # Initialize error_message for rendering in the template
    error_message = ''

    # Handle POST request when form is submitted
    if request.method == 'POST':
        # Get the OTP entered by the user
        otp = request.POST.get('otp')
        # Get the OTP stored in the session
        session_otp = request.session.get('otp')

        # Check if the entered OTP matches the session OTP
        if otp == session_otp:
            # OTP is correct, proceed to create the user
            signup_data = request.session.get('signup_data')

            if signup_data:
                try:
                    # Create the user with the provided data
                    user = User.objects.create_user(
                        username=signup_data['phone_number'],
                        first_name=signup_data['first_name'],
                        last_name=signup_data['last_name'],
                        email=signup_data['email'],
                        password=signup_data['password1']
                    )

                    # Create a profile for the user
                    Profile.objects.create(
                        user=user,
                        first_name=signup_data['first_name'],
                        last_name=signup_data['last_name'],
                        phone_number=signup_data['phone_number'],
                        email=signup_data['email']
                    )

                    # Clean up the session data after successful signup
                    del request.session['otp']
                    del request.session['signup_data']
                    del request.session['phone_number']

                    # Log the user in and redirect to the saloon list
                    login(request, user)
                    return redirect('saloon_list')

                except IntegrityError:
                    # Handle case where the user creation failed
                    messages.error(request, 'Error while creating user.')
                    return redirect('signup')
        else:
            # Set error message if OTP is invalid
            error_message = 'Invalid OTP. Please try again.'

    # Render the OTP verification page with the phone number and any error message
    return render(request, 'accounts/verify_otp.html', {'phone_number': phone_number, 'error_message': error_message})
