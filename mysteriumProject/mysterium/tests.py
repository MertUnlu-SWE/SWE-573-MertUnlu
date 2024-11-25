from django.test import TestCase, Client
from django.contrib.auth.models import User
from .wikidata_utils import fetch_wikidata_info
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Post, Comment
from pathlib import Path


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass'
        )


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


        

    def test_fetch_wikidata(self):
        response = self.client.get('/fetch_wikidata/', {'tags': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json())  # Ensure results returned

        response = self.client.get('/fetch_wikidata/', {'tags': ''})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())  # Ensure error returned

        
    def test_vote_post(self):
        post = Post.objects.create(title='Test Post', description='Test Description', user=self.user)

        # Login and vote
        self.client.login(username='testuser@example.com', password='testpass')
        response = self.client.post(f'/vote_post/{post.id}/upvote/')
        self.assertEqual(response.status_code, 200)  # Success

        # Check vote count
        post.refresh_from_db()
        self.assertEqual(post.upvotes, 1)



    def test_mark_as_solved(self):
        post = Post.objects.create(title='Test Post', description='Test Description', user=self.user)
        comment = Comment.objects.create(post=post, user=self.user, text='Test Comment')

        # Unauthorized access
        other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='otherpass')
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(f'/mark_as_solved/{post.id}/{comment.id}/')
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Authorized access
        self.client.login(username='testuser@example.com', password='testpass')
        response = self.client.post(f'/mark_as_solved/{post.id}/{comment.id}/')
        self.assertEqual(response.status_code, 200)  # Success



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



class WikidataUtilsTest(TestCase):
    def test_fetch_wikidata_info(self):
        q_number, label = fetch_wikidata_info('Python')
        self.assertIsNotNone(q_number)
        self.assertEqual(label, 'Python')
