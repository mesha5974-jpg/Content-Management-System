from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):

    def create_user(self,email,password=None,**extra_fields):

        extra_fields.setdefault("user_type",'user')
        if email is None:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email,password=password,**extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self,email,password=None, **extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_active",True)
        extra_fields.setdefault("is_superuser",True)
        extra_fields.setdefault("user_type","admin")

        return self.create_user(email,password,**extra_fields)

