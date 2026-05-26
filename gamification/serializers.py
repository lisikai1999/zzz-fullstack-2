from rest_framework import serializers
from .models import UserXP, ReadingLog, Achievement


class UserXPSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.SerializerMethodField()
    xp_to_next_level = serializers.IntegerField(read_only=True)
    xp_for_current_level = serializers.SerializerMethodField()
    xp_for_next_level = serializers.SerializerMethodField()

    class Meta:
        model = UserXP
        fields = ['id', 'username', 'avatar', 'total_xp', 'level',
                  'current_streak', 'longest_streak', 'last_read_date',
                  'xp_to_next_level', 'xp_for_current_level', 'xp_for_next_level']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            if request:
                return request.build_absolute_uri(obj.user.profile.avatar.url)
            return obj.user.profile.avatar.url
        return None

    def get_xp_for_current_level(self, obj):
        return UserXP.xp_for_level(obj.level)

    def get_xp_for_next_level(self, obj):
        return UserXP.xp_for_level(obj.level + 1)


class AchievementSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='get_achievement_type_display', read_only=True)

    class Meta:
        model = Achievement
        fields = ['id', 'achievement_type', 'display_name', 'earned_at']


class ReadingLogSerializer(serializers.ModelSerializer):
    article_title = serializers.CharField(source='article.title', read_only=True)
    article_slug = serializers.CharField(source='article.slug', read_only=True)

    class Meta:
        model = ReadingLog
        fields = ['id', 'article', 'article_title', 'article_slug', 'xp_earned', 'read_at']


class LeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = UserXP
        fields = ['id', 'username', 'avatar', 'total_xp', 'level', 'current_streak']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            if request:
                return request.build_absolute_uri(obj.user.profile.avatar.url)
            return obj.user.profile.avatar.url
        return None
