from django.db import models
from datetime import datetime
from django.forms import ModelForm
from django.utils import timezone
# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=200)
    create_date = models.DateTimeField('date created', default=datetime.now)
    def __str__(self):
        return self.name



class Team(models.Model):
    name = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    pouet = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    def was_created_recently(self):
        return self.create_date >= timezone.now() - datetime.timedelta(days=1)


class Sprint(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    start_date = models.DateField('start date', default=None)
    end_date  = models.DateField('end date', default=None)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    goal = models.CharField(max_length=500)
    def __str__(self):
        return self.team.name +'  /  '+ str(self.start_date) +'  to  '+ str(self.end_date)

PBI_STATES = (
    ('NEW', 'New'),
    ('ACTIVE', 'Active'),
    ('OPEN', 'Open'),
    ('RESOLVED', 'Resolved'),
    ('CLOSED', 'Closed'),
)

PBI_TYPES = (
    ('BUG', 'Bug'),
    ('US', 'User Story'),
)

class Pbi(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.PROTECT, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    snapshot_date = models.DateField('snapshot date', default=datetime.now)
    pbitype =  models.CharField(max_length=20, choices=PBI_TYPES)
    state =  models.CharField(max_length=20, choices=PBI_STATES)
    storyPoints = models.PositiveIntegerField(default=0)
    localId = models.CharField(max_length=2048)
    title = models.CharField(max_length=200,default='')
    link = models.URLField(max_length=500)
    def __str__(self):
        return self.localId + ' - ' + self.title+ ' / ' + str(self.snapshot_date)