from django.contrib import admin
from .models import  Match



@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('team_a', 'team_b', 'date', 'time', 'status', 'winner', 'win_name')
    list_filter = ('status', 'date')
    search_fields = ('team_a', 'team_b')

