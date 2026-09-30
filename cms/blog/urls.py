from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import PostSitemap
sitemaps = {
    "posts": PostSitemap,
}

urlpatterns = [
    path("", views.HomeView.as_view(), name='home'),
    path("register/", views.RegisterView.as_view(), name='register'),
    path("login/", views.LoginView.as_view(), name='login'),
    path("logout/", views.LogoutView.as_view(), name='logout'),
    path("write/", views.PostWriteView.as_view(), name='write'),
    path("post_detail/<slug:slug>/", views.PostDetailView.as_view(), name='post_detail'),
    path("category/<slug:slug>/",views.CategoryView.as_view(),name="category"),
    path("subscribe/",views.SubscriptionView.as_view(),name="subscribe"),
    path("editPost/<slug:slug>/",views.EditPostView.as_view(), name='post_edit'),
    path("deletePost/<slug:slug>/",views.DeletePostView.as_view(), name='post_delete'),
    path("comment/<slug:slug>/",views.CommentCreateView.as_view(),name="add_comment" ),
    path("commentsModeration/",views.CommentModerationView.as_view(),name="comment_moderation"),
    path("approve/<int:pk>/",views.ApproveCommentView.as_view(),name="approve_comment"),
    path("reject/<int:pk>/",views.RejectCommentView.as_view(),name="reject_comment"),
    path("tag/<slug:slug>/",views.TagPostView.as_view(),name="tag_posts"),
    path("rss/",views.LatestPostsFeed(),name="rss_feed"),
    path("sitemap.xml",sitemap,{"sitemaps": sitemaps},name="sitemap"
),



]