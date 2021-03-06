#needed by visual studio
#import django.test.utils
#django.setup()
#django.test.utils.setup_test_environment()
#django.test.utils.setup_databases()

from django.conf import settings
from django.test.utils import get_runner
# import unittest
# from unittest import TestCase 

# if __name__ == "__main__":
#     os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
#     django.setup()
#     TestRunner = get_runner(settings)
#     test_runner = TestRunner()
#     failures = test_runner.run_tests(["tests"])
#     sys.exit(bool(failures))


# the 4 following lines are mandatory to execute tests 
import django
import os
#add this if you want to run all tests in one shot
# if __name__ == "__main__":
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests_settings')
# django.setup()
# TestRunner = get_runner(settings)
# test_runner = TestRunner()
# failures = test_runner.run_tests(["tests"])
# sys.exit(bool(failures))

########################
from django.test import TestCase

#from unittest import TestCase 
from burnDownBackEnd.models import Company, Team, Sprint, Pbi
from burnDownBackEnd.forms import SprintForm, PbiForm
from datetime import datetime, timedelta, date
from django.utils import timezone
import logging
from django.test import Client
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from burnDownBackEnd.serializers import CompanySerializer, PbiSerializer
from django.db.models import Q
from django.urls import reverse
import json
from rest_framework import status
from django.core import mail




# Create your tests here.
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class Test_CompanyTestCase(TestCase):
    def setUp(self):
        #Team.objects.create(name="team1", pouet = 444)
        Company.objects.create(name="company1")
    
    def test_company_created(self):
        comp = Company.objects.get(name="company1")
        self.assertTrue(comp.name, "company1")

class TeamTestCase(TestCase):
    def setUp(self):
        comp = Company.objects.create(name="company1")
        Team.objects.create(name="team1", pouet = 444, company = comp)

    def test_team_have_name(self):
        team1 = Team.objects.get(name="team1")
        self.assertEqual(team1.was_created_recently(), True)
        self.assertEqual(team1.name, "team1")
        
        

# initialize the APIClient app
client = Client()
#from django.test.utils import override_settings

#to send email
#@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')        
class PbiTestCase(APITestCase):
    def setUp(self):
        comp = Company.objects.create(name="companyPbiTest")
        team = Team.objects.create(name="teamPbi", pouet = 444, company = comp)
        sprint = Sprint.objects.create(goal = 'goalPbi', team = team, start_date = timezone.now() , end_date = timezone.now() + timedelta(days=7) )
        pbi1 = Pbi.objects.create(sprint = sprint, pbi_type = "US", state = "NEW", story_points = 5, local_id = "one", title ="title 1", link = "http://link1.com", area= "area1")
        pbi2 = Pbi.objects.create(sprint = sprint, pbi_type = "US", state = "NEW", story_points = 5, local_id = "two", title ="title 2", link = "http://link2.com", area= "area1")
#         sprintForm = SprintForm(data={'goal' : 'goalPbi', 'team' : team.id, 'start_date' : timezone.now() , 'end_date' : timezone.now() + timedelta(days=7)})
#         self.assertTrue(sprintForm.is_valid())
#         sprintForm.save()

    def test_pbi_form(self):
        sprint = Sprint.objects.get(goal='goalPbi')
        form = PbiForm(data={'sprint':sprint.id, 'snapshot_date': timezone.now(), 'pbi_type':'US', 'state':'NEW','story_points':0, 'local_id':'zero','title':'pbiForm','link':'http://pbiform.com','area':'forms','is_interruption':False})
        self.assertTrue(form.is_valid())
            
    def test_pbi_no_sprint(self):
        sprint = Sprint.objects.get(goal='goalPbi')
        form = PbiForm(data={ 'snapshot_date': timezone.now(), 'pbi_type':'US', 'state':'NEW','story_points':0, 'local_id':'zero','title':'pbiForm','link':'http://pbiform.com','area':'forms','is_interruption':False})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'],
            ['Sprint cannot be null']
        )
    
    def test_pbi_cannot_create_tomorrow(self):
        sprint = Sprint.objects.get(goal='goalPbi')
        form = PbiForm(data={ 'snapshot_date': timezone.now() + timedelta(days=1), 'pbi_type':'US', 'state':'NEW','story_points':0, 'local_id':'zero','title':'pbiForm','link':'http://pbiform.com','area':'forms','is_interruption':False})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'],
            ['Pbi cannot be in the future']
        )
        
    def test_pbi_change_sprint_auto(self):
        team = Team.objects.get(name="teamPbi")
        oldSprint = Sprint.objects.create(goal = 'goalPbiold', team = team, start_date = timezone.now() - timedelta(days=20), end_date = timezone.now() - timedelta(days=10) )
        currentSprint = Sprint.objects.get(goal='goalPbi')
        
        pbi = PbiForm(data={'sprint':oldSprint.id, 'snapshot_date': timezone.now().strftime("%Y-%m-%d" ) , 'pbi_type':'US', 'state':'NEW','story_points':0, 'local_id':'zero','title':'pbiForm','link':'http://pbiform.com','area':'forms','is_interruption':False})
        self.assertTrue(pbi.is_valid())
        pouet = pbi.save()
        self.assertEqual(pouet.sprint.id, currentSprint.id)
        
        #FUCKING SERIALIZER DO NOT USE FORM VALIDATION
    def test_serilalizer_call_clean(self):
        currentSprint = Sprint.objects.get(goal='goalPbi')
        pbi = Pbi()
        #area = 'area', link = 'http://plouf.com', local_id = 'lid', title = 'title', sprint = currentSprint, pbi_type = 'US', state = 'NEW', is_interruption = False, snapshot_date = date.today().strftime("%d %m %Y" ))
        pbi.area = 'area'
        pbi.link = 'http://plouf.com'
        pbi.local_id = 'lid'
        pbi.title = 'title'
        pbi.sprint = currentSprint
        pbi.pbi_type = 'US'
        pbi.state = 'NEW'
        pbi.is_interruption = False
        pbi.snapshot_date = date.today().strftime("%Y-%m-%d" )
        pbi.story_points = 33
        
        testreverse = reverse('burnDown:pbi_list')
        serializer = PbiSerializer(instance=[pbi], many=True)
#         serializer.is_valid()
        response = client.post(testreverse, json.dumps(serializer.data), content_type="application/json" )
        #response = client.post(testreverse, json.dumps([pouet]), content_type="application/json" )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
          
    
    
    def test_pbi_create_sprint_auto(self):    
        comp = Company.objects.create(name="companyPbiTestAutoCreate")
        team = Team.objects.create(name="teamPbiAutoCreate", pouet = 555, company = comp)
        oldSprint = Sprint.objects.create(goal = 'goalPbiold2', team = team, start_date = timezone.now() - timedelta(days=11), end_date = timezone.now() - timedelta(days=1) )
        
        pbi = PbiForm(data={'sprint':oldSprint.id, 'snapshot_date': timezone.now() , 'pbi_type':'US', 'state':'NEW','story_points':0, 'local_id':'zero','title':'pbiForm','link':'http://pbiform.com','area':'forms','is_interruption':False})
        self.assertTrue(pbi.is_valid())
        pouet = pbi.save()
        self.assertNotEqual(pouet.sprint.id, oldSprint.id)
        self.assertEqual(pouet.snapshot_date, pouet.sprint.start_date)
        self.assertEqual(pouet.snapshot_date + timedelta(days=10), pouet.sprint.end_date)
        self.assertEqual(pouet.sprint.goal, 'GOAL UNDEFINED')
        
        self.assertEqual(len(mail.outbox), 1)
     
    def test_pbi_create_sprint_auto_rest(self):
        comp = Company.objects.create(name="companyPbiTest555")
        team = Team.objects.create(name="teamPbiTest", pouet = 555, company = comp)
        sprint = Sprint.objects.create(goal = 'goalPbi', team = team, start_date = timezone.now() - timedelta(days=10), end_date = timezone.now() - timedelta(days=1) )
        
        pbi = Pbi()
        #area = 'area', link = 'http://plouf.com', local_id = 'lid', title = 'title', sprint = currentSprint, pbi_type = 'US', state = 'NEW', is_interruption = False, snapshot_date = date.today().strftime("%d %m %Y" ))
        pbi.area = 'area'
        pbi.link = 'http://plouf.com'
        pbi.local_id = 'lid'
        pbi.title = 'title'
        pbi.sprint = sprint
        pbi.pbi_type = 'US'
        pbi.state = 'NEW'
        pbi.is_interruption = False
        pbi.snapshot_date = date.today().strftime("%Y-%m-%d" )
        pbi.story_points = 33
        
        testreverse = reverse('burnDown:pbi_list')
        serializer = PbiSerializer(instance=[pbi], many=True)
#         serializer.is_valid()
        response = client.post(testreverse, json.dumps(serializer.data), content_type="application/json" )
        #response = client.post(testreverse, json.dumps([pouet]), content_type="application/json" )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
           
    def test_rest_get_serialized_pbis(self):
#         pbisTested = Pbi.get_all_pbis()
#         serializerTested = PbiSerializer(pbisTested, many=True)
        response = client.get(reverse('burnDown:pbi_list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        pbis = Pbi.objects.filter(Q(local_id ='one') | Q(local_id='two')).order_by('snapshot_date')
#         serializer = PbiSerializer(pbis, many=True)
        self.assertEqual(pbis[0].local_id, response.json()[0]['local_id'])
        self.assertEqual(pbis[1].local_id, response.json()[1]['local_id'])
        self.assertEqual(len(response.json()), len(pbis))
        
# does not work and i dont know why
#         self.assertEqual(  serializer.data, response.json())
#         self.assertEqual(  list(pbis.values()), response.json())
#         self.assertQuerysetEqual(serializer.data, response.json(), ordered = False)

    def test_post_update_serialize_pbi(self):
        pbis = Pbi.objects.filter(Q(local_id ='one') | Q(local_id='two')).order_by('local_id')
        #used to evaluate whole queryset, otherwise we cannot update; see https://stackoverflow.com/questions/22980448/django-objects-filter-is-not-updating-field-but-objects-get-is
        bool(pbis)
        pbis[0].state = "ACTIVE"
        pbis[1].story_points = 5
         
        serializer = PbiSerializer(pbis, many=True)
 
        response = client.post(reverse('burnDown:pbi_list'), data=json.dumps(serializer.data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
         
        pbis = Pbi.objects.filter(Q(local_id ='one') | Q(local_id='two')).order_by('snapshot_date')
        self.assertEqual(pbis[0].state , "ACTIVE")
        self.assertEqual(pbis[1].story_points , 5)
        
    def test_get_list_date_pbis(self):
        sprint = Sprint.objects.get(goal='goalPbi')
#         testreverse = reverse('burnDown:pbisByDate', args=[1])
        testreverse = reverse('burnDown:pbisByDate', kwargs={'sprint_id':sprint.id})+'?_date='+date.today().strftime("%d %m %Y" )
        response = client.get(testreverse)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        pbis = Pbi.objects.filter(Q(local_id ='one') | Q(local_id='two')).order_by('snapshot_date')
        serializer = PbiSerializer(pbis, many=True)
        self.assertEqual(response.json(), serializer.data)
        
# TEST COMMANDS

from io import StringIO
from django.core.management import call_command
from django.test import TestCase

class CommandTest(TestCase):
    def setUp(self):
        comp = Company.objects.create(name="companyPbiTest")
        team1 = Team.objects.create(name="team1", pouet = 444, company = comp)
        team2 = Team.objects.create(name="team2", pouet = 444, company = comp)
        sprint = Sprint.objects.create(goal = 'goalPbi', team = team1, start_date = timezone.now() , end_date = timezone.now() + timedelta(days=7) )
        sprint2 = Sprint.objects.create(goal = 'goalPbi', team = team1, start_date = timezone.now() , end_date = timezone.now() + timedelta(days=7) )
        
        pbi1 = Pbi.objects.create(sprint = sprint, pbi_type = "US", state = "NEW", story_points = 5, local_id = "one", title ="title 1", link = "http://link1.com", area= "area1")
        pbi2 = Pbi.objects.create(sprint = sprint, pbi_type = "US", state = "NEW", story_points = 5, local_id = "two", title ="title 2", link = "http://link2.com", area= "area1")

        pbit2 = PbiForm(data={'sprint':sprint2.id, 'snapshot_date': timezone.now() - + timedelta(days=1) , 'pbi_type':'US', 'state':'NEW','story_points':0, 'local_id':'zero','title':'pbiForm','link':'http://pbiform.com','area':'forms','is_interruption':False})
    
    def test_command_output(self):
        out = StringIO()
        call_command('InactivityEmail', stdout=out)
        if datetime.today().weekday() < 5 :
            self.assertIn('Successfully checked activity', out.getvalue())
            self.assertEqual(len(mail.outbox), 1)
        
        