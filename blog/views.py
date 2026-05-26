from datetime import timedelta

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User
from .models import Tag, Article, Comment, Image, ReadStat, ArticleCollaborator
from .serializers import (
    TagSerializer, ArticleListSerializer, ArticleDetailSerializer,
    CommentSerializer, ImageSerializer, ArticleCollaboratorSerializer,
    ReadStatSerializer
)


class IsAuthorOrCollaborator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj.author == request.user:
            return True
        return obj.collaborators.filter(
            user=request.user, accepted=True, permission='edit'
        ).exists()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrCollaborator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'tags__name']
    ordering_fields = ['created_at', 'views_count', 'published_at']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Article.objects.all()

        if self.action in ['list', 'retrieve']:
            if not self.request.user.is_authenticated:
                queryset = queryset.filter(status='published')
            elif self.request.query_params.get('shared'):
                queryset = queryset.filter(
                    collaborators__user=self.request.user,
                    collaborators__accepted=True
                )
            elif self.request.query_params.get('mine'):
                queryset = queryset.filter(author=self.request.user)
            else:
                queryset = queryset.filter(
                    Q(status='published') | Q(author=self.request.user) |
                    Q(collaborators__user=self.request.user, collaborators__accepted=True)
                )

        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)

        status_filter = self.request.query_params.get('status')
        if status_filter and self.request.user.is_authenticated:
            queryset = queryset.filter(status=status_filter, author=self.request.user)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAuthorOrCollaborator()]

    def perform_create(self, serializer):
        article = serializer.save(author=self.request.user)
        if article.status == 'published' and not article.published_at:
            article.published_at = timezone.now()
            article.save()

    def perform_update(self, serializer):
        article = serializer.save()
        if article.status == 'published' and not article.published_at:
            article.published_at = timezone.now()
            article.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def record_view(self, request, slug=None):
        article = self.get_object()
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ',' in ip:
            ip = ip.split(',')[0].strip()

        time_threshold = timezone.now() - timedelta(hours=1)
        already_viewed = ReadStat.objects.filter(
            article=article,
            ip_address=ip,
            created_at__gte=time_threshold,
        ).exists()

        if not already_viewed:
            ReadStat.objects.create(
                article=article,
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referer=request.META.get('HTTP_REFERER', '')
            )
            article.views_count += 1
            article.save(update_fields=['views_count'])

        return Response({'views_count': article.views_count})


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = Comment.objects.filter(is_approved=True)
        article_id = self.request.query_params.get('article')
        if article_id:
            queryset = queryset.filter(article_id=article_id, parent=None)
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            serializer.save()


class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Image.objects.filter(uploader=self.request.user)

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def site_stats(request):
    return Response({
        'total_articles': Article.objects.filter(status='published').count(),
        'total_comments': Comment.objects.filter(is_approved=True).count(),
        'total_tags': Tag.objects.count(),
        'total_views': sum(
            Article.objects.filter(status='published').values_list('views_count', flat=True)
        ),
    })


class CollaborationViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleCollaboratorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ArticleCollaborator.objects.filter(
            Q(article__author=self.request.user) | Q(user=self.request.user)
        ).select_related('article', 'user', 'invited_by')

    def create(self, request, *args, **kwargs):
        article_id = request.data.get('article')
        try:
            article = Article.objects.get(id=article_id, author=request.user)
        except Article.DoesNotExist:
            return Response({'error': '只能分享自己的文章'}, status=status.HTTP_403_FORBIDDEN)
        username = request.data.get('username')
        if username == request.user.username:
            return Response({'error': '不能分享给自己'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        if ArticleCollaborator.objects.filter(article=article, user=user).exists():
            return Response({'error': '已经分享过了'}, status=status.HTTP_400_BAD_REQUEST)
        collab = ArticleCollaborator.objects.create(
            article=article,
            user=user,
            invited_by=request.user,
            permission=request.data.get('permission', 'edit'),
        )
        return Response(
            ArticleCollaboratorSerializer(collab, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def invitations(self, request):
        pending = ArticleCollaborator.objects.filter(
            user=request.user, accepted=False
        ).select_related('article', 'invited_by')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        collab = self.get_object()
        if collab.user != request.user:
            return Response({'error': '无权操作'}, status=status.HTTP_403_FORBIDDEN)
        collab.accepted = True
        collab.save(update_fields=['accepted'])
        return Response({'status': 'accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        collab = self.get_object()
        if collab.user != request.user:
            return Response({'error': '无权操作'}, status=status.HTTP_403_FORBIDDEN)
        collab.delete()
        return Response({'status': 'rejected'})


@api_view(['GET'])
def my_reading_stats(request):
    articles = Article.objects.filter(author=request.user)

    article_id = request.query_params.get('article')
    if article_id:
        articles = articles.filter(id=article_id)

    total_views = sum(articles.values_list('views_count', flat=True))
    total_articles = articles.count()

    articles_stats = []
    for article in articles.order_by('-views_count')[:20]:
        articles_stats.append({
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'views_count': article.views_count,
            'created_at': article.created_at,
        })

    daily_views = (
        ReadStat.objects.filter(article__author=request.user)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('-date')[:30]
    )

    return Response({
        'total_views': total_views,
        'total_articles': total_articles,
        'articles': articles_stats,
        'daily_views': list(daily_views),
    })


@api_view(['GET'])
def article_read_stats(request, article_id):
    try:
        article = Article.objects.get(id=article_id, author=request.user)
    except Article.DoesNotExist:
        return Response({'error': '文章不存在或无权限'}, status=status.HTTP_404_NOT_FOUND)

    stats = ReadStat.objects.filter(article=article).order_by('-created_at')[:50]
    serializer = ReadStatSerializer(stats, many=True)

    daily_views = (
        ReadStat.objects.filter(article=article)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('-date')[:30]
    )

    return Response({
        'article_title': article.title,
        'views_count': article.views_count,
        'recent_visits': serializer.data,
        'daily_views': list(daily_views),
    })
