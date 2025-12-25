import stripe
from rest_framework import serializers
from .models import Notificacion
from django.http import JsonResponse

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'mensaje', 'leida', 'creado_en']

def create_checkout_session(request):
    try:
        # Crear la sesión de checkout
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item['product']['titulo'],
                        },
                        'unit_amount': int(item['product']['precio'] * 100),  # Precio en centavos
                    },
                    'quantity': item['quantity'],
                } for item in request.data['items']
            ],
            mode='payment',
            success_url='http://localhost:3000/success',  # Cambia la URL al éxito
            cancel_url='http://localhost:3000/cancel',    # Cambia la URL de cancelación
        )
        return JsonResponse({'id': checkout_session.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
from rest_framework import serializers
from .models import Notificacion

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'mensaje', 'leido', 'fecha_creacion']