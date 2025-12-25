from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pedido
from communications.models import Notificacion  # Ajusta el import según tu estructura

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

@receiver(pre_save, sender=Pedido)
def guardar_estado_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            pedido_antiguo = Pedido.objects.get(pk=instance.pk)
            instance._estado_anterior = pedido_antiguo.estado
        except Pedido.DoesNotExist:
            instance._estado_anterior = None
    else:
        instance._estado_anterior = None

@receiver(post_save, sender=Pedido)
def notificar_cambio_estado(sender, instance, created, **kwargs):
    if not created:
        estado_antiguo = getattr(instance, '_estado_anterior', None)
        if estado_antiguo != instance.estado:
            # Crear notificación
            Notificacion.objects.create(
                usuario=instance.usuario,
                mensaje=f"Tu pedido #{instance.id} ha cambiado su estado a: {instance.estado}.",
                leido=False
            )
