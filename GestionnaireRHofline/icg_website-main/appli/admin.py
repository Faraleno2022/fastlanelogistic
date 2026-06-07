from django.contrib import admin
from appli.models import Events

# Register your models here.

class EventsAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'event_date', 'event_address', 'event_description', 'event_picture')
    
    
admin.site.register(Events, EventsAdmin)