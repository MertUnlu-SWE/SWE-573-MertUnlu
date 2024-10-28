from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('index/', views.index, name='index'),
    path('postCreation/', views.post_creation, name='postCreation'),
    path('postDetail/<int:post_id>/', views.post_detail, name='postDetail'),
    path('postCreation/', views.post_creation, name='postCreation'),
    #path('<page>', views.selectedPage)
]