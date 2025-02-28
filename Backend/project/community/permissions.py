from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class IsAuthenticatedWithJWT(BasePermission):
    """
    يسمح فقط للمستخدمين الذين يحملون JWT صالحًا بالوصول إلى الـ API.
    """

    def has_permission(self, request, view):
        """
        يتحقق مما إذا كان الطلب يحتوي على JWT صالح.
        """
        auth = JWTAuthentication()
        try:
            # استخراج بيانات المستخدم من التوكن
            user, _ = auth.authenticate(request)
            if user and user.is_authenticated:
                request.user = user  # تعيين المستخدم في الطلب
                return True
        except AuthenticationFailed:
            return False

        return False
