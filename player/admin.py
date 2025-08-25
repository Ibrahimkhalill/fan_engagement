from django.contrib import admin
from .models import Player
# Register your models here.
admin.site.site_header = "Fan Engagement"

admin.site.register(Player)