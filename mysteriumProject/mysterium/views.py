from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from .models import Post

# Create your views here.
pages = {
    "login": "login.html",
    "index": "index.html",
    "postDetail": "postDetail.html",
    "postCreation": "postCreation.html"
}


def selectedPage(request, page):
    try:
        currentPage = pages[page]

        if(currentPage == 'index.html'):
            posts = Post.objects.all()
            return render(request, currentPage, {'posts': posts})
        
        return render(request, currentPage)
    except:
        return HttpResponseNotFound('Page not found!')
