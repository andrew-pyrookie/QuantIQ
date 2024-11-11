from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    # User Profile
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Account & Authentication
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    # Investment-Related Attributes
    class RiskProfile(models.TextChoices):
        CONSERVATIVE = 'Conservative', _('Conservative')
        MODERATE = 'Moderate', _('Moderate')
        AGGRESSIVE = 'Aggressive', _('Aggressive')

    risk_profile = models.CharField(max_length=15, choices=RiskProfile.choices, blank=True, null=True)
    investment_goals = models.TextField(blank=True, null=True)
    portfolio_value = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    net_worth = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    class AccountType(models.TextChoices):
        PERSONAL = 'Personal', _('Personal')
        BUSINESS = 'Business', _('Business')

    account_type = models.CharField(max_length=10, choices=AccountType.choices, default=AccountType.PERSONAL)
    preferred_investments = models.JSONField(blank=True, null=True)

    # Notifications & Preferences
    notification_preferences = models.JSONField(blank=True, null=True)
    email_subscriptions = models.BooleanField(default=True)
    daily_digest_opt_in = models.BooleanField(default=False)

    # Security and Compliance
    class KYCStatus(models.TextChoices):
        NOT_STARTED = 'Not Started', _('Not Started')
        IN_PROGRESS = 'In Progress', _('In Progress')
        COMPLETED = 'Completed', _('Completed')

    kyc_status = models.CharField(max_length=15, choices=KYCStatus.choices, default=KYCStatus.NOT_STARTED)
    two_factor_enabled = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    last_failed_login_attempt = models.DateTimeField(blank=True, null=True)
    failed_login_attempts = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    # Relationships and Portfolio
    watchlist = models.ManyToManyField('Investment', blank=True, related_name='watchlisted_by')
    portfolio = models.ManyToManyField('Asset', blank=True, related_name='owned_by')

    def __str__(self):
        return self.username


class Investment(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)  # e.g., stock, crypto, mutual fund

    # Other fields as needed for the investment

    def __str__(self):
        return self.name


class Asset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=4)
    purchase_price = models.DecimalField(max_digits=20, decimal_places=2)

    # Other fields as needed for portfolio tracking

    def __str__(self):
        return f"{self.user.username} - {self.investment.name}"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10)  # e.g., 'buy' or 'sell'
    quantity = models.DecimalField(max_digits=20, decimal_places=4)
    transaction_price = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.investment.name}"

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=50)  # e.g., 'login', 'profile_update'
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"
