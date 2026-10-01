from django.urls import reverse_lazy
from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm,PostForm,SubscriptionForm,CommentForm
from django.views import View
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from .models import Post,Author,Category,Subscription,Comment,Visitor
from django.contrib.syndication.views import Feed
from django.conf import settings
from django.utils.html import strip_tags
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

class RegisterView(View):
    def get(self,request):
      form = RegisterForm()
      return render(request,'register.html',{'form':form})

    def post(self,request):
       form = RegisterForm(request.POST)
       if form.is_valid():
          user = form.save(commit= False)
          user.user_type = 'user'
          user.save()
          Author.objects.create(author=user)
          login(request,user,backend='django.contrib.auth.backends.Modelbackend')
          return redirect('home')
       else:
          messages.error(request,'Please Fulfill Requirements')
          return render(request,'register.html',{'form': form})

class LoginView(View):
   def get(self,request):
      form = LoginForm()
      return render(request,'login.html',{'form':form})
   def post(self,request):
      form = LoginForm(request.POST)
      if form.is_valid():
         email = form.cleaned_data['email']
         password = form.cleaned_data['password']
         user = authenticate(request,email=email,password=password)
         if user is not None:
            login(request,user)
            return redirect('home')
      return render(request,'login.html',{'form':form})

class LogoutView(View):
   def get(self,request):
      logout(request)
      return redirect('home')
from django.core.mail import send_mail

def notify_mail(post):
   subscribers = Subscription.objects.filter(is_active=True)
   for subscriber in subscribers:
     send_mail (
        subject = f'New post : {post.title}',
        message = (f"A new post has been published on Marginalia.\n\n"
                  f"Title: {post.title}\n\n"
                  f"Read the new post on our blog."
            ),
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list= [subscriber.email],
        fail_silently=False,
     )

class HomeView(ListView):
   model = Post
   template_name = 'home.html'
   context_object_name = "posts"
   ordering = ['-created_at']

   def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        context["visitor_count"] = Visitor.objects.filter(
          visited_at__year=now.year,
          visited_at__month=now.month).count()
        context["featured_post"] = Post.objects.filter(
            featured=True,
            status="published"
        ).order_by("-published_at").first()
        return context

class PostWriteView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "write.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):

        form.instance.author = self.request.user.author_profile

        action = self.request.POST.get("action")

        if action == "published":

            form.instance.status = "published"
            form.instance.published_at = timezone.now()
            form.instance.scheduled_at = None

        elif action == "scheduled":

            date_str = self.request.POST.get("scheduled_date")
            time_str = self.request.POST.get("scheduled_time")

            if not date_str or not time_str:
                form.add_error(
                    None,
                    "Please select both a schedule date and time."
                )
                return self.form_invalid(form)

            try:
                naive_dt = datetime.strptime(
                    f"{date_str} {time_str}",
                    "%Y-%m-%d %H:%M"
                )

                scheduled_at = timezone.make_aware(
                    naive_dt,
                    timezone.get_current_timezone()
                )

            except ValueError:
                form.add_error(
                    None,
                    "Invalid date or time."
                )
                return self.form_invalid(form)

            if scheduled_at <= timezone.now():
                form.add_error(
                    None,
                    "Scheduled time must be in the future."
                )
                return self.form_invalid(form)

            form.instance.status = "scheduled"
            form.instance.scheduled_at = scheduled_at
            form.instance.published_at = None

        else:

            form.instance.status = "draft"
            form.instance.scheduled_at = None
            form.instance.published_at = None

        response = super().form_valid(form)

        if self.object.status == "published":
            notify_mail(self.object)

        messages.success(
            self.request,
            f'"{self.object.title}" saved successfully.'
        )

        return response

class EditPostView(LoginRequiredMixin,UpdateView):
   model = Post
   form_class = PostForm
   login_url = "login.html"
   template_name = "write.html"
   context_object_name = "post"
   success_url = reverse_lazy('home')

   def dispatch(self, request, *args, **kwargs):
      post = self.get_object()
      if (request.user != post.author.author and request.user.user_type!="admin"):
         return HttpResponse("You are not Allowed..")
      return super().dispatch(request, *args, **kwargs)
   def form_valid(self, form):
      form.instance.author = self.get_object().author
      return super().form_valid(form)

class DeletePostView(LoginRequiredMixin,DeleteView):
   model = Post
   login_url = "login.html"
   success_url = reverse_lazy('home')

   def dispatch(self, request, *args, **kwargs):
      post = self.get_object()
      if (request.user != post.author.author and request.user.user_type !="admin"):
               return HttpResponse("You are not Allowed..")
      return super().dispatch(request, *args, **kwargs)
   
   def get(self,request,*args,**kwargs):

      self.object = self.get_object()
      messages.success(self.request,"You have been Deleted post Successfully..")
      self.object.delete()

      return redirect(self.success_url)


class PostDetailView(LoginRequiredMixin,DetailView):
   model = Post
   login_url = "login.html"
   template_name = "post_detail.html"
   context_object_name = "post"
   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['comment_form'] = CommentForm()
      context['comments'] = self.object.comments.filter(approved = True).order_by('-created_at')
      return context

class CommentCreateView(View):
   def post(self,request,slug):
      post = Post.objects.get(slug=slug)
      if not  request.user.is_authenticated :
         return redirect('login')
      form = CommentForm(request.POST)
      if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.post = post
        comment.email = request.user.email
        comment.approved = False
        comment.save()
        messages.success(request,
                     "Your comment has been submitted and is awaiting moderation.")
      return redirect("post_detail",slug=post.slug)

class CommentModerationView(LoginRequiredMixin,View):
   login_url = "login.html"
   def get(self,request):
      if not request.user.is_authenticated :
         return redirect("login")
      if request.user.user_type == 'admin':
            comments = Comment.objects.filter(approved = False).select_related('user','post')
      
      return render(request,"comment_moderation.html",{'comments':comments})

class ApproveCommentView(LoginRequiredMixin,View):
   login_url = "login.html"
   def post(self,request,pk):
      comment = Comment.objects.get(pk=pk)
      if not request.user.is_authenticated:
         return redirect('login')
      if request.user.user_type != 'admin' :
         return HttpResponse("You are not Allowed..")
      comment.approved = True
      comment.save()
      messages.success(request,"Comment approved successfully.")
      return redirect("post_detail", slug=comment.post.slug)
   
class RejectCommentView(LoginRequiredMixin,View):
   login_url = "login.html"
   def post(self,request,pk):
      comment = Comment.objects.get(pk=pk)
      if not request.user.is_authenticated:
               return redirect('login')
      if request.user.user_type != 'admin':
               return HttpResponse("You are not Allowed..")
      comment.delete()
      messages.success(request,"Comment rejected successfully.")
      return redirect("post_detail", slug=comment.post.slug)


class CategoryView(ListView):

    model = Post
    template_name = 'category.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        return Post.objects.filter(
            category__slug=self.kwargs['slug'],
            status='published'
        ).order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = Category.objects.get(
            slug=self.kwargs['slug']
        )

        return context

class SubscriptionView(View):
   def post(self,request,*args,**kwargs):
      form = SubscriptionForm(request.POST)
      if form.is_valid():
         form.save()
         messages.success(request,'You have Successfully Subscibed to New Posts!!')
      else:
         messages.error(request,'Please enter a valid email..')

      return redirect(request.META.get("HTTP_REFERER", "home"))

class TagPostView(ListView):
    model = Post
    template_name = "tag_posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        tag_slug = self.kwargs["slug"]
        return Post.objects.filter(tags__slug=tag_slug,status="published").order_by("-published_at")
   
class LatestPostsFeed(Feed):

    title = "Marginalia — Latest Posts"
    link = "/"
    description = "Latest posts from Marginalia."

    def items(self):
        return Post.objects.filter(
            status="published"
        ).order_by("-published_at")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return strip_tags(item.content)[:300]

    def item_link(self, item):
        return f"/post_detail/{item.slug}/"

    def item_pubdate(self, item):
        return item.published_at

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from .models import Post
# notify_mail is already defined in this file, above HomeView


class DashboardView(LoginRequiredMixin, ListView):
    """
    'My posts' - every post belonging to the logged-in author,
    regardless of status, with tabs to filter by draft / scheduled
    / published. Deliberately scoped to request.user.author_profile
    only: nobody sees, edits, or deletes another author's posts
    from here.
    """
    model = Post
    login_url = "login.html"
    template_name = "dashboard.html"
    context_object_name = "posts"
    paginate_by = 15

    def base_queryset(self):
        return Post.objects.filter(author=self.request.user.author_profile)

    def get_queryset(self):
        qs = self.base_queryset()
        status_filter = self.request.GET.get("status") or ""
        if status_filter in ("draft", "scheduled", "published"):
            qs = qs.filter(status=status_filter)
        return qs.order_by("-updated_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_qs = self.base_queryset()
        context["status_filter"] = self.request.GET.get("status") or ""
        context["total_count"] = base_qs.count()
        context["draft_count"] = base_qs.filter(status="draft").count()
        context["scheduled_count"] = base_qs.filter(status="scheduled").count()
        context["published_count"] = base_qs.filter(status="published").count()
        return context


class OwnPostActionMixin:
    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, slug=kwargs["slug"])
        if (request.user != self.post_obj.author.author
                and request.user.user_type != "admin"):
            return HttpResponse("You are not Allowed..")
        return super().dispatch(request, *args, **kwargs)


class PublishPostView(LoginRequiredMixin, OwnPostActionMixin, View):
    login_url = "login.html"

    def post(self, request, slug):
        post = self.post_obj
        post.status = "published"
        post.published_at = timezone.now()
        post.scheduled_at = None
        post.save(update_fields=["status", "published_at", "scheduled_at"])
        notify_mail(post)
        messages.success(request, f'"{post.title}" is now published.')
        return redirect("dashboard")


class SchedulePostView(LoginRequiredMixin, OwnPostActionMixin, View):
    login_url = "login.html"

    def post(self, request, slug):
        post = self.post_obj

        date_str = request.POST.get("scheduled_date", "")
        time_str = request.POST.get("scheduled_time", "")
        if not date_str or not time_str:
            messages.error(request, "Pick both a date and a time to schedule this post.")
            return redirect("dashboard")

        naive_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        scheduled_at = timezone.make_aware(naive_dt, timezone.get_current_timezone())

        if scheduled_at <= timezone.now():
            messages.error(request, "Scheduled time has to be in the future.")
            return redirect("dashboard")

        post.status = "scheduled"
        post.scheduled_at = scheduled_at
        post.save(update_fields=["status", "scheduled_at"])
        messages.success(
            request,
            f'"{post.title}" is scheduled for {scheduled_at.strftime("%b %-d, %Y at %-I:%M %p")}.',
        )
        return redirect("dashboard")


