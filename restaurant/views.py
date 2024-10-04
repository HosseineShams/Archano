from django.shortcuts import render, get_object_or_404, redirect
from .models import Table, Reservation, Saloon, TimeSlot
from .forms import ReservationForm
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import jdatetime
from django.core.exceptions import ValidationError


def restaurant_home(request):
    return render(request, 'restaurant/home.html')

@login_required
def make_reservation(request, table_id=None):
    table = get_object_or_404(Table, id=table_id)
    saloon = table.saloon

    if request.method == 'POST':
        form = ReservationForm(request.POST, request.FILES, table_id=table_id)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.created_by = request.user
            reservation.save()
            selected_tables = form.cleaned_data.get('tables')
            reservation.tables.set(selected_tables)
            try:
                reservation.clean()
                reservation.save()
            except ValidationError as e:
                form.add_error(None, e.message)
                reservation.delete()
                return render(request, 'restaurant/make_reservation.html', {'form': form, 'table': table, 'saloon': saloon})
            return redirect('table_detail', table_id=table.id)
    else:
        form = ReservationForm(table_id=table_id)

    return render(request, 'restaurant/make_reservation.html', {'form': form, 'table': table, 'saloon': saloon})


# @login_required
# def table_detail(request, table_id):
#     table = get_object_or_404(Table, id=table_id)
#     reservations = Reservation.objects.filter(tables=table, status='approved').order_by('-date', '-start_time')

#     return render(request, 'restaurant/table_detail.html', {
#         'table': table,
#         'reservations': reservations,
#     })
@login_required
def table_detail(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    reservations = Reservation.objects.filter(tables=table, status='approved').order_by('-date', '-start_time')
    saloon = table.saloon  # Assuming each table has a related saloon

    return render(request, 'restaurant/table_detail.html', {
        'table': table,
        'reservations': reservations,
        'saloon': saloon,  # Add saloon to the context
    })


@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST, request.FILES, instance=reservation)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.save()
            selected_tables = form.cleaned_data.get('tables')
            reservation.tables.set(selected_tables)
            reservation.clean()
            reservation.save()
            return redirect('table_detail', table_id=reservation.tables.first().id)
    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'restaurant/edit_reservation.html', {'form': form, 'reservation': reservation})


@login_required
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        reservation.delete()
        return redirect('table_history')

    return render(request, 'restaurant/delete_reservation.html', {'reservation': reservation})


@login_required
def saloon_list(request):
    saloons = Saloon.objects.all()
    return render(request, 'restaurant/saloon_list.html', {'saloons': saloons})


# @login_required
# def saloon_tables(request, saloon_id):
#     saloon = get_object_or_404(Saloon, id=saloon_id)
#     current_date = jdatetime.date.fromgregorian(date=now().date())

#     reservation_data = {}
#     for table in saloon.table_set.all():
#         reservations = Reservation.objects.filter(tables=table, date=current_date, status='approved')
#         reserved_time = sum(reservation.end_time.hour - reservation.start_time.hour for reservation in reservations)
#         reservation_data[table.id] = {'reservation_count': reservations.count(), 'reserved_time': reserved_time}

#     return render(request, 'restaurant/saloon_tables.html', {
#         'saloon': saloon,
#         'reservation_data': reservation_data,
#     })

@login_required
def saloon_tables(request, saloon_id):
    saloon = get_object_or_404(Saloon, id=saloon_id)
    current_date = jdatetime.date.fromgregorian(date=now().date())

    reservation_data = {}
    for table in saloon.table_set.all():
        reservations = Reservation.objects.filter(tables=table, date=current_date, status='approved')
        reservation_list = [{'start_time': reservation.start_time, 'end_time': reservation.end_time} for reservation in reservations]
        reservation_data[table.id] = {
            'reservation_count': reservations.count(),
            'reserved_time': sum(reservation.end_time.hour - reservation.start_time.hour for reservation in reservations),
            'reservation_times': reservation_list  # Pass the start and end times here
        }

    return render(request, 'restaurant/saloon_tables.html', {
        'saloon': saloon,
        'reservation_data': reservation_data,
    })

@login_required
def table_history(request):
    user_reservations = Reservation.objects.filter(created_by=request.user).order_by('-date', '-start_time')

    return render(request, 'restaurant/table_history.html', {
        'user_reservations': user_reservations
    })
