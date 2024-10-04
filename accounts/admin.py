from django.contrib import admin
from .models import Profile, City, State, Job, Hobby, BirthYear, BudgetRange, DietaryPreference, PreferredReservationTime, PhotographyStyle
from django.core.exceptions import ValidationError
from django_jalali.admin.filters import JDateFieldListFilter

admin.site.site_title = "مدیریت سالن آرکانو"  # Set the site title
admin.site.site_header = "مدیریت سالن آرکانو"  # Set the header title
admin.site.index_title = "خوش آمدید به پنل مدیریت سالن آرکانو"  # Set the index title

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'city', 'state']  # Display these fields in the list view
    search_fields = ['user__username', 'phone_number', 'city', 'state']  # Add search functionality
    list_filter = ['city', 'state']  # Add filters for these fields

admin.site.register(Profile, ProfileAdmin)  # Register Profile with the custom ProfileAdmin

admin.site.register(City)
admin.site.register(State)
admin.site.register(Job)
admin.site.register(Hobby)
admin.site.register(BirthYear)
admin.site.register(BudgetRange)
admin.site.register(DietaryPreference)
admin.site.register(PreferredReservationTime)
admin.site.register(PhotographyStyle)
