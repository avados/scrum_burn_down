from django.db import models
from datetime import datetime, timedelta
from django.forms import ModelForm
from django.utils import timezone
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
import logging
from django.conf import settings

# Create your models here.

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class Company(models.Model):
    name = models.CharField(max_length=200)
    create_date = models.DateTimeField('date created', default=datetime.now())
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
        return self.created_date >= timezone.now() - timedelta(days=1)



class Sprint(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    start_date = models.DateField('start date', default=None)
    end_date  = models.DateField('end date', default=None)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    goal = models.CharField(max_length=500)
    def __str__(self):
        return self.team.name +'  /  '+ self.goal +'  /  '+ str(self.start_date) +'  to  '+ str(self.end_date)
    def clean(self):#called by django on form saving, not model saving
        super(Sprint, self).clean()
        # Don't allow start date after end date.
        if self.start_date > self.end_date:
            raise ValidationError('start date cannot be after end date')
        #logger.debug(' start date '+self.start_date.strftime("%d %m %Y" ) + ' end date '+self.end_date.strftime("%d %m %Y" )+ 'team'+ self.team.name)
        
        if Sprint.objects.filter(end_date__gt=self.start_date, team=self.team).exclude(id=self.id).count() > 0 :
            raise ValidationError('This sprint starts before another one finishes')
     #                 if ( _local_id != None and _local_id != '' ) and ( _snapshot_date != None and _snapshot_date != ''):
#                     Pbi.objects.filter(local_id=_local_id, snapshot_date=_snapshot_date).delete()            


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
    pbi_type =  models.CharField(max_length=20, choices=PBI_TYPES)
    state =  models.CharField(max_length=20, choices=PBI_STATES)
    story_points = models.FloatField(default=0)
    local_id = models.CharField(max_length=2048)
    title = models.CharField(max_length=200,default='')
    link = models.URLField(max_length=500)
    area = models.CharField(max_length=2048,default='')
    is_interruption = models.BooleanField(default=False)
    
    def clean(self):#called by django on form saving, not model saving
        super(Pbi, self).clean()
        # automatically create a sprint if it does not already exists.
        
        if self.snapshot_date == None:
            self.snapshot_date = datetime.now()
        elif self.snapshot_date >= (timezone.now() + timedelta(days=1)).date():
            raise ValidationError('Pbi cannot be in the future')
             
        if self.sprint == None:
            raise ValidationError('Sprint cannot be null')
        
        sprt = Sprint.objects.get(id=self.sprint.id)
        if sprt != None:
#             si la date du pbi est en dehors du sprint
            nbrDay = (sprt.end_date - sprt.start_date).days
            if sprt.start_date >= self.snapshot_date or sprt.end_date <= self.snapshot_date:
                #if pbi is outside this sprint, check if it exists a sprint with those dates/teams
                sprint = Sprint.objects.filter(start_date__lte=self.snapshot_date, end_date__gte=self.snapshot_date, team__id=sprt.team.id)
                if sprint != None and sprint.count() == 1:
                    self.sprint = sprint[0]
                else:
                    #create new sprint
                    #import here otherwise we will have an issue 
                    from .forms import SprintForm
                    sprintForm = SprintForm(data={'goal' : 'GOAL UNDEFINED', 'team' : sprt.team.id, 'start_date' : self.snapshot_date , 'end_date' : self.snapshot_date + timedelta(days=nbrDay)})
                    if sprintForm.is_valid():
                        newSprint = sprintForm.save()
                        self.sprint = newSprint  
                        send_mail(
                            'New sprint automatically created',
                            f"A new sprint has been created for team {sprt.team}, sprint id: {self.sprint.id}, start date: {self.sprint.start_date}, end date: {self.sprint.end_date}",
                            settings.EMAIL_HOST_USER,
                            settings.EMAIL_AVADOS_TO_EMAIL,
                            fail_silently=False,
                        )
                    else:
                        raise ValidationError('Invalid sprint'+str(self.sprint.id))
                    
                    
        else:
            raise ValidationError('Invalid sprint'+str(self.sprint.id))
                    
            #def __init__(self):
#         self.isAddedInSprint = False
#         self.title= 'pouet'
#     @property
#     def isAddedInSprint(self):
#         return self._isAddedInSprint
#     @isAddedInSprint.setter
#     def isAddedInSprint(self, value):
#         self._isAddedInSprint = value
#     
    def __str__(self):
        return self.local_id + ' - ' + self.title+ ' / ' + str(self.snapshot_date)
    
#     @staticmethod
#     def updateSerializedPbis(data):
#         for vData in data:
#             #logger.error(vData)
#             _local_id = vData.get("local_id",None)
#             _snapshot_date = vData.get("snapshot_date",None)
#             #useless, is_valid should have checked that
#             if ( _local_id != None and _local_id != '' ) and ( _snapshot_date != None and _snapshot_date != ''):
#                 Pbi.objects.filter(local_id=_local_id, snapshot_date=_snapshot_date).delete()            
#         
#         serialized.save()
#         return
    
    @staticmethod
    def get_all_pbis():
        pbis = Pbi.objects.all().order_by('snapshot_date')
        return pbis
        
            
            
            
            
            
            
            
            
            
            
            
            