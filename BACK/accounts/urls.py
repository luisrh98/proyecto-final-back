from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView, RegisterView, aprobar_gestor, listar_solicitudes_gestor, me, activate, password_reset_confirm, password_reset_request, solicitar_gestor, SecureTokenRefreshView, logout
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Endpoint para iniciar sesión
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('logout/', logout, name='logout'),

    # Endpoint para refrescar el token
    path('refresh/', SecureTokenRefreshView.as_view(), name='token_refresh'),

    # Endpoint para registrar nuevos usuarios
    path('register/', RegisterView.as_view(), name='register'),

    # Endpoint para obtener datos del usuario autenticado
    path('me/', me, name='me'),

    path('activate/<uidb64>/<token>/', activate, name='activate'),

    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/', password_reset_confirm, name='password_reset_confirm'),

    path('solicitar-gestor/', solicitar_gestor, name='solicitar_gestor'),

    path('solicitudes-gestor/', listar_solicitudes_gestor, name='listar_solicitudes_gestor'),
    path('aprobar-gestor/<int:solicitud_id>/', aprobar_gestor, name='aprobar_gestor'),
]