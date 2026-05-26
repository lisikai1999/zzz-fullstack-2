from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet, basename='article')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'images', views.ImageViewSet, basename='image')
router.register(r'collaborations', views.CollaborationViewSet, basename='collaboration')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', views.site_stats, name='site-stats'),
]
