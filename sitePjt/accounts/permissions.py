from rest_framework.permissions import BasePermission

class IsActivated(BasePermission):
    message = 'Permission reuired. Awaitting server admin approval.'
    safe_method = ['GET', 'POST', 'DELETE']

    def has_permission(self, request, view):
        if request.method in self.safe_method:
            if request.user and request.user.is_authenticated:
                return request.user.is_activated
        return False


class IsActivatedOrReadOnly(BasePermission):
    message = 'Permission reuired. Awaitting server admin approval.'
    safe_method = ['GET', 'HEAD', 'OPTIONS']

    def has_permission(self, request, view):
        if request.method in self.safe_method:
            return True
        
        if request.user:
            return request.user.is_activated

        return False


class IsPostCommentOwner(BasePermission):
    message = 'You must be the owner of this post/comment.'
    safe_method = ['GET', 'POST', 'HEAD', 'OPTIONS']

    def has_permission(self, request, view, obj):
        if request.method in safe_method:
            if request.user:
                return request.user.is_activated
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in safe_method:
            if obj.author:
                return obj.author == request.user
        return False
