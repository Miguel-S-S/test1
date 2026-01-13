from django.shortcuts import render, get_object_or_404
from .models import Post, Categoria, Comentario, MensajeContacto, Notificacion
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from .forms import ComentarioForm, ContactoForm
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect

def home(request):
    # 1. Obtener todos los posts de la base
    posts = Post.objects.all()

    # ordenamiento
    orden = request.GET.get('orden') # orden es el parámetro de la URL
    
    if orden == 'antiguedad_asc':
        posts = posts.order_by('fecha_publicacion') # Más viejos primero
    elif orden == 'antiguedad_desc':
        posts = posts.order_by('-fecha_publicacion') # Más nuevos primero (y esta por defecto asi)
    elif orden == 'alfabetico_asc':
        posts = posts.order_by('titulo') # A-Z el nombre del titulo
    elif orden == 'alfabetico_desc':
        posts = posts.order_by('-titulo') # Z-A
    else:
        posts = posts.order_by('-fecha_publicacion') # Default si no hay filtro

    return render(request, 'blogInfo/home.html', {'posts': posts})

def about(request):
    return render(request, 'blogInfo/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            #form.save() guarda directo en la BD (Req. 5)
            form.save()
            
            # Reinicia el form y mandamos exito
            return render(request, 'blogInfo/contact.html', {'form': ContactoForm(), 'exito': True})
    else:
        form = ContactoForm()

    return render(request, 'blogInfo/contact.html', {'form': form})

# para ver el articulo completo 
def post_detail(request, pk):
    # Busca el Post con ese ID, si no lo encuentra, lanza el error 404
    post = get_object_or_404(Post, pk=pk)
    session_key = f'visto_post_{post.pk}'
    if not request.session.get(session_key, False):
        post.vistas += 1  # Incrementa el contador de visitas
        post.save()
        request.session[session_key] = True
    esta_likeado = False
    if post.likes.filter(id=request.user.id).exists():
        esta_likeado = True
    comentarios = post.comentarios.filter(comentario_padre=None).order_by('-fecha_creacion')

    if request.method == 'POST':
        if request.user.is_authenticated:
            form= ComentarioForm(request.POST)
            if form.is_valid():
                comentario = form.save(commit=False)
                comentario.post = post
                comentario.usuario = request.user
                comentario.save()
                return redirect('post_detail', pk=post.pk)
            else:
                return redirect('post_detail', pk=post.pk)
        else:
            return redirect('login')
    else:
        form = ComentarioForm()
            
    return render(request, 'blogInfo/post_detail.html', {
        'post': post,
        'comentarios': comentarios,
        'form': form,
        'esta_likeado': esta_likeado
        })

def responder_comentario(request, pk):
    # busca el comentario que se comenta
    comentario_padre = get_object_or_404(Comentario, pk=pk)

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            respuesta = form.save(commit=False)
            respuesta.usuario = request.user
            respuesta.post = comentario_padre.post
            respuesta.comentario_padre = comentario_padre
            respuesta.save()
            return redirect('post_detail', pk=comentario_padre.post.pk)
    else:
        form = ComentarioForm() 
    return render(request, 'blogInfo/responder.html',{
        'form': form,
        'comentario_padre': comentario_padre
    })

def category_posts(request, category_id):
    # 1. Busca la categoría
    categoria = get_object_or_404(Categoria, id=category_id)
    
    # 2. Filtra los posts de esa categoría
    posts = Post.objects.filter(categorias=categoria)

    # 3. APLICA LA LÓGICA DE ORDENAMIENTO (Igual que en Home)
    orden = request.GET.get('orden')
    
    if orden == 'antiguedad_asc':
        posts = posts.order_by('fecha_publicacion')
    elif orden == 'antiguedad_desc':
        posts = posts.order_by('-fecha_publicacion')
    elif orden == 'alfabetico_asc':
        posts = posts.order_by('titulo')
    elif orden == 'alfabetico_desc':
        posts = posts.order_by('-titulo')
    else:
        posts = posts.order_by('-fecha_publicacion') # Default

    # 4. Renderiza usando el mismo template 'home.html'
    return render(request, 'blogInfo/home.html', {
        'posts': posts,
        'categoria_seleccionada': categoria
    })

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario) # despues de la creacion Inicia sesión al usuario creado recien
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/registro.html', {'form': form})

def borrar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    
    # el dueño solamente o uno del staff puede borrarlo 
    if request.user == comentario.usuario or request.user.is_staff:
        # guarda el ID del post para volver después de borrar
        post_pk = comentario.post.pk 
        comentario.delete()
        return redirect('post_detail', pk=post_pk)
    else:
        # por si se intenta borrar un comentario ajeno
        raise PermissionDenied

# para editar un comentario
def editar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    
    # solo el dueño puede editar
        #pero pero pero... hay que dejar que los miembros del staff tambien editen cualquier comentario por eso esto
    if not request.user.is_staff and request.user != comentario.usuario:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = ComentarioForm(request.POST, instance=comentario)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=comentario.post.pk)
    else:
        # carga del formulario con el texto actual
        form = ComentarioForm(instance=comentario)

    return render(request, 'blogInfo/editar_comentario.html', {'form': form, 'comentario': comentario})


def dashboard(request):
    # Seguridad: Solo staff puede entrar
    if not request.user.is_staff:
        raise PermissionDenied

    # 1. Contadores (Req. 2)
    total_usuarios = User.objects.count()
    total_comentarios = Comentario.objects.count()
    mensajes_no_leidos = MensajeContacto.objects.filter(leido=False).count()

    # 2. Listas de datos
    # Trae los últimos 10 mensajes de contacto
    mensajes = MensajeContacto.objects.all().order_by('-fecha_envio')[:10]
    
    # Trae las notificaciones no leídas
    notificaciones = Notificacion.objects.filter(leido=False).order_by('-fecha')

    return render(request, 'blogInfo/dashboard.html', {
        'total_usuarios': total_usuarios,
        'total_comentarios': total_comentarios,
        'mensajes_no_leidos': mensajes_no_leidos,
        'mensajes': mensajes,
        'notificaciones': notificaciones,
    })

# VISTA AUXILIAR PARA MARCAR NOTIFICACIÓN COMO LEÍDA Y REDIRIGIR
def leer_notificacion(request, pk):
    notificacion = get_object_or_404(Notificacion, pk=pk)
    if request.user == notificacion.destinatario:
        notificacion.leido = True
        notificacion.save()
        # Redirigir a donde diga la notificación (al post o al admin)
        return redirect(notificacion.url_destino or 'dashboard')
    else:
        raise PermissionDenied
    
def dar_like(request, pk):
    # Solo usuarios logueados pueden dar like
    if not request.user.is_authenticated:
        return redirect('login')

    post = get_object_or_404(Post, pk=pk)
    
    # Lógica de "Toggle" (Si ya está, lo quita. Si no está, lo pone)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    # Redirige a la misma página del post
    return HttpResponseRedirect(reverse('post_detail', args=[str(pk)]))