from django.contrib import admin

# Register your models here.
from .models import Company, Sprint, Team, Pbi

admin.site.register(Company)
# admin.site.register(Sprint)
admin.site.register(Team)
# admin.site.register(Pbi)

@admin.register(Pbi)
class PbiAdmin(admin.ModelAdmin):
#     list_display = ('title' )
    list_filter = (
        ('sprint'),
    )
    
    
@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
#     list_display = ('title' )
    list_filter = (
        ('team'),
    )