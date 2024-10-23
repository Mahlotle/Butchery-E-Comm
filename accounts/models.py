from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

# Custom password validation function
def validate_password(password):
    if len(password) < 8:
        raise ValidationError(_('Password must be at least 8 characters long.'))
    if not any(char.isdigit() for char in password):
        raise ValidationError(_('Password must contain at least one digit.'))
    if not any(char.isupper() for char in password):
        raise ValidationError(_('Password must contain at least one uppercase letter.'))
    if not any(char in '!@#$%^&*()-_+=' for char in password):
        raise ValidationError(_('Password must contain at least one special character.'))

# Custom phone number validation function
def validate_phone_number(phone_number):
    if not phone_number.isdigit():
        raise ValidationError(_('Phone number must contain only digits.'))
    if len(phone_number) < 10 or len(phone_number) > 15:
        raise ValidationError(_('Phone number must be between 10 and 15 digits.'))

# Custom account manager for user creation
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        # Validate email and username
        if not email:
            raise ValueError('User must have an email address')

        if not username:
            raise ValueError('User must have a username')

        email = self.normalize_email(email)  # Normalize email
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        if password:
            validate_password(password)  # Validate password
            user.set_password(password)  # Hash the password
        user.is_active = True  # Set user as active by default
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        # Create a superuser with admin rights
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

# Custom user model extending AbstractBaseUser
class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15, validators=[validate_phone_number])  # Adjusted length

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'  # Use email for authentication
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']  # Additional required fields for createsuperuser

    objects = MyAccountManager()  # Link the custom user manager

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.full_name()  # Improved to show full name

    def has_perm(self, perm, obj=None):
        return self.is_admin  # Check if user has a specific permission

    def has_module_perms(self, add_label):
        return True  # User has permission to access the module

# User profile model to store additional user information
class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)  # Link to Account model
    address_line_1 = models.CharField(blank=True, max_length=100)
    address_line_2 = models.CharField(blank=True, max_length=100)
    profile_picture = models.ImageField(blank=True, upload_to='userprofile', null=True)
    city = models.CharField(blank=True, max_length=20)
    state = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)

    def __str__(self):
        return self.user.full_name()  # Improved to show full name

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'.strip()  # Combine address lines
