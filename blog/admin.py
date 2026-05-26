from django.contrib import admin
from .models import Tag, Article, Comment, ReadStat, Image, ArticleCollaborator


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'views_count', 'created_at']
    list_filter = ['status', 'tags', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'author', 'nickname', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']


@admin.register(ReadStat)
class ReadStatAdmin(admin.ModelAdmin):
    list_display = ['article', 'ip_address', 'created_at']
    list_filter = ['created_at']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['alt_text', 'uploader', 'created_at']


@admin.register(ArticleCollaborator)
class ArticleCollaboratorAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'invited_by', 'permission', 'accepted', 'created_at']
    list_filter = ['permission', 'accepted']
