from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
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
    image = forms.ImageField()

    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'contentType',
            'categories',
            'visibility',
            'unlisted',
            'image',
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'comment',
        ]
    
