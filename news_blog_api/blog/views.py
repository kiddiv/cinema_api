from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import DeleteByAdmin

from .models import Article, Comment, Like
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleCreateUpdateSerializer,
    CommentSerializer
)
class ArticleListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        articles = Article.objects.annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        ).select_related('author')
        author_id = request.query_params.get('author')
        if author_id:
            articles = articles.filter(author_id=author_id)
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArticleCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            article = serializer.save(author=request.user)
            return Response(
                ArticleDetailSerializer(article).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetailView(APIView):
    permission_classes = [AllowAny,DeleteByAdmin]
    def get_permissions(self):
        if self.request.method in ['PUT' 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]
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
        if article.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = ArticleCreateUpdateSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            article.refresh_from_db()
            return Response(ArticleDetailSerializer(article).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        article = get_object_or_404(Article, id=id)
        self.check_object_permissions(request, article)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ArticleCommentsView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]
    def get(self, request, id):
        article = get_object_or_404(Article, id=id)
        comments = article.comments.select_related('author').all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        article = get_object_or_404(Article, id=id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(article=article,author=request.user)
            return Response(
                CommentSerializer(comment).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        comment = get_object_or_404(Comment, id=id)
        if comment.author != request.user:
            return Response({'error': 'Ви не можете редагувати чужий коментар'}, status=403)

        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        comment = get_object_or_404(Comment, id=id)
        if comment.author != request.user:
            return Response({'error': 'Ви не можете видалити чужий коментар'}, status=403)
        comment.delete()
        return Response(status=204)

class ArticleLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        article = get_object_or_404(Article, id=id)
        if Like.objects.filter(article=article, user=request.user).exists():
            return Response(
                {'error': 'Ви вже лайкнули цю статтю'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Like.objects.create(article=article, user=request.user)
        return Response({
            'message': 'Лайк додано',
            'likes_count': article.likes.count()
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        article = get_object_or_404(Article, id=id)
        like = Like.objects.filter(article=article, user=request.user).first()

        if not like:
            return Response(
                {'error': 'Ви ще не лайкали цю статтю'},
                status=status.HTTP_404_NOT_FOUND
            )

        like.delete()
        return Response({
            'message': 'Лайк видалено',
            'likes_count': article.likes.count()
        })

