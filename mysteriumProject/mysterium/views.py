from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound

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
        return render(request, currentPage)
    except:
        return HttpResponseNotFound('Page not found!')
