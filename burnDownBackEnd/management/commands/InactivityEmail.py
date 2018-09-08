'''
Created on Jul 28, 2018

@author: C L
'''
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
import logging
from django.conf import settings
from burnDownBackEnd.models import Company, Team, Sprint, Pbi
from datetime import datetime, timedelta, date

logger = logging.getLogger(__name__)
# to be executed by a cron job:
# python3 manage.py InactivityEmail
# see https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
class Command(BaseCommand):
    help = 'Send email when no activity on weekday'

#     def add_arguments(self, parser):
#         parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        if datetime.today().weekday() >= 5 :
            return
        
        teamsWithoutActivity = Team.objects.exclude(sprint__pbi__snapshot_date=date.today()).distinct()
        teamName = []
        for teamTmp in teamsWithoutActivity:
            teamName.append(teamTmp.name)
        
        if len(teamName) > 0:
            strTeams = ", ".join(teamName)
            send_mail(
                        'No activity on '+ str(date.today()),
                        "No activity for the following team: " + strTeams,
                        settings.EMAIL_HOST_USER,
                        settings.EMAIL_AVADOS_TO_EMAIL,
                        fail_silently=False,
                    )
        self.stdout.write(self.style.SUCCESS('Successfully checked activity'))
        
        