"""
核心数据模型
包括用户、电影、评分、评论、收藏等
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """自定义用户模型"""
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
    ]
    
    nickname = models.CharField('昵称', max_length=50, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES, blank=True)
    birth_date = models.DateField('出生日期', null=True, blank=True)
    phone = models.CharField('手机号', max_length=11, blank=True)
    bio = models.TextField('个人简介', max_length=500, blank=True)
    preferences = models.JSONField('偏好设置', default=dict, blank=True)
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return self.username


class Genre(models.Model):
    """电影类型"""
    name = models.CharField('类型名称', max_length=20, unique=True)
    description = models.TextField('类型描述', max_length=200, blank=True)
    
    class Meta:
        verbose_name = '电影类型'
        verbose_name_plural = '电影类型'
    
    def __str__(self):
        return self.name


class Movie(models.Model):
    """电影信息"""
    title = models.CharField('电影标题', max_length=200)
    original_title = models.CharField('原始标题', max_length=200, blank=True)
    directors = models.CharField('导演', max_length=200, blank=True)
    actors = models.TextField('演员', max_length=1000, blank=True)
    genres = models.ManyToManyField(Genre, verbose_name='类型', blank=True)
    release_date = models.DateField('上映日期', null=True, blank=True)
    duration = models.PositiveIntegerField('片长(分钟)', null=True, blank=True)
    country = models.CharField('国家/地区', max_length=50, blank=True)
    language = models.CharField('语言', max_length=50, blank=True)
    plot = models.TextField('剧情简介', max_length=2000, blank=True)
    poster = models.ImageField('海报', upload_to='posters/', blank=True, null=True)
    poster_url = models.URLField('海报URL', blank=True)
    douban_id = models.CharField('豆瓣ID', max_length=20, unique=True, blank=True, null=True)
    douban_rating = models.FloatField('豆瓣评分', null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    douban_votes = models.PositiveIntegerField('评分人数', default=0)
    imdb_rating = models.FloatField('IMDB评分', null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    tags = models.CharField('标签', max_length=500, blank=True)
    year = models.PositiveIntegerField('年份', null=True, blank=True)
    
    # 系统字段
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '电影'
        verbose_name_plural = '电影'
        ordering = ['-douban_rating', '-douban_votes']
    
    def __str__(self):
        return f"{self.title} ({self.year})"
    
    @property
    def genre_names(self):
        return ', '.join([genre.name for genre in self.genres.all()])


class Rating(models.Model):
    """用户评分"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='电影')
    score = models.FloatField('评分', validators=[MinValueValidator(0), MaxValueValidator(10)])
    comment = models.TextField('短评', max_length=500, blank=True)
    created_at = models.DateTimeField('评分时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '评分'
        verbose_name_plural = '评分'
        unique_together = ['user', 'movie']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title}: {self.score}"


class Review(models.Model):
    """长评论"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='电影')
    title = models.CharField('评论标题', max_length=200)
    content = models.TextField('评论内容', max_length=5000)
    rating = models.FloatField('评分', validators=[MinValueValidator(0), MaxValueValidator(10)])
    likes = models.PositiveIntegerField('点赞数', default=0)
    is_approved = models.BooleanField('审核通过', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title}: {self.title}"


class Favorite(models.Model):
    """用户收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='电影')
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        unique_together = ['user', 'movie']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} 收藏 {self.movie.title}"


class WatchHistory(models.Model):
    """观看历史"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='电影')
    watched_at = models.DateTimeField('观看时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '观看历史'
        verbose_name_plural = '观看历史'
        ordering = ['-watched_at']
    
    def __str__(self):
        return f"{self.user.username} 观看 {self.movie.title}"


class SearchHistory(models.Model):
    """搜索历史"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', null=True, blank=True)
    keyword = models.CharField('搜索关键词', max_length=100)
    searched_at = models.DateTimeField('搜索时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '搜索历史'
        verbose_name_plural = '搜索历史'
        ordering = ['-searched_at']
    
    def __str__(self):
        return f"{self.keyword} - {self.searched_at}"