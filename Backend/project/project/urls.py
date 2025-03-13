from django.contrib import admin 
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import unfold.admin 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    #JWT Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', admin.site.urls),
    path('', include('frontend.urls')),
    path('api/', include('shop.urls')),
    path('api/', include('home.urls')),
    path('api/',include('account.urls')),
    path('api/',include('community.urls')),
    path('api/',include('ai.urls')),

]

handler404 = 'utils.error_view.handler404'
handler500 = 'utils.error_view.handler500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)