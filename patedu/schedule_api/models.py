from djcelery.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from datetime import datetime
from django.db import models

# Create your models here.

class TaskScheduler(models.Model):
    
    periodic_task = models.ForeignKey(PeriodicTask)

    @staticmethod
    def schedule_every(task_name, period, every, args=None, kwargs=None):
        """ TaskScheduler('mycustomtask', 'seconds', 30, [1,2,3]) """
        permissible_periods = ['days', 'hours', 'minutes', 'seconds']
        if period not in permissible_periods:
            raise Exception('Invalid period specified')
        # create the periodic task and the interval
        ptask_name = "%s_%s" % (task_name, datetime.now()) # create some name for the period task
        interval_schedules = IntervalSchedule.objects.filter(period=period, every=every)
        if interval_schedules: # just check if interval schedules exist like that already and reuse em
            interval_schedule = interval_schedules[0]
        else: # create a brand new interval schedule
            interval_schedule = IntervalSchedule()
            interval_schedule.every = every # should check to make sure this is a positive int
            interval_schedule.period = period 
            interval_schedule.save()
        ptask = PeriodicTask(name=ptask_name, task=task_name, interval=interval_schedule)
        if args:
            ptask.args = args
        if kwargs:
            ptask.kwargs = kwargs
        ptask.save()
        return TaskScheduler.objects.create(periodic_task=ptask)

    @staticmethod
    def schedule_cron(task_name, minute='*', hour='*', day_of_week='*', day_of_month='*', month_of_year='*' ,args=None, kwargs=None):
        # create the periodic task and the interval
        ptask_name = "%s_%s" % (task_name, datetime.now()) # create some name for the period task
        crontab_schedules = CrontabSchedule.objects.filter(minute=minute, hour=hour, day_of_week=day_of_week, day_of_month=day_of_month, month_of_year=month_of_year)
        if crontab_schedules: # just check if interval schedules exist like that already and reuse em
            crontab_schedule = crontab_schedules[0]
        else: # create a brand new interval schedule
            crontab_schedule = CrontabSchedule()
            crontab_schedule.minute = minute 
            crontab_schedule.hour = hour 
            crontab_schedule.day_of_week = day_of_week 
            crontab_schedule.day_of_month = day_of_month 
            crontab_schedule.month_of_year = month_of_year 
            crontab_schedule.save()
        
        ptask = PeriodicTask(name=ptask_name, task=task_name, crontab=crontab_schedule)
        if args:
            ptask.args = args
        if kwargs:
            ptask.kwargs = kwargs
        ptask.save()
        return TaskScheduler.objects.create(periodic_task=ptask)

    def stop(self):
        """ pauses the task"""
        ptask = self.periodic_task
        ptask.enabled = False
        ptask.save()

    def start(self):
        ptask = self.periodic_task
        ptask.enabled = True
        ptask.save()

    def terminate(self):
        self.stop()
        ptask = self.periodic_task
        self.delete()
        ptask.delete()
