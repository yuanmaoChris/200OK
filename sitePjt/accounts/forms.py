from django import forms
from .models import Author
import uuid
from django.conf import settings
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import (
    authenticate,
    get_user_model
)

User=get_user_model()

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Author
        fields = ('displayName', 'email')

    def clean_password2(self):
        '''
        Check that the two password entries match
        '''
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        '''
                Save the provided password in hashed format
        '''
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.id = uuid.uuid4().urn[9:]
        user.url = "{}author/{}".format(settings.HOSTNAME, user.id)
        user.active = True
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Author
        fields = ('displayName', 'bio', 'github')

    def clean_password(self):
        '''
        Regardless of what the user provides, return the initial value.
        This is done here, rather than on the field, because the
        field does not have access to the initial value
        '''
        return self.initial["password"]

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


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'displayName',
            'github',
            'bio',
        ]
