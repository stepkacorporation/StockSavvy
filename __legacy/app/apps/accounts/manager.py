from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **kwargs):
        """
        Creates and saves a user with the given username, email and password.
        """

        if not username:
            raise ValueError('Username must be provided')
        if not email:
            raise ValueError('Email must be provided')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password=None, **kwargs):
        """
        Creates and saves a superuser with the given username, email and password.
        """

        user = self.create_user(username, email, password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
