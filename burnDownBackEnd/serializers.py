from rest_framework import serializers
from .models import Company, Pbi

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
        fields = ('pbi_type', 'state', 'story_points', 'local_id', 'title','link', 'snapshot_date', 'sprint')

#     def create(self, validated_data):
#         """
#         Create and return a new `company` instance, given the validated data.
#         """
#         return Pbi.objects.create(**validated_data)

