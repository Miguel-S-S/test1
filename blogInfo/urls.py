from django.urls import path
from . import views

urlpatterns = [
   path('', views.home, name='home'),
    #about
    path('about/', views.about, name='about'),
    #contact
    path('contact/', views.contact, name='contact'),
    #ruta de los comentatios del articulo completo
    path('articulo/<int:pk>/', views.post_detail, name='post_detail'),
    #ruta de la categoria
    path('categoria/<int:category_id>/', views.category_posts, name='categoria_posts'),
    #ruta login
    path('registro/', views.registro, name='registro'),
    #comentario borrar
    path('comentario/borrar/<int:pk>/', views.borrar_comentario, name='borrar_comentario'),
    #comentario editar
    path('comentario/editar/<int:pk>/', views.editar_comentario, name='editar_comentario'),
    #comentar un comentario
    path('comentario/responder/<int:pk>/', views.responder_comentario, name='responder_comentario'),
    
]   

