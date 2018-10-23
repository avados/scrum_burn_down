from django.test import TestCase
from  burnDownBackEnd.models import Company, Team, Sprint, Pbi
from  burnDownBackEnd.forms import SprintForm, PbiForm
from datetime import datetime, timedelta, date
from django.utils import timezone
import logging
from django.test import Client
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from  burnDownBackEnd.serializers import CompanySerializer, PbiSerializer
from django.db.models import Q
from django.urls import reverse
import json
from rest_framework import status
from django.core import mail


class SprintTestCase(TestCase):
    def setUp(self):
        comp = Company.objects.create(name="company1")
        team = Team.objects.create(name="team1", pouet = 444, company = comp)
         
    def test_start_date_before_end_date(self):
        team = Team.objects.get(name="team1")

#       #sprint = Sprint.objects.create(team = team, start_date = date.today() , end_date = date.today() - timedelta(days=1))
        form = SprintForm(data={'goal' : 'goal1', 'team' : team.id, 'start_date' : timezone.now() , 'end_date' : timezone.now() - timedelta(days=1)})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'],
            ['start date cannot be after end date']
        )
        
        form = SprintForm(data={'goal' : 'goal1', 'team' : team.id, 'start_date' : timezone.now() , 'end_date' : timezone.now() + timedelta(days=1)})
        self.assertTrue(form.is_valid())
     
    def test_sprint_start_before_another_end(self):
        team = Team.objects.get(name="team1")
        form = SprintForm(data={'goal' : 'goal1', 'team' : team.id, 'start_date' : timezone.now() , 'end_date' : timezone.now() + timedelta(days=7)})
        self.assertTrue(form.is_valid())
        form.save()
        
        form = SprintForm(data={'goal' : 'goal1', 'team' : team.id, 'start_date' : timezone.now() + timedelta(days=5), 'end_date' : timezone.now() + timedelta(days=8)})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'],
            ['This sprint starts before another one finishes']
        )

    def test_create_sprint_between_sprints(self):
        team = Team.objects.get(name="team1")
        form = SprintForm(data={'goal' : 'goal1', 'team' : team.id, 'start_date' : timezone.now() - timedelta(days=30), 'end_date' : timezone.now() - timedelta(days=20)})
        self.assertTrue(form.is_valid())
        form.save()
        
        form = SprintForm(data={'goal' : 'goal3', 'team' : team.id, 'start_date' : timezone.now() - timedelta(days=10), 'end_date' : timezone.now() - timedelta(days=1)})
        self.assertTrue(form.is_valid())
        form.save()
        
        form = SprintForm(data={'goal' : 'goal2', 'team' : team.id, 'start_date' : timezone.now() - timedelta(days=19), 'end_date' : timezone.now() - timedelta(days=11)})
        self.assertTrue(form.is_valid())
        form.save()
        
