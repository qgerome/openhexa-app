import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.postgres.fields import CIEmailField
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from hexa.core.models import Base


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = CIEmailField(_("email address"), unique=True)
    accepted_tos = models.BooleanField(default=False)

    objects = UserManager()

    @property
    def display_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()

        return self.email

    @property
    def initials(self):
        if self.first_name != "" and self.last_name != "":
            return f"{self.first_name[0]}{self.last_name[0]}".upper()

        return self.email[:2].upper()

    def has_feature_flag(self, code: str) -> bool:
        try:  # Always return True for "forced-activated features"
            Feature.objects.get(code=code, force_activate=True)

            return True
        except Feature.DoesNotExist:
            return self.featureflag_set.filter(feature__code=code).exists()

    def __str__(self):
        return self.display_name


class OrganizationType(models.TextChoices):
    CORPORATE = "CORPORATE", _("Corporate")
    ACADEMIC = "ACADEMIC", _("Academic")
    GOVERNMENT = "GOVERNMENT", _("Government")
    NGO = "NGO", _("Non-governmental")


class Organization(Base):
    organization_type = models.CharField(
        choices=OrganizationType.choices, max_length=100
    )
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    url = models.URLField(blank=True)
    contact_info = models.TextField(blank=True)


class Team(Base):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField("User", through="Membership")


class Membership(Base):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.CASCADE)

    @property
    def display_name(self):
        return f"{self.user.display_name} / {self.team.display_name}"


class Feature(Base):
    code = models.CharField(max_length=200)
    force_activate = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class FeatureFlag(Base):
    feature = models.ForeignKey("Feature", on_delete=models.CharField)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    config = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.feature.code} - {self.user.username}"
