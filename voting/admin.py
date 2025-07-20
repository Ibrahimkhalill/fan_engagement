from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Voting, Fan

@admin.register(Voting)
class VotingAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'who_will_win', 'goal_difference', 'points_earned')
    list_filter = ('match',)
    search_fields = ('user__username',)

@admin.register(Fan)
class FanAdmin(admin.ModelAdmin):
    list_display = ('user', 'points')
    search_fields = ('user__username',)

