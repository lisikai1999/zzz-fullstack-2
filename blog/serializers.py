from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Tag, Article, Comment, Image


class TagSerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'article_count']
        read_only_fields = ['slug']

    def get_article_count(self, obj):
        return obj.articles.filter(status='published').count()


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'article', 'author', 'author_name', 'nickname', 'email',
                  'content', 'parent', 'replies', 'is_approved', 'created_at']
        read_only_fields = ['author', 'is_approved']

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.username
        return obj.nickname

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.filter(is_approved=True), many=True).data
        return []


class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'excerpt', 'cover_image', 'status',
                  'author', 'author_name', 'tags', 'views_count', 'comment_count',
                  'created_at', 'published_at']
        read_only_fields = ['author', 'views_count']

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class ArticleDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, source='tags', required=False
    )
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'content', 'content_html', 'excerpt',
                  'cover_image', 'status', 'author', 'author_name', 'tags', 'tag_ids',
                  'views_count', 'comments', 'created_at', 'updated_at', 'published_at',
                  'meta_description', 'meta_keywords']
        read_only_fields = ['author', 'content_html', 'views_count', 'slug']

    def get_comments(self, obj):
        top_comments = obj.comments.filter(parent=None, is_approved=True)
        return CommentSerializer(top_comments, many=True).data


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'image', 'url', 'alt_text', 'created_at']
        read_only_fields = ['uploader']

    def get_url(self, obj):
        request = self.context.get('request')
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)
        return ''
