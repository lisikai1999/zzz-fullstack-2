from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.db.models import F
from django.utils import timezone
from .models import UserXP, ReadingLog, Achievement
from .serializers import (
    UserXPSerializer, AchievementSerializer,
    ReadingLogSerializer, LeaderboardSerializer
)


STREAK_ACHIEVEMENTS = {7: 'streak_7', 30: 'streak_30', 100: 'streak_100'}
ARTICLE_ACHIEVEMENTS = {10: 'articles_10', 50: 'articles_50', 100: 'articles_100'}
LEVEL_ACHIEVEMENTS = {5: 'level_5', 10: 'level_10'}


class ReadingXPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, article_id):
        from blog.models import Article
        try:
            article = Article.objects.get(id=article_id, status='published')
        except Article.DoesNotExist:
            return Response({'error': '文章不存在'}, status=status.HTTP_404_NOT_FOUND)

        if ReadingLog.objects.filter(user=request.user, article=article).exists():
            xp_profile = UserXP.objects.filter(user=request.user).first()
            return Response({
                'already_read': True,
                'xp_profile': UserXPSerializer(xp_profile, context={'request': request}).data if xp_profile else None,
                'new_achievements': []
            })

        xp_earned = 10
        ReadingLog.objects.create(user=request.user, article=article, xp_earned=xp_earned)

        xp_profile, created = UserXP.objects.get_or_create(user=request.user)

        xp_profile.total_xp = F('total_xp') + xp_earned
        xp_profile.save(update_fields=['total_xp', 'updated_at'])
        xp_profile.refresh_from_db()

        xp_profile.level = UserXP.calculate_level(xp_profile.total_xp)

        today = timezone.localdate()
        if xp_profile.last_read_date is None:
            xp_profile.current_streak = 1
        elif xp_profile.last_read_date == today:
            pass
        elif (today - xp_profile.last_read_date).days == 1:
            xp_profile.current_streak += 1
        else:
            xp_profile.current_streak = 1

        xp_profile.last_read_date = today
        if xp_profile.current_streak > xp_profile.longest_streak:
            xp_profile.longest_streak = xp_profile.current_streak

        xp_profile.save()

        new_achievements = self._check_achievements(request.user, xp_profile)

        return Response({
            'already_read': False,
            'xp_earned': xp_earned,
            'xp_profile': UserXPSerializer(xp_profile, context={'request': request}).data,
            'new_achievements': AchievementSerializer(new_achievements, many=True).data
        })

    def _check_achievements(self, user, xp_profile):
        new_achievements = []

        for threshold, achievement_type in STREAK_ACHIEVEMENTS.items():
            if xp_profile.current_streak >= threshold:
                obj, created = Achievement.objects.get_or_create(
                    user=user, achievement_type=achievement_type
                )
                if created:
                    new_achievements.append(obj)

        total_articles = ReadingLog.objects.filter(user=user).count()
        for threshold, achievement_type in ARTICLE_ACHIEVEMENTS.items():
            if total_articles >= threshold:
                obj, created = Achievement.objects.get_or_create(
                    user=user, achievement_type=achievement_type
                )
                if created:
                    new_achievements.append(obj)

        for threshold, achievement_type in LEVEL_ACHIEVEMENTS.items():
            if xp_profile.level >= threshold:
                obj, created = Achievement.objects.get_or_create(
                    user=user, achievement_type=achievement_type
                )
                if created:
                    new_achievements.append(obj)

        return new_achievements


class MyXPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        xp_profile, created = UserXP.objects.get_or_create(user=request.user)
        achievements = Achievement.objects.filter(user=request.user)
        return Response({
            'xp_profile': UserXPSerializer(xp_profile, context={'request': request}).data,
            'achievements': AchievementSerializer(achievements, many=True).data,
            'total_articles_read': ReadingLog.objects.filter(user=request.user).count(),
        })


class LeaderboardView(ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LeaderboardSerializer

    def get_queryset(self):
        return UserXP.objects.select_related('user__profile').order_by('-total_xp')[:50]


class MyAchievementsView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AchievementSerializer

    def get_queryset(self):
        return Achievement.objects.filter(user=self.request.user)


class ReadingHistoryView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReadingLogSerializer

    def get_queryset(self):
        return ReadingLog.objects.filter(user=self.request.user).select_related('article')
