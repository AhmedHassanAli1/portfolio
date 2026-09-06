from django.http import HttpResponse
import calendar # Import the calendar module to work with dates
#from django.shortcuts import render
from calendar import *
from authuser.models import *
from Publication.models import *


class CalendarEventsForm(HTMLCalendar):
    #Method to group events by day from database to be used in formatday method
    # Based on https://stackoverflow.com/a/1458077/1639671

    def __init__(self,year,month,highlight= [], *args, **kwargs):
        # Call the parent HTMLCalendar constructor to set up defaults
        super().__init__(*args, **kwargs)

        # Store the list (or range) of days that should be highlighted
        # Example: highlight = [1, 2, 3] means days 1, 2, and 3 of the month
        self._highlight = highlight
        self.year=year
        self.month=month

    def formatday(self, day, weekday):
        """
        Return a single day cell (<td>) for the calendar.
        This overrides the parent method to add highlighting.
        """

        # If the current day is in the highlight list

        if (day in self._highlight):
            # Return a <td> with:
            # - the weekday CSS class (e.g., 'mon', 'tue', etc.)
            # - a red dot color
            # - the day number inside
            EventsCounter = self._highlight[day]
            str_html = (
                f'<td class="{self.cssclasses[weekday]}" data-day="{day}">'
                f'<a class="day-a" href="/calendarevents/{self.year}/{self.month}?day={day}">' 
                '<div>'
                f'{day}' 
                '<div class="event-wrapper">' 
                '<div class="event-dot"> </div>' 
            )
            if EventsCounter > 1:
                str_html += f'<div class="event-count">+{EventsCounter-1}</div>'
            str_html +=  (
                '</div>'
                '</div>'
                '</a>'
                f'</td>'
            )
            return str_html
            """"
            return (f'<td class="{self.cssclasses[weekday]}" data-day="{day}">'
                    f'<a class="day-a" href="/calendarevents/{self.year}/{self.month}?day={day}">'
                    '<div>'
                    f'{day}'
                        '<div class="event-wrapper">'
                        '<div class="event-dot"> </div>'
                            f'<div class="event-count">+{EventsCounter}</div>'
                        '</div>'
                        '</div>'
                        '</a>'
                     f'</td>'
                    )
            """

        else:
            # Otherwise, fall back to the default HTMLCalendar behavior
            # This will render a normal <td> cell for the day
            return super().formatday(day, weekday)


# Example usage:
# Highlight days 1 through 6 of the month
highlight = range(1, 7)


# html_calendar now contains a full <table> of the month,
# with days 1–6 rendered with a pink background.
    


