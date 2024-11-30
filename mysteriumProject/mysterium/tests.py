from django.test import TestCase
from .backends import EmailBackend
from django.contrib.auth.models import User
from .wikidata_utils import fetch_wikidata_info, fetch_wikidata_tags
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Post, Comment
from .forms import PostForm, CommentForm
from pathlib import Path


class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.other_user = User.objects.create_user(username='otheruser', email='otheruser@example.com', password='otherpass')
        self.post = Post.objects.create(title='Test Post', description='Test Description', user=self.user)
        self.comment = Comment.objects.create(post=self.post, text='Test Comment', user=self.user)

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


    def test_post_creation_view(self):
        self.client.login(username='testuser@example.com', password='testpass')

        image_path = Path(__file__).resolve().parent.parent / \
            "media" / "Images" / "skyDisk.jpg"
        with open(image_path, 'rb') as img:
            image = SimpleUploadedFile(
                name='skyDisk.jpg',
                content=img.read(),
                content_type='image/jpeg'
            )

        response = self.client.post('/postCreation/', {
            'title': 'New Post',
            'description': 'New Description',
            'object_image': image,
        })

        self.assertEqual(response.status_code, 200)  # Ensure success
        self.assertTrue(Post.objects.filter(
            title='New Post').exists())  # Check if created



    def test_post_detail_view(self):
        with open(Path(__file__).resolve().parent.parent / "media" / "Images" / "skyDisk.jpg", 'rb') as img:
            image = SimpleUploadedFile(name='skyDisk.jpg', content=img.read(), content_type='image/jpeg')

        post = Post.objects.create(
            title='Test Post',
            description='Test Description',
            user=self.user,
            object_image=image
        )

        response = self.client.get(f'/post/{post.id}/')
        self.assertEqual(response.status_code, 200)  # Ensure successful access
        self.assertContains(response, 'Test Post')  # Check content


    def test_edit_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(f'/post/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)  # Ensure successful access
        self.assertContains(response, self.post.title)  # Ensure the post title is displayed

        # Submit valid edit form
        response = self.client.post(f'/post/{self.post.id}/edit/', {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'tags': 'Updated, Tags'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful edit
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')
        self.assertEqual(self.post.description, 'Updated Description')

        # Unauthorized edit attempt
        self.client.logout()
        response = self.client.post(f'/post/{self.post.id}/edit/', {
            'title': 'Another Update'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.post.refresh_from_db()
        self.assertNotEqual(self.post.title, 'Another Update')



    def test_fetch_wikidata(self):
        response = self.client.get('/fetch_wikidata/', {'tags': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json())  # Ensure results returned

        response = self.client.get('/fetch_wikidata/', {'tags': ''})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())  # Ensure error returned

        
    def test_vote_post(self):
        post = Post.objects.create(title='Test Post', description='Test Description', user=self.user)

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
        response = self.client.post(f'/post/{self.post.id}/mark_as_solved/comment/{self.comment.id}/')
        print(f"DEBUG: Response for unauthorized access: {response.status_code}")  # Debugging
        self.assertEqual(response.status_code, 403)

        # Authorized access
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(f'/post/{self.post.id}/mark_as_solved/comment/{self.comment.id}/')
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
        self.assertFalse(self.post.is_solved)  # Ensure post is no longer solved


    def test_search_tags(self):
        # Valid query
        response = self.client.get('/search/', {'query': 'Python'})
        self.assertEqual(response.status_code, 200)  # Ensure successful response
        self.assertIn('results', response.json())  # Ensure results returned

        # Invalid or empty query
        response = self.client.get('/search/', {'query': ''})
        self.assertEqual(response.status_code, 200)  # Successful response but no results
        self.assertIn('results', response.json())
        self.assertEqual(len(response.json()['results']), 0)  # Ensure empty results

    

    def test_profile_view(self):
        self.client.login(username='testuser@example.com', password='testpass')
        response = self.client.get('/profile/')

        self.assertEqual(response.status_code, 200)  # Ensure successful access
        self.assertContains(response, 'testuser@example.com')  # Ensure user data displayed

        
    def test_logout_view(self):
        self.client.login(username='testuser@example.com', password='testpass')
        response = self.client.get('/logout/')

        self.assertEqual(response.status_code, 302)  # Redirect expected
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Successfully logged out.')



class EmailBackendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')

    def test_authenticate_success(self):
        backend = EmailBackend()
        user = backend.authenticate(None, username='testuser@example.com', password='testpass')
        self.assertEqual(user, self.user)

    def test_authenticate_failure(self):
        backend = EmailBackend()
        user = backend.authenticate(None, username='wrong@example.com', password='wrongpass')
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
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')

    def test_post_creation(self):
        post = Post.objects.create(title='Test Post', description='Test Description', user=self.user)
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.upvotes, 0)


class CommentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        self.post = Post.objects.create(title='Test Post', description='Test Description', user=self.user)

    def test_comment_creation(self):
        comment = Comment.objects.create(post=self.post, user=self.user, text='Test Comment')
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
