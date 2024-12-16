from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from .models import Post, Comment, Bookmark
from django.db.models import Count
from .forms import PostForm, CommentForm
from .wikidata_utils import fetch_wikidata_tags, fetch_wikidata_info
from django.contrib import messages
from django.db import transaction
import boto3
import json
from django.views.decorators.cache import never_cache


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
    if 'next' not in request.GET and 'HTTP_REFERER' in request.META:
        previous_url = request.META.get('HTTP_REFERER', '/')
        if not previous_url.endswith('/login/'):
            request.session['previous_url'] = previous_url

    next_url = request.GET.get('next', request.session.get('previous_url', '/'))

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
                login(request, user, backend='mysterium.backends.EmailBackend')
                messages.success(request, 'Successfully logged in.')
                next_url = request.session.pop('previous_url', '/')
                return redirect(next_url)
            else:
                return render(request, 'login.html', {'error': 'Invalid email or password.'})
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Login error: {e}")
            return render(request, 'login.html', {'error': 'An unexpected error occurred. Please try again later.'})
    
    # GET request (load the login page)
    return render(request, 'login.html', {'next': next_url})



@never_cache
def profile_view(request, user_id=None):
    if user_id:
        profile_user = get_object_or_404(User, id=user_id)
        is_own_profile = request.user.is_authenticated and profile_user == request.user
    else:
        if not request.user.is_authenticated:
            messages.error(request, "You must log in to view your profile.")
            return redirect('login')
        profile_user = request.user
        is_own_profile = True

    user_posts = Post.objects.filter(user=profile_user).order_by('-created_at')
    bookmarked_comments = (
        Bookmark.objects.filter(user=request.user).select_related('comment__post') if is_own_profile else None
    )

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'user_posts': user_posts,
        'bookmarked_comments': bookmarked_comments,
    })




def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('index')

@never_cache
def index(request):
    try:
        posts = Post.objects.all().order_by('-upvotes')  # Ensure no database issues
        return render(request, 'index.html', {'posts': posts})
    except Exception as e:
        return JsonResponse({'error': f"Index view error: {str(e)}"}, status=500)

@never_cache
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-created_at')

    # Login Check
    if request.method == 'POST' and not request.user.is_authenticated:
        return JsonResponse({'error': 'You must login to add a comment!'}, status=403)
    
    # Volume hesaplama (width, height, length varsa hesaplanır)
    volume = None
    if post.width and post.height and post.length:
        try:
            width = float(post.width) if post.width_unit == 'cm' else float(post.width) * 100
            height = float(post.height) if post.height_unit == 'cm' else float(post.height) * 100
            length = float(post.length) if post.length_unit == 'cm' else float(post.length) * 100

            volume = width * height * length
        except (TypeError, ValueError):
            volume = None
    

    tags = []
    if post.tags:
        raw_tags = post.tags.split(',')
        for tag in raw_tags:
            tag = tag.strip()
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
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()

    print("Post Details openned!")
    # Login Check
    if request.user.is_authenticated:
        bookmarks = Bookmark.objects.filter(user=request.user, comment__in=comments)
        bookmarked_comment_ids = list(bookmarks.values_list('comment_id', flat=True))  # Liste formatı
        print("Bookmarked Comment IDs:", bookmarked_comment_ids)
    else:
        bookmarked_comment_ids = []

    return render(request, 'postDetail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'tags': tags,
        'bookmarked_comment_ids': json.dumps(bookmarked_comment_ids),
        'calculated_volume': volume,
    })

@login_required
def vote_post(request, post_id, vote_type):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must login before voting!'}, status=403)

    post = get_object_or_404(Post, id=post_id)

    # Check if the user has already voted on this post
    user_vote = post.votes.filter(user=request.user).first()

    # Handle vote toggling or changing
    if user_vote:
        if user_vote.vote_type == vote_type:
            # User clicks the same vote type again: retract the vote
            user_vote.delete()
            if vote_type == 'upvote':
                post.upvotes -= 1
            elif vote_type == 'downvote':
                post.downvotes -= 1
            post.save()
            return JsonResponse({'success': True, 'action': 'retracted', 'upvotes': post.upvotes, 'downvotes': post.downvotes})
        else:
            # User changes vote type: remove old vote and add new
            if user_vote.vote_type == 'upvote':
                post.upvotes -= 1
            elif user_vote.vote_type == 'downvote':
                post.downvotes -= 1

            user_vote.vote_type = vote_type
            user_vote.save()
    else:
        # User has not voted before: add new vote
        post.votes.create(user=request.user, vote_type=vote_type)

    # Adjust vote counts
    if vote_type == 'upvote':
        post.upvotes += 1
    elif vote_type == 'downvote':
        post.downvotes += 1

    post.save()
    return JsonResponse({'success': True, 'action': 'voted', 'upvotes': post.upvotes, 'downvotes': post.downvotes})


@login_required
def vote_comment(request, comment_id, vote_type):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must login before commenting!'}, status=403)

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
def mark_as_solved(request, post_id, comment_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id, post=post)

        print(f"DEBUG: User: {request.user}, Post Owner: {post.user}")  # Debugging
        # Sadece post sahibi işlem yapabilir
        if request.user != post.user:
            print(f"Unauthorized Attempt by User: {request.user.username}")
            return JsonResponse({'error': 'You are not authorized to mark this post as solved.'}, status=403)

        # Post'u çözülmüş olarak işaretleyin ve doğru yorumu kaydedin
        post.is_solved = True
        post.solved_comment = comment
        post.save()
        print("DEBUG: Post marked as solved successfully")  # Debugging

        # Çözüm işaretlendiğinde yorumu güncelleyin
        comment.is_solved = True
        comment.save()

        return JsonResponse({
            'post_is_solved': post.is_solved,
            'solved_comment_id': comment.id,
            'solved_comment_text': comment.text,
            'success': True,
        })
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


@login_required
def unmark_as_solved(request, post_id):
    print("Unmark Called")  # Debug log
    print(f"Request Method: {request.method}, Post ID: {post_id}")
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        print(f"Post Found: {post.id}, Solved Status: {post.is_solved}")

        if request.user != post.user:
            print(f"Unauthorized Attempt by User: {request.user.username}")
            return JsonResponse({'error': 'You are not authorized to unmark this post as solved.'}, status=403)

        post.is_solved = False
        post.solved_comment = None
        post.save()
        print(f"Post Updated: Solved Status: {post.is_solved}")

        return JsonResponse({'post_is_solved': post.is_solved})
    print("Invalid Request Method")
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


@login_required
def bookmark_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)

        # Check if already bookmarked
        if Bookmark.objects.filter(user=request.user, comment=comment).exists():
            return JsonResponse({'success': False, 'message': 'Already bookmarked.'})

        # Create bookmark
        Bookmark.objects.create(user=request.user, comment=comment)
        return JsonResponse({'success': True, 'action': 'bookmarked', 'comment_id': comment.id})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required
def unbookmark_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)

        # Check if bookmark exists
        if not Bookmark.objects.filter(user=request.user, comment=comment).exists():
            return JsonResponse({'success': False, 'message': 'Not bookmarked.'})

        # Delete bookmark
        Bookmark.objects.filter(user=request.user, comment=comment).delete()
        return JsonResponse({'success': True, 'action': 'unbookmarked', 'comment_id': comment.id})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)




@login_required
@never_cache
def post_creation(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                request.session['unsaved_post'] = form.cleaned_data

                # Tags işlemi
                new_tags = form.cleaned_data.get('tags', '').strip()
                post.tags = ', '.join([tag.strip() for tag in new_tags.split(',') if tag.strip()])

                # Dynamically handle all fields in form.cleaned_data
                for field, value in form.cleaned_data.items():
                    if value is not None:  # Only set fields with non-None values
                        setattr(post, field, value)

                # Dinamik alanları formdan çek
                unit_fields = ['width_unit', 'height_unit', 'length_unit', 'weight_unit', 'price_unit']
                for unit_field in unit_fields:
                    setattr(post, unit_field, form.cleaned_data.get(unit_field))
                

                if 'object_image' in request.FILES:
                    print("Object Image Detected in Request Files")  # Debugging Log
                else:
                    print("Object Image NOT Found in Request Files")  # Debugging Log

                post.object_image = request.FILES['object_image']
                print(f"Object Image: {post.object_image}")  # Debugging Log

                post.save()
                print(f"Image uploaded to: {post.object_image.url}")
                print(f"Tags: {post.tags}")
                del request.session['unsaved_post']  # Clear session if successfully saved
                messages.success(request, "Post created successfully!")
                return redirect('post_detail', post_id=post.id)
            else:
                # Form hatalarını yakala ve mesaj olarak kullanıcıya göster
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        except Exception as e:
            messages.error(request, f"An error occurred while creating the post: {str(e)}")
            print(f"Error in post creation: {str(e)}")  # Debugging log
    else:
        # On GET request, check if there are unsaved changes
        unsaved_post = request.session.pop('unsaved_post', None)
        form = PostForm(initial=unsaved_post) if unsaved_post else PostForm()

    return render(request, 'postCreation.html', {'form': form})



def fetch_wikidata(request):
    try:
        tags_param = request.GET.get('tags', '').strip()
        if not tags_param:
            return JsonResponse({'error': 'No tags provided.'}, status=400)
        
        tags = [tags_param.strip()] if ',' not in tags_param else [
            tag.strip() for tag in tags_param.strip("[]").split(',') if tag.strip()
        ]
        
        all_results = {}
        for tag in tags:
            results = fetch_wikidata_tags(tag)
            if results:
                all_results[tag] = [
                    {'qNumber': res[0].split('/')[-1].lstrip('Q'), 'label': res[1], 'description': res[2]}
                    for res in results
                ]
        return JsonResponse({'results': all_results})
    except Exception as e:
        return JsonResponse({'error': f"Error: {str(e)}"}, status=500)




@login_required
@never_cache
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('post_detail', post_id=post.id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        replace_image = request.POST.get('replace_image') == 'true'
        if form.is_valid():
            updated_post = form.save(commit=False)

            # Update current and changed fields
            for field in form.cleaned_data:
                if form.cleaned_data[field] is not None:
                    setattr(updated_post, field, form.cleaned_data[field])

            # Tags işlemi
            new_tags = form.cleaned_data.get('tags', '').strip()
            updated_post.tags = ', '.join([tag.strip() for tag in new_tags.split(',') if tag.strip()])

            # Dynamically update fields and units
            updated_post.width_unit = form.cleaned_data.get('width_unit', post.width_unit)
            updated_post.height_unit = form.cleaned_data.get('height_unit', post.height_unit)
            updated_post.length_unit = form.cleaned_data.get('length_unit', post.length_unit)
            updated_post.weight_unit = form.cleaned_data.get('weight_unit', post.weight_unit)
            updated_post.price_unit = form.cleaned_data.get('price_unit', post.price_unit)

            # Handle image replacement logic
            if replace_image:
                if post.object_image:
                    try:
                        post.object_image.open()
                        post.object_image.delete(save=False)
                        post.object_image.close()
                    except Exception as e:
                        messages.error(request, f"Error deleting image: {str(e)}")
                updated_post.object_image = request.FILES.get('object_image')

            updated_post.save()
            messages.success(request, "Post updated successfully!")
            return redirect('post_detail', post_id=post.id)
        else:
            messages.error(request, "Form validation failed.")
    else:
        form = PostForm(instance=post)

    existing_tags = post.tags.split(',') if post.tags else []
    return render(request, 'editPost.html', {'form': form, 'post': post, 'existing_tags': existing_tags})


def basic_search(request):
    query = request.GET.get("query", "").strip()
    if query:
        # Filter titles by partial matches (case-insensitive)
        posts = Post.objects.filter(title__icontains=query)
    else:
        posts = Post.objects.none()  # Return no results if the query is empty

    return render(request, 'searchResults.html', {
        'posts': posts,
        'query': query,
        'method': 'basic',  # Indicate this is a basic search
    })




def advanced_search(request):
    filters = {}
    print("Advanced Search Called")
    # Title Filter
    query = request.GET.get("title", "").strip()
    if query:
        filters["title__icontains"] = query

    # Price Range
    if request.GET.get("min_price"):
        filters["price__gte"] = request.GET["min_price"]
    if request.GET.get("max_price"):
        filters["price__lte"] = request.GET["max_price"]

     # Tags Filter
    if request.GET.get("tags"):
        tags = request.GET["tags"].split(",")
        q_numbers = []
        for tag in tags:
            q_number, _ = fetch_wikidata_info(tag.strip())
            if q_number:  # Only add if q_number is valid
                q_numbers.append(q_number)
        if q_numbers:
            filters["tags__icontains"] = ",".join(q_numbers)

    # Additional Filters
    if request.GET.get("color"):
        filters["color__icontains"] = request.GET["color"]
    if request.GET.get("material"):
        filters["material__icontains"] = request.GET["material"]
    if request.GET.get("volume"):
        filters["volume__icontains"] = request.GET["volume"]
    if request.GET.get("width"):
        filters["width__icontains"] = request.GET["width"]
    if request.GET.get("height"):
        filters["height__icontains"] = request.GET["height"]
    if request.GET.get("length"):
        filters["length__icontains"] = request.GET["length"]
    if request.GET.get("weight"):
        filters["weight__icontains"] = request.GET["weight"]
    if request.GET.get("condition"):
        filters["condition__icontains"] = request.GET["condition"]
    if request.GET.get("shape"):
        filters["shape__icontains"] = request.GET["shape"]
    if request.GET.get("physical_state"):
        filters["physical_state__icontains"] = request.GET["physical_state"]
    if request.GET.get("sound"):
        filters["sound__icontains"] = request.GET["sound"]
    if request.GET.get("taste"):
        filters["taste__icontains"] = request.GET["taste"]
    if request.GET.get("smell"):
        filters["smell__icontains"] = request.GET["smell"]
    if request.GET.get("location"):
        filters["location__icontains"] = request.GET["location"]
    if request.GET.get("markings"):
        filters["markings__icontains"] = request.GET["markings"]
    if request.GET.get("historical_context"):
        filters["historical_context__icontains"] = request.GET["historical_context"]
    if request.GET.get("distinctive_features"):
        filters["distinctive_features__icontains"] = request.GET["distinctive_features"]

    # Query the database
    posts = Post.objects.filter(**filters).distinct().order_by('-created_at')

    # Sorting
    # Handle sorting
    sort_by = request.GET.get("sort_by", "none")  # Default to "none"
    if sort_by == "date":
        posts = posts.order_by("-created_at")
    elif sort_by == "title":
        posts = posts.order_by("title")
    elif sort_by == "solved":
        posts = posts.order_by("-is_solved")
    elif sort_by == "upvotes":
        posts = posts.order_by("-upvotes")
    elif sort_by == "comments":
        posts = posts.annotate(comment_count=Count("comments")).order_by("-comment_count")
    # If "None" is selected, do not apply any sorting
    # else:
    # No ordering applied

    return render(request, 'searchResults.html', {
        'posts': posts,
        'query': query,
        'sort_by': sort_by,
        'method': 'advanced',
    })

