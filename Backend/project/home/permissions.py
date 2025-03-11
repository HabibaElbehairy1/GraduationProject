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
            # محاولة المصادقة باستخدام JWT
            auth_result = auth.authenticate(request)

            if auth_result is None:  # التحقق من أن المصادقة لم تفشل
                return False
            
            user, token = auth_result  # تفكيك البيانات إذا كانت صالحة

            if user and user.is_authenticated:
                request.user = user  # تعيين المستخدم في الطلب
                return True

        except AuthenticationFailed:
            return False

        return False
