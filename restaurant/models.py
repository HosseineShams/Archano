from django.db import models
from django_jalali.db import models as jmodels
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from datetime import datetime, timedelta
from accounts.middleware import CurrentUserMiddleware
from accounts.models import Profile

class Saloon(models.Model):
    name = models.CharField(null=True, blank=True, max_length=30, verbose_name='Saloon Name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "سالن"
        verbose_name_plural = "سالن ها"


class Table(models.Model):
    saloon = models.ForeignKey(Saloon, verbose_name='Saloon', on_delete=models.CASCADE, null=True)
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=30, null=True)
    capacity = models.IntegerField(null=True)

    def __str__(self):
        return f"Table {self.name}"

    class Meta:
        verbose_name = "میز"
        verbose_name_plural = "میزها"


class Capacity(models.Model):
    value = models.IntegerField(unique=True, verbose_name='Capacity')

    def __str__(self):
        return f"{self.value} guests"

    class Meta:
        verbose_name = "ظرفیت"
        verbose_name_plural = "ظرفیت ها"


class TimeSlot(models.Model):
    name = models.CharField(max_length=50, verbose_name="Time Slot Name")
    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="End Time")

    def __str__(self):
        return f"{self.name}: {self.start_time} - {self.end_time}"

    class Meta:
        verbose_name = "زمان"
        verbose_name_plural = "زمان ها"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
    ]

    tables = models.ManyToManyField(Table, verbose_name='Tables')
    date = jmodels.jDateField(verbose_name='Date')
    start_time = models.TimeField(verbose_name='Start Time')
    end_time = models.TimeField(verbose_name='End Time')
    first_name = models.CharField(verbose_name='First Name', max_length=20, null=True, blank=True)
    last_name = models.CharField(verbose_name='Last Name', max_length=50, null=False, blank=False)
    phone_number = models.CharField(verbose_name='Phone Number', max_length=11, null=False, blank=False)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    image = models.ImageField(verbose_name='Payment Receipt', upload_to='images/', validators=[], null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Created By', related_name='created_reservations', null=True)
    created_at = jmodels.jDateField(auto_now_add=True, verbose_name='Created Date', null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Updated By', related_name='updated_reservations', null=True)
    updated_at = jmodels.jDateField(auto_now=True, verbose_name='Updated Date')

    class Meta:
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'

    def clean(self):
        if self.pk:  # Only perform validation if the reservation has been saved and has a primary key
            if self.status in ['pending', 'approved']:
                overlapping_reservations = Reservation.objects.filter(
                    tables__in=self.tables.all(),
                    date=self.date,
                    start_time__lt=self.end_time,
                    end_time__gt=self.start_time,
                    status__in=['pending', 'approved'],
                ).exclude(id=self.id).distinct()

                if overlapping_reservations.exists():
                    raise ValidationError("Selected table is already reserved at the chosen time.")

                # Handle duration across midnight
                if self.end_time < self.start_time:
                    duration = (datetime.combine(datetime.min + timedelta(days=1), self.end_time) - datetime.combine(datetime.min, self.start_time)).total_seconds() / 3600
                else:
                    duration = (datetime.combine(datetime.min, self.end_time) - datetime.combine(datetime.min, self.start_time)).total_seconds() / 3600

                if duration > 2.5:
                    raise ValidationError("Reservation duration cannot exceed 2.5 hours.")

                if not self.is_within_time_slots():
                    raise ValidationError("Reservations are allowed only between 12 PM to 4 PM and 6 PM to 1 AM.")

    def is_within_time_slots(self):
        slots = TimeSlot.objects.all()
        for slot in slots:
            if slot.start_time < slot.end_time:
                # Normal case: Time slot within the same day
                if self.start_time >= slot.start_time and self.end_time <= slot.end_time:
                    return True
            else:
                # Case where the time slot spans midnight
                if (self.start_time >= slot.start_time or self.start_time < slot.end_time) and (
                    self.end_time > slot.start_time or self.end_time <= slot.end_time):
                    return True
        return False

    def save(self, *args, **kwargs):
        # Temporarily bypass clean during the first save to avoid accessing the many-to-many before the ID is available
        if not self.pk:
            super().save(*args, **kwargs)
        else:
            self.clean()  # Perform the validation now that we have a primary key
            super().save(*args, **kwargs)

    def calculate_reserved_and_remaining_time(self):
        gregorian_date = self.date.togregorian()
        time_slots = TimeSlot.objects.all()
        reserved_time = 0
        total_slot_time = 0

        for slot in time_slots:
            slot_start = datetime.combine(gregorian_date, slot.start_time)
            if slot.end_time < slot.start_time:
                slot_end = datetime.combine(gregorian_date + timedelta(days=1), slot.end_time)
            else:
                slot_end = datetime.combine(gregorian_date, slot.end_time)
            
            slot_total_seconds = (slot_end - slot_start).total_seconds()
            total_slot_time += slot_total_seconds

            reservations = Reservation.objects.filter(
                tables__in=self.tables.all(),
                date=self.date,
                status='approved',
                start_time__lt=slot_end.time(),
                end_time__gt=slot_start.time()
            ).distinct()

            for reservation in reservations:
                res_start = datetime.combine(gregorian_date, reservation.start_time)
                if reservation.end_time < reservation.start_time:
                    res_end = datetime.combine(gregorian_date + timedelta(days=1), reservation.end_time)
                else:
                    res_end = datetime.combine(gregorian_date, reservation.end_time)

                overlap_start = max(slot_start, res_start)
                overlap_end = min(slot_end, res_end)

                if overlap_start < overlap_end:
                    overlap_seconds = (overlap_end - overlap_start).total_seconds()
                    reserved_time += overlap_seconds

        remaining_time = round((total_slot_time - reserved_time) / 3600, 2)
        reserved_time_hours = round(reserved_time / 3600, 2)
        
        return reserved_time_hours, remaining_time

    def get_image(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" alt="{self.last_name}" width="150" height="100">')
        else:
            return mark_safe('<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRsNGGjrfSqqv8UjL18xS4YypbK-q7po_8oVQ&usqp=CAU" width="100" height="100">')
    get_image.short_description = 'Payment Receipt'

    def __str__(self):
        return f"Reservation for {self.get_date()} from {self.start_time} to {self.end_time}"

    def get_date(self):
        return self.date.strftime('%Y/%m/%d')
    get_date.short_description = "Reservation Date"


    class Meta:
        verbose_name = 'رزرو'
        verbose_name_plural = 'رزروها'


@receiver(pre_save, sender=Reservation)
def set_updated_by(sender, instance, **kwargs):
    current_user = CurrentUserMiddleware.get_current_user()
    if current_user and instance.pk:  
        instance.updated_by = current_user
