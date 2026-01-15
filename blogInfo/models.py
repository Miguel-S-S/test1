from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.models import User


class Autor(models.Model):
    id_autor = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    biografia = models.TextField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categorías" #aparece en español "Categorías" en el admin

    def __str__(self):
        return self.nombre


class Post(models.Model):
    autor_post = models.ForeignKey("Autor", on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)

    #campo adicional para mejorar el diseno del blog
    subtitulo = models.CharField(max_length=300, blank=True, null=True, verbose_name="Subtítulo")

    #agregar una imagen
    imagen = models.ImageField(upload_to='blog_images/', blank=True, null=True, verbose_name="Imagen de Portada")

    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_publicacion = models.DateTimeField(blank=True, null=True)
    categorias = models.ManyToManyField("Categoria", related_name="posts", blank=True)
    #contador de visitas
    vistas = models.PositiveIntegerField(default=0)
    #sistema de likes (relacion mucho a muchos)
    likes = models.ManyToManyField(User, related_name='blog_posts_likes', blank=True)

    def total_likes(self):
        return self.likes.count()

    class Meta:
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo

    def publicar_articulo(self):
        self.fecha_publicacion = timezone.now()
        self.save()

validador_telefono_corrientes = RegexValidator(
    regex=r'^37\d{8}$',
    message='El teléfono debe tener formato 37XXXXXXXX (10 dígitos, Corrientes). Ej: 3794095682'
)
# MODELO: MENSAJES DE CONTACTO (Req. 5)
class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=100)
    #email = models.EmailField()
    telefono = models.CharField(
        max_length=10,
        verbose_name="Teléfono",
        validators=[validador_telefono_corrientes]
    )
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False) # 

    def __str__(self):
        return f"Mensaje de {self.nombre} - {self.telefono}"


# MODELO: NOTIFICACIONES (Req. 1, 3 y 4)
class Notificacion(models.Model):
    TIPO_CHOICES = (
        ('NU', 'Nuevo Usuario'),
        ('NC', 'Nuevo Comentario'),
    )
    
    # Destinatario suele ser el admin, pero lo dejamos abierto por si escala
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES)
    mensaje = models.CharField(max_length=255)
    leido = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
    
    # Req. 4: Guardamos la URL para redirigir al admin directo al evento
    url_destino = models.CharField(max_length=200, blank=True, null=True) 

    def __str__(self):
        return f"Alerta: {self.mensaje}"


class Comentario(models.Model):
    #vinvular al user de django para identicacion del comentario
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comentarios")
    autor_comentario = models.CharField(max_length=200)
    contenido_comentario = models.TextField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comentarios")
    comentario_padre = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="respuestas"
    )

    class Meta:
        ordering = ['fecha_creacion']

    def __str__(self):
        return f"Comentario de {self.autor_comentario}: {self.contenido_comentario[:30]}..."
