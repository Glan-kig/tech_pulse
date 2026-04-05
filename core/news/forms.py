from django import forms
from .models import Comment
from django.contrib.auth.forms import PasswordChangeForm

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'placeholder': 'Laissez un commentaire constructif...',
                'rows': '3',
            }),
        }

# On peut hériter du formulaire par défaut pour ajouter des classes CSS
class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'}) # Pour Bootstrap ou ton CSS