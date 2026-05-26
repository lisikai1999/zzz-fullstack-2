from django.urls import path
from . import views

urlpatterns = [
    path('read/<int:article_id>/', views.ReadingXPView.as_view(), name='record-read'),
    path('me/', views.MyXPView.as_view(), name='my-xp'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('achievements/', views.MyAchievementsView.as_view(), name='my-achievements'),
    path('history/', views.ReadingHistoryView.as_view(), name='reading-history'),
]
