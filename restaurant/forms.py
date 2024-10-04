from django import forms
from .models import Reservation, Table
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['tables', 'date', 'start_time', 'end_time', 'first_name', 'last_name', 'phone_number', 'description', 'image']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'tables': forms.SelectMultiple(),  # Use SelectMultiple to allow selecting multiple tables
        }
        labels = {
            'tables': 'Tables',
            'date': 'Reservation Date',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': 'Phone Number',
            'description': 'Description',
            'image': 'Payment Receipt'
        }

    def __init__(self, *args, **kwargs):
        table_id = kwargs.pop('table_id', None)
        super(ReservationForm, self).__init__(*args, **kwargs)

        self.fields['tables'].queryset = Table.objects.all()

        if table_id:
            table = Table.objects.get(id=table_id)
            self.fields['tables'].initial = [table]

        self.fields['date'] = JalaliDateField(
            label='Date',
            widget=AdminJalaliDateWidget(attrs={'class': 'jalali_date-date'}),
        )
