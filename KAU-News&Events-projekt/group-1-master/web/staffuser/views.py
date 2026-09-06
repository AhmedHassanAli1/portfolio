
from django.shortcuts import render, redirect
from Publication.models import Publication_News, Publication_Event, NewsFile, EventFile, RecurringEvent
from authuser.models import Department, Tag
from .ApprovalForm import ApprovalNewsForm, ApprovalEventForm
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.core.mail import * 
from django.conf import settings


# Create your views here.

def SendRejectionEmail(request, entry, reject_text):
    if(reject_text):
                    
        # Send rejection email
        message = reject_text
        email = entry.Email
        name = entry.Author
        subject = 'Your Publication Request has been Rejected'
        text_message = f'Dear {name},\n\nWe regret to inform you that your publication request has been rejected for the following reason:\n\n{reject_text}\n\nBest regards,\nStaff User Team'
        send_mail(
                        subject,
                        text_message,
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )
        entry.delete()
        messages.success(request, 'Request was rejected successfully')
    else:
        messages.error(request,'Error: Request could not be rejected due to empty reject text')


def staffuser_home(request):
    query = request.GET.get('q', '').strip()
    news = Publication_News.objects.all().order_by('-PublicationDate')
    events = Publication_Event.objects.all().order_by('-PublicationDate')

    if query:
        news = news.filter(
            Q(NewsTitle__icontains=query) |
            Q(Author__icontains=query) |
            Q(NewsDesc__icontains=query)
        )
        events = events.filter(
            Q(EventTitle__icontains=query) |
            Q(Author__icontains=query) |
            Q(EventDesc__icontains=query)
        )

    departments = Department.objects.all()
    tags = Tag.objects.all()
    context = {
        'tags': tags,
        'news': news,
        'events': events,
        'departments': departments,
        'query': query,
        }
    return render(request, 'staffuser/staffuser.html', context)

def view_request(request,id):
    rec_event = None
    type = request.GET.get('type','Not provided')
    if not type:
        type = request.POST.get('type','Not provided')
    form = None
    entry = None
    if type=='news':
        entry = Publication_News.objects.get(News_PublicationID=id)
        files = NewsFile.objects.filter(News=id)
        form = ApprovalNewsForm()
    elif type=='event':
        entry = Publication_Event.objects.get(Event_PublicationID=id)
        if entry.is_recurring:
            rec_event = RecurringEvent.objects.get(event=id)
        files = EventFile.objects.filter(Event=id)
        form = ApprovalEventForm()
    if request.method == "POST": 
        if type=='news':
            form = ApprovalNewsForm(request.POST)
        elif type=='event':
            form = ApprovalEventForm(request.POST)
        if form.is_valid():
            entry.is_approved = form.cleaned_data['is_approved']
            if(entry.is_approved == "True"):
                entry.save()
                messages.success(request, 'Request processed successfully.')
            elif (entry.is_approved == "False"):
                reject_text = form.cleaned_data['reject_text']
                try:
                    SendRejectionEmail(request, entry, reject_text)
                except Exception as e:
                    #HttpResponse(request, f'Error sending rejection email: {str(e)}')
                    messages.error(request, f'Error sending rejection email: {str(e)}')

            return redirect('/staffuser')    
    
    context = {
        'form': form,
        'entry': entry,
        'rec_event': rec_event,
        'files': files,
        'type': type,
    }

    return render(request, 'staffuser/view_request.html',context) 


