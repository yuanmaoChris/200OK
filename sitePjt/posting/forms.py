from django import forms
from .models import Post, Comment

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
            'contentType',
            'categories',
            'visibility',
            'unlisted',
    
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'comment',
        ]
    
