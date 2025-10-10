from django.contrib import admin
from .models import Article, Comment, Like


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'created_at', 'get_likes_count', 'get_comments_count']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'article', 'author', 'created_at']
    list_filter = ['created_at', 'article']
    search_fields = ['content']
    readonly_fields = ['created_at', 'updated_at']



@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'article', 'user', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']