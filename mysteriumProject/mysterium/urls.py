from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('index/', views.index, name='index'),
    path('search/basic/', views.basic_search, name='basic_search'),
    path('search/advanced/', views.advanced_search, name='advanced_search'),
    path('postCreation/', views.post_creation, name='postCreation'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),  # Place edit_post before vote_post
    path('post/<int:post_id>/unmark_as_solved/', views.unmark_as_solved, name='unmark_as_solved'),
    path('post/<int:post_id>/<str:vote_type>/', views.vote_post, name='vote_post'),
    path('post/<int:post_id>/mark_as_solved/comment/<int:comment_id>/', views.mark_as_solved, name='mark_as_solved'),
    path('comment/<int:comment_id>/<str:vote_type>/', views.vote_comment, name='vote_comment'),
    path('fetch_wikidata/', views.fetch_wikidata, name='fetch_wikidata'),
]