from django.contrib import admin
from .models import CustomUser,Category,Author,Post,Subscription,Visitor,Comment
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Author)
admin.site.register(Subscription)
admin.site.register(Visitor)
admin.site.register(Comment)

