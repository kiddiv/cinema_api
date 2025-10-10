from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Article, Comment, Like
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleCreateUpdateSerializer,
    CommentSerializer
)
class ArticleListCreateView(APIView):
    def get(self, request):
        articles = Article.objects.annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        ).select_related('author')

        serializer = ArticleListSerializer(articles, many=True)
        return Response({'data': serializer.data})

    def post(self, request):
        serializer = ArticleCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            article = serializer.save()
            return Response(
                ArticleDetailSerializer(article).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetailView(APIView):
    def get(self, request, id):
        article = get_object_or_404(
            Article.objects.annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments')
            ),
            id=id
        )
        serializer = ArticleDetailSerializer(article)
        return Response(serializer.data)

    def put(self, request, id):
        article = get_object_or_404(Article, id=id)
        serializer = ArticleCreateUpdateSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            article.refresh_from_db()
            return Response(ArticleDetailSerializer(article).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        article = get_object_or_404(Article, id=id)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ArticleCommentsView(APIView):
    def get(self, request, id):
        article = get_object_or_404(Article, id=id)
        comments = article.comments.select_related('author').all()
        serializer = CommentSerializer(comments, many=True)
        return Response({'data': serializer.data})

    def post(self, request, id):
        article = get_object_or_404(Article, id=id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(article=article)
            return Response(
                CommentSerializer(comment).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    def put(self, request, id):
        comment = get_object_or_404(Comment, id=id)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        comment = get_object_or_404(Comment, id=id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ArticleLikeView(APIView):
    def post(self, request, id):
        article = get_object_or_404(Article, id=id)
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        like, created = Like.objects.get_or_create(
            article=article,
            user_id=user_id
        )

        if not created:
            return Response(
                {'error': 'Already liked'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'message': 'Article liked successfully',
            'likes_count': article.likes.count()
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        article = get_object_or_404(Article, id=id)
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            like = Like.objects.get(article=article, user_id=user_id)
            like.delete()
            return Response({
                'message': 'Like removed successfully',
                'likes_count': article.likes.count()
            })
        except Like.DoesNotExist:
            return Response(
                {'error': 'Like not found'},
                status=status.HTTP_404_NOT_FOUND
            )
