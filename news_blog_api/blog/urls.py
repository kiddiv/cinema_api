from django.urls import path
from .views import (ArticleListCreateView,ArticleDetailView,ArticleCommentsView,CommentDetailView,ArticleLikeView)

urlpatterns = [
    path('articles/', ArticleListCreateView.as_view(), name='article-list-create'),
    path('articles/<int:id>/', ArticleDetailView.as_view(), name='article-detail'),

    path('articles/<int:id>/comments/', ArticleCommentsView.as_view(), name='article-comments'),
    path('comments/<int:id>/', CommentDetailView.as_view(), name='comment-detail'),

    path('articles/<int:id>/like/', ArticleLikeView.as_view(), name='article-like'),
]