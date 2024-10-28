from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from .models import Post, Comment
from .forms import CommentForm

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
    
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            print(f"Authenticated: {user}")
            login(request, user)
            return redirect('index')  # Giriş başarılı, ana sayfaya yönlendir
        else:
            print("Invalid credentials")
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def index(request):
    posts = Post.objects.all()  # Retrieve all posts to display on the index page
    return render(request, 'index.html', {'posts': posts})

def post_creation(request):
    return render(request, 'postCreation.html')

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # İlgili post için yorumları getir
    comments = Comment.objects.filter(post=post)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('postDetail', post_id=post.id)
    else:
        form = CommentForm()

    return render(request, 'postDetail.html', {'post': post, 'form': form, 'comments': comments})