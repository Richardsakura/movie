"""
推荐算法实现
混合推荐：基于内容推荐 + 协同过滤
"""

import numpy as np
from django.db.models import Q, Count, Avg
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from collections import defaultdict
import jieba
import re
from core.models import Movie, Rating, Favorite, WatchHistory


class Recommender:
    """推荐系统核心类"""
    
    def __init__(self):
        self.movies = None
        self.movie_features = None
        self.tfidf_vectorizer = None
        self.user_item_matrix = None
        self.movie_similarity_matrix = None
        
    def preprocess_text(self, text):
        """预处理文本：分词、去停用词"""
        if not text:
            return ''
        
        # 去除标点符号
        text = re.sub(r'[^\u4e00-\u9fff\w\s]', ' ', str(text))
        # 分词
        words = jieba.lcut(text)
        # 过滤停用词（简单示例）
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        words = [word for word in words if word not in stop_words and len(word) > 1]
        
        return ' '.join(words)
    
    def prepare_movie_features(self):
        """准备电影特征"""
        movies = Movie.objects.all()
        self.movies = {movie.id: movie for movie in movies}
        
        features = []
        movie_ids = []
        
        for movie in movies:
            # 组合特征：类型 + 标签 + 剧情简介 + 导演 + 演员
            genres = ' '.join([genre.name for genre in movie.genres.all()])
            tags = movie.tags if movie.tags else ''
            plot = movie.plot if movie.plot else ''
            directors = movie.directors if movie.directors else ''
            actors = movie.actors if movie.actors else ''
            
            combined_text = f"{genres} {tags} {plot} {directors} {actors}"
            processed_text = self.preprocess_text(combined_text)
            features.append(processed_text)
            movie_ids.append(movie.id)
        
        # 使用TF-IDF向量化
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, min_df=2, max_df=0.8)
        self.movie_features = self.tfidf_vectorizer.fit_transform(features)
        self.movie_ids = movie_ids
        
        # 计算电影相似度矩阵
        self.movie_similarity_matrix = cosine_similarity(self.movie_features)
        
        return self.movie_features
    
    def prepare_user_item_matrix(self):
        """准备用户-物品矩阵（基于评分）"""
        # 获取所有评分
        ratings = Rating.objects.all()
        
        # 获取所有用户和电影
        user_ids = set([rating.user_id for rating in ratings])
        movie_ids = set([rating.movie_id for rating in ratings])
        
        # 构建矩阵
        user_index = {user_id: idx for idx, user_id in enumerate(user_ids)}
        movie_index = {movie_id: idx for idx, movie_id in enumerate(movie_ids)}
        
        self.user_item_matrix = np.zeros((len(user_ids), len(movie_ids)))
        
        for rating in ratings:
            user_idx = user_index[rating.user_id]
            movie_idx = movie_index[rating.movie_id]
            self.user_item_matrix[user_idx, movie_idx] = rating.score
        
        self.user_index = user_index
        self.movie_index = movie_index
        self.reverse_movie_index = {v: k for k, v in movie_index.items()}
        
        return self.user_item_matrix
    
    def get_user_similarity_matrix(self):
        """计算用户相似度矩阵"""
        if self.user_item_matrix is None:
            self.prepare_user_item_matrix()
        
        # 填充零值（简单均值填充）
        user_mean_ratings = np.mean(self.user_item_matrix, axis=1, keepdims=True)
        user_item_filled = np.where(self.user_item_matrix > 0, self.user_item_matrix, user_mean_ratings)
        
        # 计算用户相似度
        user_similarity = cosine_similarity(user_item_filled)
        
        return user_similarity
    
    def get_content_based_recommendations(self, movie_ids, top_n=10):
        """基于内容的推荐"""
        if self.movie_similarity_matrix is None:
            self.prepare_movie_features()
        
        # 获取目标电影的索引
        movie_indices = []
        valid_movie_ids = []
        for movie_id in movie_ids:
            try:
                idx = self.movie_ids.index(movie_id)
                movie_indices.append(idx)
                valid_movie_ids.append(movie_id)
            except ValueError:
                continue
        
        if not movie_indices:
            return []
        
        # 计算相似度得分
        similarity_scores = np.zeros(len(self.movie_ids))
        for idx in movie_indices:
            similarity_scores += self.movie_similarity_matrix[idx]
        
        # 归一化
        similarity_scores = similarity_scores / len(movie_indices)
        
        # 排除已经看过的电影
        for idx in movie_indices:
            similarity_scores[idx] = -1
        
        # 获取top_n推荐
        top_indices = np.argsort(similarity_scores)[::-1][:top_n]
        
        recommendations = []
        for idx in top_indices:
            if similarity_scores[idx] > 0:
                movie_id = self.movie_ids[idx]
                movie = self.movies.get(movie_id)
                if movie:
                    recommendations.append(movie)
        
        return recommendations
    
    def get_collaborative_filtering_recommendations(self, user_id, top_n=10):
        """协同过滤推荐"""
        if self.user_item_matrix is None:
            self.prepare_user_item_matrix()
        
        # 获取用户索引
        if user_id not in self.user_index:
            return []
        
        user_idx = self.user_index[user_id]
        user_similarity = self.get_user_similarity_matrix()
        
        # 获取相似用户
        similar_users = np.argsort(user_similarity[user_idx])[::-1][1:11]  # 排除自己，取前10个相似用户
        
        # 预测用户对未评分电影的评分
        user_ratings = self.user_item_matrix[user_idx]
        predicted_ratings = np.zeros_like(user_ratings)
        
        for movie_idx in range(len(user_ratings)):
            if user_ratings[movie_idx] == 0:  # 用户未评分的电影
                similarity_sum = 0
                rating_sum = 0
                
                for sim_user_idx in similar_users:
                    sim_rating = self.user_item_matrix[sim_user_idx, movie_idx]
                    if sim_rating > 0:
                        similarity = user_similarity[user_idx, sim_user_idx]
                        rating_sum += similarity * sim_rating
                        similarity_sum += similarity
                
                if similarity_sum > 0:
                    predicted_ratings[movie_idx] = rating_sum / similarity_sum
        
        # 获取top_n推荐
        recommended_indices = np.argsort(predicted_ratings)[::-1][:top_n]
        
        recommendations = []
        for idx in recommended_indices:
            if predicted_ratings[idx] > 0:
                movie_id = self.reverse_movie_index[idx]
                movie = self.movies.get(movie_id)
                if movie:
                    recommendations.append(movie)
        
        return recommendations
    
    def get_hybrid_recommendations(self, user, top_n=10):
        """混合推荐算法"""
        # 获取用户行为数据
        user_ratings = Rating.objects.filter(user=user).values_list('movie_id', flat=True)
        user_favorites = Favorite.objects.filter(user=user).values_list('movie_id', flat=True)
        user_watched = WatchHistory.objects.filter(user=user).values_list('movie_id', flat=True)
        
        user_interacted_movies = list(set(list(user_ratings) + list(user_favorites) + list(user_watched)))
        
        # 如果用户没有历史行为，返回热门电影
        if not user_interacted_movies:
            return Movie.objects.order_by('-douban_rating', '-douban_votes')[:top_n]
        
        # 基于内容的推荐（权重0.6）
        content_recs = self.get_content_based_recommendations(user_interacted_movies, top_n=top_n*2)
        
        # 协同过滤推荐（权重0.4）
        cf_recs = self.get_collaborative_filtering_recommendations(user.id, top_n=top_n*2)
        
        # 合并推荐结果
        movie_scores = defaultdict(float)
        
        # 内容推荐得分
        for i, movie in enumerate(content_recs):
            score = 0.6 * (1.0 - i / len(content_recs))  # 排名越靠前，得分越高
            movie_scores[movie.id] += score
        
        # 协同过滤得分
        for i, movie in enumerate(cf_recs):
            score = 0.4 * (1.0 - i / len(cf_recs))
            movie_scores[movie.id] += score
        
        # 排除用户已经交互过的电影
        for movie_id in user_interacted_movies:
            if movie_id in movie_scores:
                del movie_scores[movie_id]
        
        # 按得分排序
        sorted_movie_ids = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        # 获取电影对象
        recommended_movies = []
        for movie_id, score in sorted_movie_ids:
            try:
                movie = Movie.objects.get(id=movie_id)
                recommended_movies.append(movie)
            except Movie.DoesNotExist:
                continue
        
        # 如果推荐结果不足，用热门电影补充
        if len(recommended_movies) < top_n:
            popular_movies = Movie.objects.exclude(id__in=user_interacted_movies)\
                .order_by('-douban_rating', '-douban_votes')[:top_n - len(recommended_movies)]
            recommended_movies.extend(popular_movies)
        
        return recommended_movies


# 全局推荐器实例
_recommender = None

def get_recommender():
    """获取推荐器实例（单例模式）"""
    global _recommender
    if _recommender is None:
        _recommender = Recommender()
    return _recommender

def get_recommendations(user, limit=10):
    """获取用户推荐"""
    recommender = get_recommender()
    return recommender.get_hybrid_recommendations(user, top_n=limit)

if __name__ == '__main__':
    # 测试推荐算法
    from core.models import User
    import django
    django.setup()
    
    # 获取一个测试用户
    try:
        user = User.objects.first()
        if user:
            recommender = Recommender()
            recommendations = recommender.get_hybrid_recommendations(user, top_n=10)
            print(f"为用户 {user.username} 的推荐结果：")
            for i, movie in enumerate(recommendations, 1):
                print(f"{i}. {movie.title} ({movie.year}) - {movie.douban_rating:.1f}")
        else:
            print("没有找到用户，请先创建用户。")
    except Exception as e:
        print(f"错误：{e}")