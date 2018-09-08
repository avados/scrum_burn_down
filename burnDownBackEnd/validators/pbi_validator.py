from datetime import datetime, timedelta, date
from django.utils import timezone
from django.core.validators import ValidationError
# from ..models import Sprint, Pbi
# from ..forms import SprintForm, PbiForm
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def validate_snapshot_date(_date):
    if _date == None:
        return datetime.now()
    elif _date >= (timezone.now() + timedelta(days=1)).date():
        raise ValidationError('Pbi cannot be in the future')
    
    return _date
    
def validate_pbi_sprint(sprint, snapshot_date):
    """ Validate sprint in a pbi, try to create it if possible """
    if sprint is None:
        raise ValidationError('Sprint cannot be null')
    from ..models import Sprint
    sprt = Sprint.objects.get(id=sprint.id)
    if sprt is not None:
#             si la date du pbi est en dehors du sprint
        nbr_day = (sprt.end_date - sprt.start_date).days
        if sprt.start_date >= snapshot_date or sprt.end_date <= snapshot_date:
            #if pbi is outside this sprint, check if it exists a sprint with those dates/teams
            sprint = Sprint.objects.filter(start_date__lte=snapshot_date, end_date__gte=snapshot_date, team__id=sprt.team.id)
            if sprint != None and sprint.count() == 1:
                logger.debug(f"Updating PBI : from sprint {sprint} to {sprint[0]}")
                return sprint[0]
            elif sprint.count() > 1:
                raise ValidationError('More than one active sprints at the same time for the same team')
            else:
                #create new sprint
                #import here otherwise we will have an issue 
                from ..forms import SprintForm
                sprint_form = SprintForm(data={'goal' : 'GOAL UNDEFINED', 'team' : sprt.team.id, 'start_date' : snapshot_date , 'end_date' : snapshot_date + timedelta(days=nbr_day)})
                if sprint_form.is_valid():
                    new_sprint = sprint_form.save()
                      
                    #f"A new sprint has been created for team {sprt.team}, sprint id: {self.sprint.id}, start date: {self.sprint.start_date}, end date: {self.sprint.end_date}",
                    logger.debug(f"Updating PBI : new sprint created id: {new_sprint.id} {new_sprint}")
                    send_mail(
                        'New sprint automatically created',
                        
                        "A new sprint has been created for team "+ str(sprt.team)+", sprint id: "+str(new_sprint.id)+", start date: "+str(new_sprint.start_date)+", end date: "+str(new_sprint.end_date),
                        settings.EMAIL_HOST_USER,
                        settings.EMAIL_AVADOS_TO_EMAIL,
                        fail_silently=False,
                    )
                    return new_sprint 
                else:
                    raise ValidationError('Invalid sprint'+str(new_sprint.id))
                
                
    else:
        raise ValidationError('Invalid sprint'+str(sprint.id))

    