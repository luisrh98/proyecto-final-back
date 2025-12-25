# urls.py
from django.urls import path
from .views import NotificacionesUsuarioView, marcar_notificacion_leida

urlpatterns = [
    path('notificaciones/', NotificacionesUsuarioView.as_view(), name='notificaciones-usuario'),
    path('notificaciones/<int:pk>/marcar-leida/', marcar_notificacion_leida, name='marcar-notificacion-leida'),
]