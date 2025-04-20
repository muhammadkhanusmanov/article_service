from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Editor, Article, ArticleAssignment, Feedback, Statistics

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'is_active', 'created_at')
    list_filter = ('is_active', 'specialization')
    search_fields = ('user__username', 'user__email', 'specialization')
    ordering = ('-created_at',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'editor', 'edit_type', 'status', 'is_approved', 'created_at')
    list_filter = ('status', 'edit_type', 'is_approved')
    search_fields = ('title', 'author__username', 'editor__user__username')
    readonly_fields = ('created_at', 'updated_at', 'approved_at')
    ordering = ('-created_at',)

@admin.register(ArticleAssignment)
class ArticleAssignmentAdmin(admin.ModelAdmin):
    list_display = ('article', 'editor', 'assigned_at', 'is_active')
    list_filter = ('is_active', 'assigned_at')
    search_fields = ('article__title', 'editor__user__username')
    ordering = ('-assigned_at',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('article', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('article__title', 'author__username', 'comment')
    ordering = ('-created_at',)

@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('total_articles', 'active_editors', 'completed_articles', 'last_updated')
    readonly_fields = ('total_articles', 'active_editors', 'completed_articles', 'average_processing_time', 'last_updated')
