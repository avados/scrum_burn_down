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
    save_as = True
    list_filter = (
        ('sprint'),
        ('snapshot_date'),
    )
    search_fields = (
       ('local_id'),
       ('title'),
    )
    
@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    save_as = True
#     list_display = ('title' )
    list_filter = (
        ('team'),
    )
    search_fields = (
       ('goal'),
    )