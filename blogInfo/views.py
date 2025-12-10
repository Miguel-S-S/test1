from django.shortcuts import render, get_object_or_404
from .models import Post, Categoria, Comentario
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from .forms import ComentarioForm, ContactoForm

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
    return render(request, 'blogInfo/contact.html')

# para ver el articulo completo 
def post_detail(request, pk):
    # Busca el Post con ese ID, si no lo encuentra, lanza el error 404
    post = get_object_or_404(Post, pk=pk)
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
        'form': form
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
    # 1. Buscamos la categoría
    categoria = get_object_or_404(Categoria, id=category_id)
    
    # 2. Filtramos los posts de esa categoría
    posts = Post.objects.filter(categorias=categoria)

    # 3. APLICAMOS LA LÓGICA DE ORDENAMIENTO (Igual que en Home)
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

    # 4. Renderizamos usando el mismo template 'home.html'
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
        #pero pero pero... hay que dejar que los miembros del staff editen cualquier comentario por eso esto
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

def contact(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            # Aca va la data para enviar el email real. 
            # atributos :
            # nombre = form.cleaned_data['nombre']
            # email = form.cleaned_data['email']
            # mensaje = form.cleaned_data['mensaje']            
            # la misma página pero con un mensaje de envio exitoso
            return render(request, 'blogInfo/contact.html', {'form': ContactoForm(), 'exito': True})
    else:
        form = ContactoForm()

    return render(request, 'blogInfo/contact.html', {'form': form})
