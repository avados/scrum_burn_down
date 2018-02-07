from django.contrib import admin

# Register your models here.
from .models import Company, Sprint, Team, Pbi

admin.site.register(Company)
admin.site.register(Sprint)
admin.site.register(Team)
admin.site.register(Pbi)