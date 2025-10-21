from django.test import TestCase
from django.contrib.auth.models import User
from .models import Article, Comment
from rest_framework.test import  APIClient

class BlogTest(TestCase):
    fixtures = ['blog/fixtures/data.json']

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.get(pk=1)
        self.article = Article.objects.get(pk=1)
        self.comment = Comment.objects.get(pk=1)
    def test_articles_list(self):
        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.status_code, 200)
    def test_articles_id(self):
        response = self.client.get(f'/api/v1/articles/{self.article.id}/')
        self.assertEqual(response.status_code, 200)
    def test_article_not_existing_id(self):
        response = self.client.get(f'/api/v1/articles/53535/')
        self.assertEqual(response.status_code, 404)
    def test_article_create(self):
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New Article', 'content': 'New content'}
        response = self.client.post('/api/v1/articles/', data)
        self.assertEqual(response.status_code, 201)
    def test_article_unauthorization_create(self):
        data = {'title': 'New Article', 'content': 'New content'}
        response = self.client.post('/api/v1/articles/', data)
        self.assertEqual(response.status_code, 401)
    def test_article_fail_create(self):
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New Article'}
        response = self.client.post('/api/v1/articles/', data)
        self.assertEqual(response.status_code, 400)
    def test_article_view_by_id(self):
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New Article', 'content': 'New content'}
        response = self.client.put(f'/api/v1/articles/{self.article.id}/', data)
        self.assertEqual(response.status_code, 200)
    def test_article_delete(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/v1/articles/{self.article.id}/')
        self.assertEqual(response.status_code, 204)
    def test_article_delete_invalid_id(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/api/v1/articles/42442/')
        self.assertEqual(response.status_code, 404)
    def test_article_update_forbidden(self):
        other_user = User.objects.create_user(username='other', password='12345')
        self.client.force_authenticate(user=other_user)
        data = {'title': 'ewewewew', 'content': 'bruh'}
        response = self.client.put(f'/api/v1/articles/{self.article.id}/', data)
        self.assertEqual(response.status_code, 403)


    def test_article_comments(self):
        response = self.client.get(f'/api/v1/articles/{self.article.id}/comments/')
        self.assertEqual(response.status_code, 200)
    def test_article_comments_fail(self):
        response = self.client.get(f'/api/v1/articles/234/comments/')
        self.assertEqual(response.status_code, 404)
    def test_article_commet_create(self):
       self.client.force_authenticate(user=self.user)
       data = {'article': self.article.id , 'content': 'New content'}
       response = self.client.post(f'/api/v1/articles/{self.article.id}/comments/', data)
       self.assertEqual(response.status_code, 201)
    def test_article_comment_fail_create(self):
        self.client.force_authenticate(user=self.user)
        data = {'article': self.article.id}
        response = self.client.post(f'/api/v1/articles/{self.article.id}/comments/', data)
        self.assertEqual(response.status_code, 400)
    def test_article_comment_unauthorizate_create(self):
        data = {'article': self.article.id , 'content': 'New content'}
        response = self.client.post(f'/api/v1/articles/{self.article.id}/comments/', data)
        self.assertEqual(response.status_code, 401)
    def test_comment_delete(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/v1/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, 204)
    def test_comment_delete_invalid_id(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/api/v1/comments/239/')
        self.assertEqual(response.status_code, 404)



    def test_like_create(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/v1/articles/{self.article.id}/like/')
        self.assertEqual(response.status_code, 201)
    def test_like_unauthorizated_create(self):
        response = self.client.post(f'/api/v1/articles/1/like/')
        self.assertEqual(response.status_code, 401)
    def test_like_duplicate(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(f'/api/v1/articles/{self.article.id}/like/')
        response = self.client.post(f'/api/v1/articles/{self.article.id}/like/')
        self.assertEqual(response.status_code, 400)


