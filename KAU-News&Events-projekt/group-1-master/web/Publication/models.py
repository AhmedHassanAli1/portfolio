from django.db import models
from authuser.models import Department, Tag, CustomUser
from django.utils import timezone
import pathlib
import uuid
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
from dateutil.rrule import *
import os
import shutil
# Create your models here.
class Publication_Event(models.Model):
    Event_PublicationID = models.AutoField(primary_key=True,unique=True)
    Author = models.CharField(max_length=200, default = '00000')
    Username = models.CharField(max_length=200, default='00000')
    EventTitle = models.CharField(max_length=200, default = '00000')
    EventDesc = models.TextField(default = '00000')
    EventStartDate = models.DateField(default = timezone.now)
    EventStartTime = models.TimeField(default = '00:00')
    EventEndDate = models.DateField(default = timezone.now)
    EventEndTime = models.TimeField(default = '00:00')
    PublicationDate = models.DateField(auto_now_add=True)
    Department = models.ManyToManyField(Department,related_name='Event_Publications')
    Email = models.EmailField(max_length=200, default = '00000')
    Organization = models.CharField(max_length=200, default = '00000')
    EventLocation = models.CharField(max_length=200, default = '00000')
    Tag = models.ManyToManyField(Tag,related_name='Event_Tag')
    CustomUser = models.ManyToManyField(CustomUser, related_name='Event_Attendees')
    is_approved = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=False)

    def __str__(self):
        return self.EventTitle
    class Meta:
        verbose_name_plural = "events"

class RecurringEvent(models.Model):
    event = models.ForeignKey(Publication_Event,on_delete=models.CASCADE,related_name="rec_events")
    rrule = models.CharField(null=True,blank=True)
    class Freq(models.IntegerChoices):
        DAILY = 1, 'Daily',
        WEEKLY = 2, 'Weekly'
        MONTHLY = 3, 'Monthly',
        YEARLY = 4, 'Yearly'
    freq = models.IntegerField(choices=Freq.choices)
    interval = models.IntegerField()
    dtstart = models.DateField(null=True,blank=True)
    duration = models.DurationField(null=True,blank=True)
    count = models.PositiveIntegerField(null=True,blank=True)
    until = models.DateField(null=True,blank=True)
    class Month(models.IntegerChoices):
        JAN = 1, 'January',
        FEB = 2, 'February',
        MAR = 3, 'March',
        APR = 4, 'April',
        MAY = 5, 'May',
        JUN = 6, 'June',
        JUL = 7, 'July'
        AUG = 8, 'August'
        SEP = 9, 'September'
        OCT = 10, 'October'
        NOV = 11, 'November'
        DEC = 12, 'December'
    bymonth = ArrayField(models.IntegerField(
        null = True,
        blank = True,
        choices=Month.choices
    ),null=True, blank=True)
    bymonthday = ArrayField(models.IntegerField(
        null = True,
        blank = True,
        validators=[MaxValueValidator(31),MinValueValidator(-30)]
    ),null=True, blank=True)
    byyearday = ArrayField(models.IntegerField(
        null = True,
        blank = True,
        validators=[MaxValueValidator(365),MinValueValidator(-364)]
    ),null=True, blank=True)
    byweekno = ArrayField(models.IntegerField(
        null = True,
        blank = True,
        validators=[MaxValueValidator(52),MinValueValidator(-51)]
    ),null=True, blank=True)
    class Weekday(models.IntegerChoices):
        MO = 0, 'Monday',
        TU = 1, 'Tuesday',
        WE = 2, 'Wednesday',
        TH = 3, 'Thursday',
        FR = 4, 'Friday',
        SA = 5, 'Saturday',
        SU = 6, 'Sunday'
    byweekday = ArrayField(models.IntegerField(
        null = True,
        blank = True,
        choices=Weekday.choices
    ),null=True, blank=True)
    class Byday(models.IntegerChoices):
        NONCE = 0, '-',
        FIRST = 1, 'First',
        SECOND = 2, 'Second',
        THIRD = 3, 'Third',
        FOURTH = 4, 'Fourth',
        FIFTH = 5, 'Fifth',
        NTL = -2, 'Next to last'
        LAST = -1, 'Last'

    weekday_byday = ArrayField(models.IntegerField(
        null = True,
        blank = True,
        choices=Byday.choices
    ),null=True, blank=True)

    def __is_byday(self):
        for i in range(0,len(self.weekday_byday)):
            if self.weekday_byday[i] != 0:
                return True
        return False

    def __str_freq(self):
        if self.interval == 1:
            if self.freq == self.Freq.DAILY:
                return "day"
            if self.freq == self.Freq.WEEKLY:
                return "week"
            if self.freq == self.Freq.MONTHLY:
                return "month"
            if self.freq == self.Freq.YEARLY:
                return "year"
        else:
            if self.freq == self.Freq.DAILY:
                return "days"
            if self.freq == self.Freq.WEEKLY:
                return "weeks"
            if self.freq == self.Freq.MONTHLY:
                return "months"
            if self.freq == self.Freq.YEARLY:
                return "years"
    
    def __str_interval(self):
        if self.interval == 1:
            return "Every"
        else:
            return f"Every {self.interval}"
    
    def __str_weekday(self):
        str_res = ""
        for value in self.byweekday:
            str_res += f"{self.Weekday.choices[value][1]}, "
        return str_res[:-2]

    def __str_monthdays(self):
        str_res = ""
        for value in self.bymonthday:
            str_res += f"{value}, "
        return str_res[:-2]

    def __str_weekday_byday(self):
        str_res = ""
        for i in range(0,len(self.weekday_byday)-1,2):
            if self.weekday_byday[i] != 0:
                i_by = self.weekday_byday[i]
                i_day = self.weekday_byday[i+1]
                str_res += f"{self.Byday.choices[i_by][1]} {self.Weekday.choices[i_day-1][1]}, "
        return str_res[:-2]
    def __str_yeardays(self):
        str_res = ""
        for value in self.byyearday:
            str_res += f"{value}, "
        return str_res
    def __str_month(self):
        str_res = ""
        for value in self.bymonth:
            str_res += f"{self.Month.choices[value-1][1]}, "
        return str_res[:-2]

    def get_rrule_as_text(self):
        str_rrule = self.__str_weekday()
        str_rrule = ""

        # Eg Every 3 months...
        # Interval + freq
        # if weekly and weekdays -> on monday, sunday...
        # if monthly and monthday -> On day: 3,10,-1...
        # if monthly and On the -> First monday, third Wednesday...
        # yearly and yeardays -> On day: 50, 100, -20...
        # yearly and months -> In months: ...
        # yearly and months and weekdays -> In months: ..., On the
        str_rrule += f"{self.__str_interval()} {self.__str_freq()} "

        if self.freq == self.Freq.DAILY:
            pass
        elif self.freq == self.Freq.WEEKLY:
            if self.byweekday:
                str_rrule += f"On: {self.__str_weekday()}"
        elif self.freq == self.Freq.MONTHLY:
            if self.bymonthday:
                str_rrule += f"on days: {self.__str_monthdays()}"
            elif self.__is_byday():
                str_rrule += f"on the: {self.__str_weekday_byday()}"
        elif self.freq == self.Freq.YEARLY:
            if self.byyearday:
                str_rrule += f"on days: {self.__str_yeardays()}"
            elif self.bymonth:
                str_rrule += f"in months: {self.__str_month()}"
                if self.__is_byday():
                    str_rrule += f" | on the: {self.__str_weekday_byday()}"
        return str_rrule.lower().capitalize()
    def get_last_recurrence(self):
        str_res = ""
        if self.count or self.until:
            last_rec = list(eval(self.rrule))[-1]
            str_res += f"\nFrom {last_rec.strftime("%Y-%m-%d")} to {(last_rec + self.duration).strftime("%Y-%m-%d")}"
        else: 
            str_res = "Always recurring"
        return str_res
        

    def get_next_recurrences(self):
        strs_recs = []
        today = datetime.now()
        recs = list(eval(self.rrule).xafter(today,3))
        if recs:
            for rec in recs:
                strs_recs.append(f"From {rec.strftime("%Y-%m-%d %H:%M")} to {(rec + self.duration).strftime("%Y-%m-%d %H:%M")}")
        else:
            strs_recs.append("Nothing found")    
        return strs_recs

        
    
    



class Publication_News(models.Model):
    News_PublicationID = models.AutoField(primary_key=True,unique=True)
    Author = models.CharField(max_length=200, default = '00000')
    NewsTitle = models.CharField(max_length=200, default = '00000')
    NewsDesc = models.TextField(default = '00000')
    PublicationDate = models.DateField(auto_now_add=True)
    Department = models.ManyToManyField(Department,related_name= 'News_Publications')
    Email = models.EmailField(max_length=200, default = '00000')
    Organization = models.CharField(max_length=200, default = '00000')
    Tag = models.ManyToManyField(Tag,related_name='News_Tags')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.NewsTitle
    class Meta:
        verbose_name_plural = "news"




def event_upload_dir(instance,filename):
    return f"event_files/{instance.Event.Event_PublicationID}/{pathlib.Path(filename)}"

class EventFile(models.Model):

    Event = models.ForeignKey(Publication_Event,on_delete=models.CASCADE,related_name="files")
    File = models.FileField(upload_to=event_upload_dir)
    
    def filename(self):
        return pathlib.Path(self.File.name).name

    def filetype(self):
        return pathlib.Path(self.File.name).suffix
    
    def is_image(self):
        f_type = self.filetype()
        return f_type == ".jpg" or f_type == ".jpeg" or f_type == ".png"

@receiver(models.signals.pre_delete, sender=Publication_Event)
def auto_delete_files_pre_delete(sender, instance: Publication_Event, **kwargs):
    """
    Delete folder with files when corresponding event is deleted
    """
    event_file = EventFile.objects.filter(Event=instance).first()
    if event_file:
        folder = pathlib.Path(event_file.File.path).resolve().parent
        if folder.exists():
            shutil.rmtree(folder)





def news_upload_dir(instance,filename):
    return f"news_files/{instance.News.News_PublicationID}/{pathlib.Path(filename)}"

class NewsFile(models.Model):
    News = models.ForeignKey(Publication_News,on_delete=models.CASCADE,related_name="files")
    File = models.FileField(upload_to=news_upload_dir)
    
    def filename(self):
        return pathlib.Path(self.File.name).name

    def filetype(self):
        return pathlib.Path(self.File.name).suffix
    
    def is_image(self):
        f_type = self.filetype()
        return f_type == ".jpg" or f_type == ".jpeg" or f_type == ".png"

@receiver(models.signals.pre_delete, sender=Publication_News)
def auto_delete_files_pre_delete(sender, instance: Publication_News, **kwargs):
    """
    Delete folder with files when corresponding news is deleted
    """
    news_file = NewsFile.objects.filter(News=instance).first()
    if news_file:
        folder = pathlib.Path(news_file.File.path).resolve().parent
        if folder.exists():
            shutil.rmtree(folder)
    

