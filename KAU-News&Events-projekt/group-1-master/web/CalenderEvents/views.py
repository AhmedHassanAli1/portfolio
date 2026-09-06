# Create your views here.
from django.http import HttpResponse
import calendar # Import the calendar module to work with dates
from django.shortcuts import render
from calendar import HTMLCalendar
from authuser.models import *
from Publication.models import *
from .CalendarEventsForm import CalendarEventsForm
from datetime import *
from dateutil import relativedelta
from collections import Counter
from dateutil.rrule import *


now_date = datetime.now()
# Get events that overlap a specific day
def get_day_events(year,month,day):
    date = datetime(year,month,day)
    next_day = date + timedelta(days=1)
    events = Publication_Event.objects.all()
    event_list = []
    for event in events:
        if event.is_approved:
            if event.is_recurring:
                rec_event = RecurringEvent.objects.get(event=event.Event_PublicationID)
                rec_rrule = eval(rec_event.rrule)
                rec_date = rec_rrule.before(next_day)
                if rec_date and rec_date + rec_event.duration >= date:
                    entry = {"event": event, "start": rec_date, "end": rec_date+rec_event.duration}
                    event_list.append(entry)
            else:
                dtstart = datetime.combine(event.EventStartDate,event.EventStartTime)
                dtend = datetime.combine(event.EventEndDate,event.EventEndTime)
                if (dtstart <= date and date <= dtend) or dtstart.day == date.day:
                    entry = {"event": event, "start": dtstart, "end": dtend}
                    event_list.append(entry)
    return event_list

#–––––––––––––––––––––––––––– Useful functions begin
# Returns an interval list with all relevant event occurences
def get_recurrences(rrule,current_month,duration):
    interval_list = []
    next_month = current_month + relativedelta.relativedelta(months=1)
    date = next_month
    while True:
        rec = rrule.before(date) # Get first occurence before date
        if rec:
            if rec + duration >= current_month: # occurence is visible in month
                interval = {"start": rec, "end": rec+duration}
                interval_list.append(interval)
            else: # occurence is not visible -> don't need to go further back
                return interval_list
        else:
            return interval_list # no more occurences
        date = rec # Use current occurence to check next occurence

# Input a event interval and current month, returns interval type (-1) to 3
def interval_type(event,current_month):
    next_month = current_month + relativedelta.relativedelta(months=1)

    if event["start"] >= next_month:
        return -1 # Event start after this month

    if event["start"] < current_month:
        if event["end"] < next_month:
            return 0 # Event begins before and ends after this month
        elif event["end"] >= next_month:
            return 3 # Event begins before and ends after this month
    
    if event["start"] >= current_month:
        if event["end"] < next_month:
            return 1 # Event begins and ends this month
        elif event["end"] >= next_month:
            return 2 # Event begins but does not end this month
# Get correctly numbered days between two dates if in same month
def get_days(startdate,enddate):
    days_list = []
    for day in range(0,((enddate-startdate).days)+1):
        days_list.append(day+startdate.day)
    return days_list

# Input a interval_list and current month, returns a dict with day number as key and event occurences as value
def get_all_days(interval_list, current_month):
    event_days = []
    next_month = current_month + relativedelta.relativedelta(months=1)

    for entry in interval_list:
        interval = interval_type(entry,current_month) # get interval type
        if interval == 0:
            event_days += get_days(current_month,entry["end"]) # days from month start to event end
        elif interval == 1:
            event_days += get_days(entry["start"],entry["end"]) # days from event start to event end
        elif interval == 2:
            event_days += get_days(entry["start"],next_month) # days from event start to month end
        elif interval == 3:
            event_days += get_days(current_month,next_month) # all days of the month
    return Counter(event_days) 
#–––––––––––––––––––––––––––– Useful functions end

# Create your views here.
def CalendarEvents_view(request):#, year, month):
    if request.method == "GET":
        departments = Department.objects.all()
        tags = Tag.objects.all()
        publication_Events = Publication_Event.objects.all()
        RecurringEventsList = RecurringEvent.objects.all()
        RelavantDaysList = []
        RelavantMonthsList = []
        IntervalEventsList = []
        

        #Define current month and year
        month = calendar.month_name[now_date.month]
        year = now_date.year
            
        # Convert month name to month number by finding its index in the list of month names
        month_number = int(list(calendar.month_name).index(month)) 
        previousYear = year
        nextYear = year
        if month_number <= 0:
            return HttpResponse("Invalid month name")  # Return an error if the month name is invalid
        else:
            if month_number > 1 and month_number <= 11:
                previous_month = month_number - 1
                next_month = month_number + 1

            elif month_number == 12:
                previous_month = month_number - 1
                next_month = 1
                if next_month == 1 :
                    nextYear = year + 1

            elif month_number == 1:
                previous_month = 12 
                previousYear = year - 1
                next_month = month_number + 1
            
            if month_number == 1:
                year  = nextYear  

            elif month_number == 12:
                year = previousYear
            
            
            for event in publication_Events:
                if event.is_approved:
                    if event.is_recurring:
                        for recurringEvent in RecurringEventsList:
                            if event.Event_PublicationID == recurringEvent.event.Event_PublicationID:
                                # Get all occurences of the recurring event in the current month 
                                IntervalEventsList += get_recurrences(eval(recurringEvent.rrule),datetime(year,month_number,1),recurringEvent.duration)
                                break
                    else:
                        #Convert Event start and end from date to datetime objects
                        EventStartDateTime = datetime.combine(event.EventStartDate, event.EventStartTime)
                        EventEndDateTime = datetime.combine(event.EventEndDate, event.EventEndTime)

                        IntervalEventsList += [{"start": EventStartDateTime, "end": EventEndDateTime}]
                    

            EventsDictionary = get_all_days(IntervalEventsList, datetime(year,month_number,1))
           # EventsList = list(EventsDictionary.keys())

            previous_monthName = calendar.month_name[previous_month]  # Get the name of the previous month
            next_monthName = calendar.month_name[next_month]  # Get the name of the next month
            
            # Generate the HTML calendar for the specified year and month
            CalendarHTML = CalendarEventsForm(highlight=EventsDictionary,year=year,month=month).formatmonth(year,month_number)
        #print(RecurringEventsList)
        #print(publication_Events)
    context = {
        #"EventsDictionary": EventsDictionary,
        #"EventsList": EventsList,
        "departments": departments,
        "tags": tags,
        "publication_Events": publication_Events,
        "year": year,
        "nextYear": nextYear,
        "previousYear": previousYear,
        "month": month,
        "month_number": month_number,
        "previous_monthName": previous_monthName,
        "next_monthName": next_monthName,
        "CalendarHTML": CalendarHTML,
    }
    #Render the CalendarEvents.html template with the form as context
    return render(request, "CalenderEvents/CalendarEvents.html", context)  

def CalendarEvents_view_previous_or_next(request, year, month):
    if request.method == "GET":
        day = request.GET.get('day',None)
        day_events = []
        departments = Department.objects.all()
        tags = Tag.objects.all()
        publication_Events = Publication_Event.objects.all()
        RelavantDaysList = []
        RelavantMonthsList = []
        RecurringEventsList = RecurringEvent.objects.all()

        IntervalEventsList = []
       
        # Capitalize the first letter of the month to match the format in calendar.month_name
        month = month.capitalize()

        # Convert month name to month number by finding its index in the list of month names
        month_number = int(list(calendar.month_name).index(month)) 
        previousYear = year
        nextYear = year
        if month_number <= 0:
            return HttpResponse("Invalid month name")  # Return an error if the month name is invalid
        else:
            if month_number > 1 and month_number <= 11:
                previous_month = month_number - 1
                next_month = month_number + 1

            elif month_number == 12:
                previous_month = month_number - 1
                next_month = 1
                if next_month == 1 :
                    nextYear = year + 1

            elif month_number == 1:
                previous_month = 12 
                previousYear = year - 1
                next_month = month_number + 1
            
            if month_number == 1:
                year  = nextYear  

            elif month_number == 12:
                year = previousYear
            
            for event in publication_Events:
                if event.is_approved:
                    if event.is_recurring:
                        for recurringEvent in RecurringEventsList:
                            if event.Event_PublicationID == recurringEvent.event.Event_PublicationID:
                                # Get all occurences of the recurring event in the current month 
                                IntervalEventsList += get_recurrences(eval(recurringEvent.rrule),datetime(year,month_number,1),recurringEvent.duration)
                                break
                    else:
                        #Convert Event start and end from date to datetime objects
                        EventStartDateTime = datetime.combine(event.EventStartDate, event.EventStartTime)
                        EventEndDateTime = datetime.combine(event.EventEndDate, event.EventEndTime)

                        IntervalEventsList += [{"start": EventStartDateTime, "end": EventEndDateTime}]                    

            EventsDictionary = get_all_days(IntervalEventsList, datetime(year,month_number,1))
            #EventsList = list(EventsDictionary.values())

            previous_monthName = calendar.month_name[previous_month]  # Get the name of the previous month
            next_monthName = calendar.month_name[next_month]  # Get the name of the next month

            # Generate the HTML calendar for the specified year and month
            CalendarHTML = CalendarEventsForm(highlight=EventsDictionary,year=year,month=month).formatmonth(year,month_number)

            if day:
                day_events = get_day_events(year,month_number,int(day))
                print(day_events)
            
    context = {
        #"EventsDictionary": EventsDictionary,
        #"EventsList": EventsList,
        "departments": departments,
        "tags": tags,
        "publication_Events": publication_Events,
        "year": year,
        "nextYear": nextYear,
        "previousYear": previousYear,
        "month": month,
        "month_number": month_number,
        "previous_monthName": previous_monthName,
        "next_monthName": next_monthName,
        "CalendarHTML": CalendarHTML,
        "day_events": day_events,
        "day": day
    }
    #Render the CalendarEvents.html template with the form as context
    return render(request, "CalenderEvents/CalendarEvents.html", context)  