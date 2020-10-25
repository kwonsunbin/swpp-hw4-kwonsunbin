from django.test import TestCase, Client
import json
from .models import Article, Comment
from django.contrib.auth.models import User



class BlogTestCase(TestCase):

        
    def test_check_models(self):
        new_user = User.objects.create_user(username='swpp', password='iluvswpp')  # Django default user model
        new_article = Article(title='I Love SWPP!', content='Believe it or not', author=new_user)
        new_article.save()
        new_comment = Comment(article=new_article, content='Comment!', author=new_user)
        new_comment.save()

    def test_csrf(self):
        # By default, csrf checks are disabled in test client
        # To test csrf protection we enforce csrf checks here
        client = Client(enforce_csrf_checks=True)
        response = client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  # Request without csrf token returns 403 response

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection

        response = client.post('/api/token/',  HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

    def test_signup(self):
        client = Client()
        signup_dict = {"username": "hi", "password": "hi"}
        response = client.post('/api/signup/', json.dumps(signup_dict), content_type='application/json')

        self.assertEqual(response.status_code, 201)

        signup_dict = {"username": "bye"}
        response = client.post('/api/signup/', json.dumps(signup_dict), content_type='application/json')

        self.assertEqual(response.status_code, 400)

        response = client.get('/api/signup/')

        self.assertEqual(response.status_code, 405)
    
    def test_signout(self):

        User.objects.create_user(username='swpp', password='iluvswpp')
        stranger = Client()
        user = Client()
        user.post('/api/signin/', json.dumps({'username': 'swpp', 'password': 'iluvswpp'}),
                               content_type='application/json')
        
        response = stranger.get('/api/signout/')
        self.assertEqual(response.status_code, 401)

        response = user.get('/api/signout/')
        self.assertEqual(response.status_code, 204)

        user.post('/api/signin/', json.dumps({'username': 'swpp', 'password': 'iluvswpp'}),
                               content_type='application/json')
        response = user.delete('/api/signout/')
        self.assertEqual(response.status_code, 405)

    def test_signin(self):

        User.objects.create_user(username='swpp', password='iluvswpp')
        stranger = Client()
        user = Client()

        response = user.put('/api/signin/', json.dumps({'username': 'swpp2', 'password': 'iluvswpp'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 405)
        
        response = user.post('/api/signin/', json.dumps({'username': 'swpp2', 'password': 'iluvswpp'}),
                               content_type='application/json')

        self.assertEqual(response.status_code, 401)

    def test_article_general(self):

        new_user = User.objects.create_user(username='swpp', password='iluvswpp')
        stranger = Client()

        new_article1 = Article(title='I Love SWPP!', content='Do not believe it', author=new_user)
        new_article1.save()
        new_article2 = Article(title='I hate SWPP!', content='Believe it', author=new_user)
        new_article2.save()

        response = stranger.get('/api/article/')

        self.assertEqual(response.status_code, 401)

        user = Client()
        user.post('/api/signin/', json.dumps({'username': 'swpp', 'password': 'iluvswpp'}),
                               content_type='application/json')
        response = user.get('/api/article/')

        self.assertEqual(response.status_code,200)

        response = user.post('/api/article/', json.dumps({'content': 'hi', 'title': 'hi'}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code,201)

        response = user.post('/api/article/', json.dumps({'content': 'hi'}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code,400)

        response = user.delete('/api/article/', json.dumps({'content': 'hi'}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code,405)

    def test_article_specified(self):

        User.objects.create_user(username='swpp1', password='iluvswpp')
        User.objects.create_user(username='swpp2', password='iluvswpp')
        stranger = Client()

        new_article1 = Article(title='I Love SWPP!', content='Do not believe it', author=User.objects.get(username="swpp1"))
        new_article1.save()
        new_article2 = Article(title='I hate SWPP!', content='Believe it', author=User.objects.get(username="swpp2"))
        new_article2.save()

        response = stranger.get('/api/article/1/')

        self.assertEqual(response.status_code, 401)

        swpp1 = Client()
        swpp1.post('/api/signin/', json.dumps({'username': 'swpp1', 'password': 'iluvswpp'}),
                               content_type='application/json')
        swpp2 = Client()
        swpp2.post('/api/signin/', json.dumps({'username': 'swpp2', 'password': 'iluvswpp'}),
                               content_type='application/json')
        response = swpp1.get('/api/article/1/')

        self.assertEqual(response.status_code,200)

        response = swpp1.get('/api/article/100/')

        self.assertEqual(response.status_code,404)

        response = swpp1.post('/api/article/10/', json.dumps({'username': 'swpp', 'password': 'iluvswpp'}),
                               content_type='application/json')
        self.assertEqual(response.status_code,405)

        response = swpp1.put('/api/article/1/', json.dumps({'content': 'bye', 'title': 'bye'}),
                               content_type='application/json')
        self.assertEqual(response.status_code,200)

        response = swpp1.put('/api/article/1/', json.dumps({'content': 'bye'}),
                               content_type='application/json')
        self.assertEqual(response.status_code,400)

        response = swpp1.put('/api/article/101/', json.dumps({'content': 'bye'}),
                               content_type='application/json')
        self.assertEqual(response.status_code,404)


        response = swpp2.put('/api/article/1/', json.dumps({'content': 'bye', 'title': 'bye'}),
                               content_type='application/json')
        self.assertEqual(response.status_code,403)

        response = swpp2.delete('/api/article/1/')
        self.assertEqual(response.status_code,403)

        response = swpp2.delete('/api/article/100/')
        self.assertEqual(response.status_code,404)

        response = swpp1.delete('/api/article/1/')
        self.assertEqual(response.status_code,200)


    def test_comment_article(self):

        User.objects.create_user(username='swpp1', password='iluvswpp')
        User.objects.create_user(username='swpp2', password='iluvswpp')
        stranger = Client()
        swpp1 = Client()
        swpp1.post('/api/signin/', json.dumps({'username': 'swpp1', 'password': 'iluvswpp'}),
                               content_type='application/json')
        swpp2 = Client()
        swpp2.post('/api/signin/', json.dumps({'username': 'swpp2', 'password': 'iluvswpp'}),
                               content_type='application/json')

        new_article1 = Article(title='I Love SWPP!', content='Do not believe it', author=User.objects.get(username="swpp1"))
        new_article1.save()
        new_article2 = Article(title='I hate SWPP!', content='Believe it', author=User.objects.get(username="swpp2"))
        new_article2.save()

        new_comment1 = Comment(content='Do not believe it', author=User.objects.get(username="swpp1"), article=Article.objects.get(id="1"))
        new_comment1.save()
        new_comment2 = Comment(content='Believe it', author=User.objects.get(username="swpp2"),  article=Article.objects.get(id="2"))
        new_comment2.save()

        response = stranger.get('/api/article/1/comment/')

        self.assertEqual(response.status_code, 401)

        response = swpp1.get('/api/article/1/comment/')

        self.assertEqual(response.status_code,200)

        response = swpp1.post('/api/article/1/comment/', json.dumps({"content":"hi"}), content_type="application/json")

        self.assertEqual(response.status_code,201)

        response = swpp1.post('/api/article/100/comment/', json.dumps({"content":"hi"}), content_type="application/json")

        self.assertEqual(response.status_code,404)

        response = swpp1.post('/api/article/1/comment/', json.dumps({}), content_type="application/json")

        self.assertEqual(response.status_code,400)

        response = swpp1.get('/api/article/1/comment/')

        self.assertEqual(response.status_code,200)

        response = swpp1.get('/api/article/100/comment/')

        self.assertEqual(response.status_code,404)

        response = swpp1.delete('/api/article/1/comment/')

        self.assertEqual(response.status_code,405)

    def test_comment_specified(self):
        User.objects.create_user(username='swpp1', password='iluvswpp')
        User.objects.create_user(username='swpp2', password='iluvswpp')
        stranger = Client()
        swpp1 = Client()
        swpp1.post('/api/signin/', json.dumps({'username': 'swpp1', 'password': 'iluvswpp'}),
                               content_type='application/json')
        swpp2 = Client()
        swpp2.post('/api/signin/', json.dumps({'username': 'swpp2', 'password': 'iluvswpp'}),
                               content_type='application/json')

        new_article1 = Article(title='I Love SWPP!', content='Do not believe it', author=User.objects.get(username="swpp1"))
        new_article1.save()
        new_article2 = Article(title='I hate SWPP!', content='Believe it', author=User.objects.get(username="swpp2"))
        new_article2.save()

        new_comment1 = Comment(content='Do not believe it', author=User.objects.get(username="swpp1"), article=Article.objects.get(id="1"))
        new_comment1.save()
        new_comment2 = Comment(content='Believe it', author=User.objects.get(username="swpp2"),  article=Article.objects.get(id="2"))
        new_comment2.save()

        response = stranger.get('/api/comment/1/')

        self.assertEqual(response.status_code, 401)

        response = swpp1.get('/api/comment/1/')

        self.assertEqual(response.status_code, 200)

        response = swpp1.get('/api/comment/100/')

        self.assertEqual(response.status_code, 404)

        response = swpp1.put('/api/comment/1/', json.dumps({"content":"bye"}), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)

        response = swpp1.put('/api/comment/100/', json.dumps({"content":"bye"}), content_type="application/json")
        
        self.assertEqual(response.status_code, 404)

        response = swpp1.put('/api/comment/1/', json.dumps({}), content_type="application/json")

        self.assertEqual(response.status_code, 400)

        response = swpp2.put('/api/comment/1/', json.dumps({"content":"bye"}), content_type="application/json")
        
        self.assertEqual(response.status_code, 403)

        response = swpp2.delete('/api/comment/1/', json.dumps({"content":"bye"}), content_type="application/json")
        
        self.assertEqual(response.status_code, 403)

        response = swpp1.delete('/api/comment/100/')
        
        self.assertEqual(response.status_code, 404)

        response = swpp1.delete('/api/comment/1/')
        
        self.assertEqual(response.status_code, 200)

        response = swpp1.post('/api/comment/1/', json.dumps({"content":"bye"}), content_type="application/json")
        
        self.assertEqual(response.status_code, 405)





            


