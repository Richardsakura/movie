"""
管理员后台配置
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Movie, Genre, Rating, Review, Favorite, WatchHistory, SearchHistory


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'nickname', 'gender', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'gender')
    search_fields = ('username', 'email', 'nickname')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('nickname', 'email', 'avatar', 'gender', 'birth_date', 'phone', 'bio', 'preferences')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'douban_rating', 'douban_votes', 'country')
    list_filter = ('year', 'country')
    search_fields = ('title', 'original_title', 'directors', 'actors')
    filter_horizontal = ('genres',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'original_title', 'year', 'release_date', 'duration', 'country', 'language')
        }),
        ('内容', {
            'fields': ('plot', 'directors', 'actors', 'genres', 'tags')
        }),
        ('评分', {
            'fields': ('douban_id', 'douban_rating', 'douban_votes', 'imdb_rating')
        }),
        ('媒体', {
            'fields': ('poster', 'poster_url')
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'movie__title', 'comment')
    readonly_fields = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'title', 'rating', 'likes', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('user__username', 'movie__title', 'title', 'content')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'movie__title')
    readonly_fields = ('created_at',)


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'watched_at')
    list_filter = ('watched_at',)
    search_fields = ('user__username', 'movie__title')
    readonly_fields = ('watched_at',)


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'keyword', 'searched_at')
    list_filter = ('searched_at',)
    search_fields = ('keyword', 'user__username')
    readonly_fields = ('searched_at',)