"""
核心视图函数
处理用户注册、登录、电影浏览、搜索、评分、评论等功能
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Movie, Rating, Review, Favorite, WatchHistory, SearchHistory, Genre
from .forms import UserRegistrationForm, UserLoginForm, RatingForm, ReviewForm


def index(request):
    """首页 - 电影推荐和热门电影"""
    # 热门电影
    popular_movies = Movie.objects.annotate(
        avg_rating=Avg('rating__score')
    ).order_by('-douban_rating', '-douban_votes')[:12]

    # 最新电影
    new_movies = Movie.objects.order_by('-release_date')[:12]

    # 所有类型
    genres = Genre.objects.all()

    context = {
        'popular_movies': popular_movies,
        'new_movies': new_movies,
        'genres': genres,
    }

    # 如果用户已登录，添加个性化推荐
    if request.user.is_authenticated:
        from recommender.recommendation import get_recommendations
        recommended_movies = get_recommendations(request.user, limit=6)
        context['recommended_movies'] = recommended_movies

    return render(request, 'core/index.html', context)


def movie_list(request):
    """电影列表页"""
    movies = Movie.objects.all()

    # 搜索
    query = request.GET.get('q')
    if query:
        movies = movies.filter(
            Q(title__icontains=query) |
            Q(original_title__icontains=query) |
            Q(directors__icontains=query) |
            Q(actors__icontains=query) |
            Q(plot__icontains=query)
        )
        # 记录搜索历史
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, keyword=query)

    # 类型过滤
    genre_id = request.GET.get('genre')
    if genre_id:
        movies = movies.filter(genres__id=genre_id)

    # 年份过滤
    year = request.GET.get('year')
    if year:
        movies = movies.filter(year=year)

    # 排序
    sort_by = request.GET.get('sort', 'rating')
    if sort_by == 'rating':
        movies = movies.order_by('-douban_rating', '-douban_votes')
    elif sort_by == 'date':
        movies = movies.order_by('-release_date')
    elif sort_by == 'title':
        movies = movies.order_by('title')

    # 分页
    paginator = Paginator(movies, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    genres = Genre.objects.all()
    years = Movie.objects.values_list('year', flat=True).distinct().order_by('-year')

    context = {
        'page_obj': page_obj,
        'genres': genres,
        'years': years,
        'query': query,
        'selected_genre': genre_id,
        'selected_year': year,
        'sort_by': sort_by,
    }

    return render(request, 'core/movie_list.html', context)


def movie_detail(request, movie_id):
    """电影详情页"""
    movie = get_object_or_404(Movie, id=movie_id)

    # 记录观看历史
    if request.user.is_authenticated:
        WatchHistory.objects.get_or_create(user=request.user, movie=movie)

    # 评分信息
    ratings = Rating.objects.filter(movie=movie).select_related('user')
    rating_stats = ratings.aggregate(
        avg_score=Avg('score'),
        total_ratings=Count('id')
    )

    # 评论
    reviews = Review.objects.filter(
        movie=movie, is_approved=True
    ).select_related('user').order_by('-created_at')

    # 收藏 & 自己的评分
    is_favorited = False
    user_rating = None
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, movie=movie).exists()
        user_rating = Rating.objects.filter(user=request.user, movie=movie).first()

    context = {
        'movie': movie,
        'ratings': ratings[:10],
        'rating_stats': rating_stats,
        'reviews': reviews[:5],
        'is_favorited': is_favorited,
        'user_rating': user_rating,
        'rating_form': RatingForm(),
    }

    return render(request, 'core/movie_detail.html', context)


def register(request):
    """用户注册"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('index')
    else:
        form = UserRegistrationForm()

    return render(request, 'core/register.html', {'form': form})


def user_login(request):
    """用户登录"""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # 支持用邮箱登录的话，可以再扩展；先用用户名
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '登录成功！')
                return redirect('index')
            else:
                messages.error(request, '用户名或密码错误')
    else:
        form = UserLoginForm()

    return render(request, 'core/login.html', {'form': form})


def user_logout(request):
    """用户登出"""
    logout(request)
    messages.success(request, '已成功登出。')
    return redirect('index')


@login_required
def profile(request):
    """用户个人中心"""
    user = request.user

    ratings = Rating.objects.filter(user=user).select_related('movie').order_by('-created_at')
    favorites = Favorite.objects.filter(user=user).select_related('movie').order_by('-created_at')
    watch_history = WatchHistory.objects.filter(user=user).select_related('movie').order_by('-watched_at')[:20]

    context = {
        'ratings': ratings,
        'favorites': favorites,
        'watch_history': watch_history,
    }
    return render(request, 'core/profile.html', context)


@login_required
@require_POST
def rate_movie(request, movie_id):
    """用户评分"""
    movie = get_object_or_404(Movie, id=movie_id)

    form = RatingForm(request.POST)
    if form.is_valid():
        score = form.cleaned_data['score']
        comment = form.cleaned_data.get('comment', '')

        Rating.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={'score': score, 'comment': comment}
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'score': score})

        messages.success(request, '评分成功！')
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors})
        messages.error(request, '评分失败，请检查输入。')

    return redirect('movie_detail', movie_id=movie_id)


@login_required
@require_POST
def toggle_favorite(request, movie_id):
    """收藏/取消收藏"""
    movie = get_object_or_404(Movie, id=movie_id)

    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        favorite.delete()
        is_favorited = False
    else:
        is_favorited = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'is_favorited': is_favorited})

    return redirect('movie_detail', movie_id=movie_id)


@login_required
def add_review(request, movie_id):
    """添加评论"""
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.save()
            messages.success(request, '评论发表成功！')
            return redirect('movie_detail', movie_id=movie_id)
    else:
        form = ReviewForm()

    context = {
        'movie': movie,
        'form': form,
    }
    return render(request, 'core/add_review.html', context)


def genre_list(request):
    """类型列表"""
    genres = Genre.objects.annotate(movie_count=Count('movie')).order_by('-movie_count')
    return render(request, 'core/genre_list.html', {'genres': genres})


def genre_detail(request, genre_id):
    """类型详情"""
    genre = get_object_or_404(Genre, id=genre_id)
    movies = Movie.objects.filter(genres=genre).order_by('-douban_rating', '-douban_votes')

    paginator = Paginator(movies, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'genre': genre,
        'page_obj': page_obj,
    }
    return render(request, 'core/genre_detail.html', context)