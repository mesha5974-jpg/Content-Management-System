from django import forms
from .models import CustomUser,Post,Subscription,Comment,Visitor
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username','email','phone']

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields= [ 
            "category",
            "title",
            "slug",
            "content",
            "image",
            "featured",
            "tags",
        ]

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['email']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
    