from rest_framework.permissions import BasePermission


class IsShare(BasePermission):
    message = 'Share permission reuired. Awaitting server admin approval.'
    safe_method = ['GET', 'POST']

    def has_permission(self, request, view):
        if request.method in self.safe_method:
            if request.user:
                return request.user.has_perm('share')
        return False

class IsShareImage(BasePermission):
    message = 'Share images permission reuired. Awaitting server admin approval.'
    safe_method = ['GET', 'POST']

    def has_permission(self, request, view):
        if request.method in self.safe_method:
            if request.user:
                return request.user.has_perm('share_image')
        return False

class IsAuthenticatedAndNode(BasePermission):
    message = 'Node Authentication reuired.'
    safe_method = ['GET', 'POST']
    def has_permission(self, request, view):
        if request.method in self.safe_method:
            if request.user.is_authenticated:
                return request.user.node
        return False
