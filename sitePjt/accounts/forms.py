from django import forms
from .models import Author
from django.contrib.auth import (
    authenticate,
    get_user_model
)

User=get_user_model()
class UserLoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('passowrd')

        if email and password:
            user=authenticate(email=email,password=password)
            if not user:
                raise forms.ValidationError('email does not exist')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect password')
        return super(UserLoginForm,self).clean(*args, **kwargs)


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label='Email Address')
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model=User
        fields=[
            'email',
            'displayName',
            'password',
            'url',
            'github',
            'bio',
        ]

    def clean(self,*args,**kwargs):
        email=self.cleaned_data.get('email')
        valid=User.objects.filter(email=email)
        if valid.exists():
            raise forms.ValidationError("Email already being used")
        return super(UserRegisterForm,self).clean(*args,**kwargs)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'email',
        ]
