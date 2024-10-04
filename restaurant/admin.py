from django.contrib import admin
from .models import Table, Reservation, Saloon, Capacity, TimeSlot
from django.core.exceptions import ValidationError
from django_jalali.admin.filters import JDateFieldListFilter


class ReservationAdmin(admin.ModelAdmin):
    list_display = ['get_date', 'start_time', 'end_time', 'first_name', 'last_name', 'phone_number', 'get_image', 'status', 'created_by', 'created_at', 'updated_by', 'updated_at']
    list_filter = (
        ('date', JDateFieldListFilter),
    )

class CapacityAdmin(admin.ModelAdmin):
    list_display = ('value',)

    def save_model(self, request, obj, form, change):
        if Capacity.objects.filter(value=obj.value).exclude(pk=obj.pk).exists():
            raise ValidationError(f"The capacity {obj.value} already exists.")
        super().save_model(request, obj, form, change)

class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')

admin.site.register(Saloon)
admin.site.register(Table)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Capacity, CapacityAdmin)
admin.site.register(TimeSlot, TimeSlotAdmin)

