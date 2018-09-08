from rest_framework import serializers
from django.forms.models import model_to_dict
from .models import Company, Pbi, Sprint
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.core.mail import send_mail
import logging
from django.conf import settings
import burnDownBackEnd.validators.pbi_validator as pbi_val

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
        fields = ('id','pbi_type', 'state', 'story_points', 'local_id', 'title','link', 'snapshot_date', 'sprint','is_interruption', 'area')
    
    #validate otherwize it is not clean 
    #TODO use mixin to have same validation a smodel : https://stackoverflow.com/questions/32921956/where-should-i-do-the-django-validations-for-objects-and-fields
    def validate(self, data):
#         instance = Pbi(**data)
#         instance.clean()
        #TODO change this to use the same validation as in the model
        data['snapshot_date'] = pbi_val.validate_snapshot_date(data['snapshot_date'])

        data['sprint'] = pbi_val.validate_pbi_sprint(data['sprint'], data['snapshot_date'])
                 
        return data
        
#     def create(self, validated_data):
#         """
#         Create and return a new `company` instance, given the validated data.
#         """
#         return Pbi.objects.create(**validated_data)

