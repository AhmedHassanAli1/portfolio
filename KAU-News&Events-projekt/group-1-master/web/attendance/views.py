from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from Publication.models import Publication_Event
from .models import EventAttendance
from django.shortcuts import render
from .attendanceform import EventAttendanceForm
from django.http import HttpResponse
from django.contrib import messages

def attendance_home(request):
    events = Publication_Event.objects.filter(is_approved=True)
    return render(request, 'attendance/attendance.html', {'events': events})


@login_required
def attend_event(request, event_id):
    event = get_object_or_404(Publication_Event, pk=event_id)


    if request.method == "POST":
        if EventAttendance.objects.filter(event=event, user=request.user).exists():
            messages.error(request, f"You have already signed up for {event.EventTitle}.")
            return redirect('attendance_home')
        allergies = request.POST.get("allergies")
        dietary = request.POST.get("dietary_preferences")
        notes = request.POST.get("notes")
        attendance = EventAttendance.objects.create(
            event=event,
            user=request.user,
            allergies=allergies,
            dietary_preferences=dietary,
            notes=notes,
        )
        messages.success(request, f"Thank you for signing up for {event.EventTitle}.")
        return redirect('attendance_home')
        
        

    return render(request, "attendance/attend_form.html", {"event": event})


@login_required
def unattend_event(request, event_id):
    if request.method == "POST":
        event = get_object_or_404(Publication_Event, pk=event_id)
        attendance = EventAttendance.objects.filter(event=event, user=request.user)
        if attendance.exists():
            attendance.delete()
            messages.success(request, f"You have cancelled your registration for {event.EventTitle}.")
        else:
            messages.warning(request, "You were not registered for this event.")
        return redirect('attendance_home')
    else:
        messages.error(request, "Invalid request method.")
        return redirect("/")