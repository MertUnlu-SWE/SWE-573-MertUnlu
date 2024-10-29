from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from .models import Post, Comment
from .forms import PostForm
from django.db.models import Q
from .wikidata_utils import fetch_wikidata_info
from django.contrib import messages

# Create your views here.


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

    comments = Comment.objects.filter(post=post).order_by('-created_at')

    tags = []
    if post.tags:
        raw_tags = post.tags.split(',')
        for tag in raw_tags:
            if ' (Q' in tag:
                parts = tag.split(' (Q')
                tag_name = parts[0]
                q_number = parts[1].rstrip(')')
                tags.append((tag_name, q_number))
            else:
                tags.append((tag, None))

    context = {
        'post': post,
        'comments': comments,
        'tags': tags,
    }
    return render(request, 'postDetail.html', context)


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
                    tag_info.append(
                        {'tag': tag, 'wikidata_id': wikidata_id, 'wikidata_label': wikidata_label})

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


def fetch_wikidata_tag(request):
    tag = request.GET.get('tag', '').strip()
    if tag:
        q_number, _ = fetch_wikidata_info([tag])
        if q_number:
            return JsonResponse({'qNumber': q_number})
    return JsonResponse({'qNumber': None})

    #return JsonResponse({'results': []})


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Owner of post
    if request.user != post.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('post_detail', post_id=post.id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'editPost.html', {'form': form, 'post': post})
