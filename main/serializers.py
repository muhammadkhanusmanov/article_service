from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import Editor, Article, ArticleAssignment, Feedback, Statistics

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'password')
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)

class EditorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Editor
        fields = ('id', 'user', 'specialization', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        editor = Editor.objects.create(user=user, **validated_data)
        return editor
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        # Update user fields
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Update editor fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance

class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    editor = EditorSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Article
        fields = (
            'id', 'title', 'author', 'editor', 'original_file', 'edited_file',
            'edit_type', 'status', 'comments', 'created_at', 'updated_at',
            'is_approved', 'approved_at', 'approved_by'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'approved_at', 'approved_by')

class ArticleAssignmentSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)
    editor = EditorSerializer(read_only=True)
    
    class Meta:
        model = ArticleAssignment
        fields = ('id', 'article', 'editor', 'assigned_at', 'is_active')
        read_only_fields = ('id', 'assigned_at')

class FeedbackSerializer(serializers.ModelSerializer):
    article = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all())
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Feedback
        fields = ('id', 'article', 'author', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'created_at', 'author')
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = ('id', 'total_articles', 'active_editors', 'completed_articles', 
                 'average_processing_time', 'last_updated')
        read_only_fields = ('id', 'total_articles', 'active_editors', 'completed_articles', 
                          'average_processing_time', 'last_updated')

# Nested serializers for detailed views
class ArticleDetailSerializer(ArticleSerializer):
    assignments = ArticleAssignmentSerializer(many=True, read_only=True)
    feedbacks = FeedbackSerializer(many=True, read_only=True)
    
    class Meta(ArticleSerializer.Meta):
        fields = ArticleSerializer.Meta.fields + ('assignments', 'feedbacks',)

class EditorDetailSerializer(EditorSerializer):
    assigned_articles = ArticleSerializer(many=True, read_only=True)
    
    class Meta(EditorSerializer.Meta):
        fields = EditorSerializer.Meta.fields + ('assigned_articles',) 