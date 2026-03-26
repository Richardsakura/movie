"""
核心URL配置
"""

from django.urls import path
from . import views

urlpatterns = [
    # 首页和电影相关
    path('', views.index, name='index'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    
    # 用户认证
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # 用户操作
    path('profile/', views.profile, name='profile'),
    path('movies/<int:movie_id>/rate/', views.rate_movie, name='rate_movie'),
    path('movies/<int:movie_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('movies/<int:movie_id>/review/', views.add_review, name='add_review'),
    
    # 类型相关
    path('genres/', views.genre_list, name='genre_list'),
    path('genres/<int:genre_id>/', views.genre_detail, name='genre_detail'),
]