from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class User(AbstractUser):
    """Custom user model for authors"""
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return self.email

class Editor(models.Model):
    """Editor model for article reviewers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='editor_profile')
    specialization = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if not self.user.is_staff and not self.user.is_superuser:
            raise ValidationError('Editor must be a staff member or superuser')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialization}"

class Article(models.Model):
    """Article model for scientific papers"""
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Admin Approval')
        SUBMITTED = 'SUBMITTED', _('Submitted')
        IN_REVIEW = 'IN_REVIEW', _('In Review')
        COMPLETED = 'COMPLETED', _('Completed')
        REJECTED = 'REJECTED', _('Rejected')
    
    class EditType(models.TextChoices):
        GRAMMAR = 'GRAMMAR', _('Grammar Check')
        SCIENTIFIC = 'SCIENTIFIC', _('Scientific Review')
        TECHNICAL = 'TECHNICAL', _('Technical Review')
        COMPREHENSIVE = 'COMPREHENSIVE', _('Comprehensive Review')
    
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    editor = models.ForeignKey(Editor, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_articles')
    original_file = models.FileField(upload_to='articles/original/')
    edited_file = models.FileField(upload_to='articles/edited/', null=True, blank=True)
    edit_type = models.CharField(max_length=20, choices=EditType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_articles')
    
    def clean(self):
        if self.status == self.Status.COMPLETED and not self.edited_file:
            raise ValidationError('Edited file is required for completed articles')
        if self.is_approved and not self.approved_by:
            raise ValidationError('Approved by field is required when article is approved')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class ArticleAssignment(models.Model):
    """Model for tracking article assignments to editors"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='assignments')
    editor = models.ForeignKey(Editor, on_delete=models.CASCADE, related_name='article_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['article', 'editor']
    
    def __str__(self):
        return f"{self.article.title} - {self.editor.user.get_full_name()}"

class Feedback(models.Model):
    """Feedback model for article reviews"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='feedbacks')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_feedbacks')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for {self.article.title}"

class Statistics(models.Model):
    """Statistics model for tracking system usage"""
    total_articles = models.IntegerField(default=0)
    active_editors = models.IntegerField(default=0)
    completed_articles = models.IntegerField(default=0)
    average_processing_time = models.DurationField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Statistics as of {self.last_updated}"
