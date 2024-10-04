from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, City, State, Job, Hobby, DietaryPreference, BudgetRange, PreferredReservationTime, PhotographyStyle
from django.db import IntegrityError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required')
    email = forms.EmailField(required=True, help_text='Required')
    phone_number = forms.CharField(max_length=15, required=True, help_text='Required')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check if the email is already in use in both the User model and Profile model
        if User.objects.filter(email=email).exists() or Profile.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        # Check if the phone number is already in use in both the User model and Profile model
        if User.objects.filter(username=phone_number).exists():
            raise ValidationError('This phone number is already registered as a username.')
        
        if Profile.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('This phone number is already associated with another profile.')

        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        phone_number = self.cleaned_data['phone_number']

        # Set the phone number as the username
        user.username = phone_number
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        try:
            # Use atomic transaction to ensure both user and profile are saved together
            with transaction.atomic():
                user.save()  # Save the user to the database
                
                # After saving the user, create the associated profile
                Profile.objects.create(
                    user=user,
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name'],
                    phone_number=phone_number,
                    email=self.cleaned_data['email'],
                )
        except IntegrityError:
            # If an integrity error occurs, ensure that no partial saves exist
            self.add_error('phone_number', 'A user with this phone number already exists.')
            return None  # Return None so the view knows the save failed
        
        return user


class NameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['sex', 'city', 'state', 'job', 'hobby', 'dietary_preference', 
                  'budget_range', 'number_of_guests', 'preferred_reservation_time', 
                  'photography_style', 'birth_day', 'birth_month', 'birth_year']
        widgets = {
            'sex': forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Select Gender'}),
            'city': forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Select City'}),
            'state': forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Select State'}),
            'job': forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Select Job'}),
            'hobby': forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Select Hobby'}),
            'dietary_preference': forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Select Dietary Preference'}),
            'budget_range': forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Select Budget Range'}),
            'preferred_reservation_time': forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Select Reservation Time'}),
            'photography_style': forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Select Photography Style'}),
            'birth_day': forms.Select(choices=Profile.DAYS, attrs={'class': 'form-control select2', 'placeholder': 'Day'}),
            'birth_month': forms.Select(choices=Profile.MONTHS, attrs={'class': 'form-control select2', 'placeholder': 'Month'}),
            'birth_year': forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Year'}),
        }
