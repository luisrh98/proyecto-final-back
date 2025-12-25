# accounts/serializers.py
from rest_framework import serializers
from .models import Direccion, SolicitudGestor, Usuario
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework import exceptions

class UsuarioMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'username', 'first_name', 'last_name']

class SolicitudGestorSerializer(serializers.ModelSerializer):
    usuario = UsuarioMiniSerializer(read_only=True)

    class Meta:
        model = SolicitudGestor
        fields = [
            'id',
            'usuario',
            'nombre_tienda',
            'identificacion_fiscal',
            'direccion', # Nueva dirección
            'telefono',  # Nuevo teléfono
            'estado',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['usuario', 'estado', 'fecha_creacion', 'fecha_actualizacion']


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ['id', 'calle', 'ciudad', 'codigo_postal', 'pais']

# accounts/serializers.py
class PerfilSerializer(serializers.ModelSerializer):
    direccion = DireccionSerializer(required=False, allow_null=True)  # Permitir null

    class Meta:
        model = Usuario
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'telefono',
            'direccion',
            'tipo',
        ]
        extra_kwargs = {
            'username': {'read_only': True},
            'tipo': {'read_only': True},
        }

    def update(self, instance, validated_data):
        direccion_data = validated_data.pop('direccion', None)  # Obtener datos de dirección
        
        # Actualizar campos básicos del usuario
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.save()

        # Manejar eliminación/modificación de dirección
        if direccion_data is None:
            # Eliminar dirección si se recibe null
            if hasattr(instance, 'direccion'):
                instance.direccion.delete()
                instance.direccion = None
                instance.save()
        else:
            # Crear/actualizar dirección
            Direccion.objects.update_or_create(
                usuario=instance,
                defaults=direccion_data
            )
        
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password1 = serializers.CharField(write_only=True, required=True, min_length=8)
    telefono = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Usuario
        # No incluimos 'tipo' para que no pueda enviarlo el cliente
        fields = ['username', 'email', 'password', 'password1', 'telefono']
        extra_kwargs = {
            'username': {'min_length': 4},
        }

    def validate_username(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("El nombre de usuario debe tener al menos 4 caracteres.")
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("El nombre de usuario ya está en uso.")
        return value

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("El correo electrónico ya está registrado.")
        return value

    def validate(self, data):
        if data['password'] != data['password1']:
            raise serializers.ValidationError({"password1": "Las contraseñas no coinciden."})
        return data

    def create(self, validated_data):
        validated_data.pop('password1', None)
        # Siempre tipo 'cliente' para mayor seguridad (no confiamos en el frontend)
        tipo = 'cliente'
        telefono = validated_data.pop('telefono', None)

        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            tipo=tipo,
            telefono=telefono
        )
        return user
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Autenticar por username o email
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            # Si falla con username, intenta con email
            user = Usuario.objects.filter(email=username).first()
            if user and user.check_password(password):
                attrs["username"] = user.username  # Forzar username para JWT
            else:
                raise exceptions.AuthenticationFailed("Credenciales inválidas")

        attrs["username"] = user.username  # Asegurar username válido
        data = super().validate(attrs)
        data['user'] = {
            'username': user.username,
            'tipo': user.tipo,
        }
        return data
    

class PasswordResetRequestSerializer(serializers.Serializer):
      email = serializers.EmailField()

      def validate_email(self, value):
          try:
              user = User.objects.get(email=value)
          except User.DoesNotExist:
              raise serializers.ValidationError("No se ha encontrado un usuario con esa dirección de correo.")
          return value

class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    token = serializers.CharField()

    def validate_token(self, value):
        # Lógica para validar el token
        return value