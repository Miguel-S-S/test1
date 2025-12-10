from django.contrib import admin
from .models import Autor, Categoria, Post, Comentario

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'user')
    search_fields = ('nombre', 'email')
    
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor_post', 'fecha_publicacion', 'get_categorias')
    search_fields = ('titulo', 'contenido')
    list_filter = ('fecha_publicacion', 'categorias', 'autor_post')
    date_hierarchy = 'fecha_publicacion'
    ordering = ('-fecha_publicacion',)

    def get_categorias(self, obj):
        return ", ".join([c.nombre for c in obj.categorias.all()])
    get_categorias.short_description = 'Categorías'

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'contenido_corto', 'fecha_creacion', 'post')
    list_filter = ('fecha_creacion', 'post')

    def contenido_corto(self, obj):
        return obj.contenido_comentario[:50]
    contenido_corto.short_description = 'Comentario'

