from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
        )
    )
    image = forms.ImageField(required=False)
    title = forms.CharField(
        widget=forms.TextInput(
        )
    )
    categories = forms.CharField(
        required=False,
        widget =forms.TextInput(
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
            'image',
            'visibleTo',
        ]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'comment',
        ]
    
