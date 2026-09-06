from django.shortcuts import render
from Publication.models import Publication_Event, Publication_News, EventFile, NewsFile, RecurringEvent
from authuser.models import Department, Tag  
from staffuser.views import view_request
from attendance.views import attendance_home
from attendance.models import EventAttendance
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q


def index(request):
    query = request.GET.get('q', '').strip()

    news = Publication_News.objects.filter(is_approved=True).order_by('-PublicationDate')
    events = Publication_Event.objects.filter(is_approved=True).order_by('-PublicationDate')

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
        'news': news,
        'events': events,
        'departments': departments,
        'tags': tags,
        'query': query,
    }
    return render(request, "template.html", context)

def publication_events (request):
    return render(request, 'Publication/publication_events.html')

def publication_news (request):
    return render(request, 'Publication/publication_news.html')

def register(request):
    return render(request, 'register/register.html')

def index4 (request):
    return render(request, 'login/login.html')

def index6 (request):
    return render(request, 'template.html')

def read_more(request, id): 
    rec_event = None
    type = request.GET.get('type', 'Not provided')
    if not type:  
        type = request.POST.get('type', 'Not provided')  
    entry = None
    if type == 'news':  
        entry = Publication_News.objects.get(News_PublicationID=id)
        files = NewsFile.objects.filter(News=id)
    elif type == 'event':  
        entry = Publication_Event.objects.get(Event_PublicationID=id)
        files = EventFile.objects.filter(Event=id)
        if entry.is_recurring:
            rec_event = RecurringEvent.objects.get(event=id)

    context = {
        'entry': entry,
        'rec_event': rec_event,
        'files': files,
        'type': type
    }
    return render(request, 'read_more.html', context)


def admin_index():
    return render(request, 'custom_admin/base.html')

def get_attend(request):
    user = User.objects.get(id=request.user.id)
    entry = entry.objects.get(id=entry_id)

    return render(request, 'read_more.html'), {'user': user, 'entry' : entry}

def att_list(request, id):
    event = Publication_Event.objects.get(Event_PublicationID=id)
    attendees = EventAttendance.objects.filter(event=event).select_related('user')
    
    context = {
        'event' : event,
        'attendees' : attendees
    }
    return render(request, 'att_list.html', context)
def calendar_view(request):
    return render(request, 'CalenderEvents/CalendarEvents.html')

def delete_publication(request,id):
    type = request.GET.get('type', None)
    if not type:
        type = request.POST.get('type', None)
    if request.method == 'POST':
        print(request.POST)
        if type=='news':
            entry=Publication_News.objects.get(News_PublicationID=id)
        elif type=='event':
            entry=Publication_Event.objects.get(Event_PublicationID=id)
        
        messages.success(request, 'Publication was deleted')
        entry.delete()
        return redirect('/')
        
    return redirect('/')
