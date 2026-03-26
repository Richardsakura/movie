"""
表单定义
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Rating, Review


class UserRegistrationForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(label='邮箱', required=True)
    nickname = forms.CharField(label='昵称', max_length=50, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'nickname', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 自定义字段标签和帮助文本
        self.fields['username'].label = '用户名'
        self.fields['password1'].label = '密码'
        self.fields['password2'].label = '确认密码'
        
        for fieldname in ['username', 'email', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.nickname = self.cleaned_data['nickname'] or user.username
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """用户登录表单"""
    username = forms.CharField(label='用户名/邮箱')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': '请输入用户名或邮箱'})
        self.fields['password'].widget.attrs.update({'placeholder': '请输入密码'})
        
        for fieldname in ['username', 'password']:
            self.fields[fieldname].help_text = None


class RatingForm(forms.ModelForm):
    """评分表单"""
    score = forms.FloatField(
        label='评分',
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={'step': '0.5', 'min': '0', 'max': '10'})
    )
    
    class Meta:
        model = Rating
        fields = ('score', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': '写下你的短评（可选）'}),
        }
        labels = {
            'comment': '短评',
        }


class ReviewForm(forms.ModelForm):
    """评论表单"""
    rating = forms.FloatField(
        label='评分',
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={'step': '0.5', 'min': '0', 'max': '10'})
    )
    
    class Meta:
        model = Review
        fields = ('title', 'content', 'rating')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': '评论标题'}),
            'content': forms.Textarea(attrs={'rows': 10, 'placeholder': '写下你的详细评论...'}),
        }
        labels = {
            'title': '标题',
            'content': '内容',
            'rating': '评分',
        }


class ProfileForm(forms.ModelForm):
    """个人资料表单"""
    class Meta:
        model = User
        fields = ('nickname', 'email', 'avatar', 'gender', 'birth_date', 'phone', 'bio')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'nickname': '昵称',
            'email': '邮箱',
            'avatar': '头像',
            'gender': '性别',
            'birth_date': '出生日期',
            'phone': '手机号',
            'bio': '个人简介',
        }