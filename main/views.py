from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
from django.db.models import Q
from .models import Editor, Article, ArticleAssignment, Feedback, Statistics
from .serializers import (
    UserSerializer, EditorSerializer, ArticleSerializer, 
    ArticleDetailSerializer, ArticleAssignmentSerializer, 
    FeedbackSerializer, StatisticsSerializer, EditorDetailSerializer
)
from rest_framework import serializers

User = get_user_model()

# Authentication Views
class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': serializer.data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    authentication_classes = [BasicAuthentication]
    
    def post(self, request):
        user = request.user        
        
        if not user:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Article Viewsets
class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Article.objects.all()
        elif hasattr(user, 'editor_profile'):
            return Article.objects.filter(
                Q(editor=user.editor_profile) | 
                Q(status=Article.Status.SUBMITTED, is_approved=True)
            )
        else:
            return Article.objects.filter(author=user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# Editor Viewsets
class EditorViewSet(viewsets.ModelViewSet):
    queryset = Editor.objects.all()
    serializer_class = EditorSerializer
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EditorDetailSerializer
        return EditorSerializer

# Feedback Viewsets
class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Feedback.objects.all()
        return Feedback.objects.filter(author=user)
    
    def perform_create(self, serializer):
        article_id = self.request.data.get('article')
        if not article_id:
            raise serializers.ValidationError({'article': 'This field is required.'})
        
        try:
            article = Article.objects.get(id=article_id)
            serializer.save(author=self.request.user, article=article)
        except Article.DoesNotExist:
            raise serializers.ValidationError({'article': 'Article not found.'})

# Statistics Viewsets
class StatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer
    permission_classes = [IsAdminUser]

# Author-specific Views
class AuthorArticleListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        articles = Article.objects.filter(author=request.user)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

class ArticleDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        
        # Check if user is author or editor
        if article.author != request.user and not hasattr(request.user, 'editor_profile'):
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if article is completed
        if article.status != Article.Status.COMPLETED:
            return Response({"error": "Article not ready for download"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Return the file
        response = HttpResponse(article.edited_file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{article.edited_file.name}"'
        return response

# Editor-specific Views
class EditorAvailableArticlesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not hasattr(request.user, 'editor_profile'):
            return Response({"error": "Not an editor"}, status=status.HTTP_403_FORBIDDEN)
        
        editor = request.user.editor_profile
        available_articles = Article.objects.filter(
            status=Article.Status.SUBMITTED,
            is_approved=True,
            edit_type=editor.specialization
        ).exclude(
            assignments__editor=editor,
            assignments__is_active=True
        )
        
        serializer = ArticleSerializer(available_articles, many=True)
        return Response(serializer.data)

class EditorTakeArticleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        if not hasattr(request.user, 'editor_profile'):
            return Response({"error": "Not an editor"}, status=status.HTTP_403_FORBIDDEN)
        
        article = get_object_or_404(Article, pk=pk)
        editor = request.user.editor_profile
        
        # Check if article is available
        if article.status != Article.Status.SUBMITTED or not article.is_approved:
            return Response({"error": "Article not available"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if editor specialization matches
        if article.edit_type != editor.specialization:
            return Response({"error": "Specialization mismatch"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create assignment
        ArticleAssignment.objects.create(article=article, editor=editor)
        
        # Update article status
        article.status = Article.Status.IN_REVIEW
        article.editor = editor
        article.save()
        
        return Response({"message": "Article taken successfully"})

class EditorSubmitArticleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        if not hasattr(request.user, 'editor_profile'):
            return Response({"error": "Not an editor"}, status=status.HTTP_403_FORBIDDEN)
        
        article = get_object_or_404(Article, pk=pk)
        editor = request.user.editor_profile
        
        # Check if editor is assigned to this article
        if article.editor != editor or article.status != Article.Status.IN_REVIEW:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Update article
        article.edited_file = request.FILES.get('edited_file')
        article.comments = request.data.get('comments', '')
        article.status = Article.Status.COMPLETED
        article.save()
        
        # Update assignment
        assignment = ArticleAssignment.objects.get(article=article, editor=editor)
        assignment.is_active = False
        assignment.save()
        
        return Response({"message": "Article submitted successfully"})

class EditorAssignedArticlesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not hasattr(request.user, 'editor_profile'):
            return Response({"error": "Not an editor"}, status=status.HTTP_403_FORBIDDEN)
        
        editor = request.user.editor_profile
        assigned_articles = Article.objects.filter(
            editor=editor,
            assignments__is_active=True
        )
        
        serializer = ArticleSerializer(assigned_articles, many=True)
        return Response(serializer.data)

# Admin-specific Views
class AdminPendingArticlesView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        pending_articles = Article.objects.filter(status=Article.Status.PENDING)
        serializer = ArticleSerializer(pending_articles, many=True)
        return Response(serializer.data)

class AdminApproveArticleView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        
        if article.status != Article.Status.PENDING:
            return Response({"error": "Article not pending"}, status=status.HTTP_400_BAD_REQUEST)
        
        article.is_approved = True
        article.approved_at = timezone.now()
        article.approved_by = request.user
        article.status = Article.Status.SUBMITTED
        article.save()
        
        return Response({"message": "Article approved successfully"})

class AdminRejectArticleView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        
        if article.status != Article.Status.PENDING:
            return Response({"error": "Article not pending"}, status=status.HTTP_400_BAD_REQUEST)
        
        article.status = Article.Status.REJECTED
        article.comments = request.data.get('reason', '')
        article.save()
        
        return Response({"message": "Article rejected successfully"})
