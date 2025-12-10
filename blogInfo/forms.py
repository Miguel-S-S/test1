from django import forms
from .models import Comentario

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

class ContactoForm(forms.Form):
    nombre = forms.CharField(label="Tu Nombre", widget=forms.TextInput(attrs={
        'style': 'width: 100%; padding: 10px; border: 1px solid var(--ink-muted); background: transparent; font-family: var(--font-body);'
    }))
    email = forms.EmailField(label="Tu Email", widget=forms.EmailInput(attrs={
        'style': 'width: 100%; padding: 10px; border: 1px solid var(--ink-muted); background: transparent; font-family: var(--font-body);'
    }))
    mensaje = forms.CharField(label="Mensaje", widget=forms.Textarea(attrs={
        'rows': 5,
        'style': 'width: 100%; padding: 10px; border: 1px solid var(--ink-muted); background: transparent; font-family: var(--font-body);'
    }))