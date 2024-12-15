from django.test import TestCase
from .backends import EmailBackend
from django.contrib.auth.models import User
from django.db.models import Count
from decimal import Decimal
from .wikidata_utils import fetch_wikidata_info, fetch_wikidata_tags
from unittest.mock import patch
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Post, Comment, Bookmark
from .forms import PostForm, CommentForm
from pathlib import Path


class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpass')
        self.other_user = User.objects.create_user(
            username='otheruser', email='otheruser@example.com', password='otherpass')
        self.post = Post.objects.create(
            title='Test Post', description='Test Description', user=self.user)
        self.comment = Comment.objects.create(
            post=self.post, text='Test Comment', user=self.user)

        print(f"DEBUG: Created Post ID: {self.post.id}, Comment ID: {self.comment.id}")  # Debugging


    def test_register_view(self):
        response = self.client.post('/register/', {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        })

        # Redirect expected on success
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(
            username='newuser').exists())  # Ensure user created


    def test_login_view(self):
        response = self.client.post('/login/', {
            'email': 'testuser@example.com',
            'password': 'testpass'
        })
        # Redirect expected on success
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Successfully logged in.')


    @patch('mysterium.wikidata_utils.fetch_wikidata_info', return_value=("Q12345", "Sample Label"))
    def test_post_creation_view(self, mock_fetch_wikidata_info):
        self.client.login(username='testuser', password='testpass')

        image_path = Path(__file__).resolve().parent.parent / "media" / "Images" / "skyDisk.jpg"
        with open(image_path, 'rb') as img:
            test_image = SimpleUploadedFile(
                name='skyDisk.jpg',
                content=img.read(),
                content_type='image/jpeg'
            )

        # Post data for creating a post
        post_data = {
            'title': 'Test Post Title',
            'description': 'Test Post Description',
            'tags': 'tag1, tag2',
            'price': '123.45',
            'volume': '300 cm³',
            'width': '20 cm',
            'height': '30 cm',
            'length': '40 cm',
            'material': 'Plastic',
            'color': 'Red',
            'object_image': test_image,
        }

        # Make a POST request to create a post
        response = self.client.post('/postCreation/', data=post_data)

        # Verify the response redirects to the post detail page
        self.assertEqual(response.status_code, 302)

        # Verify the post is created in the database
        created_post = Post.objects.get(title='Test Post Title')
        self.assertIsNotNone(created_post)
        self.assertEqual(created_post.description, 'Test Post Description')
        self.assertEqual(created_post.price, Decimal('123.45'))
        self.assertEqual(created_post.material, 'Plastic')
        self.assertEqual(created_post.color, 'Red')
        self.assertEqual(created_post.tags, 'tag1, tag2')

        # Verify the success message
        self.assertRedirects(response, f'/post/{created_post.id}/')



    def test_post_detail_view(self):
        image_path = Path(__file__).resolve().parent.parent / "media" / "Images" / "skyDisk.jpg"
        with open(image_path, 'rb') as img:
            test_image = SimpleUploadedFile(
                name='skyDisk.jpg',
                content=img.read(),
                content_type='image/jpeg'
            )
        self.post.object_image = test_image
        self.post.save()

        response = self.client.get(f'/post/{self.post.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.description)

        self.post.tags = 'tag1, tag2'
        self.post.save()

        response = self.client.get(f'/post/{self.post.id}/')
        self.assertContains(response, 'tag1')
        self.assertContains(response, 'tag2')


    def test_edit_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(f'/post/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)  # Ensure successful access
        # Ensure the post title is displayed
        self.assertContains(response, self.post.title)

        # Submit valid edit form
        response = self.client.post(f'/post/{self.post.id}/edit/', {
            'title': 'Updated Title',
            'description': 'Updated description',
            'tags': 'newtag1, newtag2',
            'price': '99.99',
            'color': 'Blue',
        })

        # Redirect after successful edit
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')
        self.assertEqual(self.post.description, 'Updated description')
        self.assertEqual(self.post.tags.replace(" ", ""), 'newtag1,newtag2')  # Ensure the format includes spaces
        self.assertEqual(self.post.price, Decimal('99.99'))
        self.assertEqual(self.post.color, 'Blue')


    def test_fetch_wikidata(self):
        response = self.client.get('/fetch_wikidata/', {'tags': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json())  # Ensure results returned

        response = self.client.get('/fetch_wikidata/', {'tags': ''})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())  # Ensure error returned


    def test_vote_post(self):
        post = Post.objects.create(
            title='Test Post', description='Test Description', user=self.user)

        self.client.login(username='testuser', password='testpass')
        response = self.client.post(f'/post/{self.post.id}/upvote/')
        print(f"DEBUG: Response for upvote: {response.status_code}")  # Debugging
        self.assertEqual(response.status_code, 200)

        self.post.refresh_from_db()
        print(f"DEBUG: Upvotes after vote: {self.post.upvotes}")  # Debugging
        self.assertEqual(self.post.upvotes, 1)


    def test_mark_as_solved(self):
        # Unauthorized access
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(
            f'/post/{self.post.id}/mark_as_solved/comment/{self.comment.id}/')
        print(f"DEBUG: Response for unauthorized access: {response.status_code}")  # Debugging
        self.assertEqual(response.status_code, 403)

        # Authorized access
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            f'/post/{self.post.id}/mark_as_solved/comment/{self.comment.id}/')
        print(f"DEBUG: Response for authorized access: {response.status_code}")  # Debugging
        self.assertEqual(response.status_code, 200)


    def test_unmark_as_solved(self):
        # Mark post as solved first
        self.post.is_solved = True
        self.post.save()

        # Unauthorized unmark attempt
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(f'/post/{self.post.id}/unmark_as_solved/')
        self.assertEqual(response.status_code, 403)  # Forbidden access
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_solved)  # Ensure post is still solved

        # Authorized unmark attempt
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(f'/post/{self.post.id}/unmark_as_solved/')
        self.assertEqual(response.status_code, 200)  # Success
        self.post.refresh_from_db()
        # Ensure post is no longer solved
        self.assertFalse(self.post.is_solved)


    def test_bookmark_comment(self):
        response = self.client.post(f'/comment/{self.comment.id}/bookmark/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Bookmark.objects.filter(user=self.user, comment=self.comment).exists())


    def test_unbookmark_comment(self):
        Bookmark.objects.create(user=self.user, comment=self.comment)
        response = self.client.post(f'/comment/{self.comment.id}/unbookmark/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Bookmark.objects.filter(user=self.user, comment=self.comment).exists())


    def test_view_bookmarked_comments(self):
        Bookmark.objects.create(user=self.user, comment=self.comment)
        response = self.client.get('/profile/')
        self.assertContains(response, 'Test Comment')


    def test_basic_search(self):
        # Create test data
        user = User.objects.create_user(
            username='searchuser', email='searchuser@example.com', password='searchpass')

        post1 = Post.objects.create(
            title="Mystery Object 1",
            description="A fascinating mystery.",
            user=user,
            is_solved=False,
            upvotes=5
        )
        post2 = Post.objects.create(
            title="A Space Disk?",
            description="A potential alien artifact.",
            user=user,
            is_solved=True,
            upvotes=10
        )
        post3 = Post.objects.create(
            title="Ancient Artifact",
            description="An artifact from ancient times.",
            user=user,
            is_solved=False,
            upvotes=2
        )

        # Test title search
        response = self.client.get('/search/basic/', {'query': 'Mystery'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mystery Object 1")
        self.assertNotContains(response, "A Space Disk?")
        self.assertNotContains(response, "Ancient Artifact")

        # Test sorting by title
        response = self.client.get(
            '/search/basic/', {'query': '', 'sort_by': 'title'})
        self.assertEqual(response.status_code, 200)
        titles = list(post.title for post in response.context['posts'])
        # Ensure titles are sorted alphabetically
        self.assertEqual(titles, sorted(titles))

        # Test sorting by upvotes
        response = self.client.get(
            '/search/basic/', {'query': '', 'sort_by': 'upvotes'})
        self.assertEqual(response.status_code, 200)
        upvotes = list(post.upvotes for post in response.context['posts'])
        # Ensure sorted by upvotes descending
        self.assertEqual(upvotes, sorted(upvotes, reverse=True))

        # Test sorting by solved status
        response = self.client.get(
            '/search/basic/', {'query': '', 'sort_by': 'solved'})
        self.assertEqual(response.status_code, 200)
        solved_status = list(
            post.is_solved for post in response.context['posts'])
        self.assertEqual(solved_status, sorted(
            solved_status, reverse=True))  # Solved posts first

        # Test invalid query
        response = self.client.get('/search/basic/', {'query': 'Nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Mystery Object 1")
        self.assertNotContains(response, "A Space Disk?")
        self.assertNotContains(response, "Ancient Artifact")
        # Ensure no results
        self.assertEqual(len(response.context['posts']), 0)


    def test_profile_view(self):
        # Log in as the test user
        self.client.login(username='testuser', password='testpass')

        # Make a GET request to the profile view
        response = self.client.get('/profile/')

        # Verify the response status
        self.assertEqual(response.status_code, 200)

        # Ensure the correct template is used
        self.assertTemplateUsed(response, 'profile.html')

        # Verify user information is displayed
        self.assertContains(response, 'testuser')  # Username
        self.assertContains(response, self.user.first_name or "")  # First Name
        self.assertContains(response, self.user.last_name or "")  # Last Name

        # Verify the user's posts are displayed
        self.assertContains(response, self.post.title)  # Post title
        self.assertContains(response, self.post.description)  # Post description

        # Ensure only the test user's posts are shown
        self.assertNotContains(response, self.other_user.username)


    def test_logout_view(self):
        self.client.login(username='testuser@example.com', password='testpass')
        response = self.client.get('/logout/')

        self.assertEqual(response.status_code, 302)  # Redirect expected
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Successfully logged out.')


class EmailBackendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpass')

    def test_authenticate_success(self):
        backend = EmailBackend()
        user = backend.authenticate(
            None, username='testuser@example.com', password='testpass')
        self.assertEqual(user, self.user)

    def test_authenticate_failure(self):
        backend = EmailBackend()
        user = backend.authenticate(
            None, username='wrong@example.com', password='wrongpass')
        self.assertIsNone(user)

    def test_get_user(self):
        backend = EmailBackend()
        user = backend.get_user(self.user.id)
        self.assertEqual(user, self.user)


class PostFormTests(TestCase):
    def test_post_form_valid(self):
        form_data = {
            'title': 'Test Post',
            'description': 'This is a test description',
            'tags': 'tag1, tag2'
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_post_form_invalid(self):
        form_data = {}  # Missing required fields
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())


class CommentFormTests(TestCase):
    def test_comment_form_valid(self):
        form_data = {'text': 'This is a test comment'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_invalid(self):
        form_data = {}  # Missing required fields
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())


class PostModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass')

    def test_post_creation(self):
        post = Post.objects.create(
            title='Test Post', description='Test Description', user=self.user)
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.upvotes, 0)


class CommentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass')
        self.post = Post.objects.create(
            title='Test Post', description='Test Description', user=self.user)

    def test_comment_creation(self):
        comment = Comment.objects.create(
            post=self.post, user=self.user, text='Test Comment')
        self.assertEqual(comment.text, 'Test Comment')
        self.assertEqual(comment.upvotes, 0)


class WikidataUtilsTests(TestCase):
    @patch('mysterium.wikidata_utils.SPARQLWrapper.query')
    def test_fetch_wikidata_info_success(self, mock_query):
        # Mock the SPARQL query response
        mock_query.return_value.convert.return_value = {
            'results': {'bindings': [{'item': {'value': 'https://wikidata.org/wiki/Q123'}}]}
        }
        q_number, label = fetch_wikidata_info('Python')
        self.assertEqual(q_number, 'Q123')
        self.assertEqual(label, 'Python')

    @patch('mysterium.wikidata_utils.requests.get')
    def test_fetch_wikidata_tags_success(self, mock_get):
        # Mock the requests.get response
        mock_get.return_value.json.return_value = {
            'search': [{'id': 'Q123', 'label': 'Python'}]
        }
        results = fetch_wikidata_tags('Python')
        self.assertEqual(results[0][1], 'Python')
