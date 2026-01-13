from django import forms
from .models import Comentario, MensajeContacto

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido_comentario'] 
        
        widgets = {
            'contenido_comentario': forms.Textarea(attrs={
                'class': 'comment-box',
                'rows': 4,
                'placeholder': 'Danos tu opinión ...',
                'style': 'width: 100%; padding: 15px; border: 2px solid var(--ink-muted); '
                'background: transparent; '
                'font-family: var(--font-body); '
                'font-size: 1rem;'
            }),
        }
        labels = {
            'contenido_comentario': '' 
        }

class ContactoForm(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'email', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tu nombre', 'style': 'width: 100%; padding: 10px; margin-bottom: 10px;'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Tu email', 'style': 'width: 100%; padding: 10px; margin-bottom: 10px;'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Escribe tu mensaje...', 'rows': 5, 'style': 'width: 100%; padding: 10px;'}),
        }