from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class BirthYear(models.Model):
    year = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return self.year

    class Meta:
        verbose_name = "سال تولد"
        verbose_name_plural = "سال‌های تولد"
        
        
class City(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "شهر"
        verbose_name_plural = "شهرها"


class State(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "منطقه"
        verbose_name_plural = "مناطق"


class Job(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "شغل"
        verbose_name_plural = "شغل‌ها"


class Hobby(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "سرگرمی"
        verbose_name_plural = "سرگرمی‌ها"


class DietaryPreference(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Dietary Preference')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ترجیحات غذایی"
        verbose_name_plural = "ترجیحات غذایی"


class BudgetRange(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Budget Range')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "محدوده بودجه"
        verbose_name_plural = "محدوده‌های بودجه"


class PreferredReservationTime(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Preferred Reservation Time')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "زمان رزرو مورد علاقه"
        verbose_name_plural = "زمان‌های رزرو مورد علاقه"


class PhotographyStyle(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Preferred Photography Style')

    def __str__(self):
        return self.name

    class  Meta:
        verbose_name = "سبک عکاسی مورد علاقه"
        verbose_name_plural = "سبک‌های عکاسی مورد علاقه"
        

class Profile(models.Model):
    SEX_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True, validators=[EmailValidator()], null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, verbose_name='شهر')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, verbose_name='منطقه')
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, default='M', verbose_name='جنسیت')
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, verbose_name='شغل')
    hobby = models.ForeignKey(Hobby, on_delete=models.SET_NULL, null=True, verbose_name='سرگرمی')
    dietary_preference = models.ForeignKey(DietaryPreference, on_delete=models.SET_NULL, null=True, verbose_name='غذای مورد علاقه شما')
    budget_range = models.ForeignKey(BudgetRange, on_delete=models.SET_NULL, null=True, verbose_name='برای یک کافه رفتن معمولا چه مبلغی را در نظر می‌گیرید؟')
    number_of_guests = models.PositiveIntegerField(null=True, blank=True, verbose_name='معمولا با چند نفر می‌آیید؟')
    preferred_reservation_time = models.ForeignKey(PreferredReservationTime, on_delete=models.SET_NULL, null=True, verbose_name='زمان مورد علاقه برای رزرو')
    photography_style = models.ForeignKey(PhotographyStyle, on_delete=models.SET_NULL, null=True, verbose_name='سبک عکاسی مورد علاقه شما')

    DAYS = [(str(i), str(i)) for i in range(1, 32)]
    MONTHS = [
        ('1', 'فروردین'), ('2', 'اردیبهشت'), ('3', 'خرداد'),
        ('4', 'تیر'), ('5', 'مرداد'), ('6', 'شهریور'),
        ('7', 'مهر'), ('8', 'آبان'), ('9', 'آذر'),
        ('10', 'دی'), ('11', 'بهمن'), ('12', 'اسفند')
    ]

    birth_day = models.CharField(max_length=2, choices=DAYS, default='1', verbose_name='روز تولد')
    birth_month = models.CharField(max_length=2, choices=MONTHS, default='1', verbose_name='ماه تولد')
    birth_year = models.ForeignKey('BirthYear', on_delete=models.SET_NULL, null=True, verbose_name='سال تولد')

    def __str__(self):
        return f"{self.first_name} {self.last_name}'s Profile"

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل‌ها"


# # Signal to create a profile for each new user
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# # Signal to save profile when user is saved
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
