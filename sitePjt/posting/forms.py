from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "textarea form-control",
                "rows": 30,
                "cols": 50,
                "style": "resize:none;width:500px;",
                "placeholder":"What's Happenning?",
            }
        )
    )
    image = forms.ImageField(required=False)
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "style":"width:500px;",
                "placeholder":"Enter title",
            }
        )
    )
    categories = forms.CharField(
        required=False,
        widget =forms.TextInput(
            attrs={
                "class":"form-control",
                 "style":"width:500px;",
                "placeholder":"Enter categories"
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
            'image',
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'comment',
        ]
    
