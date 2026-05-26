from django.contrib import admin
from .models import UserXP, ReadingLog, Achievement


@admin.register(UserXP)
class UserXPAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_xp', 'level', 'current_streak', 'longest_streak', 'last_read_date']
    search_fields = ['user__username']


@admin.register(ReadingLog)
class ReadingLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'xp_earned', 'read_at']
    list_filter = ['read_at']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement_type', 'earned_at']
    list_filter = ['achievement_type']
