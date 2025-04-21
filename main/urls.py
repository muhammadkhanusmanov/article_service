from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet, basename='article')
router.register(r'editors', views.EditorViewSet, basename='editor')
router.register(r'feedbacks', views.FeedbackViewSet, basename='feedback')
router.register(r'statistics', views.StatisticsViewSet, basename='statistics')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', views.UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='user-logout'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Author endpoints
    path('articles/my/', views.AuthorArticleListView.as_view(), name='author-articles'),
    path('articles/<int:pk>/download/', views.ArticleDownloadView.as_view(), name='article-download'),
    
    # Editor endpoints
    path('editor/articles/available/', views.EditorAvailableArticlesView.as_view(), name='editor-available-articles'),
    path('editor/articles/<int:pk>/take/', views.EditorTakeArticleView.as_view(), name='editor-take-article'),
    path('editor/articles/<int:pk>/submit/', views.EditorSubmitArticleView.as_view(), name='editor-submit-article'),
    path('editor/articles/assigned/', views.EditorAssignedArticlesView.as_view(), name='editor-assigned-articles'),
    
    # Admin endpoints
    path('admin/articles/pending/', views.AdminPendingArticlesView.as_view(), name='admin-pending-articles'),
    path('admin/articles/<int:pk>/approve/', views.AdminApproveArticleView.as_view(), name='admin-approve-article'),
    path('admin/articles/<int:pk>/reject/', views.AdminRejectArticleView.as_view(), name='admin-reject-article'),
    
    # Include router URLs
    path('', include(router.urls)),
] 