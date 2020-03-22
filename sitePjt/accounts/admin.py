from django.contrib import admin
from .models import Author
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserChangeForm, UserCreationForm


class AuthorAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'admin', 'active', 'activated')
    list_filter = ('admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'url')}),
        ('Permissions', {'fields': ('admin', 'activated')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'admin'),
        }),
    )
    search_fields = ('email', 'displayName')
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(Author, AuthorAdmin)


