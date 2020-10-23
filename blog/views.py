from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from json import JSONDecodeError
from django.contrib.auth import authenticate, login, logout
from .models import Article
from .models import Comment
from django.contrib.auth.decorators import login_required


def signup(request):
    if request.method == 'POST':
        try:
            req_data = json.loads(request.body.decode())
            username = req_data['username']
            password = req_data['password']
            User.objects.create_user(username, None ,password)
            return HttpResponse(status=201)
        except :
            return HttpResponse(status=400)

    else:
        return HttpResponse(status=405)

@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=405)


def signin(request):
    if request.method == 'POST':
        body = request.body.decode()
        username = json.loads(body)['username']
        password = json.loads(body)['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse( status=204)
        else:
            return HttpResponse( status=401)
    else:
        return HttpResponse(status=405)

def signout(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    if request.method == 'GET':
        logout(request)
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=405)

def article_general(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    if request.method == 'GET':
        all_article_list = [article for article in Article.objects.all().values()]
        all_article_list = list(map(lambda x : {"title":x["title"], "content":x["content"], "author":x["author_id"]},all_article_list))
        return JsonResponse(all_article_list, safe=False)
    elif request.method == "POST":
        try :
            body = request.body.decode()
            title = json.loads(body)['title']
            content = json.loads(body)['content']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        
        article = Article(title=title, content=content, author=request.user)
        article.save()
        res_dict ={"title":title,"content":content,"id":article.id}
        return JsonResponse(res_dict, status=201)
    else :
        return HttpResponse(status=405)


def article_specified(request, article_id=""):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    if request.method == 'GET':
        article = Article.objects.filter(id=article_id).values()
        if not article :
            return HttpResponse(status=404)
        article = article[0]
        username = User.objects.get(id=article["author_id"]).username
        res_dict = {"title":article["title"],"content":article["content"],"author":username}
        return JsonResponse(res_dict, safe=False)
    elif request.method == "PUT":
        article = Article.objects.filter(id=article_id).values()
        if not article :
            return HttpResponse(status=404)
        article = article[0]
        author_id= article["author_id"]
        if author_id != request.user.id :
            return HttpResponse(status=403)
        try:
            body = request.body.decode()
            title = json.loads(body)['title']
            content = json.loads(body)['content']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        article = Article.objects.filter(id=article_id).first()
        article.title=title
        article.content=content
        article.save()
        response_dict = {'id': article.id, 'title': article.title, 'content':article.content, 'author':request.user.username}
        return JsonResponse(response_dict, status=200, safe=False)
    elif request.method == 'DELETE':
        article = Article.objects.filter(id=article_id).values()
        if not article :
            return HttpResponse(status=404)
        article = article[0]
        author_id= article["author_id"]
        if author_id != request.user.id :
            return HttpResponse(status=403)
        Article.objects.filter(id=article_id).delete()
        return HttpResponse(status=200)
    else :
        return HttpResponse(status=405)



def comment_article(request, article_id=""):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    if request.method == 'POST':
        if not Article.objects.filter(id=article_id):
            return HttpResponse(status=404)
        try :
            body = request.body.decode()
            content = json.loads(body)['content']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        comment = Comment(content=content, author=request.user, article=Article.objects.filter(id=article_id).first())
        comment.save()
        res_dict = {"content":content,"id":comment.id}
        return JsonResponse(res_dict,status=201)
    elif request.method == 'GET':
        if not Article.objects.filter(id=article_id):
            return HttpResponse(status=404)
        comment = Comment.objects.filter(article=Article.objects.filter(id=article_id).first()).values()
        res_dict = {"article":comment[0]["article_id"], "author":comment[0]["author_id"],"content":comment[0]["content"]}
        return JsonResponse(res_dict, safe=False)
    else:
        return HttpResponse(status=405)

def comment_specified(request, comment_id=""):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    if request.method == 'GET':
        comment = Comment.objects.filter(id=comment_id).values()
        if not comment :
            return HttpResponse(status=404)
        res_dict = {"article":comment[0]["article_id"],"author":comment[0]["author_id"],"content":comment[0]["content"]}
        return JsonResponse(res_dict, safe=False)
    elif request.method == "PUT":
        comment = Comment.objects.filter(id=comment_id).values()
        if not comment :
            return HttpResponse(status=404)
        comment= comment[0]
        author_id= comment["author_id"]
        if author_id != request.user.id :
            return HttpResponse(status=403)
        try:
            body = request.body.decode()
            content = json.loads(body)['content']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        comment = Comment.objects.filter(id=comment_id).first()
        comment.content=content
        comment.save()
        response_dict = {'id': comment.id, 'content':comment.content}
        return JsonResponse(response_dict, status=200, safe=False)
    elif request.method == 'DELETE':
        comment = Comment.objects.filter(id=comment_id).values()
        if not comment :
            return HttpResponse(status=404)
        comment= comment[0]
        author_id= comment["author_id"]
        if author_id != request.user.id :
            return HttpResponse(status=403)
        comment = Comment.objects.filter(id=comment_id).delete()
        return HttpResponse(status=200)
    else :
        return HttpResponse(status=405)

