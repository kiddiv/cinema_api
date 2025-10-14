from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Article, Comment, Like


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class ArticleListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    content_preview = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'content_preview', 'author','likes_count', 'comments_count', 'created_at', 'updated_at']

    def get_content_preview(self, obj):
        return obj.get_content_preview()


class ArticleDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'likes_count','comments_count', 'created_at', 'updated_at']


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content',  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        return Article.objects.create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    article_id = serializers.IntegerField(read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'author_id', 'article_id','created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        author_id = validated_data.pop('author_id', None)
        if author_id:
            validated_data['author_id'] = author_id
        return super().create(validated_data)