from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Comentario, Notificacion
from django.urls import reverse

# 1. ALERTA DE NUEVO USUARIO REGISTRADO
@receiver(post_save, sender=User)
def crear_notificacion_usuario(sender, instance, created, **kwargs):
    if created and not instance.is_superuser: # Si se creó y no es el admin
        # Buscamos al admin (asumimos que el ID 1 es el dueño)
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if admin_user:
            Notificacion.objects.create(
                destinatario=admin_user,
                tipo='NU', # Nuevo Usuario
                mensaje=f"Se ha registrado un nuevo usuario: {instance.username}",
                url_destino='/admin/auth/user/' # Opcional: link al admin de usuarios
            )

# 2. ALERTA DE NUEVO COMENTARIO
@receiver(post_save, sender=Comentario)
def crear_notificacion_comentario(sender, instance, created, **kwargs):
    if created:
        admin_user = User.objects.filter(is_superuser=True).first()
        
        # Generamos la URL para ir directo al post
        url_post = reverse('post_detail', args=[instance.post.pk])
        
        if admin_user and instance.usuario != admin_user: # No notificarnos nuestros propios comentarios
            Notificacion.objects.create(
                destinatario=admin_user,
                tipo='NC', # Nuevo Comentario
                mensaje=f"{instance.usuario.username} comentó en: {instance.post.titulo}",
                url_destino=url_post # Req. 4: Redirección al comentario
            )