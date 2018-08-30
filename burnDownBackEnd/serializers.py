from rest_framework import serializers
from django.forms.models import model_to_dict
from .models import Company, Pbi, Sprint
from django.utils import timezone
from datetime import datetime, timedelta, date
import logging

logger = logging.getLogger(__name__)

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name')

    def create(self, validated_data):
        """
        Create and return a new `company` instance, given the validated data.
        """
        return Company.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class PbiSerializer(serializers.ModelSerializer):
#     isAddedInSprint = serializers.ReadOnlyField()
    class Meta:
        model = Pbi
        fields = ('pbi_type', 'state', 'story_points', 'local_id', 'title','link', 'snapshot_date', 'sprint','is_interruption', 'area')
    
    #validate otherwize it is not clean 
    def validate(self, data):
#         instance = Pbi(**data)
#         instance.clean()
        #TODO change this to use the same validation as in the model
        if data['snapshot_date'] == None:
            data['snapshot_date'] = datetime.now()
        elif data['snapshot_date'] >= (timezone.now() + timedelta(days=1)).date():
            raise ValidationError('Pbi cannot be in the future')
             
        if data['sprint'] == None:
            raise ValidationError('Sprint cannot be null')
        logger.info(f"new PBI with sprint : {data['sprint']} ")
        sprt = Sprint.objects.get(id=data['sprint'].id)
        if sprt != None:
#             si la date du pbi est en dehors du sprint
            nbrDay = (sprt.end_date - sprt.start_date).days
            if sprt.start_date >= data['snapshot_date'] or sprt.end_date <= data['snapshot_date']:
                #if pbi is outside this sprint, check if it exists a sprint with those dates/teams
                sprint = Sprint.objects.filter(start_date__lte=data['snapshot_date'], end_date__gte=data['snapshot_date'], team__id=sprt.team.id)
                if sprint != None and sprint.count() == 1:
                    logger.info(f"Updating PBI : from sprint {data['sprint']} to {sprint[0]}")
                    data['sprint'] = sprint[0]
                elif sprint.count() > 1:
                    raise ValidationError('More than one active sprints at the same time for the same team')
                else:
                    #create new sprint
                    #import here otherwise we will have an issue 
                    from .forms import SprintForm
                    sprintForm = SprintForm(data={'goal' : 'GOAL UNDEFINED', 'team' : sprt.team.id, 'start_date' : data['snapshot_date'] , 'end_date' : data['snapshot_date'] + timedelta(days=nbrDay)})
                    if sprintForm.is_valid():
                        newSprint = sprintForm.save()
                        data['sprint'] = newSprint  
                        #f"A new sprint has been created for team {sprt.team}, sprint id: {data.sprint.id}, start date: {data.sprint.start_date}, end date: {data.sprint.end_date}",
                        logger.info(f"Updating PBI : new sprint created id: {newSprint.id} {newSprint}")
                        send_mail(
                            'New sprint automatically created',
                            
                            "A new sprint has been created for team "+ str(sprt.team)+", sprint id: "+str(data['sprint'].id)+", start date: "+str(data['sprint.start_date'])+", end date: "+str(data['sprint.end_date']),
                            settings.EMAIL_HOST_USER,
                            settings.EMAIL_AVADOS_TO_EMAIL,
                            fail_silently=False,
                        )
                    else:
                        raise ValidationError('Invalid sprint'+str(data.sprint.id))
                                
        return data
        
#     def create(self, validated_data):
#         """
#         Create and return a new `company` instance, given the validated data.
#         """
#         return Pbi.objects.create(**validated_data)

