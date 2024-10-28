from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from .models import Post, Comment
from .forms import CommentForm, PostForm
from django.db.models import Q
from .wikidata_utils import fetch_wikidata_info

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
            return redirect('index')
        else:
            print("Invalid credentials")
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def index(request):
    posts = Post.objects.all()
    return render(request, 'index.html', {'posts': posts})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)

    # Split tags into a list
    tags = post.tags.split(',') if post.tags else []
    
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

    return render(request, 'postDetail.html', {'post': post, 'comments': comments, 'tags': tags})

def post_creation(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user

            # Handle tags and Wikidata integration
            tags = form.cleaned_data['tags']
            post.tags = ', '.join([tag.strip() for tag in tags.split(',')])

            # Fetch Wikidata information for each tag
            tag_info = []
            for tag in tags.split(','):
                wikidata_id, wikidata_label = fetch_wikidata_info(tag.strip())
                if wikidata_id:
                    tag_info.append({'tag': tag, 'wikidata_id': wikidata_id, 'wikidata_label': wikidata_label})

            post.save()
            return render(request, 'postDetail.html', {'post': post, 'tag_info': tag_info})
    else:
        form = PostForm()

    return render(request, 'postCreation.html', {'form': form})

def search_posts(request):
    query = request.GET.get('query')
    if query:
        tags = query.split(',')
        posts = Post.objects.filter(Q(tags__icontains=tags))
    else:
        posts = Post.objects.all()
    return render(request, 'index.html', {'posts': posts})