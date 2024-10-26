from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound

# Create your views here.
pages = {
    "login": "Log in Page",
    "index": "Main Page",
    "postDetail": "Post Detail Page",
    "postCreation": "Post Creation Page"
}


def selectedPage(request, page):
    try:
        currentPage = pages[page]
        return render(request, 'login.html')
    except:
        return HttpResponseNotFound('Page not found!')
