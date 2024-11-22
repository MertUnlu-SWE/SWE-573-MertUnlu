from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from .models import Post, Comment
from .forms import PostForm, CommentForm
from .wikidata_utils import fetch_wikidata_tags, fetch_wikidata_info
from django.contrib import messages

# Create your views here.
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        
        # Create the user and set additional fields
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        # Specify the backend explicitly
        backend = settings.AUTHENTICATION_BACKENDS[0]  # Use the first backend, adjust if necessary
        login(request, user, backend=backend)
        
        return redirect('index')  # Redirect to a desired page after registration
    
    return render(request, 'login.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Check if both fields are provided
        if not email or not password:
            return render(request, 'login.html', {'error': 'Email and password are required.'})
        
        try:
            # Authenticate the user
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                return render(request, 'login.html', {'error': 'Invalid email or password.'})
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Login error: {e}")
            return render(request, 'login.html', {'error': 'An unexpected error occurred. Please try again later.'})
    
    # GET request (load the login page)
    return render(request, 'login.html')


@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

def logout_view(request):
    logout(request)
    return redirect('index')

def index(request):
    try:
        posts = Post.objects.all().order_by('-upvotes')  # Ensure no database issues
        return render(request, 'index.html', {'posts': posts})
    except Exception as e:
        return JsonResponse({'error': f"Index view error: {str(e)}"}, status=500)


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

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            return redirect('post_detail', post_id=post.id)  # Yönlendirme ekle
    else:
        form = CommentForm()

    return render(request, 'postDetail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'tags': tags,
    })

def vote_post(request, post_id, vote_type):
    post = Post.objects.get(id=post_id)
    
    # Check if the user has already voted
    if request.user in post.voted_users.all():
        return JsonResponse({'error': 'You have already voted on this post.'}, status=403)
    
    # Increment the upvote or downvote count
    if vote_type == 'upvote':
        post.upvotes += 1
    elif vote_type == 'downvote':
        post.downvotes += 1
    post.save()
    
    # Add the user to the voted_users field to track that they have voted
    post.voted_users.add(request.user)
    
    return JsonResponse({'upvotes': post.upvotes, 'downvotes': post.downvotes})

def vote_comment(request, comment_id, vote_type):
    comment = Comment.objects.get(id=comment_id)
    
    # Check if the user has already voted
    if request.user in comment.voted_users.all():
        return JsonResponse({'error': 'You have already voted on this comment.'}, status=403)
    
    # Increment the upvote or downvote count
    if vote_type == 'upvote':
        comment.upvotes += 1
    elif vote_type == 'downvote':
        comment.downvotes += 1
    comment.save()
    
    # Add the user to the voted_users field to track that they have voted
    comment.voted_users.add(request.user)
    
    return JsonResponse({'upvotes': comment.upvotes, 'downvotes': comment.downvotes})

@login_required
def mark_post_as_solved(request, post_id, comment_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id, post=post)

        # Sadece post sahibi işlem yapabilir
        if request.user != post.user:
            return JsonResponse({'error': 'You are not authorized to mark this post as solved.'}, status=403)

        # Post'u çözülmüş olarak işaretleyin ve doğru yorumu kaydedin
        post.is_solved = True
        post.solved_comment = comment
        post.save()

        # Çözüm işaretlendiğinde yorumu güncelleyin
        comment.is_solved = True
        comment.save()

        return JsonResponse({
            'post_is_solved': post.is_solved,
            'solved_comment_id': comment.id,
            'solved_comment_text': comment.text,
        })
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required
def unmark_post_as_solved(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)

        # Sadece post sahibi işlem yapabilir
        if request.user != post.user:
            return JsonResponse({'error': 'You are not authorized to unmark this post as solved.'}, status=403)

        # Çözüm durumunu sıfırlayın
        post.is_solved = False
        post.solved_comment = None
        post.save()

        return JsonResponse({'post_is_solved': post.is_solved})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


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


def fetch_wikidata(request):
    try:
        tags = request.GET.get('tags', '').strip("[]").split(",")
        tags = [tag.strip().strip('"') for tag in tags]
        all_results = {}

        for tag in tags:
            try:
                results = fetch_wikidata_tags(tag)
                if results:
                    all_results[tag] = results
            except Exception as e:
                all_results[tag] = f"Error fetching data for tag '{tag}': {str(e)}"

        return JsonResponse({'results': all_results})
    except Exception as e:
        return JsonResponse({'error': f"Failed to fetch Wikidata information: {str(e)}"}, status=500)



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


def search_tags(request):
    results = []
    query = request.GET.get('query', None)

    if query:
        results = fetch_wikidata_tags(query)
        print("Fetched Tags:", results)

    return JsonResponse({'results': results, 'query': query})
