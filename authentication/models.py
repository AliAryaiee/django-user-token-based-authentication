from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


class UserManager(BaseUserManager):
    """
        User Account Manger
    """

    def create_user(self, username: str, phone: str, password=None):
        """
            Creates and Saves a User with the Given Username, Mobile Number and Password.
        """
        if not username:
            raise ValueError("Users Must Have an Valid Username!")
        if not phone:
            raise ValueError("Users Must Have an Valid Mobile Number!")

        user = self.model(
            username=username.strip().lower(),
            phone=phone
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,  username: str, phone: str, password=None):
        """
            Creates and Saves a User with the Given Username, Mobile Number and Password.
        """
        user = self.create_user(
            username,
            phone,
            password
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
        User Account
    """
    username = models.CharField(max_length=256, unique=True)
    phone = models.CharField(max_length=256)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["phone"]

    def __str__(self):
        return self.username
