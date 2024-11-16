from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('index/', views.index, name='index'),
    path('postCreation/', views.post_creation, name='postCreation'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),  # Place edit_post before vote_post
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/<str:vote_type>/', views.vote_post, name='vote_post'),
    path('comment/<int:comment_id>/<str:vote_type>/', views.vote_comment, name='vote_comment'),
    path('search/', views.search_tags, name='search_tags'),
    path('fetch_wikidata/', views.fetch_wikidata, name='fetch_wikidata'),
]