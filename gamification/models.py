import math
from django.db import models
from django.contrib.auth.models import User


class UserXP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='xp_profile')
    total_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_read_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_xp']

    def __str__(self):
        return f'{self.user.username} - Lv.{self.level} ({self.total_xp} XP)'

    @staticmethod
    def calculate_level(xp):
        return int(math.floor(math.sqrt(xp / 100))) + 1

    @staticmethod
    def xp_for_level(level):
        return ((level - 1) ** 2) * 100

    @property
    def xp_to_next_level(self):
        next_level_xp = self.xp_for_level(self.level + 1)
        return next_level_xp - self.total_xp


class ReadingLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_logs')
    article = models.ForeignKey('blog.Article', on_delete=models.CASCADE, related_name='reading_logs')
    xp_earned = models.PositiveIntegerField(default=10)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-read_at']
        unique_together = ['user', 'article']

    def __str__(self):
        return f'{self.user.username} read {self.article.title}'


class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('streak_7', '连续阅读7天'),
        ('streak_30', '连续阅读30天'),
        ('streak_100', '连续阅读100天'),
        ('articles_10', '阅读10篇文章'),
        ('articles_50', '阅读50篇文章'),
        ('articles_100', '阅读100篇文章'),
        ('level_5', '达到5级'),
        ('level_10', '达到10级'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'achievement_type']
        ordering = ['-earned_at']

    def __str__(self):
        return f'{self.user.username} - {self.get_achievement_type_display()}'
