# accounts/views.py

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
import urllib
from .serializers import CustomTokenObtainPairSerializer, PasswordResetRequestSerializer, PasswordResetSerializer, RegisterSerializer, PerfilSerializer, DireccionSerializer, SolicitudGestorSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from django.http import HttpResponseRedirect, JsonResponse
from rest_framework import generics, permissions
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from .models import SolicitudGestor, Usuario
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        # Redirigir al login del frontend
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}/login?activated=true")
    else:
        return HttpResponse('El enlace de activación es inválido.', status=400)



class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()

            # Enviar email de activación (igual que antes)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_path = reverse('activate', kwargs={'uidb64': uid, 'token': token})
            activation_link = self.request.build_absolute_uri(activation_path)
            subject = "Activa tu cuenta en Tienda Pro"
            message = (
                f"Hola {user.username},\n\n"
                f"Para activar tu cuenta, haz clic en el siguiente enlace:\n{activation_link}\n\n"
                "Si no solicitaste este registro, ignora este mensaje."
            )
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

            return Response(
                {"message": "Usuario creado correctamente. Revisa tu email para activar la cuenta."},
                status=status.HTTP_201_CREATED
            )
        else:
            # Devolver errores con formato JSON para que el frontend los muestre por campo
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class SecureTokenRefreshView(TokenRefreshView):
    """
    Refresca el access token solo si el Origin está en la lista permitida.
    Aprovecha la rotación y blacklist configuradas en settings.
    """
    def post(self, request, *args, **kwargs):
        origin = request.META.get('HTTP_ORIGIN')
        if origin not in settings.ALLOWED_REFRESH_ORIGINS:
            raise AuthenticationFailed('Origen no autorizado para refresh.')

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except InvalidToken as e:
            return Response({'detail': 'Refresh token inválido o expirado.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Al validar, SimpleJWT crea el nuevo par (access, refresh) y blacklistea el antiguo
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def me(request):
    if request.method == 'GET':
        serializer = PerfilSerializer(request.user)  # ← Corregido aquí
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = PerfilSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Recibe en body { "refresh": "<token>" } y lo agrega a la blacklist.
    """
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'error': 'Se requiere refresh token.'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        return Response({'error': 'Token inválido o ya revocado.'},
                        status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Logout exitoso'}, status=status.HTTP_200_OK)


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.tipo == 'admin'

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])  # ← Composición de permisos
def admin_dashboard(request):
    # Lógica para administradores
    return Response({})



@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    email = request.data.get('email')
    user = Usuario.objects.filter(email=email).first()

    if user:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        send_mail(
            subject="Restablecimiento de contraseña",
            message=f"Para restablecer tu contraseña, haz clic en el siguiente enlace:\n{reset_url}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

    # Siempre devolvemos 200 para no revelar si el email existe o no
    return Response({"message": "Si el email existe, se ha enviado un enlace de recuperación."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """
    Endpoint para confirmar el restablecimiento de la contraseña.
    Se espera un JSON con:
      - uid: El uid codificado en base64 (tal como fue generado)
      - token: El token (URL-decoded) enviado en el correo
      - new_password: La nueva contraseña del usuario
    """
    uidb64 = request.data.get('uid')
    # Descodifica el token recibido en la petición (en caso de que esté URL-encoded)
    token = urllib.parse.unquote(request.data.get('token'))
    new_password = request.data.get('new_password')

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        return Response({'error': 'El enlace no es válido.'}, status=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, token):
        # (Opcional) Validar la nueva contraseña (longitud, complejidad, etc.)
        user.set_password(new_password)
        user.save()
        return Response({'message': 'La contraseña se ha restablecido correctamente.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'El token es inválido o ha expirado.'}, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def solicitar_gestor(request):
    user = request.user
    if user.tipo != 'cliente':
        return Response({'error': 'Solo los clientes pueden solicitar ser gestores.'}, status=status.HTTP_400_BAD_REQUEST)

    if SolicitudGestor.objects.filter(usuario=user, estado='pendiente').exists():
        return Response({'error': 'Ya has enviado una solicitud pendiente.'}, status=status.HTTP_400_BAD_REQUEST)

    nombre_tienda = request.data.get('nombre_tienda')
    identificacion_fiscal = request.data.get('identificacion_fiscal')
    telefono = request.data.get('telefono')
    direccion = request.data.get('direccion')

    if not nombre_tienda or not identificacion_fiscal:
        return Response({'error': 'Datos de gestor requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

    solicitud = SolicitudGestor.objects.create(
        usuario=user,
        nombre_tienda=nombre_tienda,
        identificacion_fiscal=identificacion_fiscal,
        telefono=telefono,
        direccion=direccion,
    )
    return Response({'message': 'Solicitud enviada con éxito.'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def listar_solicitudes_gestor(request):
    solicitudes = SolicitudGestor.objects.filter(estado='pendiente')
    serializer = SolicitudGestorSerializer(solicitudes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def aprobar_gestor(request, solicitud_id):
    try:
        solicitud = SolicitudGestor.objects.get(id=solicitud_id, estado='pendiente')
    except SolicitudGestor.DoesNotExist:
        return Response({'error': 'Solicitud no encontrada o ya procesada.'}, status=status.HTTP_404_NOT_FOUND)

    accion = request.data.get('accion')  # 'aprobar' o 'rechazar'
    if accion not in ['aprobar', 'rechazar']:
        return Response({'error': 'Acción inválida.'}, status=status.HTTP_400_BAD_REQUEST)

    if accion == 'aprobar':
        solicitud.estado = 'aprobada'
        solicitud.usuario.tipo = 'gestor'
        solicitud.usuario.save()
    elif accion == 'rechazar':
        solicitud.estado = 'rechazada'

    solicitud.save()
    return Response({'message': f'Solicitud {accion} correctamente.'}, status=status.HTTP_200_OK)
