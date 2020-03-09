from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'author', 
            'content', 
            'visibility',
            'category',
        ]


class PostNewForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "textarea form-control",
                "rows": 30,
                "cols": 50,
                "style": "resize:none",
            }
        )
    )
    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'content_type',
            'category',
            'visibility',
            'unlisted',
    
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'content',
        ]
    
