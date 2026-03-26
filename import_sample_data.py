"""
示例电影数据导入脚本
用于填充数据库中的电影数据
"""

import os
import sys
import django
from pathlib import Path

# 设置Django环境
sys.path.insert(0, str(Path(__file__).parent.absolute()))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommendation.settings')
django.setup()

from core.models import Movie, Genre, Rating, User
from django.contrib.auth.models import User as AuthUser
import random
from datetime import datetime, date

def create_sample_data():
    """创建示例数据"""
    print("开始创建示例数据...")
    
    # 创建电影类型
    genres_data = [
        {'name': '剧情', 'description': '剧情类电影'},
        {'name': '喜剧', 'description': '喜剧类电影'},
        {'name': '动作', 'description': '动作类电影'},
        {'name': '爱情', 'description': '爱情类电影'},
        {'name': '科幻', 'description': '科幻类电影'},
        {'name': '恐怖', 'description': '恐怖类电影'},
        {'name': '悬疑', 'description': '悬疑类电影'},
        {'name': '动画', 'description': '动画类电影'},
        {'name': '冒险', 'description': '冒险类电影'},
        {'name': '犯罪', 'description': '犯罪类电影'},
    ]
    
    genres = {}
    for genre_info in genres_data:
        genre, created = Genre.objects.get_or_create(
            name=genre_info['name'],
            defaults={'description': genre_info['description']}
        )
        genres[genre.name] = genre
        print(f"创建类型: {genre.name}")
    
    # 示例电影数据
    movies_data = [
        {
            'title': '肖申克的救赎',
            'original_title': 'The Shawshank Redemption',
            'directors': '弗兰克·德拉邦特',
            'actors': '蒂姆·罗宾斯,摩根·弗里曼,鲍勃·冈顿',
            'genres': ['剧情', '犯罪'],
            'release_date': date(1994, 9, 23),
            'duration': 142,
            'country': '美国',
            'language': '英语',
            'plot': '讲述了银行家安迪·杜弗雷斯被冤枉杀害妻子和她的情人，被判终身监禁，在肖申克监狱中通过自己的智慧和毅力最终成功越狱的故事。',
            'douban_rating': 9.7,
            'douban_votes': 2500000,
            'imdb_rating': 9.3,
            'tags': '经典,励志,人性',
            'year': 1994
        },
        {
            'title': '这个杀手不太冷',
            'original_title': 'Léon: The Professional',
            'directors': '吕克·贝松',
            'actors': '让·雷诺,娜塔莉·波特曼,加里·奥德曼',
            'genres': ['剧情', '动作', '犯罪'],
            'release_date': date(1994, 9, 14),
            'duration': 110,
            'country': '法国',
            'language': '英语',
            'plot': '讲述了一名职业杀手与一个小女孩的感人故事。',
            'douban_rating': 9.4,
            'douban_votes': 1900000,
            'imdb_rating': 8.5,
            'tags': '经典,温情,动作',
            'year': 1994
        },
        {
            'title': '泰坦尼克号',
            'original_title': 'Titanic',
            'directors': '詹姆斯·卡梅隆',
            'actors': '莱昂纳多·迪卡普里奥,凯特·温丝莱特,比利·赞恩',
            'genres': ['剧情', '爱情', '灾难'],
            'release_date': date(1997, 12, 19),
            'duration': 194,
            'country': '美国',
            'language': '英语',
            'plot': '讲述了穷画家杰克和贵族女露丝在泰坦尼克号邮轮上相识相爱的故事。',
            'douban_rating': 9.4,
            'douban_votes': 1700000,
            'imdb_rating': 7.9,
            'tags': '爱情,灾难,经典',
            'year': 1997
        },
        {
            'title': '盗梦空间',
            'original_title': 'Inception',
            'directors': '克里斯托弗·诺兰',
            'actors': '莱昂纳多·迪卡普里奥,玛丽昂·歌迪亚,渡边谦',
            'genres': ['剧情', '科幻', '悬疑'],
            'release_date': date(2010, 9, 1),
            'duration': 148,
            'country': '美国',
            'language': '英语',
            'plot': '讲述了一群能够进入他人梦境窃取秘密的盗梦者的故事。',
            'douban_rating': 9.3,
            'douban_votes': 1600000,
            'imdb_rating': 8.8,
            'tags': '科幻,悬疑,梦境',
            'year': 2010
        },
        {
            'title': '千与千寻',
            'original_title': '千と千尋の神隠し',
            'directors': '宫崎骏',
            'actors': '柊瑠美,入野自由,夏木真理',
            'genres': ['剧情', '动画', '奇幻'],
            'release_date': date(2001, 7, 20),
            'duration': 125,
            'country': '日本',
            'language': '日语',
            'plot': '讲述了小女孩千寻在神秘世界中冒险的故事。',
            'douban_rating': 9.4,
            'douban_votes': 1800000,
            'imdb_rating': 8.6,
            'tags': '动画,奇幻,宫崎骏',
            'year': 2001
        },
        # 可以继续添加更多电影...
    ]
    
    # 创建电影
    for movie_info in movies_data:
        movie, created = Movie.objects.get_or_create(
            title=movie_info['title'],
            defaults={
                'original_title': movie_info['original_title'],
                'directors': movie_info['directors'],
                'actors': movie_info['actors'],
                'release_date': movie_info['release_date'],
                'duration': movie_info['duration'],
                'country': movie_info['country'],
                'language': movie_info['language'],
                'plot': movie_info['plot'],
                'douban_rating': movie_info['douban_rating'],
                'douban_votes': movie_info['douban_votes'],
                'imdb_rating': movie_info['imdb_rating'],
                'tags': movie_info['tags'],
                'year': movie_info['year']
            }
        )
        
        # 添加类型
        for genre_name in movie_info['genres']:
            if genre_name in genres:
                movie.genres.add(genres[genre_name])
        
        print(f"创建电影: {movie.title}")
    
    # 创建测试用户和评分
    print("创建测试用户和评分...")
    
    # 创建测试用户
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'password': 'testpassword123',
            'nickname': '测试用户'
        }
    )
    if created:
        test_user.set_password('testpassword123')
        test_user.save()
        print("创建测试用户: testuser")
    
    # 为电影添加一些随机评分
    all_movies = Movie.objects.all()
    for movie in all_movies:
        # 为测试用户添加评分
        rating, created = Rating.objects.get_or_create(
            user=test_user,
            movie=movie,
            defaults={'score': round(random.uniform(7.0, 10.0), 1)}
        )
        if created:
            print(f"为用户 {test_user.username} 添加对 {movie.title} 的评分: {rating.score}")
    
    print("示例数据导入完成！")
    print(f"测试用户: testuser")
    print(f"密码: testpassword123")

if __name__ == "__main__":
    create_sample_data()
