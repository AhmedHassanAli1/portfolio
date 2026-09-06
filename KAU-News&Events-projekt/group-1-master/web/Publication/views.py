from django.shortcuts import render, redirect
from django.http import HttpResponse
from .PublicationForm import PublicationEventForm, PublicationNewsForm, MultipleFilesForm
from .RecurringEventForm import RecurringEventForm, BydayForm
from .models import NewsFile, EventFile, RecurringEvent, Publication_Event
from django.contrib import messages
from django.forms import formset_factory
from dateutil.rrule import *
from datetime import datetime, timedelta, time
from dateutil import relativedelta

# Create your views here.

def rec_event_create(data,event):
    RecurringEvent.objects.create(
        event_id=event.Event_PublicationID,
        rrule=data["rrule"],
        freq=data["freq"],
        interval=data["interval"],
        dtstart=datetime.combine(event.EventStartDate,event.EventStartTime),
        duration=calc_duration(event),
        count=data["count"],
        until=data["until"],
        bymonth=data["bymonth"],
        bymonthday=data["bymonthday"],
        byyearday=data["byyearday"],
        byweekno=data["byweekno"],
        byweekday=data["byweekday"],
        weekday_byday=data["weekday_byday"]


    )
def get_byday_formset_data(formset):
    tmp_list = []
    for form in formset:
        tmp_list.append(int(form.cleaned_data["byday"]))
        tmp_list.append(int(form.cleaned_data["day"]))
    return tmp_list
def calc_duration(event):
    if type(event)==dict:
        start = datetime.combine(event["EventStartDate"],event["EventStartTime"])
        end = datetime.combine(event["EventEndDate"],event["EventEndTime"])
    else:
        start = datetime.combine(event.EventStartDate,event.EventStartTime)
        end = datetime.combine(event.EventEndDate,event.EventEndTime)

    return end-start

def create_rrule(data,event):
    #from .models import Publication_Event # Solves circular import problem
    #event = Publication_Event.objects.get(Event_PublicationID=data["event_id"])
    start = datetime.combine(event["EventStartDate"],event["EventStartTime"])
    #end = datetime.combine(event["EventEndDate"],event["EventEndTime"])
    #data["duration"] = end-start
    str_rrule = "rrule("
    str_rrule += f"freq={get_freq(data)},"
    str_rrule += f"interval={data["interval"]},"
    dtstart = repr(start).replace(".datetime","")
    str_rrule += f"dtstart={dtstart},"
    if data["count"] and data["count"] > 0:
        str_rrule += f"count={data["count"]},"
    if data["until"]:
        dt_until = datetime.combine(data["until"],time(0,0))
        str_until = repr(dt_until).replace(".datetime","")
        print(str_until)
        str_rrule += f"until={str_until},"
    if data["bymonth"]:
        str_rrule += f"bymonth={get_list(data["bymonth"])},"
    if data["bymonthday"]:
        str_rrule += f"bymonthday={get_list(data["bymonthday"])},"
    if data["byyearday"]:
        str_rrule += f"byyearday={get_list(data["byyearday"])},"
    if data["byweekday"]:
        str_rrule += f"byweekday={get_list(data["byweekday"])},"
    elif is_weekday_byday(data):
        str_rrule += f"byweekday={get_weekday_byday(data)}"
    str_rrule += ")"
    return str_rrule

        
        
def get_freq(data):
    if data["freq"]=="1":
        return "DAILY"
    elif data["freq"]=="2":
        return "WEEKLY"
    elif data["freq"]=="3":
        return "MONTHLY"
    elif data["freq"]=="4":
        return "YEARLY"
def get_list(arr):
    if len(arr) == 1:
        return str(arr[0])
    else:
        str_arr = "("
        for value in arr:
            str_arr += f"{value},"
        str_arr += ")"
        return str_arr
def is_weekday_byday(data):
    if(data["weekday_byday"]):
        for value in data["weekday_byday"]:
            if value != 0:
                return True
    return False
def get_weekday_byday(data):
    str_byday = "("
    for i in range(0,len(data["weekday_byday"]),2):
        nth = data["weekday_byday"][i]
        day = data["weekday_byday"][i+1]
        if day != 0:
            str_byday += f"{get_byday_day(day)}({nth}),"
    str_byday += ")"
    return str_byday
def get_byday_day(value):
    if value==1:
        return "MO"
    elif value==2:
        return "TU"
    elif value==3:
        return "WE"
    elif value==4:
        return "TU"
    elif value==5:
        return "FR"
    elif value==6:
        return "SA"
    elif value==7:
        return "SU"
    else:
        return "ERROR"
def byday_ok(byday_list):
    for i in range(0,len(byday_list)-1,2):
        if byday_list[i] == 0 and byday_list[i+1] != 0:
            return False
        if byday_list[i] != 0 and byday_list[i+1] == 0:
            return False
    return True
def recurrence_ok(str_rrule,event,duration):
    rrule = eval(str_rrule)
    startdate = datetime.combine(event["EventStartDate"],event["EventStartTime"])
    recs = list(rrule.xafter(startdate,2))
    if len(recs) > 1:
        for i in range(0,len(recs)-1):
            if recs[i] + duration > recs[i+1]:
                return False
            if i > 10:
                return True
    elif startdate + duration > recs[0]:
        return False
    
    return True
def date_ok(data):
    sdate = datetime.combine(data["EventStartDate"],data["EventStartTime"])
    edate = datetime.combine(data["EventEndDate"],data["EventEndTime"])
    now = datetime.now()
    if sdate < now:
        return False
    elif sdate > edate:
        return False
    return True
def get_date_error(data):
    sdate = datetime.combine(data["EventStartDate"],data["EventStartTime"])
    edate = datetime.combine(data["EventEndDate"],data["EventEndTime"])
    now = datetime.now()
    if sdate < now:
        return f"Invalid start date: {sdate.strftime("%Y-%m-%d")}. Event cannot begin before current date: {now.strftime("%Y-%m-%d")}."
    elif sdate > edate:
        return f"Invalid start date: {sdate.strftime("%Y-%m-%d")}. Event start must be before end date: {edate.strftime("%Y-%m-%d")}"
    return True

def publication_event_view(request):
    byday_formset = formset_factory(BydayForm,extra=10)
    if request.method == "POST":
        event_form = PublicationEventForm(request.POST)
        files_form = MultipleFilesForm(request.POST,request.FILES)
        rec_form = RecurringEventForm(request.POST)
        files = request.FILES.getlist('files')
        formset = byday_formset(request.POST)
        if event_form.is_valid() and files_form.is_valid() and rec_form.is_valid() and formset.is_valid():
            if date_ok(event_form.cleaned_data):
                if request.POST.get("is_recurring"):
                    rec_form.cleaned_data.update({"weekday_byday": get_byday_formset_data(formset)})
                    byday_is_ok = byday_ok(rec_form.cleaned_data["weekday_byday"])
                    if byday_is_ok:
                        rrule = create_rrule(rec_form.cleaned_data,event_form.cleaned_data)
                        rec_form.cleaned_data.update({"rrule": rrule})
                        rec_is_ok = recurrence_ok(rrule,event_form.cleaned_data,calc_duration(event_form.cleaned_data))
                        if  rec_is_ok:
                            event = event_form.save()
                            rec_event_create(rec_form.cleaned_data,event)
                            for f in files:
                                EventFile.objects.create(Event=event,File=f)
                            messages.success(request, 'Request successfully.')
                            return redirect('/')
                        else:
                            messages.error(request, 'Recurrence overlap, event cannot recur before it\'s completed')
                    else:
                        messages.error(request, 'Invalid byday settings, use \'-\' for both or none')
                else:
                    event = event_form.save()
                    for f in files:
                        EventFile.objects.create(Event=event,File=f)
                    messages.success(request, 'Request successfully.')
                    return redirect('/')
            else:
                messages.error(request, get_date_error(event_form.cleaned_data))
        else:
            messages.error(request, 'Request unsuccessful.') 


    else:
        event_form = PublicationEventForm()
        files_form = MultipleFilesForm()
        rec_form = RecurringEventForm()
        formset = byday_formset()

    return render(request, "Publication/publication_events.html", {
        "event_form": event_form,
        "files_form": files_form,
        "rec_form": rec_form,
        "formset": formset
        })


def publication_news_view(request):
    if request.method == "POST":
        news_form = PublicationNewsForm(request.POST)
        files_form = MultipleFilesForm(request.POST,request.FILES)
        files = request.FILES.getlist('files')
        if news_form.is_valid() and files_form.is_valid():
            news = news_form.save()
            for f in files:
                NewsFile.objects.create(News=news,File=f)
            messages.success(request, 'Request  successfully.')
            return redirect('/')
        messages.error(request, 'Request unsuccessful.')    
    else:
        news_form = PublicationNewsForm()
        files_form = MultipleFilesForm()
       

    return render(request, "Publication/publication_news.html", {
        "news_form": news_form,
        "files_form": files_form,
        })


