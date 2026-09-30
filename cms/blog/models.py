from django.db import models
from .manager import CustomUserManager
from django.contrib.auth.models import AbstractUser,PermissionsMixin
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from django.urls import reverse
# Create your models here.

class CustomUser(AbstractUser,PermissionsMixin):
    TYPE = (
        ('admin', 'Admin'),
        ('user' , 'User'),

    )
    username = models.CharField(max_length=100,unique=True,null=False, blank = False)
    email = models.EmailField(max_length=100,null=False,blank=False,unique=True)
    user_type = models.CharField(choices = TYPE , default='user')
    phone = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','phone']

    objects = CustomUserManager()

    def __str__(self):
        return self.username

class Author(models.Model):
    author = models.OneToOneField(CustomUser,on_delete = models.CASCADE,related_name='author_profile')
    author_pic = models.ImageField(upload_to='photos/',blank=True,null=True)
    author_bio = models.TextField(max_length=100,blank=True) 
    author_social_link = models.URLField(max_length=20,blank=True,null=True) 
    def __str__(self):
        return self.author.username
    
class Category(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS = (
        ("draft","Draft"),
        ("published","Published"),
        ("scheduled","Scheduled"),
    )
    author = models.ForeignKey(Author, on_delete=models.CASCADE,related_name="author_post")
    category= models.ForeignKey(Category, on_delete=models.CASCADE,related_name="cate_posts")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="photos/",null=True,blank=True)
    slug = models.SlugField(unique=True)
    content = RichTextField()
    status = models.CharField(max_length=20,choices=STATUS,default='draft')
    featured = models.BooleanField(blank= False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now= True)
    published_at = models.DateTimeField(blank=True,null=True)
    scheduled_at = models.DateTimeField(blank=True,null=True)
    tags = TaggableManager()
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title[0:20]

class Comment(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="comments")
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="comments")
    email = models.EmailField(blank=True,null=True)
    comment = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Comment by {self.user.username} '

class Subscription(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribe_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Visitor(models.Model):
    ip_address = models.GenericIPAddressField()
    page = models.CharField()
    visited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.ip_address} - {self.page}'